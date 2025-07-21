const db = require("../db");
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const { MAX_TEAM_MEMBERS } = require('../constants');
const { uploadToS3 } = require('../utils/s3');
const { isValidSessionUrl } = require('../utils/sessionValidation');

exports.createSession = async (req, res) => {
    const { footage_url, team_name, team_color } = req.body;

    // Add validation
    if (!footage_url?.trim()) {
        return res.status(400).json({ error: 'Game footage URL is required' });
    }

    if (!team_name?.trim()) {
        return res.status(400).json({ error: 'Team name is required' });
    }

    if (!team_color?.trim()) {
        return res.status(400).json({ error: 'Team color is required' });
    }

    try {
        // Check if URL already exists
        const existingUrl = await db.query(
            'SELECT id FROM Sessions WHERE footage_url = $1',
            [footage_url.trim()]
        );

        if (existingUrl.rows.length > 0) {
            return res.status(400).json({ error: 'This footage URL has already been uploaded' });
        }

        // Start transaction
        await db.query('BEGIN');

        // Check if team exists for this user
        const existingTeam = await db.query(`
            SELECT t.* 
            FROM Teams t
            INNER JOIN TeamMembers tm ON t.id = tm.team_id
            WHERE LOWER(t.name) = LOWER($1) AND tm.user_id = $2
        `, [team_name, req.user.id]);

        let teamId, teamCode;

        if (existingTeam.rows.length > 0) {
            // Use existing team
            teamId = existingTeam.rows[0].id;
            teamCode = existingTeam.rows[0].team_code;

            // Check member count for existing team
            const memberCountResult = await db.query(
                'SELECT COUNT(*) as count FROM TeamMembers WHERE team_id = $1',
                [teamId]
            );

            if (memberCountResult.rows[0].count >= MAX_TEAM_MEMBERS) {
                await db.query('ROLLBACK');
                return res.status(400).json({
                    error: `Team has reached maximum capacity of ${MAX_TEAM_MEMBERS} members`
                });
            }
        } else {
            // Create new team
            teamId = uuidv4();
            teamCode = Math.random().toString(36).substring(2, 8).toUpperCase();

            await db.query(
                "INSERT INTO Teams (id, name, team_code) VALUES ($1, $2, $3)",
                [teamId, team_name, teamCode]
            );

            // Add user as team admin in TeamMembers table
            await db.query(
                "INSERT INTO TeamMembers (team_id, user_id, is_admin) VALUES ($1, $2, $3)",
                [teamId, req.user.id, true]
            );
        }

        // Create session
        const sessionId = uuidv4();
        const result = await db.query(
            "INSERT INTO Sessions (id, team_id, footage_url, game_date, status, uploaded_by, team_color) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *",
            [sessionId, teamId, footage_url, new Date(), 'PENDING', req.user.id, team_color]
        );

        // Commit transaction
        await db.query('COMMIT');

        res.json({
            ...result.rows[0],
            team_name,
            team_code: teamCode,
            team_color
        });
    } catch (err) {
        // Rollback on error
        await db.query('ROLLBACK');
        res.status(500).json({ error: err.message });
    }
};

exports.getSessions = async (req, res) => {
    const userId = req.user.id;
    try {
        const result = await db.query(`
            SELECT 
                s.*,
                t.name as team_name,
                t.team_code,
                u.email as uploaded_by_email
            FROM Sessions s
            INNER JOIN Teams t ON s.team_id = t.id
            INNER JOIN TeamMembers tm ON t.id = tm.team_id
            INNER JOIN Users u ON s.uploaded_by = u.id
            WHERE tm.user_id = $1
            ORDER BY s.created_at DESC
        `, [userId]);

        res.json(result.rows);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch sessions: ' + err.message });
    }
};

exports.deleteSession = async (req, res) => {
    const { id } = req.params;
    try {
        await db.query('BEGIN');

        // Get the team ID associated with the session
        const sessionResult = await db.query(
            "SELECT team_id FROM Sessions WHERE id = $1",
            [id]
        );

        if (sessionResult.rows.length === 0) {
            await db.query('ROLLBACK');
            return res.status(404).json({ error: 'Session not found' });
        }

        // Delete the session (no need to delete analysis separately)
        await db.query(
            "DELETE FROM Sessions WHERE id = $1",
            [id]
        );

        await db.query('COMMIT');
        res.json({ message: 'Session deleted successfully' });
    } catch (err) {
        await db.query('ROLLBACK');
        res.status(500).json({ error: 'Failed to delete session' });
    }
};

