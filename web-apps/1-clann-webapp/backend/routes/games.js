const express = require('express');
const { authenticateToken, requireCompanyRole } = require('../middleware/auth');
const { 
  getUserGames, 
  getAllGames,
  getDemoGames,
  getGameById, 
  createGame, 
  updateGame,
  isTeamMember,
  getUserTeams 
} = require('../utils/database');
const { generatePresignedUploadUrl, getFileInfo } = require('../utils/s3');

const router = express.Router();

// HLS conversion removed - using direct MP4 playback

// Get user's games (or all games for company admins)
router.get('/', authenticateToken, async (req, res) => {
  try {
    // Company users see all games, regular users see only their team's games
    const games = req.user.role === 'company' 
      ? await getAllGames() 
      : await getUserGames(req.user.id);

    res.json({
      games: games.map(game => ({
        id: game.id,
        title: game.title,
        description: game.description,
        video_url: game.video_url,
        s3_key: game.s3_key,
        thumbnail_url: game.thumbnail_url,
        duration: game.duration,
        status: game.status,
        file_type: game.file_type,
        team_id: game.team_id,
        team_name: game.team_name,
        team_color: game.team_color,
        // Include uploader info for company admins (discretely)
        ...(req.user.role === 'company' && {
          uploaded_by_name: game.uploaded_by_name,
          uploaded_by_email: game.uploaded_by_email
        }),
        created_at: game.created_at,
        updated_at: game.updated_at,
        has_analysis: !!game.ai_analysis
      }))
    });
  } catch (error) {
    console.error('Get games error:', error);
    res.status(500).json({ error: 'Failed to get games' });
  }
});

// Upload a single metadata JSON (company only) to configure video, events, tactical, and team identity
// Expected schema (minimal):
// {
//   "video_url": "https://...mp4",
//   "events_url": "https://...web_events_array-json.json",
//   "tactical_url": "https://...tactical_analysis-json.json",
//   "team_identity": { "home": {...}, "away": {...}, "mapping": {...} }
// }
router.post('/:id/upload-metadata', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const { metadataUrl } = req.body;

    if (!metadataUrl) {
      return res.status(400).json({ error: 'metadataUrl is required' });
    }

    const axios = require('axios');
    console.log('📥 Fetching game metadata from:', metadataUrl);
    const metaResp = await axios.get(metadataUrl, { responseType: 'json' });
    const meta = typeof metaResp.data === 'string' ? JSON.parse(metaResp.data) : metaResp.data;

    const updates = {};
    const currentGame = await getGameById(gameId);
    if (!currentGame) {
      return res.status(404).json({ error: 'Game not found' });
    }

    const currentMetadata = currentGame.metadata || {};
    const tacticalFiles = currentMetadata.tactical_files || {};
    const analysisFiles = currentMetadata.analysis_files || {};

    // 1) Video
    if (meta.video_url) {
      updates.s3_key = meta.video_url;
      console.log('✅ metadata set video_url');
    }

    // 2) Events
    let hasEvents = false;
    if (meta.events_url) {
      try {
        const ev = await axios.get(meta.events_url);
        const eventsData = ev.data;
        const events = Array.isArray(eventsData) ? eventsData : eventsData.events || [];
        if (events.length > 0) {
          updates.ai_analysis = events;
          hasEvents = true;
          console.log(`✅ metadata loaded ${events.length} events`);
        }
        // Also store canonical reference
        analysisFiles.latest_events = {
          url: meta.events_url,
          filename: meta.events_url.split('/').pop() || 'events.json',
          uploaded_at: new Date().toISOString()
        };
      } catch (e) {
        console.log('⚠️ metadata events fetch failed:', e.message);
      }
    }

    // 3) Tactical
    if (meta.tactical_url) {
      try {
        const ta = await axios.get(meta.tactical_url, { responseType: 'text' });
        let analysisData = ta.data;
        if (typeof analysisData === 'string') {
          try { analysisData = JSON.parse(analysisData); } catch {}
        }
        const transformedData = { tactical: {}, analysis: {} };
        if (analysisData && analysisData.tactical_analysis) {
          const t = analysisData.tactical_analysis;
          if (t.red_team) transformedData.tactical.red_team = { content: JSON.stringify(t.red_team, null, 2) };
          if (t.blue_team) transformedData.tactical.blue_team = { content: JSON.stringify(t.blue_team, null, 2) };
        }
        if (analysisData && analysisData.match_overview) transformedData.analysis.match_overview = analysisData.match_overview;
        if (analysisData && analysisData.key_moments) transformedData.analysis.key_moments = analysisData.key_moments;
        if (analysisData && analysisData.manager_recommendations) transformedData.analysis.manager_recommendations = analysisData.manager_recommendations;

        updates.tactical_analysis = JSON.stringify(transformedData);

        tacticalFiles.latest = {
          url: meta.tactical_url,
          filename: meta.tactical_url.split('/').pop() || 'tactical.json',
          uploaded_at: new Date().toISOString()
        };
        console.log('✅ metadata set tactical');
      } catch (e) {
        console.log('⚠️ metadata tactical fetch failed:', e.message);
      }
    }

    // 4) Team identity and match metadata
    const metadataUpdates = {
      ...currentMetadata,
      tactical_files: { ...tacticalFiles },
      analysis_files: { ...analysisFiles }
    };

    // Store teams data (red_team/blue_team with jersey colors)
    if (meta.teams && typeof meta.teams === 'object') {
      metadataUpdates.teams = meta.teams;
      console.log('✅ metadata set teams');
    }

    // Store match counts (goals, shots, etc.)
    if (meta.counts && typeof meta.counts === 'object') {
      metadataUpdates.counts = meta.counts;
      console.log('✅ metadata set counts');
    }

    // Store match_id
    if (meta.match_id) {
      metadataUpdates.match_id = meta.match_id;
      console.log('✅ metadata set match_id');
    }

    // Legacy team_identity support
    if (meta.team_identity && typeof meta.team_identity === 'object') {
      metadataUpdates.team_identity = meta.team_identity;
      console.log('✅ metadata set team_identity');
    }

    updates.metadata = metadataUpdates;

    // 5) Store the metadata URL itself for display in company dashboard
    updates.metadata_url = metadataUrl;
    console.log('✅ metadata_url stored');

    // 6) Status auto-advance
    if (updates.s3_key && (hasEvents || updates.tactical_analysis)) {
      updates.status = 'analyzed';
    }

    const updated = await updateGame(gameId, updates);
    return res.json({
      message: 'Metadata applied successfully',
      applied: {
        video: !!updates.s3_key,
        events: hasEvents,
        tactical: !!updates.tactical_analysis,
        team_identity: !!(meta.team_identity)
      },
      game: { id: updated.id, status: updated.status }
    });
  } catch (error) {
    console.error('Upload metadata error:', error);
    return res.status(500).json({ error: 'Failed to upload metadata' });
  }
});

