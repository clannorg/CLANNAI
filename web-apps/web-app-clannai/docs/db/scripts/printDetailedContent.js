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

async function printDetailedContent() {
    try {
        // 1. Detailed User Info
        console.log('\n=== DETAILED USER INFO ===');
        const userDetails = await pool.query(`
            SELECT 
                u.email,
                u.role,
                u.created_at,
                COUNT(DISTINCT tm.team_id) as team_count,
                COUNT(DISTINCT s.id) as uploaded_sessions
            FROM Users u
            LEFT JOIN TeamMembers tm ON u.id = tm.user_id
            LEFT JOIN Sessions s ON u.id = s.uploaded_by
            GROUP BY u.id, u.email, u.role, u.created_at
            ORDER BY u.created_at DESC;
        `);
        console.table(userDetails.rows);

        // 2. Team Membership Details
        console.log('\n=== TEAM MEMBERSHIP DETAILS ===');
        const teamMemberDetails = await pool.query(`
            SELECT 
                t.id as team_id,
                t.name as team_name,
                t.team_code,
                u.email as member_email,
                tm.is_admin
            FROM Teams t
            JOIN TeamMembers tm ON t.id = tm.team_id
            JOIN Users u ON tm.user_id = u.id
            ORDER BY t.name, tm.is_admin DESC;
        `);
        console.table(teamMemberDetails.rows);

        // 3. Session Details
        console.log('\n=== SESSION DETAILS ===');
        const sessionDetails = await pool.query(`
            SELECT 
                t.name as team_name,
                u.email as uploaded_by,
                s.status,
                s.game_date,
                s.created_at,
                CASE 
                    WHEN s.analysis_image1_url IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END as has_analysis
            FROM Sessions s
            JOIN Teams t ON s.team_id = t.id
            JOIN Users u ON s.uploaded_by = u.id
            ORDER BY s.created_at DESC;
        `);
        console.table(sessionDetails.rows);

    } catch (err) {
        console.error('Error printing detailed content:', err);
    } finally {
        await pool.end();
    }
}

printDetailedContent(); 