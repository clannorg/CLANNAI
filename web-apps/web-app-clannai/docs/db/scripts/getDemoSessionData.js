const { Pool } = require('pg');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../../server/.env') });

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT,
    ssl: { rejectUnauthorized: false }
});

async function getDemoSessionData() {
    try {
        const result = await pool.query(`
            SELECT 
                s.id,
                t.name as team_name,
                s.team_metrics,
                s.session_data,
                s.status,
                s.created_at
            FROM Sessions s
            JOIN Teams t ON s.team_id = t.id
            WHERE t.name LIKE '%Clann%'
            OR t.name LIKE '%Demo%'
            ORDER BY s.created_at DESC;
        `);

        console.log('\n=== DEMO TEAM SESSIONS ===');
        result.rows.forEach(row => {
            console.log('\nSession:', row.id);
            console.log('Team:', row.team_name);
            console.log('Status:', row.status);
            console.log('Created:', row.created_at);
            console.log('\nOld Metrics:', JSON.stringify(row.team_metrics, null, 2));
            console.log('\nNew Format:', JSON.stringify(row.session_data, null, 2));
            console.log('------------------------');
        });

    } catch (error) {
        console.error('Error:', error);
    } finally {
        await pool.end();
    }
}

getDemoSessionData(); 