// Get demo games (visible to all users)
router.get('/demo', authenticateToken, async (req, res) => {
  try {
    const demoGames = await getDemoGames();

    res.json({
      games: demoGames.map(game => ({
        id: game.id,
        title: game.title,
        description: game.description,
        video_url: game.video_url,
        s3_key: game.s3_key,
        thumbnail_url: game.thumbnail_url,
        duration: game.duration,
        status: game.status,
        file_type: game.file_type,
        team_id: game.team_id,
        team_name: game.team_name,
        team_color: game.team_color,
        is_demo: true,
        created_at: game.created_at,
        updated_at: game.updated_at,
        has_analysis: !!game.ai_analysis
      }))
    });
  } catch (error) {
    console.error('Get demo games error:', error);
    res.status(500).json({ error: 'Failed to get demo games' });
  }
});

// Test endpoint for local development (no auth required)
router.get('/demo-test', async (req, res) => {
  try {
    const demoGames = await getDemoGames();

    res.json({
      games: demoGames.map(game => ({
        id: game.id,
        title: game.title,
        description: game.description,
        video_url: game.video_url,
        s3_key: game.s3_key,
        status: game.status,
        ai_analysis: game.ai_analysis,
        tactical_analysis: game.tactical_analysis,
        team_id: game.team_id,
        team_name: game.team_name,
        team_color: game.team_color,
        is_demo: true,
        created_at: game.created_at,
        updated_at: game.updated_at,
        has_analysis: !!game.ai_analysis
      }))
    });
  } catch (error) {
    console.error('Get demo games error:', error);
    res.status(500).json({ error: 'Failed to get demo games' });
  }
});

// All games endpoint for local development (no auth required)
router.get('/all-test', async (req, res) => {
  try {
    const { Pool } = require('pg');
    const isAWSRDS = process.env.DATABASE_URL && process.env.DATABASE_URL.includes('rds.amazonaws.com');
    const pool = new Pool({
      connectionString: process.env.DATABASE_URL || `postgresql://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`,
      ssl: isAWSRDS ? { rejectUnauthorized: false } : false
    });

    const result = await pool.query(`
      SELECT * FROM games 
      ORDER BY created_at DESC 
      LIMIT 20
    `);

    await pool.end();

    res.json({
      games: result.rows.map(game => ({
        id: game.id,
        title: game.title,
        description: game.description,
        video_url: game.video_url,
        s3_key: game.s3_key,
        status: game.status,
        ai_analysis: game.ai_analysis,
        tactical_analysis: game.tactical_analysis,
        team_id: game.team_id,
        team_name: game.team_name,
        team_color: game.team_color,
        is_demo: game.is_demo,
        created_at: game.created_at,
        updated_at: game.updated_at,
        has_analysis: !!game.ai_analysis
      }))
    });
  } catch (error) {
    console.error('Get all games error:', error);
    res.status(500).json({ error: 'Failed to get all games' });
  }
});

// Test upload endpoints for local development (no auth required)
router.post('/:id/upload-analysis-file-test', async (req, res) => {
  try {
    const gameId = req.params.id;
    const { s3Key, originalFilename, fileType } = req.body;

    if (!s3Key) {
      return res.status(400).json({ error: 'S3 key is required' });
    }

    console.log(`📊 Test upload: ${fileType} for game ${gameId}`);
    
    // Fetch events from S3 and save to database
    if (fileType === 'events') {
      const axios = require('axios');
      console.log('📥 Fetching events from:', s3Key);
      
      const eventsResponse = await axios.get(s3Key, {
        responseType: 'text'
      });
      
      let eventsData = eventsResponse.data;
      if (typeof eventsData === 'string') {
        eventsData = JSON.parse(eventsData);
      }
      
      console.log(`📊 Fetched ${eventsData.length} events`);
      
      // Update game with events
      const updatedGame = await updateGame(gameId, {
        ai_analysis: JSON.stringify({ events: eventsData }),
        status: 'analyzed'
      });
      
      if (!updatedGame) {
        return res.status(404).json({ error: 'Game not found' });
      }
      
      console.log('✅ Events saved to database');
    }
    
    res.json({
      message: 'Events uploaded and saved successfully',
      game: { id: gameId },
      fileType: fileType
    });
  } catch (error) {
    console.error('Test upload error:', error);
    res.status(500).json({ error: 'Failed to upload file: ' + error.message });
  }
});

