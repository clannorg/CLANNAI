const express = require('express');
const { authenticateToken, requireCompanyRole } = require('../middleware/auth');
const { getAllGames } = require('../utils/database');

const router = express.Router();

// Get all games from all users/teams (company view)
router.get('/games', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const { status, limit = 50, offset = 0 } = req.query;
    
    // Get all games
    let games = await getAllGames();

    // Filter by status if provided
    if (status && ['pending', 'analyzed'].includes(status)) {
      games = games.filter(game => game.status === status);
    }

    // Apply pagination
    const totalGames = games.length;
    const paginatedGames = games.slice(parseInt(offset), parseInt(offset) + parseInt(limit));

    res.json({
      games: paginatedGames.map(game => {
        // Extract tactical analysis URL from metadata
        const metadata = game.metadata || {};
        const tacticalFiles = metadata.tactical_files || {};
        const tacticalAnalysisUrl = tacticalFiles.latest?.url ||
                                    tacticalFiles.coaching_insights?.url || 
                                    tacticalFiles.match_summary?.url || 
                                    tacticalFiles.general?.url ||
                                    Object.values(tacticalFiles)[0]?.url || null;

        // Extract events S3 URL from metadata
        const eventsFiles = metadata.events_files || {};
        const eventsUrl = eventsFiles.web_events?.url || 
                         eventsFiles.web_events_array?.url || 
                         eventsFiles.enhanced_events?.url ||
                         Object.values(eventsFiles)[0]?.url || null;

        return {
          id: game.id,
          title: game.title,
          description: game.description,
          video_url: game.video_url,
          s3_key: game.s3_key,
          chunks_base_url: game.chunks_base_url,
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
          has_analysis: !!game.ai_analysis,
          has_tactical: !!game.tactical_analysis,
          tactical_analysis_url: tacticalAnalysisUrl,
          metadata_url: game.metadata_url,
          training_url: game.training_url,
          events_url: eventsUrl,
          // Event modification status
          has_modified_events: !!game.events_modified,
          events_last_modified_by: game.events_last_modified_by,
          events_last_modified_at: game.events_last_modified_at,
          ai_events_count: game.ai_analysis ? game.ai_analysis.length : 0,
          modified_events_count: game.events_modified ? game.events_modified.length : 0,
          created_at: game.created_at,
          updated_at: game.updated_at
        };
      }),
      pagination: {
        total: totalGames,
        limit: parseInt(limit),
        offset: parseInt(offset),
        has_more: (parseInt(offset) + parseInt(limit)) < totalGames
      }
    });
  } catch (error) {
    console.error('Get all games error:', error);
    res.status(500).json({ error: 'Failed to get games' });
  }
});

// Get company dashboard stats
router.get('/stats', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const allGames = await getAllGames();

    const stats = {
      total_games: allGames.length,
      pending_games: allGames.filter(g => g.status === 'pending').length,
      analyzed_games: allGames.filter(g => g.status === 'analyzed').length,
      veo_uploads: allGames.filter(g => g.file_type === 'veo').length,
      file_uploads: allGames.filter(g => g.file_type === 'upload').length,
      teams_count: new Set(allGames.map(g => g.team_id)).size,
      users_count: new Set(allGames.map(g => g.uploaded_by)).size
    };

    // Recent activity (last 7 days)
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    const recentGames = allGames.filter(game => 
      new Date(game.created_at) > sevenDaysAgo
    );

    stats.recent_uploads = recentGames.length;
    stats.recent_analysis = recentGames.filter(g => g.status === 'analyzed').length;

    res.json({
      stats,
      last_updated: new Date().toISOString()
    });
  } catch (error) {
    console.error('Get stats error:', error);
    res.status(500).json({ error: 'Failed to get stats' });
  }
});

// Get pending VEO URLs for processing
router.get('/pending-veo', [authenticateToken, requireCompanyRole], async (req, res) => {
  try {
    const allGames = await getAllGames();
    
    const pendingVeoGames = allGames.filter(game => 
      game.status === 'pending' && 
      game.file_type === 'veo' && 
      game.video_url
    );

    res.json({
      message: 'Pending VEO URLs for processing',
      count: pendingVeoGames.length,
      games: pendingVeoGames.map(game => ({
        id: game.id,
        title: game.title,
        video_url: game.video_url,
        team_name: game.team_name,
        uploaded_by_name: game.uploaded_by_name,
        uploaded_by_email: game.uploaded_by_email,
        created_at: game.created_at
      }))
    });
  } catch (error) {
    console.error('Get pending VEO error:', error);
    res.status(500).json({ error: 'Failed to get pending VEO URLs' });
  }
});

// Company workflow instructions
router.get('/workflow', [authenticateToken, requireCompanyRole], (req, res) => {
  res.json({
    message: 'Company Analysis Workflow',
    steps: [
      {
        step: 1,
        title: 'View VEO URLs',
        description: 'Check /api/company/pending-veo for new uploads',
        endpoint: 'GET /api/company/pending-veo'
      },
      {
        step: 2,
        title: 'Download & Process',
        description: 'Manually download VEO video on VM and run AI analysis',
        note: 'Use ai/footy/ pipeline for analysis'
      },
      {
        step: 3,
        title: 'Upload to S3',
        description: 'Upload processed video file to S3 bucket',
        endpoint: 'POST /api/games/:id/upload-video'
      },
      {
        step: 4,
        title: 'Upload Analysis',
        description: 'Upload JSON analysis results from VM',
        endpoint: 'POST /api/games/:id/analysis'
      },
      {
        step: 5,
        title: 'Mark Analyzed',
        description: 'Update game status to "analyzed"',
        endpoint: 'PUT /api/games/:id/status'
      }
    ],
    demo_credentials: {
      email: 'admin@clann.ai',
      password: 'demo123',
      role: 'company'
    }
  });
});

module.exports = router; 