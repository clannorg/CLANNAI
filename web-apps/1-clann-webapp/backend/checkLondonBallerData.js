const { Pool } = require('pg');
const fs = require('fs');

function loadEnv() {
  const envContent = fs.readFileSync('.env', 'utf8');
  const env = {};
  envContent.split('\n').forEach(line => {
    line = line.trim();
    if (line && !line.startsWith('#')) {
      const [key, ...values] = line.split('=');
      if (key && values.length > 0) {
        env[key] = values.join('=').replace(/^["']|["']$/g, '');
      }
    }
  });
  return env;
}

async function checkLondonBallerData() {
  const env = loadEnv();
  const pool = new Pool({
    host: env.DB_HOST,
    user: env.DB_USER,
    password: env.DB_PASSWORD,
    database: env.DB_NAME,
    port: env.DB_PORT || 5432,
    ssl: { rejectUnauthorized: false }
  });

  try {
    console.log('🔍 Checking East London Baller data...\n');
    
    // Find the team
    const teamQuery = `
      SELECT id, name, team_code, owner_id, created_at 
      FROM teams 
      WHERE LOWER(name) LIKE '%london%' OR LOWER(name) LIKE '%baller%'
    `;
    
    const teamResult = await pool.query(teamQuery);
    console.log('📋 Teams found:', teamResult.rows.length);
    teamResult.rows.forEach(team => {
      console.log(`  - ${team.name} (ID: ${team.id})`);
    });
    
    // Find games with VEO URL containing the match ID
    const matchQuery = `
      SELECT 
        g.id, g.title, g.video_url, g.s3_key, g.status, g.created_at,
        g.metadata, g.ai_analysis IS NOT NULL as has_ai_analysis,
        g.tactical_analysis IS NOT NULL as has_tactical_analysis,
        t.name as team_name, u.email as uploaded_by_email
      FROM games g
      LEFT JOIN teams t ON g.team_id = t.id  
      LEFT JOIN users u ON g.uploaded_by = u.id
      WHERE g.video_url LIKE '%20250523-match-23-may-2025-3fc1de88%'
         OR LOWER(g.title) LIKE '%london%' 
         OR LOWER(g.title) LIKE '%baller%'
         OR LOWER(t.name) LIKE '%london%'
         OR LOWER(t.name) LIKE '%baller%'
    `;
    
    const matchResult = await pool.query(matchQuery);
    console.log(`\n🎮 Relevant games found: ${matchResult.rows.length}`);
    
    matchResult.rows.forEach((game, i) => {
      console.log(`\n--- Game ${i + 1} ---`);
      console.log(`ID: ${game.id}`);
      console.log(`Title: ${game.title}`);
      console.log(`Team: ${game.team_name || 'Unknown'}`);
      console.log(`Uploaded by: ${game.uploaded_by_email || 'Unknown'}`);
      console.log(`Status: ${game.status}`);
      console.log(`Created: ${game.created_at}`);
      console.log(`VEO URL: ${game.video_url || 'None'}`);
      console.log(`S3 Key: ${game.s3_key || 'None'}`);
      console.log(`Has AI Analysis: ${game.has_ai_analysis}`);
      console.log(`Has Tactical Analysis: ${game.has_tactical_analysis}`);
      
      if (game.metadata) {
        console.log(`Metadata available: ${Object.keys(game.metadata).join(', ')}`);
        if (game.metadata.teams) {
          console.log(`  Teams: ${game.metadata.teams.red_team?.name || 'Unknown'} vs ${game.metadata.teams.blue_team?.name || 'Unknown'}`);
        }
        if (game.metadata.counts) {
          console.log(`  Stats: ${game.metadata.counts.goals || 0} goals, ${game.metadata.counts.shots || 0} shots`);
        }
      }
    });
    
    // Check users
    const userQuery = `
      SELECT id, email, name, created_at 
      FROM users 
      WHERE email LIKE '%eastlondon%' OR LOWER(name) LIKE '%london%' OR LOWER(name) LIKE '%baller%'
    `;
    
    const userResult = await pool.query(userQuery);
    console.log(`\n👤 Relevant users found: ${userResult.rows.length}`);
    userResult.rows.forEach(user => {
      console.log(`  - ${user.email} (${user.name || 'No name'}) - ID: ${user.id}`);
    });
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await pool.end();
  }
}

checkLondonBallerData().catch(console.error);