router.post('/:id/upload-tactical-test', async (req, res) => {
  try {
    const gameId = req.params.id;
    const { s3Key, originalFilename, fileType } = req.body;

    if (!s3Key) {
      return res.status(400).json({ error: 'S3 key is required' });
    }

    console.log(`🧠 Test tactical upload for game ${gameId}`);
    
    // Fetch tactical analysis from S3 and save to database
    const axios = require('axios');
    console.log('📥 Fetching tactical analysis from:', s3Key);
    
    const analysisResponse = await axios.get(s3Key, {
      responseType: 'text'
    });
    
    let analysisData = analysisResponse.data;
    if (typeof analysisData === 'string') {
      analysisData = JSON.parse(analysisData);
    }
    
    console.log('📊 Fetched tactical analysis with keys:', Object.keys(analysisData));
    
    // Update game with tactical analysis
    const updatedGame = await updateGame(gameId, {
      tactical_analysis: JSON.stringify(analysisData)
    });
    
    if (!updatedGame) {
      return res.status(404).json({ error: 'Game not found' });
    }
    
    console.log('✅ Tactical analysis saved to database');
    
    res.json({
      message: 'Tactical analysis uploaded and saved successfully',
      game: { id: gameId }
    });
  } catch (error) {
    console.error('Test tactical upload error:', error);
    res.status(500).json({ error: 'Failed to upload tactical file: ' + error.message });
  }
});

router.put('/:id/test', async (req, res) => {
  try {
    const gameId = req.params.id;
    const updateData = req.body;

    console.log(`🔄 Test update game ${gameId}`);
    
    // For now, just return success for testing
    res.json({
      message: 'Test game update successful',
      game: { id: gameId }
    });
  } catch (error) {
    console.error('Test update error:', error);
    res.status(500).json({ error: 'Failed to update game' });
  }
});

// Get single game by ID (for game viewing page)
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const gameId = req.params.id;
    const game = await getGameById(gameId);
    
    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }
    
    // Check if user has access to this game (their game, team member, company admin, or demo game)
    if (req.user.role !== 'company' && !game.is_demo) {
      const userGames = await getUserGames(req.user.id);
      const hasAccess = userGames.some(g => g.id === gameId);
      
      if (!hasAccess) {
        return res.status(403).json({ error: 'Access denied' });
      }
    }
    
    // Convert S3 URL to HTTPS format for browser compatibility
    let s3Url = game.s3_key || game.video_url;
    if (s3Url && s3Url.startsWith('s3://')) {
      // Convert s3://bucket-name/path to https://bucket-name.s3.region.amazonaws.com/path
      const s3Match = s3Url.match(/^s3:\/\/([^\/]+)\/(.*)$/);
      if (s3Match) {
        const bucketName = s3Match[1];
        const objectKey = s3Match[2];
        const region = process.env.AWS_REGION || 'eu-west-1';
        s3Url = `https://${bucketName}.s3.${region}.amazonaws.com/${objectKey}`;
      }
    }

    res.json({ 
      game: {
        id: game.id,
        title: game.title,
        description: game.description,
        video_url: game.video_url,
        s3_key: game.s3_key,
        status: game.status,
        is_demo: game.is_demo || false,
        ai_analysis: game.ai_analysis,
        tactical_analysis: game.tactical_analysis,
        team_id: game.team_id,
        team_name: game.team_name,
        team_color: game.team_color,
        metadata: game.metadata,
        created_at: game.created_at,
        // Video player needs browser-compatible HTTPS URL
        s3Url: s3Url,
        // HLS URL for adaptive streaming
        hlsUrl: game.hls_url
      }
    });
  } catch (error) {
    console.error('Get game error:', error);
    res.status(500).json({ error: 'Failed to get game' });
  }
});

// Save modified events for a game (manual annotation tool)
router.put('/:id/events', authenticateToken, async (req, res) => {
  try {
    const gameId = req.params.id;
    const { events } = req.body;
    
    if (!events || !Array.isArray(events)) {
      return res.status(400).json({ error: 'Events array is required' });
    }
    
    // Get game and check access
    const game = await getGameById(gameId);
    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }
    
    // Check if user has access to modify this game
    if (req.user.role !== 'company' && !game.is_demo) {
      const userGames = await getUserGames(req.user.id);
      const hasAccess = userGames.some(g => g.id === gameId);
      
      if (!hasAccess) {
        return res.status(403).json({ error: 'Access denied' });
      }
    }
    
    // Update the game with modified events using the existing updateGame function
    const updates = {
      events_modified: JSON.stringify(events),
      events_last_modified_by: req.user.id,
      events_last_modified_at: new Date()
    };
    
    const updatedGame = await updateGame(gameId, updates);
    
    res.json({
      success: true,
      events_modified: events,
      modified_by: req.user.id,
      modified_at: new Date()
    });
    
  } catch (error) {
    console.error('Save modified events error:', error);
    res.status(500).json({ error: 'Failed to save modified events' });
  }
});

// Get events for a game (returns modified events if they exist, otherwise AI events)
router.get('/:id/events', authenticateToken, async (req, res) => {
  try {
    const gameId = req.params.id;
    const game = await getGameById(gameId);
    
    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }
    
    // Check access
    if (req.user.role !== 'company' && !game.is_demo) {
      const userGames = await getUserGames(req.user.id);
      const hasAccess = userGames.some(g => g.id === gameId);
      
      if (!hasAccess) {
        return res.status(403).json({ error: 'Access denied' });
      }
    }
    
    // Return modified events if they exist, otherwise AI events
    let events = [];
    if (game.events_modified) {
      events = game.events_modified;
    } else if (game.ai_analysis) {
      // Handle both array format and object format
      events = Array.isArray(game.ai_analysis) 
        ? game.ai_analysis 
        : (game.ai_analysis.events || []);
    }
    const isModified = !!game.events_modified;
    
    res.json({
      events,
      is_modified: isModified,
      modified_by: game.events_last_modified_by,
      modified_at: game.events_last_modified_at,
      original_count: game.ai_analysis ? game.ai_analysis.length : 0,
      current_count: events.length
    });
    
  } catch (error) {
    console.error('Get events error:', error);
    res.status(500).json({ error: 'Failed to get events' });
  }
});

