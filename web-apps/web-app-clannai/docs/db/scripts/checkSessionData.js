// docs/db/scripts/checkSessionData.js
const { Pool } = require('pg');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../../server/.env') });

console.log('Connecting to database:', {
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  // Not logging password for security
});

// Configure database connection using environment variables
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

async function checkSessionData() {
  try {
    // Get total count of sessions
    const totalResult = await pool.query('SELECT COUNT(*) FROM sessions');
    const totalSessions = parseInt(totalResult.rows[0].count);
    
    console.log(`Total sessions in database: ${totalSessions}`);
    
    // Count sessions with non-default session_data
    const populatedResult = await pool.query(`
      SELECT COUNT(*) FROM sessions 
      WHERE session_data != '{"match_info": {"score": {"team1": 0, "team2": 0}, "team1": {"name": "", "metrics": {"energy": 0, "total_sprints": 0, "total_distance": 0, "sprint_distance": 0, "avg_sprint_speed": 0}}, "team2": {"name": "", "metrics": {"energy": 0, "total_sprints": 0, "total_distance": 0, "sprint_distance": 0, "avg_sprint_speed": 0}}}}'::jsonb
    `);
    const populatedSessions = parseInt(populatedResult.rows[0].count);
    
    console.log(`Sessions with populated data: ${populatedSessions} (${(populatedSessions/totalSessions*100).toFixed(2)}%)`);
    
    // Check for sessions with specific metrics populated
    const metricsQueries = [
      "session_data->'match_info'->'team1'->'metrics'->'energy' != '0'",
      "session_data->'match_info'->'team1'->'metrics'->'total_sprints' != '0'",
      "session_data->'match_info'->'team1'->'metrics'->'total_distance' != '0'",
      "session_data->'match_info'->'team1'->'metrics'->'sprint_distance' != '0'",
      "session_data->'match_info'->'team1'->'metrics'->'avg_sprint_speed' != '0'"
    ];
    
    console.log("\nMetrics population breakdown:");
    
    for (const query of metricsQueries) {
      const metricResult = await pool.query(`
        SELECT COUNT(*) FROM sessions WHERE ${query}
      `);
      const metricCount = parseInt(metricResult.rows[0].count);
      console.log(`- ${query.split("'")[3]}: ${metricCount} (${(metricCount/totalSessions*100).toFixed(2)}%)`);
    }
    
    // Check for sessions with team names populated
    const teamNamesResult = await pool.query(`
      SELECT COUNT(*) FROM sessions 
      WHERE session_data->'match_info'->'team1'->'name' != '""'
      AND session_data->'match_info'->'team2'->'name' != '""'
    `);
    const teamNamesCount = parseInt(teamNamesResult.rows[0].count);
    console.log(`\nSessions with team names populated: ${teamNamesCount} (${(teamNamesCount/totalSessions*100).toFixed(2)}%)`);
    
    // Check for sessions with scores populated
    const scoresResult = await pool.query(`
      SELECT COUNT(*) FROM sessions 
      WHERE (session_data->'match_info'->'score'->'team1' != '0'
      OR session_data->'match_info'->'score'->'team2' != '0')
    `);
    const scoresCount = parseInt(scoresResult.rows[0].count);
    console.log(`Sessions with scores populated: ${scoresCount} (${(scoresCount/totalSessions*100).toFixed(2)}%)`);
    
    // Get a sample of the most recently populated sessions
    console.log("\nMost recent populated sessions:");
    const recentResult = await pool.query(`
      SELECT id, created_at, session_data 
      FROM sessions 
      WHERE session_data != '{"match_info": {"score": {"team1": 0, "team2": 0}, "team1": {"name": "", "metrics": {"energy": 0, "total_sprints": 0, "total_distance": 0, "sprint_distance": 0, "avg_sprint_speed": 0}}, "team2": {"name": "", "metrics": {"energy": 0, "total_sprints": 0, "total_distance": 0, "sprint_distance": 0, "avg_sprint_speed": 0}}}}'::jsonb
      ORDER BY created_at DESC 
      LIMIT 5
    `);
    
    recentResult.rows.forEach((row, i) => {
      console.log(`\n[${i+1}] Session ID: ${row.id}, Created: ${row.created_at}`);
      console.log(`Team 1: ${row.session_data.match_info.team1.name}`);
      console.log(`Team 2: ${row.session_data.match_info.team2.name}`);
      console.log(`Score: ${row.session_data.match_info.score.team1} - ${row.session_data.match_info.score.team2}`);
      console.log("Team 1 Metrics:", row.session_data.match_info.team1.metrics);
    });
    
  } catch (err) {
    console.error('Error executing query', err);
  } finally {
    await pool.end();
  }
}

checkSessionData();