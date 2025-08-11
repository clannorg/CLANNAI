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

async function checkLondonGame() {
  const env = loadEnv();
  const pool = new Pool({
    host: env.DB_HOST,
    user: env.DB_USER,
    password: env.DB_PASSWORD,
    database: env.DB_NAME,
    port: env.DB_PORT || 5432,
    ssl: { rejectUnauthorized: false }
  });

  const gameId = 'd8e8ec0a-bda1-4f8c-baeb-61c51e36a346';
  
  const result = await pool.query('SELECT ai_analysis FROM games WHERE id = $1', [gameId]);
  
  if (result.rows.length > 0) {
    const analysis = result.rows[0].ai_analysis;
    console.log('🎮 London Game AI Analysis:');
    console.log('📊 Type:', typeof analysis);
    console.log('📊 Is Array:', Array.isArray(analysis));
    console.log('📊 Length:', analysis ? analysis.length : 'N/A');
    console.log('📋 First event:', analysis && analysis[0] ? JSON.stringify(analysis[0], null, 2) : 'None');
    console.log('📋 Sample events:');
    if (analysis && analysis.length > 0) {
      analysis.slice(0, 3).forEach((event, i) => {
        console.log(`  ${i + 1}. Type: ${event.type || event.event_type}, Timestamp: ${event.timestamp || event.timestamp_seconds}`);
      });
    }
  } else {
    console.log('❌ Game not found');
  }
  
  await pool.end();
}

checkLondonGame().catch(console.error);