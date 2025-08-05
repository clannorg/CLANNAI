const { Pool } = require("pg");
const path = require('path');
require("dotenv").config({ path: path.join(__dirname, '../../backend/.env') });

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT || 5432,
    ssl: { rejectUnauthorized: false }  // Required for AWS RDS
});

async function printDetailedContent() {
    try {
        console.log('🔍 CLANNAI DATABASE CONTENT');
        console.log('============================\n');

        // 1. Users Overview
        console.log('👤 USERS');
        console.log('--------');
        const users = await pool.query(`
            SELECT 
                email,
                name,
                role,
                created_at,
                (SELECT COUNT(*) FROM team_members tm WHERE tm.user_id = u.id) as teams_count,
                (SELECT COUNT(*) FROM games g WHERE g.uploaded_by = u.id) as games_uploaded
            FROM users u
            ORDER BY created_at DESC;
        `);
        console.table(users.rows);

        // 2. Teams Overview
        console.log('\n⚽ TEAMS');
        console.log('--------');
        const teams = await pool.query(`
            SELECT 
                t.name,
                t.team_code,
                t.color,
                (SELECT COUNT(*) FROM team_members tm WHERE tm.team_id = t.id) as members_count,
                (SELECT COUNT(*) FROM games g WHERE g.team_id = t.id) as games_count,
                t.created_at
            FROM teams t
            ORDER BY t.created_at DESC;
        `);
        console.table(teams.rows);

        // 3. Team Membership
        console.log('\n🤝 TEAM MEMBERSHIP');
        console.log('------------------');
        const membership = await pool.query(`
            SELECT 
                t.name as team_name,
                t.team_code,
                u.email as member_email,
                u.name as member_name,
                tm.joined_at
            FROM team_members tm
            JOIN teams t ON tm.team_id = t.id
            JOIN users u ON tm.user_id = u.id
            ORDER BY t.name, tm.joined_at;
        `);
        console.table(membership.rows);

        // 4. Games Overview
        console.log('\n🎮 GAMES');
        console.log('--------');
        const games = await pool.query(`
            SELECT 
                g.title,
                t.name as team_name,
                u.email as uploaded_by,
                g.status,
                CASE 
                    WHEN g.ai_analysis IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END as has_analysis,
                CASE 
                    WHEN g.tactical_analysis IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END as has_tactical,
                g.created_at
            FROM games g
            JOIN teams t ON g.team_id = t.id
            JOIN users u ON g.uploaded_by = u.id
            ORDER BY g.created_at DESC;
        `);
        console.table(games.rows);

        // 5. Greenisland Specific (if exists)
        console.log('\n🌿 GREENISLAND DATA');
        console.log('------------------');
        const greenisland = await pool.query(`
            SELECT 
                'Team' as type,
                t.name as name,
                t.team_code as code,
                '' as email,
                t.created_at
            FROM teams t 
            WHERE LOWER(t.name) LIKE '%greenisland%'
            
            UNION ALL
            
            SELECT 
                'User' as type,
                u.name,
                '' as code,
                u.email,
                u.created_at
            FROM users u 
            WHERE LOWER(u.email) LIKE '%greenisland%' OR LOWER(u.name) LIKE '%greenisland%'
            
            UNION ALL
            
            SELECT 
                'Game' as type,
                g.title,
                g.status as code,
                '' as email,
                g.created_at
            FROM games g 
            JOIN teams t ON g.team_id = t.id
            WHERE LOWER(t.name) LIKE '%greenisland%'
            
            ORDER BY created_at DESC;
        `);
        
        if (greenisland.rows.length > 0) {
            console.table(greenisland.rows);
        } else {
            console.log('No Greenisland data found');
        }

    } catch (err) {
        console.error('❌ Error:', err.message);
    } finally {
        await pool.end();
    }
}

printDetailedContent();