// Reset events to AI analysis (clear modified events)
router.delete('/:id/events', authenticateToken, async (req, res) => {
  try {
    const gameId = req.params.id;
    const game = await getGameById(gameId);
    
    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }
    
    // Check if user has access to modify this game (company users can reset any game)
    if (req.user.role !== 'company' && !game.is_demo) {
      const userGames = await getUserGames(req.user.id);
      const hasAccess = userGames.some(g => g.id === gameId);
      
      if (!hasAccess) {
        return res.status(403).json({ error: 'Access denied' });
      }
    }
    
    // Check if there are modified events to reset
    if (!game.events_modified) {
      return res.status(400).json({ error: 'No modified events to reset' });
    }
    
    // Clear the modified events
    const updates = {
      events_modified: null,
      events_last_modified_by: null,
      events_last_modified_at: null
    };
    
    await updateGame(gameId, updates);
    
    const aiEventsCount = game.ai_analysis ? game.ai_analysis.length : 0;
    
    res.json({
      success: true,
      message: `Events reset to AI analysis (${aiEventsCount} events)`,
      ai_events_count: aiEventsCount
    });
    
  } catch (error) {
    console.error('Reset events error:', error);
    res.status(500).json({ error: 'Failed to reset events' });
  }
});

// Upload VEO URL (create new game)
router.post('/', authenticateToken, async (req, res) => {
  try {
    const { title, description, videoUrl, teamId } = req.body;

    // Validation
    if (!title || !videoUrl || !teamId) {
      return res.status(400).json({ 
        error: 'Title, video URL, and team ID are required' 
      });
    }

    // Validate VEO URL format (basic check)
    if (!videoUrl.includes('veo.co') && !videoUrl.includes('localhost')) {
      return res.status(400).json({ 
        error: 'Invalid VEO URL format' 
      });
    }

    // Check if user is a member of the team
    const isMember = await isTeamMember(req.user.id, teamId);
    if (!isMember && req.user.role !== 'company') {
      return res.status(403).json({ 
        error: 'You are not a member of this team' 
      });
    }

    // Create game
    const newGame = await createGame(
      title,
      description || '',
      videoUrl,
      teamId,
      req.user.id,
      'veo'
    );

    res.status(201).json({
      message: 'VEO URL uploaded successfully',
      game: {
        id: newGame.id,
        title: newGame.title,
        description: newGame.description,
        video_url: newGame.video_url,
        team_id: newGame.team_id,
        status: newGame.status,
        file_type: newGame.file_type,
        created_at: newGame.created_at
      }
    });
  } catch (error) {
    console.error('Create game error:', error);
    res.status(500).json({ error: 'Failed to upload VEO URL' });
  }
});

// Get game by ID with analysis
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const gameId = req.params.id;
    const game = await getGameById(gameId);

    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }

    // Check if user has access to this game
    const isMember = await isTeamMember(req.user.id, game.team_id);
    if (!isMember && req.user.role !== 'company') {
      return res.status(403).json({ 
        error: 'You do not have access to this game' 
      });
    }

    // Return game with analysis
    res.json({
      game: {
        id: game.id,
        title: game.title,
        description: game.description,
        video_url: game.video_url,
        s3_key: game.s3_key,
        original_filename: game.original_filename,
        file_size: game.file_size,
        file_type: game.file_type,
        thumbnail_url: game.thumbnail_url,
        duration: game.duration,
        status: game.status,
        team_id: game.team_id,
        team_name: game.team_name,
        team_color: game.team_color,
        uploaded_by: game.uploaded_by,
        uploaded_by_name: game.uploaded_by_name,
        uploaded_by_email: game.uploaded_by_email,
        ai_analysis: game.ai_analysis,
        tactical_analysis: game.tactical_analysis,
        metadata: game.metadata,
        created_at: game.created_at,
        updated_at: game.updated_at
      }
    });
  } catch (error) {
    console.error('Get game error:', error);
    res.status(500).json({ error: 'Failed to get game' });
  }
});

// Upload S3 video file (company only)
router.post('/:id/upload-video', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const { s3Key, originalFilename, fileSize, duration } = req.body;

    if (!s3Key) {
      return res.status(400).json({ error: 'S3 key is required' });
    }

    // Update game with S3 information
    const updatedGame = await updateGame(gameId, {
      s3_key: s3Key,
      original_filename: originalFilename,
      file_size: fileSize,
      duration: duration,
      file_type: 'upload'
    });

    if (!updatedGame) {
      return res.status(404).json({ error: 'Game not found' });
    }

    // Auto-trigger HLS conversion
    // await autoTriggerHLSConversion(gameId, s3Key); // Disabled - MediaConvert removed

    res.json({
      message: 'Video uploaded successfully',
      game: {
        id: updatedGame.id,
        title: updatedGame.title,
        s3_key: updatedGame.s3_key,
        status: updatedGame.status,
        updated_at: updatedGame.updated_at
      }
    });
  } catch (error) {
    console.error('Upload video error:', error);
    res.status(500).json({ error: 'Failed to upload video' });
  }
});