// Add this new function to get all sessions for company users
exports.getAllSessions = async (req, res) => {
    try {
        const result = await db.query(`
            SELECT 
                s.*,
                t.name as team_name,
                t.team_code,
                u.email as uploaded_by_email,
                u.id as uploader_id,
                CASE 
                    WHEN footage_url LIKE '%veo.co%' THEN 'Veo'
                    WHEN footage_url LIKE '%youtu%' THEN 'YouTube'
                    ELSE 'Invalid'
                END as url_type,
                EXTRACT(DAY FROM (CURRENT_TIMESTAMP - s.created_at)) as days_waiting
            FROM Sessions s
            LEFT JOIN Teams t ON s.team_id = t.id
            LEFT JOIN Users u ON s.uploaded_by = u.id
            WHERE footage_url LIKE '%veo.co%' 
               OR footage_url LIKE '%youtu%'
            ORDER BY s.created_at DESC
        `);

        const sessionsWithStatus = result.rows.map(session => ({
            ...session,
            priority: session.days_waiting > 2 ? 'HIGH' : 'NORMAL',
            valid_url: isValidSessionUrl(session.footage_url),
            uploaded_by: session.uploaded_by_username || session.uploaded_by_email || 'Unknown'
        }));

        res.json(sessionsWithStatus);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch sessions' });
    }
};

exports.addAnalysis = async (req, res) => {
    try {
        if (req.user.role !== 'COMPANY_MEMBER') {
            return res.status(403).json({ error: 'Not authorized' });
        }

        if (!req.file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }

        const { sessionId, type } = req.body;
        if (!sessionId || !type) {
            return res.status(400).json({ error: 'Missing sessionId or type' });
        }

        // Upload to S3 instead of local storage
        const imageUrl = await uploadToS3(req.file);
        console.log('Processing upload:', { sessionId, type, imageUrl });

        // Update the appropriate column based on analysis type
        let updateQuery;
        switch (type.toUpperCase()) {
            case 'HEATMAP':
                updateQuery = `
                    UPDATE Sessions 
                    SET analysis_image1_url = $1,
                        reviewed_by = $2,
                        status = 'REVIEWED',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = $3
                    RETURNING *`;
                break;
            case 'SPRINT_MAP':
                updateQuery = `
                    UPDATE Sessions 
                    SET analysis_image2_url = $1,
                        reviewed_by = $2,
                        status = 'REVIEWED',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = $3
                    RETURNING *`;
                break;
            case 'GAME_MOMENTUM':
                updateQuery = `
                    UPDATE Sessions 
                    SET analysis_image3_url = $1,
                        reviewed_by = $2,
                        status = 'REVIEWED',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = $3
                    RETURNING *`;
                break;
            case 'VIDEO_1':
            case 'VIDEO_2':
            case 'VIDEO_3':
            case 'VIDEO_4':
            case 'VIDEO_5':
                updateQuery = `
                    UPDATE Sessions 
                    SET analysis_video${type.split('_')[1]}_url = $1,
                        reviewed_by = $2,
                        status = 'REVIEWED',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = $3
                    RETURNING *`;
                break;
            default:
                return res.status(400).json({ error: 'Invalid analysis type' });
        }

        const result = await db.query(updateQuery, [imageUrl, req.user.id, sessionId]);
        res.json(result.rows[0]);
    } catch (err) {
        console.error('Analysis upload error:', err);
        res.status(500).json({ error: err.message });
    }
};

exports.toggleSessionStatus = async (req, res) => {
    if (req.user.role !== 'COMPANY_MEMBER') {
        return res.status(403).json({ error: 'Not authorized' });
    }

    const { sessionId } = req.params;

    try {
        // Check if the session exists
        const currentStatusResult = await db.query(
            'SELECT status FROM Sessions WHERE id = $1',
            [sessionId]
        );

        if (currentStatusResult.rows.length === 0) {
            return res.status(404).json({ error: 'Session not found' });
        }

        const currentStatus = currentStatusResult.rows[0].status;
        const newStatus = currentStatus === 'PENDING' ? 'REVIEWED' : 'PENDING';

        // Update the session status
        const updateResult = await db.query(
            `
            UPDATE Sessions 
            SET 
                status = $1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $2
            RETURNING *
            `,
            [newStatus, sessionId]
        );

        res.json(updateResult.rows[0]);
    } catch (error) {
        res.status(500).json({ error: 'Internal server error' });
    }
};

