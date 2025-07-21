const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    // Remove SSL for local development
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

async function printGames() {
    try {
        console.log('\n=== ALL SESSIONS ===');
        const result = await pool.query(`
            SELECT 
                s.id,
                t.name as team_name,
                s.footage_url,
                s.status,
                s.created_at,
                EXTRACT(DAY FROM (CURRENT_TIMESTAMP - s.created_at)) as days_old,
                CASE 
                    WHEN footage_url LIKE '%veo%' THEN 'Veo'
                    WHEN footage_url LIKE '%youtu%' THEN 'YouTube'
                    ELSE 'Other'
                END as url_type
            FROM Sessions s
            LEFT JOIN Teams t ON s.team_id = t.id
            ORDER BY s.created_at DESC;
        `);
        
        console.table(result.rows);
        
    } catch (err) {
        console.error('Error:', err);
        console.error('Connection details:', {
            host: process.env.DB_HOST,
            database: process.env.DB_NAME,
            user: process.env.DB_USER,
            // Don't log password
        });
    } finally {
        await pool.end();
    }
}

printGames();