// Upload S3 events file (company only)
router.post('/:id/upload-events', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const { s3Key, originalFilename } = req.body;

    if (!s3Key) {
      return res.status(400).json({ error: 'S3 key is required' });
    }

    // Fetch events from S3 URL using axios (already imported in the project)
    const axios = require('axios');
    const eventsResponse = await axios.get(s3Key, {
      responseType: 'text' // Get as text first to avoid auto-parsing issues
    });
    
    let eventsData = eventsResponse.data;
    
    // Handle different response types - sometimes S3 returns string, sometimes object
    if (typeof eventsData === 'string') {
      try {
        eventsData = JSON.parse(eventsData);
      } catch (parseError) {
        console.error('Failed to parse JSON string:', parseError);
        return res.status(400).json({ error: 'Invalid JSON format in S3 file' });
      }
    }
    
    const events = Array.isArray(eventsData) ? eventsData : eventsData.events || [];
    
    console.log(`📊 Fetched ${events.length} events from ${s3Key}`);
    console.log('📋 Sample event:', events[0]);
    
    // Store events URL in metadata along with the events data
    const currentGame = await getGameById(gameId);
    if (!currentGame) {
      return res.status(404).json({ error: 'Game not found' });
    }

    const currentMetadata = currentGame.metadata || {};
    const eventsFiles = currentMetadata.events_files || {};
    
    // Determine file type from filename
    const filename = originalFilename?.toLowerCase() || s3Key.toLowerCase();
    let eventsType = 'general';
    if (filename.includes('web_events_array')) eventsType = 'web_events_array';
    else if (filename.includes('web_events')) eventsType = 'web_events';
    else if (filename.includes('enhanced_events')) eventsType = 'enhanced_events';

    eventsFiles[eventsType] = {
      url: s3Key,
      filename: originalFilename,
      uploaded_at: new Date().toISOString()
    };
    
    // Convert events to JSON string for PostgreSQL JSONB storage
    console.log('📝 About to store events in database...');
    console.log('📝 First few events:', JSON.stringify(events.slice(0, 2), null, 2));
    
    const updatedGame = await updateGame(gameId, {
      ai_analysis: JSON.stringify(events), // Convert to JSON string for PostgreSQL
      status: 'analyzed',
      metadata: {
        ...currentMetadata,
        events_files: eventsFiles
      }
    });

    if (!updatedGame) {
      return res.status(404).json({ error: 'Game not found' });
    }

    res.json({
      message: 'Events uploaded successfully',
      game: {
        id: updatedGame.id,
        title: updatedGame.title,
        status: updatedGame.status,
        events_count: events.length,
        events_type: eventsType,
        events_url: s3Key,
        updated_at: updatedGame.updated_at
      }
    });
  } catch (error) {
    console.error('Upload events error:', error);
    if (error.response) {
      console.error('HTTP Error:', error.response.status, error.response.statusText);
    }
    res.status(500).json({ error: 'Failed to upload even3ts: ' + error.message });
  }
});

// Upload chunks base URL (company only)
router.post('/:id/upload-chunks', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const { chunksBaseUrl } = req.body;

    if (!chunksBaseUrl) {
      return res.status(400).json({ error: 'Chunks base URL is required' });
    }

    console.log(`📦 Setting chunks base URL for game ${gameId}:`, chunksBaseUrl);

    // Update the game with the chunks base URL
    const updatedGame = await updateGame(gameId, {
      chunks_base_url: chunksBaseUrl
    });

    console.log('✅ Chunks base URL saved successfully');

    res.json({
      success: true,
      message: 'Chunks base URL saved successfully',
      chunks_base_url: chunksBaseUrl,
      updated_at: updatedGame.updated_at
    });
  } catch (error) {
    console.error('Upload chunks URL error:', error);
    res.status(500).json({ error: 'Failed to save chunks URL: ' + error.message });
  }
});

// Upload events JSON directly (for AI pipeline automation)
router.post('/:id/upload-events-direct', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const { events, source = 'ai_pipeline' } = req.body;

    if (!events || !Array.isArray(events)) {
      return res.status(400).json({ error: 'Events array is required' });
    }

    console.log(`📊 Direct upload: ${events.length} events for game ${gameId}`);
    console.log('📋 Sample event:', events[0]);
    
    // Convert events to JSON string for PostgreSQL JSONB storage
    const updatedGame = await updateGame(gameId, {
      ai_analysis: JSON.stringify(events),
      status: 'analyzed'
    });

    if (!updatedGame) {
      return res.status(404).json({ error: 'Game not found' });
    }

    res.json({
      message: 'Events uploaded successfully via direct JSON',
      game: {
        id: updatedGame.id,
        title: updatedGame.title,
        status: updatedGame.status,
        events_count: events.length,
        source: source,
        updated_at: updatedGame.updated_at
      }
    });
  } catch (error) {
    console.error('Direct events upload error:', error);
    res.status(500).json({ error: 'Failed to upload events: ' + error.message });
  }
});

