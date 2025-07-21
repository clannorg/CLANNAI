const { Pool } = require('pg');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../../server/.env') });

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

async function listPopulatedSessions() {
  try {
    // Get all populated sessions
    const result = await pool.query(`
      SELECT id, created_at, footage_url, session_data 
      FROM sessions 
      WHERE session_data != '{"match_info": {"score": {"team1": 0, "team2": 0}, "team1": {"name": "", "metrics": {"energy": 0, "total_sprints": 0, "total_distance": 0, "sprint_distance": 0, "avg_sprint_speed": 0}}, "team2": {"name": "", "metrics": {"energy": 0, "total_sprints": 0, "total_distance": 0, "sprint_distance": 0, "avg_sprint_speed": 0}}}}'::jsonb
      ORDER BY created_at DESC
    `);
    
    console.log(`Found ${result.rows.length} sessions with populated data:\n`);
    
    result.rows.forEach((row, i) => {
      console.log(`\n[${i+1}] Session ID: ${row.id}`);
      console.log(`Created: ${row.created_at}`);
      console.log(`Footage URL: ${row.footage_url}`);
      console.log(`Team 1: ${row.session_data.match_info.team1.name}`);
      console.log(`Team 2: ${row.session_data.match_info.team2.name}`);
      console.log(`Score: ${row.session_data.match_info.score.team1} - ${row.session_data.match_info.score.team2}`);
      
      // Check if metrics are populated
      const team1Metrics = row.session_data.match_info.team1.metrics;
      const team2Metrics = row.session_data.match_info.team2.metrics;
      
      const hasPopulatedMetrics = Object.values(team1Metrics).some(v => v !== 0) || 
                                 Object.values(team2Metrics).some(v => v !== 0);
      
      console.log(`Has populated metrics: ${hasPopulatedMetrics ? 'YES' : 'NO'}`);
      
      if (hasPopulatedMetrics) {
        console.log("Team 1 Metrics:", team1Metrics);
        console.log("Team 2 Metrics:", team2Metrics);
      }
      
      console.log('-'.repeat(80));
    });
    
  } catch (err) {
    console.error('Error executing query', err);
  } finally {
    await pool.end();
  }
}

listPopulatedSessions(); 