exports.deleteAnalysis = async (req, res) => {
    try {
        if (req.user.role !== 'COMPANY_MEMBER') {
            return res.status(403).json({ error: 'Not authorized' });
        }

        const { sessionId, type } = req.params;

        let updateColumn;
        switch (type.toUpperCase()) {
            case 'HEATMAP': updateColumn = 'analysis_image1_url'; break;
            case 'SPRINT_MAP': updateColumn = 'analysis_image2_url'; break;
            case 'GAME_MOMENTUM': updateColumn = 'analysis_image3_url'; break;
            case 'VIDEO_1': updateColumn = 'analysis_video1_url'; break;
            case 'VIDEO_2': updateColumn = 'analysis_video2_url'; break;
            case 'VIDEO_3': updateColumn = 'analysis_video3_url'; break;
            case 'VIDEO_4': updateColumn = 'analysis_video4_url'; break;
            case 'VIDEO_5': updateColumn = 'analysis_video5_url'; break;
            default: return res.status(400).json({ error: 'Invalid analysis type' });
        }

        const query = `
            UPDATE Sessions 
            SET ${updateColumn} = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
            RETURNING *
        `;

        const result = await db.query(query, [sessionId]);

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Session not found' });
        }

        res.json({ message: 'Analysis deleted successfully' });
    } catch (err) {
        console.error('Delete analysis error:', err);
        res.status(500).json({ error: 'Failed to delete analysis' });
    }
};

exports.addDescription = async (req, res) => {
    try {
        console.log('Starting description add...');

        if (req.user.role !== 'COMPANY_MEMBER') {
            return res.status(403).json({ error: 'Not authorized' });
        }

        const { sessionId } = req.params;
        const { description } = req.body;

        console.log('Adding description for session:', sessionId);
        console.log('Description:', description);

        // First check if description already exists
        const existing = await db.query(
            `SELECT id FROM analysis 
             WHERE session_id = $1 AND type = 'DESCRIPTION'`,
            [sessionId]
        );

        let result;
        if (existing.rows.length > 0) {
            // Update existing
            result = await db.query(
                `UPDATE analysis 
                 SET description = $1, 
                     updated_at = CURRENT_TIMESTAMP
                 WHERE session_id = $2 AND type = 'DESCRIPTION'
                 RETURNING *`,
                [description, sessionId]
            );
        } else {
            // Insert new
            result = await db.query(
                `INSERT INTO analysis 
                 (session_id, analyst_id, description, type)
                 VALUES ($1, $2, $3, 'DESCRIPTION')
                 RETURNING *`,
                [sessionId, req.user.id, description]
            );
        }

        // Update session status to REVIEWED
        await db.query(
            `UPDATE sessions 
             SET status = 'REVIEWED' 
             WHERE id = $1`,
            [sessionId]
        );

        res.json(result.rows[0]);
    } catch (error) {
        console.error('Error in addDescription:', error);
        res.status(500).json({
            error: 'Failed to add description',
            details: error.message
        });
    }
};

exports.updateAnalysisDescription = async (req, res) => {
    try {
        if (req.user.role !== 'COMPANY_MEMBER') {
            return res.status(403).json({ error: 'Not authorized' });
        }

        const { sessionId } = req.params;
        const { description } = req.body;

        // First, check if an analysis description already exists
        const existingAnalysis = await db.query(
            `SELECT id FROM analysis 
             WHERE session_id = $1 AND type = 'DESCRIPTION'`,
            [sessionId]
        );

        let result;
        if (existingAnalysis.rows.length > 0) {
            // Update existing description
            result = await db.query(
                `UPDATE analysis 
                 SET description = $1, updated_at = CURRENT_TIMESTAMP
                 WHERE session_id = $2 AND type = 'DESCRIPTION'
                 RETURNING *`,
                [description, sessionId]
            );
        } else {
            // Create new description
            result = await db.query(
                `INSERT INTO analysis 
                 (session_id, analyst_id, description, type)
                 VALUES ($1, $2, $3, 'DESCRIPTION')
                 RETURNING *`,
                [sessionId, req.user.id, description]
            );
        }

        res.json(result.rows[0]);
    } catch (error) {
        console.error('Error updating description:', error);
        res.status(500).json({ error: 'Failed to update description' });
    }
};