// Upload S3 tactical file (company only) 
router.post('/:id/upload-tactical', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const { s3Key, originalFilename, fileType } = req.body;

    if (!s3Key) {
      return res.status(400).json({ error: 'S3 key is required' });
    }

    // Handle both full S3 URLs and just keys
    let actualS3Key = s3Key;
    if (s3Key.startsWith('https://')) {
      // Extract key from full S3 URL
      const urlParts = s3Key.split('/');3
      actualS3Key = urlParts.slice(3).join('/'); // Remove bucket name and domain
    }

    // Fetch tactical analysis from S3 URL
    const axios = require('axios');
    console.log('📥 Fetching tactical analysis from:', s3Key);
    const analysisResponse = await axios.get(s3Key, {
      responseType: 'text' // Get as text first to avoid auto-parsing issues
    });
    
    let analysisData = analysisResponse.data;
    
    // Handle different response types - sometimes S3 returns string, sometimes object
    if (typeof analysisData === 'string') {
      try {
        analysisData = JSON.parse(analysisData);
      } catch (parseError) {
        console.error('Failed to parse JSON string:', parseError);
        return res.status(400).json({ error: 'Invalid JSON format in S3 file' });
      }
    }
    
    console.log('📊 Fetched tactical analysis with keys:', Object.keys(analysisData));
    console.log('📋 Sample analysis preview:', JSON.stringify(analysisData).substring(0, 200) + '...');

    // Transform data structure to match frontend expectations
    const transformedData = {
      tactical: {},
      analysis: {}
    };

    // Handle both nested (tactical_analysis.red_team) and direct (red_team) structures
    let tacticalData = analysisData;
    if (analysisData.tactical_analysis) {
      tacticalData = analysisData.tactical_analysis;
    }
    
    // Transform team data
    if (tacticalData.red_team) {
      transformedData.tactical.red_team = {
        content: JSON.stringify(tacticalData.red_team, null, 2)
      };
    }
    
    if (tacticalData.blue_team) {
      transformedData.tactical.blue_team = {
        content: JSON.stringify(tacticalData.blue_team, null, 2)
      };
    }
    
    // Handle match summary
    if (tacticalData.match_summary) {
      transformedData.analysis.match_summary = tacticalData.match_summary;
    }

    // Include other analysis data
    if (analysisData.match_overview) {
      transformedData.analysis.match_overview = analysisData.match_overview;
    }
    
    if (analysisData.key_moments) {
      transformedData.analysis.key_moments = analysisData.key_moments;
    }
    
    if (analysisData.manager_recommendations) {
      transformedData.analysis.manager_recommendations = analysisData.manager_recommendations;
    }

    console.log('🔄 Transformed data structure:', Object.keys(transformedData));
    console.log('🔄 Tactical keys:', Object.keys(transformedData.tactical));

    // Store tactical analysis URL in metadata AND populate tactical_analysis field
    const currentGame = await getGameById(gameId);
    if (!currentGame) {
      return res.status(404).json({ error: 'Game not found' });
    }

    const currentMetadata = currentGame.metadata || {};
    const tacticalFiles = currentMetadata.tactical_files || {};
    
    // Determine file type from filename or explicit type
    let tacticalType = fileType;
    if (!tacticalType) {
      const filename = originalFilename?.toLowerCase() || s3Key.toLowerCase();
      if (filename.includes('red_team')) tacticalType = 'red_team';
      else if (filename.includes('yellow_team')) tacticalType = 'yellow_team';
      else if (filename.includes('coaching') || filename.includes('insights')) tacticalType = 'coaching_insights';
      else if (filename.includes('summary')) tacticalType = 'match_summary';
      else tacticalType = 'general';
    }

    tacticalFiles[tacticalType] = {
      url: s3Key,
      filename: originalFilename,
      uploaded_at: new Date().toISOString()
    };

    // Always keep a canonical pointer to the latest tactical file so the UI can display it directly
    tacticalFiles.latest = {
      url: s3Key,
      filename: originalFilename,
      uploaded_at: new Date().toISOString()
    };

    const updatedGame = await updateGame(gameId, {
      metadata: {
        ...currentMetadata,
        tactical_files: tacticalFiles
      },
      tactical_analysis: JSON.stringify(transformedData), // Store the transformed content for frontend display
      status: 'analyzed'
    });

    res.json({
      message: 'Tactical analysis uploaded successfully',
      game: {
        id: updatedGame.id,
        title: updatedGame.title,
        status: updatedGame.status,
        tactical_type: tacticalType,
        has_tactical: true,
        updated_at: updatedGame.updated_at
      }
    });
  } catch (error) {
    console.error('Upload tactical error:', error);
    res.status(500).json({ error: 'Failed to upload tactical analysis' });
  }
});

// Get tactical analysis content for a game
router.get('/:id/tactical-analysis', authenticateToken, async (req, res) => {
  try {
    const gameId = req.params.id;
    const game = await getGameById(gameId);

    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }

    const metadata = game.metadata || {};
    const tacticalFiles = metadata.tactical_files || {};
    const analysisFiles = metadata.analysis_files || {};

    // Fetch content from tactical files
    const tacticalContent = {};
    
    for (const [type, fileInfo] of Object.entries(tacticalFiles)) {
      if (fileInfo && fileInfo.url) {
        try {
          const axios = require('axios');
          const response = await axios.get(fileInfo.url, { responseType: 'text' });
          tacticalContent[type] = {
            content: response.data,
            filename: fileInfo.filename,
            uploaded_at: fileInfo.uploaded_at
          };
        } catch (error) {
          console.error(`Failed to fetch tactical file ${type}:`, error);
          tacticalContent[type] = {
            content: `Error loading content: ${error.message}`,
            filename: fileInfo.filename,
            uploaded_at: fileInfo.uploaded_at
          };
        }
      }
    }

    // Also fetch analysis files content 
    const analysisContent = {};
    for (const [type, fileInfo] of Object.entries(analysisFiles)) {
      if (fileInfo && fileInfo.url) {
        try {
          const axios = require('axios');
          const response = await axios.get(fileInfo.url, { responseType: 'text' });
          analysisContent[type] = {
            content: response.data,
            filename: fileInfo.filename,
            uploaded_at: fileInfo.uploaded_at
          };
        } catch (error) {
          console.error(`Failed to fetch analysis file ${type}:`, error);
          analysisContent[type] = {
            content: `Error loading content: ${error.message}`,
            filename: fileInfo.filename,
            uploaded_at: fileInfo.uploaded_at
          };
        }
      }
    }

    res.json({
      tactical: tacticalContent,
      analysis: analysisContent,
      game: {
        id: game.id,
        title: game.title,
        team_name: game.team_name
      }
    });

  } catch (error) {
    console.error('Get tactical analysis error:', error);
    res.status(500).json({ error: 'Failed to get tactical analysis' });
  }
});

