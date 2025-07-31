const express = require('express');
const { authenticateToken, requireCompanyRole } = require('../middleware/auth');
const { 
  getUserGames, 
  getGameById, 
  createGame, 
  updateGame,
  isTeamMember,
  getUserTeams 
} = require('../utils/database');

const router = express.Router();

// Get user's games
router.get('/', authenticateToken, async (req, res) => {
  try {
    const games = await getUserGames(req.user.id);

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

// Get single game by ID (for game viewing page)
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const gameId = req.params.id;
    const game = await getGameById(gameId);
    
    if (!game) {
      return res.status(404).json({ error: 'Game not found' });
    }
    
    // Check if user has access to this game (their game or team member)
    const userGames = await getUserGames(req.user.id);
    const hasAccess = userGames.some(g => g.id === gameId);
    
    if (!hasAccess) {
      return res.status(403).json({ error: 'Access denied' });
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
        ai_analysis: game.ai_analysis,
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

// Upload analysis JSON (company only)
router.post('/:id/analysis', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const { analysis } = req.body;

    if (!analysis) {
      return res.status(400).json({ error: 'Analysis data is required' });
    }

    // Validate analysis structure (basic check)
    if (typeof analysis !== 'object') {
      return res.status(400).json({ error: 'Analysis must be a valid JSON object' });
    }

    // Update game with analysis
    const updatedGame = await updateGame(gameId, {
      ai_analysis: analysis
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

// Add S3 analysis files for a game (company only)
router.post('/:id/analysis-files', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const gameId = req.params.id;
    const { s3AnalysisFiles } = req.body; // JSON object of S3 URLs

    if (!s3AnalysisFiles || typeof s3AnalysisFiles !== 'object') {
      return res.status(400).json({ error: 's3AnalysisFiles JSON object required' });
    }

    const updatedGame = await updateGame(gameId, {
      s3_analysis_files: s3AnalysisFiles
    });

    if (!updatedGame) {
      return res.status(404).json({ error: 'Game not found' });
    }

    res.json({
      message: 'Analysis files updated',
      s3_analysis_files: updatedGame.s3_analysis_files
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