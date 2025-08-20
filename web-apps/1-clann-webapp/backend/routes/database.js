const express = require('express');
const { authenticateToken, requireCompanyRole } = require('../middleware/auth');
const { Pool } = require('pg');

const router = express.Router();

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT || 5432,
    ssl: { rejectUnauthorized: false }
});

// Get comprehensive database overview - company users only
router.get('/overview', authenticateToken, requireCompanyRole, async (req, res) => {
    try {
        console.log('📊 Loading comprehensive database overview...');
        
        // 1. Users Overview with Team Memberships
        const users = await pool.query(`
            SELECT 
                u.email,
                u.name,
                u.role,
                u.created_at,
                (SELECT COUNT(*) FROM team_members tm WHERE tm.user_id = u.id) as teams_count,
                (SELECT COUNT(*) FROM games g WHERE g.uploaded_by = u.id) as games_uploaded,
                ARRAY_AGG(DISTINCT t.name ORDER BY t.name) FILTER (WHERE t.name IS NOT NULL) as team_names
            FROM users u
            LEFT JOIN team_members tm ON u.id = tm.user_id
            LEFT JOIN teams t ON tm.team_id = t.id
            GROUP BY u.id, u.email, u.name, u.role, u.created_at
            ORDER BY u.created_at DESC
        `);

        // 2. Teams Overview with Member List
        const teams = await pool.query(`
            SELECT 
                t.name,
                t.team_code,
                t.color,
                t.created_at,
                (SELECT COUNT(*) FROM team_members tm WHERE tm.team_id = t.id) as members_count,
                (SELECT COUNT(*) FROM games g WHERE g.team_id = t.id) as games_count,
                ARRAY_AGG(DISTINCT u.name ORDER BY u.name) FILTER (WHERE u.name IS NOT NULL) as member_names
            FROM teams t
            LEFT JOIN team_members tm ON t.id = tm.team_id
            LEFT JOIN users u ON tm.user_id = u.id
            GROUP BY t.id, t.name, t.team_code, t.color, t.created_at
            ORDER BY t.created_at DESC
        `);

        // 3. Games Overview with Events Count (sorted by most recent)
        const games = await pool.query(`
            SELECT 
                g.title,
                COALESCE(t.name, 'Unknown Team') as team_name,
                g.status,
                CASE WHEN g.ai_analysis IS NOT NULL AND g.ai_analysis != '[]' THEN 'Yes' ELSE 'No' END as has_analysis,
                CASE WHEN g.tactical_analysis IS NOT NULL AND g.tactical_analysis != '{}' THEN 'Yes' ELSE 'No' END as has_tactical,
                CASE 
                    WHEN g.events_modified IS NOT NULL 
                    THEN jsonb_array_length(g.events_modified)
                    WHEN g.ai_analysis IS NOT NULL AND g.ai_analysis != '[]' 
                    THEN jsonb_array_length(g.ai_analysis) 
                    ELSE 0 
                END as events_count,
                CASE WHEN g.events_modified IS NOT NULL THEN 'Modified' ELSE 'AI' END as events_type,
                CASE 
                    WHEN g.ai_analysis IS NOT NULL AND g.ai_analysis != '[]' 
                    THEN jsonb_array_length(g.ai_analysis) 
                    ELSE 0 
                END as ai_events_count,
                CASE 
                    WHEN g.events_modified IS NOT NULL 
                    THEN jsonb_array_length(g.events_modified)
                    ELSE 0 
                END as modified_events_count,
                u.email as uploaded_by,
                u.name as uploaded_by_name,
                g.created_at
            FROM games g
            LEFT JOIN teams t ON g.team_id = t.id
            LEFT JOIN users u ON g.uploaded_by = u.id
            ORDER BY g.created_at DESC
        `);

        // 4. Summary Stats
        const summary = {
            total_users: users.rows.length,
            company_users: users.rows.filter(u => u.role === 'company').length,
            regular_users: users.rows.filter(u => u.role === 'user').length,
            total_teams: teams.rows.length,
            total_games: games.rows.length,
            analyzed_games: games.rows.filter(g => g.status === 'analyzed').length,
            pending_games: games.rows.filter(g => g.status === 'pending').length,
            games_with_events: games.rows.filter(g => g.events_count > 0).length,
            total_events: games.rows.reduce((sum, g) => sum + parseInt(g.events_count || 0), 0)
        };

        console.log(`✅ Database overview loaded: ${users.rows.length} users, ${teams.rows.length} teams, ${games.rows.length} games`);
        
        res.json({
            success: true,
            summary,
            users: users.rows,
            teams: teams.rows,
            games: games.rows
        });

    } catch (error) {
        console.error('❌ Database overview error:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to load database overview',
            message: error.message
        });
    }
});

module.exports = router;