// Upload S3 analysis file (company only) - for timeline, accuracy, ground truth, etc.
router.post('/:id/upload-analysis-file', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const { s3Key, originalFilename, fileType } = req.body;

    if (!s3Key) {
      return res.status(400).json({ error: 'S3 key is required' });
    }

    // Handle both full S3 URLs and just keys
    let actualS3Key = s3Key;
    if (s3Key.startsWith('https://')) {
      // Extract key from full S3 URL
      const urlParts = s3Key.split('/');
      actualS3Key = urlParts.slice(3).join('/'); // Remove bucket name and domain
    }

    // Store analysis file URL in metadata
    const currentGame = await getGameById(gameId);
    if (!currentGame) {
      return res.status(404).json({ error: 'Game not found' });
    }

    const currentMetadata = currentGame.metadata || {};
    const analysisFiles = currentMetadata.analysis_files || {};
    
    // Determine file type from filename or explicit type
    let analysisType = fileType;
    if (!analysisType) {
      const filename = originalFilename?.toLowerCase() || s3Key.toLowerCase();
      if (filename.includes('ground_truth')) analysisType = 'ground_truth';
      else if (filename.includes('complete_timeline')) analysisType = 'complete_timeline';
      else if (filename.includes('validated_timeline')) analysisType = 'validated_timeline';
      else if (filename.includes('accuracy')) analysisType = 'accuracy_comparison';
      else analysisType = 'general';
    }

    analysisFiles[analysisType] = {
      url: actualS3Key,
      filename: originalFilename,
      uploaded_at: new Date().toISOString()
    };

    const updatedGame = await updateGame(gameId, {
      metadata: {
        ...currentMetadata,
        analysis_files: analysisFiles
      }
    });

    res.json({
      message: 'Analysis file uploaded successfully',
      game: {
        id: updatedGame.id,
        title: updatedGame.title,
        status: updatedGame.status,
        analysis_type: analysisType,
        updated_at: updatedGame.updated_at
      }
    });
  } catch (error) {
    console.error('Upload analysis file error:', error);
    res.status(500).json({ error: 'Failed to upload analysis file' });
  }
});

// Upload analysis JSON (company only)
router.post('/:id/analysis', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const { analysis } = req.body;

    if (!analysis) {
      return res.status(400).json({ error: 'Analysis data is required' });
    }

    // Validate and clean analysis structure
    let cleanAnalysis;
    if (typeof analysis === 'string') {
      try {
        cleanAnalysis = JSON.parse(analysis);
      } catch (e) {
        return res.status(400).json({ error: 'Analysis string is not valid JSON: ' + e.message });
      }
    } else if (typeof analysis === 'object') {
      cleanAnalysis = analysis;
    } else {
      return res.status(400).json({ error: 'Analysis must be a valid JSON object or string' });
    }

    // Additional validation - ensure it's serializable
    try {
      JSON.stringify(cleanAnalysis);
    } catch (e) {
      return res.status(400).json({ error: 'Analysis contains non-serializable data: ' + e.message });
    }

    // Update game with analysis
    const updatedGame = await updateGame(gameId, {
      ai_analysis: cleanAnalysis
    });

    if (!updatedGame) {
      return res.status(404).json({ error: 'Game not found' });
    }

    res.json({
      message: 'Analysis uploaded successfully',
      game: {
        id: updatedGame.id,
        title: updatedGame.title,
        status: updatedGame.status,
        has_analysis: true,
        updated_at: updatedGame.updated_at
      }
    });
  } catch (error) {
    console.error('Upload analysis error:', error);
    res.status(500).json({ error: 'Failed to upload analysis' });
  }
});

// Add S3 analysis files for a game (company only) - Enhanced VM Processing
router.post('/:id/analysis-files', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const { s3AnalysisFiles } = req.body; // JSON object of S3 URLs

    if (!s3AnalysisFiles || typeof s3AnalysisFiles !== 'object') {
      return res.status(400).json({ error: 's3AnalysisFiles JSON object required' });
    }

    console.log('🧠 Processing VM analysis files:', Object.keys(s3AnalysisFiles));

    // Enhanced VM Processing: Extract key files for video player
    let gameUpdates = {
      // Note: s3_analysis_files column doesn't exist, storing in metadata instead
      metadata: { s3_analysis_files: s3AnalysisFiles }
    };

    // 1. Extract video URL
    const videoFile = Object.keys(s3AnalysisFiles).find(key => 
      key.includes('video.mp4') || key.includes('.mp4')
    );
    if (videoFile && s3AnalysisFiles[videoFile]) {
      gameUpdates.s3_key = s3AnalysisFiles[videoFile];
      console.log('✅ Found video URL:', s3AnalysisFiles[videoFile]);
    }

    // 2. Process events from web_events.json or web_events_array.json  
    const eventsFile = Object.keys(s3AnalysisFiles).find(key => 
      key.includes('web_events') && key.includes('.json')
    );
    
    if (eventsFile && s3AnalysisFiles[eventsFile]) {
      try {
        console.log('📥 Fetching events from:', s3AnalysisFiles[eventsFile]);
        const eventsResponse = await fetch(s3AnalysisFiles[eventsFile]);
        
        if (eventsResponse.ok) {
          const eventsData = await eventsResponse.json();
          
          // Handle both array and {events: [...]} formats
          const events = Array.isArray(eventsData) ? eventsData : eventsData.events || [];
          
          if (events.length > 0) {
            gameUpdates.ai_analysis = events;
            console.log(`✅ Loaded ${events.length} events for video player`);
          }
        } else {
          console.log('⚠️ Could not fetch events file (non-critical)');
        }
      } catch (fetchError) {
        console.log('⚠️ Error fetching events (non-critical):', fetchError.message);
      }
    }

    // 3. Auto-mark as analyzed if we have video + events
    if (gameUpdates.s3_key && gameUpdates.ai_analysis) {
      gameUpdates.status = 'analyzed';
      console.log('🎉 Auto-marking game as analyzed (has video + events)');
    }

    const updatedGame = await updateGame(gameId, gameUpdates);

    if (!updatedGame) {
      return res.status(404).json({ error: 'Game not found' });
    }

    res.json({
      message: 'VM analysis files processed successfully',
      filesProcessed: Object.keys(s3AnalysisFiles).length,
      hasVideo: !!gameUpdates.s3_key,
      hasEvents: !!gameUpdates.ai_analysis,
      autoAnalyzed: gameUpdates.status === 'analyzed',
      game: {
        id: updatedGame.id,
        title: updatedGame.title,
        status: updatedGame.status,
        s3_analysis_files: updatedGame.s3_analysis_files
      }
    });
  } catch (error) {
    console.error('Update analysis files error:', error);
    res.status(500).json({ error: 'Failed to update analysis files' });
  }
});

