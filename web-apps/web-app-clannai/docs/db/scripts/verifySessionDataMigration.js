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

async function verifyMigration() {
    try {
        const result = await pool.query(`
            SELECT 
                id,
                team_metrics,
                session_data,
                (SELECT name FROM Teams WHERE id = team_id) as team_name
            FROM Sessions
            WHERE team_metrics IS NOT NULL
            OR session_data->'match_info'->'team1'->'metrics'->>'total_distance' != '0';
        `);

        console.log('\n=== MIGRATION VERIFICATION ===');
        console.log(`Found ${result.rows.length} sessions with data\n`);

        result.rows.forEach(row => {
            console.log(`Session ID: ${row.id}`);
            console.log(`Team: ${row.team_name}`);
            console.log('Old Data:', JSON.stringify(row.team_metrics, null, 2));
            console.log('New Data:', JSON.stringify(row.session_data, null, 2));
            console.log('-------------------\n');
        });

    } catch (error) {
        console.error('Error verifying migration:', error);
    } finally {
        await pool.end();
    }
}

verifyMigration(); 