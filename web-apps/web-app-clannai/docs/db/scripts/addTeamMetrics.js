const { Pool } = require('pg');
require('dotenv').config({ path: '../../server/.env' });

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT,
    ssl: {
        rejectUnauthorized: false
    }
});

async function addTeamMetricsColumn() {
    try {
        await pool.query(`
            ALTER TABLE Sessions 
            ADD COLUMN team_metrics JSONB DEFAULT '{
                "total_distance": 0,
                "total_sprints": 0,
                "sprint_distance": 0,
                "high_intensity_sprints": 0,
                "top_sprint_speed": 0
            }'::jsonb;
        `);
    } catch (error) {
        process.exit(1);
    } finally {
        await pool.end();
    }
}

addTeamMetricsColumn(); 