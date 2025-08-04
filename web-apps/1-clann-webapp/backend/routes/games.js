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

const router = express.Router();

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

// Get single game by ID (for game viewing page)
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const gameId = req.params.id;
    const game = await getGameById(gameId);
    
    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }
    
    // Check if user has access to this game (their game, team member, company admin, demo game, or newmills)
    const isNewmillsGame = game.team_name === 'newmills';
    
    if (req.user.role !== 'company' && !game.is_demo && !isNewmillsGame) {
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
        created_at: game.created_at,
        // Video player needs browser-compatible HTTPS URL
        s3Url: s3Url
      }
    });
  } catch (error) {
    console.error('Get game error:', error);
    res.status(500).json({ error: 'Failed to get game' });
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
    
    // Convert events to JSON string for PostgreSQL JSONB storage
    console.log('📝 About to store events in database...');
    console.log('📝 First few events:', JSON.stringify(events.slice(0, 2), null, 2));
    
    const updatedGame = await updateGame(gameId, {
      ai_analysis: JSON.stringify(events), // Convert to JSON string for PostgreSQL
      status: 'analyzed'
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
        updated_at: updatedGame.updated_at
      }
    });
  } catch (error) {
    console.error('Upload events error:', error);
    if (error.response) {
      console.error('HTTP Error:', error.response.status, error.response.statusText);
    }
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

    // Store tactical file URL in metadata
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

    const updatedGame = await updateGame(gameId, {
      metadata: {
        ...currentMetadata,
        tactical_files: tacticalFiles
      }
    });

    res.json({
      message: 'Tactical file uploaded successfully',
      game: {
        id: updatedGame.id,
        title: updatedGame.title,
        status: updatedGame.status,
        tactical_type: tacticalType,
        updated_at: updatedGame.updated_at
      }
    });
  } catch (error) {
    console.error('Upload tactical error:', error);
    res.status(500).json({ error: 'Failed to upload tactical file' });
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
      url: s3Key,
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

module.exports = router; 