exports.getUserSessions = async (req, res) => {
    try {
        const result = await db.query(
            `SELECT s.*, 
                    s.analysis_image1_url,
                    s.analysis_image2_url,
                    s.analysis_image3_url,
                    s.analysis_description
             FROM Sessions s
             WHERE s.user_id = $1
             ORDER BY s.created_at DESC`,
            [req.user.id]
        );
        res.json(result.rows);
    } catch (error) {
        console.error('Error fetching user sessions:', error);
        res.status(500).json({ error: 'Failed to fetch sessions' });
    }
};

exports.getSessionDetails = async (req, res) => {
    try {
        const { sessionId } = req.params;

        const result = await db.query(`
            SELECT 
                s.*,
                t.name as team_name,
                t.team_code,
                u.email as uploaded_by_email
            FROM Sessions s
            LEFT JOIN Teams t ON s.team_id = t.id
            LEFT JOIN Users u ON s.uploaded_by = u.id
            WHERE s.id = $1
        `, [sessionId]);

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Session not found' });
        }

        res.json(result.rows[0]);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch session details' });
    }
};

exports.updateTeamMetrics = async (req, res) => {
    try {
        if (req.user.role !== 'COMPANY_MEMBER') {
            return res.status(403).json({ error: 'Not authorized' });
        }

        const { sessionId } = req.params;
        const metrics = req.body;

        const result = await db.query(
            `UPDATE Sessions 
             SET team_metrics = $1,
                 updated_at = CURRENT_TIMESTAMP,
                 status = 'REVIEWED'
             WHERE id = $2
             RETURNING *`,
            [metrics, sessionId]
        );

        res.json(result.rows[0]);
    } catch (error) {
        res.status(500).json({ error: 'Failed to update team metrics' });
    }
};

exports.updateSessionData = async (req, res) => {
    try {
        if (req.user.role !== 'COMPANY_MEMBER') {
            return res.status(403).json({ error: 'Not authorized' });
        }

        const { sessionId } = req.params;
        const { match_info } = req.body;

        // Validate required structure
        if (!match_info?.team1?.metrics || !match_info?.team2?.metrics) {
            return res.status(400).json({ 
                error: 'Invalid data structure. Required: match_info with team1 and team2 metrics' 
            });
        }

        // Also update team_metrics for backward compatibility
        const team1Metrics = match_info.team1.metrics;
        const oldFormatMetrics = {
            total_distance: team1Metrics.total_distance,
            sprint_distance: team1Metrics.sprint_distance,
            total_sprints: team1Metrics.total_sprints,
            top_sprint_speed: team1Metrics.avg_sprint_speed, // Note the field name change
            high_intensity_sprints: 0 // Keeping for compatibility
        };

        const result = await db.query(
            `UPDATE Sessions 
             SET session_data = $1,
                 team_metrics = $2,
                 updated_at = CURRENT_TIMESTAMP,
                 status = 'REVIEWED'
             WHERE id = $3
             RETURNING *`,
            [req.body, oldFormatMetrics, sessionId]
        );

        res.json(result.rows[0]);
    } catch (error) {
        res.status(500).json({ error: 'Failed to update session data' });
    }
};

exports.getSessionStats = async (req, res) => {
    try {
        console.log('Starting stats calculation...');

        // First, let's log the raw counts
        const debugCounts = await db.query(`
            SELECT 
                status,
                COUNT(*) as count,
                STRING_AGG(id::text, ', ') as session_ids,
                STRING_AGG(team_id::text, ', ') as team_ids
            FROM Sessions 
            WHERE footage_url LIKE '%veo.co%' 
               OR footage_url LIKE '%youtu%'
            GROUP BY status
        `);
        console.log('Debug counts:', debugCounts.rows);

        const stats = await db.query(`
            WITH ValidSessions AS (
                SELECT * FROM Sessions 
                WHERE (footage_url LIKE '%veo.co%' OR footage_url LIKE '%youtu%')
                  AND footage_url IS NOT NULL
                  AND footage_url != ''
            )
            SELECT 
                (SELECT COUNT(DISTINCT team_id) FROM ValidSessions) as total_teams,
                (SELECT COUNT(DISTINCT tm.user_id) 
                 FROM TeamMembers tm
                 INNER JOIN ValidSessions s ON tm.team_id = s.team_id) as total_accounts,
                (SELECT COUNT(*) FROM ValidSessions) as all_sessions,
                (SELECT COUNT(*) FROM ValidSessions WHERE status = 'PENDING') as pending_valid,
                (SELECT COUNT(*) FROM ValidSessions WHERE status = 'REVIEWED') as completed_valid
        `);

        console.log('Stats query result:', stats.rows[0]);
        res.json(stats.rows[0]);
    } catch (err) {
        console.error('Failed to fetch stats:', {
            error: err.message,
            stack: err.stack,
            query: err.query // This will show the failing query if it exists
        });
        res.status(500).json({ error: 'Failed to fetch stats' });
    }
};

