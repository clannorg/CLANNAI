const { Pool } = require("pg");
const path = require('path');
require("dotenv").config({ path: path.join(__dirname, '../../../server/.env') });

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT,
    ssl: { rejectUnauthorized: false }
});

async function printDbContent() {
    try {
        // 1. Users Summary
        console.log('\n=== USERS SUMMARY ===');
        const userStats = await pool.query(`
            SELECT 
                role,
                COUNT(*) as count,
                MIN(created_at) as earliest_user,
                MAX(created_at) as latest_user
            FROM Users
            GROUP BY role;
        `);
        console.table(userStats.rows);

        // 2. Teams and Members
        console.log('\n=== TEAMS AND MEMBERS ===');
        const teamStats = await pool.query(`
            SELECT 
                t.name as team_name,
                t.team_code,
                COUNT(DISTINCT tm.user_id) as member_count,
                COUNT(DISTINCT s.id) as session_count,
                MIN(s.created_at) as earliest_session,
                MAX(s.created_at) as latest_session
            FROM Teams t
            LEFT JOIN TeamMembers tm ON t.id = tm.team_id
            LEFT JOIN Sessions s ON t.id = s.team_id
            GROUP BY t.id
            ORDER BY t.created_at DESC;
        `);
        console.table(teamStats.rows);

        // 3. Sessions Analysis Stats
        console.log('\n=== SESSIONS ANALYSIS STATS ===');
        const sessionStats = await pool.query(`
            SELECT 
                status,
                COUNT(*) as count,
                COUNT(analysis_image1_url) as with_analysis,
                COUNT(distance_covered) as with_distance,
                MIN(game_date) as earliest_game,
                MAX(game_date) as latest_game
            FROM Sessions
            GROUP BY status;
        `);
        console.table(sessionStats.rows);

    } catch (error) {
        console.error('Error:', error);
    } finally {
        await pool.end();
    }
}

printDbContent();
