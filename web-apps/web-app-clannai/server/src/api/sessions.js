const express = require("express");
const router = express.Router();
const sessionsController = require('./sessionsController');
const auth = require("../middleware/auth");
const multer = require('multer');
const path = require('path');
const db = require('../db');

// Configure multer first
const storage = multer.memoryStorage();

const fileFilter = (req, file, cb) => {
    if (file.mimetype.startsWith('image/') || file.mimetype.startsWith('video/')) {
        cb(null, true);
    } else {
        cb(new Error('Only image and video files are allowed!'), false);
    }
};

const upload = multer({
    storage: storage,
    limits: { fileSize: 100 * 1024 * 1024 }, // 100MB limit
    fileFilter: fileFilter
});

// First, define specific routes (EXACT MATCHES FIRST)
router.post("/create", auth, sessionsController.createSession);
router.get("/", auth, sessionsController.getSessions);
router.get('/all', auth, sessionsController.getAllSessions);
router.get('/stats', auth, sessionsController.getSessionStats);
router.post('/analysis', auth, upload.single('file'), sessionsController.addAnalysis);
router.get('/teams-with-valid-sessions', auth, sessionsController.getTeamsWithValidSessions);

// Then, define parameterized routes (WILDCARDS LAST)
router.get("/database-content", auth, async (req, res) => {
    try {
        await sessionsController.getDatabaseContent(req, res);
    } catch (err) {
        console.error('Database content route error:', err);
        res.status(500).json({ error: 'Failed to fetch database content' });
    }
});

router.get("/:sessionId", auth, sessionsController.getSessionDetails);
router.delete("/:id", auth, sessionsController.deleteSession);
router.put('/:sessionId/toggle-status', auth, sessionsController.toggleSessionStatus);
router.delete('/analysis/:sessionId/:type', auth, sessionsController.deleteAnalysis);
router.post('/:sessionId/description', auth, sessionsController.addDescription);
router.put('/:sessionId/description', auth, sessionsController.updateAnalysisDescription);
router.put('/:sessionId/metrics', auth, sessionsController.updateTeamMetrics);

// Add this route handler if it doesn't exist
router.put('/:sessionId/title', auth, async (req, res) => {
    try {
        const { sessionId } = req.params;
        const { team_name } = req.body;

        const result = await db.query(
            'UPDATE sessions SET team_name = $1 WHERE id = $2 RETURNING *',
            [team_name, sessionId]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Session not found' });
        }

        res.json(result.rows[0]);
    } catch (error) {
        console.error('Update title error:', error);
        res.status(500).json({ error: 'Failed to update session title' });
    }
});

// Add this route explicitly
router.get("/stats", auth, async (req, res) => {
    try {
        console.log('Stats request received, auth:', req.user);

        // Simpler, more efficient query
        const stats = await db.query(`
            SELECT 
                COALESCE(COUNT(DISTINCT team_id), 0) as total_teams,
                COALESCE(COUNT(DISTINCT uploaded_by), 0) as total_accounts,
                COALESCE(COUNT(*), 0) as all_sessions,
                COALESCE(SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END), 0) as pending_valid,
                COALESCE(SUM(CASE WHEN status = 'REVIEWED' THEN 1 ELSE 0 END), 0) as completed_valid
            FROM Sessions
            WHERE footage_url IS NOT NULL
            AND (footage_url LIKE '%veo.co%' OR footage_url LIKE '%youtu%')
        `);

        console.log('Query result:', stats.rows[0]);
        res.json(stats.rows[0]);
    } catch (err) {
        console.error('Stats route error:', err);
        res.status(500).json({ error: 'Failed to fetch stats' });
    }
});

// Add new route
router.put('/:sessionId/session-data', auth, sessionsController.updateSessionData);

module.exports = router;