// Mark game as analyzed (company only)
router.put('/:id/status', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const { status } = req.body;

    if (!status || !['pending', 'analyzed'].includes(status)) {
      return res.status(400).json({ 
        error: 'Status must be either "pending" or "analyzed"' 
      });
    }

    // Update game status
    const updatedGame = await updateGame(gameId, { status });

    if (!updatedGame) {
      return res.status(404).json({ error: 'Game not found' });
    }

    res.json({
      message: `Game marked as ${status}`,
      game: {
        id: updatedGame.id,
        title: updatedGame.title,
        status: updatedGame.status,
        updated_at: updatedGame.updated_at
      }
    });
  } catch (error) {
    console.error('Update status error:', error);
    res.status(500).json({ error: 'Failed to update game status' });
  }
});

// Update game metadata (for auto-upload script)
router.put('/:id', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const updateData = req.body;

    console.log(`🔄 Updating game ${gameId} with:`, Object.keys(updateData));

    const updatedGame = await updateGame(gameId, updateData);

    if (!updatedGame) {
      return res.status(404).json({ error: 'Game not found' });
    }

    res.json({
      message: 'Game updated successfully',
      game: {
        id: updatedGame.id,
        title: updatedGame.title,
        status: updatedGame.status,
        video_url: updatedGame.video_url,
        metadata: updatedGame.metadata,
        updated_at: updatedGame.updated_at
      }
    });
  } catch (error) {
    console.error('Update game error:', error);
    res.status(500).json({ error: 'Failed to update game' });
  }
});

// Generate pre-signed URL for direct file upload
router.post('/upload/presigned-url', authenticateToken, async (req, res) => {
  try {
    const { fileName, fileType, fileSize, teamId } = req.body;

    // Validation
    if (!fileName || !fileType || !fileSize || !teamId) {
      return res.status(400).json({ 
        error: 'Missing required fields: fileName, fileType, fileSize, teamId' 
      });
    }

    // Check if user is member of the team
    const isMember = await isTeamMember(req.user.id, teamId);
    if (!isMember) {
      return res.status(403).json({ 
        error: 'You are not a member of this team' 
      });
    }

    // Generate presigned URL
    const uploadData = await generatePresignedUploadUrl(fileName, fileType, fileSize);

    res.json({
      success: true,
      uploadUrl: uploadData.uploadUrl,
      s3Key: uploadData.s3Key,
      publicUrl: uploadData.publicUrl
    });
  } catch (error) {
    console.error('Presigned URL generation error:', error);
    res.status(400).json({ error: error.message || 'Failed to generate upload URL' });
  }
});

// Confirm file upload and create game record
router.post('/upload/confirm', authenticateToken, async (req, res) => {
  try {
    const { 
      title, 
      description, 
      teamId, 
      s3Key, 
      originalFilename, 
      fileSize,
      fileType 
    } = req.body;

    // Validation
    if (!title || !teamId || !s3Key || !originalFilename) {
      return res.status(400).json({ 
        error: 'Missing required fields: title, teamId, s3Key, originalFilename' 
      });
    }

    // Check if user is member of the team
    const isMember = await isTeamMember(req.user.id, teamId);
    if (!isMember) {
      return res.status(403).json({ 
        error: 'You are not a member of this team' 
      });
    }

    // Verify file exists in S3
    try {
      await getFileInfo(s3Key);
    } catch (error) {
      return res.status(400).json({ 
        error: 'File not found in S3. Upload may have failed.' 
      });
    }

    // Create game record in database
    const newGame = await createGame(
      title.trim(),
      description?.trim() || '',
      null, // video_url (this is for VEO URLs)
      teamId,
      req.user.id,
      'upload' // file_type
    );

    // Update with S3 details
    const updatedGame = await updateGame(newGame.id, {
      s3_key: s3Key,
      original_filename: originalFilename,
      file_size: fileSize
    });

    console.log(`📹 New video uploaded: ${title} (${originalFilename}) for team ${teamId}`);

    // Auto-trigger HLS conversion
    // await autoTriggerHLSConversion(updatedGame.id, s3Key); // Disabled - MediaConvert removed

    res.json({
      success: true,
      message: 'Video uploaded successfully',
      game: {
        id: updatedGame.id,
        title: updatedGame.title,
        description: updatedGame.description,
        s3_key: updatedGame.s3_key,
        original_filename: updatedGame.original_filename,
        file_size: updatedGame.file_size,
        file_type: updatedGame.file_type,
        team_id: updatedGame.team_id,
        status: updatedGame.status,
        created_at: updatedGame.created_at
      }
    });
  } catch (error) {
    console.error('Upload confirmation error:', error);
    res.status(500).json({ error: 'Failed to confirm upload' });
  }
});

// Delete game (only for game creators or company admins)
router.delete('/:id', authenticateToken, async (req, res) => {
  try {
    const gameId = req.params.id;
    const game = await getGameById(gameId);

    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }

    // Check if user has permission to delete this game
    const isCreator = game.uploaded_by === req.user.id;
    const isCompanyAdmin = req.user.role === 'company';
    const isMemberOfTeam = await isTeamMember(req.user.id, game.team_id);

    if (!isCreator && !isCompanyAdmin && !isMemberOfTeam) {
      return res.status(403).json({ 
        error: 'You do not have permission to delete this game' 
      });
    }

    // Delete the game from database
    const { pool } = require('../utils/database');
    await pool.query('DELETE FROM games WHERE id = $1', [gameId]);

    console.log(`🗑️ Game deleted: ${game.title} (${gameId}) by user ${req.user.id}`);

    res.json({
      success: true,
      message: 'Game deleted successfully'
    });
  } catch (error) {
    console.error('Delete game error:', error);
    res.status(500).json({ error: 'Failed to delete game' });
  }
});

module.exports = router; 