exports.getStats = async (req, res) => {
    try {
        const statsQuery = await db.query(`
            SELECT /* your existing stats query */
        `);

        res.json(statsQuery.rows[0]);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch stats' });
    }
};

exports.getTeamsWithValidSessions = async (req, res) => {
    try {
        const result = await db.query(`
            SELECT 
                t.id,
                t.name,
                t.team_code,
                t.subscription_status,
                COUNT(s.id) as valid_session_count
            FROM Teams t
            INNER JOIN Sessions s ON t.id = s.team_id
            WHERE (s.footage_url LIKE '%veo.co%' OR s.footage_url LIKE '%youtu%')
                AND s.footage_url IS NOT NULL
                AND s.footage_url != ''
            GROUP BY t.id, t.name, t.team_code
            ORDER BY valid_session_count DESC
        `);

        res.json(result.rows);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch teams with valid sessions' });
    }
};

exports.getDatabaseContent = async (req, res) => {
    try {
        // 1. All User Details
        const userDetails = await db.query(`
            SELECT 
                u.email,
                u.role,
                u.cognito_id,
                u.created_at,
                COUNT(DISTINCT tm.team_id) as team_count,
                COUNT(DISTINCT s.id) as uploaded_sessions
            FROM Users u
            LEFT JOIN TeamMembers tm ON u.id = tm.user_id
            LEFT JOIN Sessions s ON u.id = s.uploaded_by
            GROUP BY u.id, u.email, u.role, u.cognito_id, u.created_at
            ORDER BY u.created_at DESC
        `);

        // 2. All Team & Membership Details
        const teamMemberDetails = await db.query(`
            SELECT 
                t.name as team_name,
                t.team_code,
                t.is_premium,
                t.subscription_status,
                t.trial_ends_at,
                t.subscription_id,
                t.created_at as team_created_at,
                u.email as member_email,
                tm.is_admin,
                tm.joined_at
            FROM Teams t
            JOIN TeamMembers tm ON t.id = tm.team_id
            JOIN Users u ON tm.user_id = u.id
            ORDER BY t.name, tm.is_admin DESC
        `);

        // 3. All Session Details
        const sessionDetails = await db.query(`
            SELECT 
                t.name as team_name,
                u.email as uploaded_by,
                ru.email as reviewed_by,
                s.status,
                s.game_date,
                s.created_at,
                s.updated_at,
                s.footage_url,
                s.distance_covered,
                s.analysis_description,
                s.analysis_image1_url,
                s.analysis_image2_url,
                s.analysis_image3_url,
                s.team_metrics,
                CASE 
                    WHEN s.analysis_image1_url IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END as has_analysis
            FROM Sessions s
            JOIN Teams t ON s.team_id = t.id
            JOIN Users u ON s.uploaded_by = u.id
            LEFT JOIN Users ru ON s.reviewed_by = ru.id
            ORDER BY s.created_at DESC
        `);

        // Teams query with debug logging
        const teamDetails = await db.query(`
            SELECT 
                t.id,
                t.name,
                t.team_code,
                t.created_at,
                t.is_premium,
                t.subscription_status,
                t.trial_ends_at,
                t.updated_at,
                COUNT(DISTINCT tm.user_id) as member_count,
                COUNT(DISTINCT s.id) as session_count
            FROM Teams t
            LEFT JOIN TeamMembers tm ON t.id = tm.team_id
            LEFT JOIN Sessions s ON t.id = s.team_id
            GROUP BY 
                t.id, 
                t.name, 
                t.team_code, 
                t.created_at,
                t.is_premium,
                t.subscription_status,
                t.trial_ends_at,
                t.updated_at
            ORDER BY t.created_at DESC
        `);

        res.json({
            userDetails: userDetails.rows,
            teamDetails: teamDetails.rows,
            teamMemberDetails: teamMemberDetails.rows,
            sessionDetails: sessionDetails.rows
        });
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch database content' });
    }
};