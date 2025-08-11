const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');

// Read .env file manually since dotenv might not be available
function loadEnv() {
  const envPath = path.join(__dirname, '../../backend/.env');
  
  if (!fs.existsSync(envPath)) {
    console.error('❌ .env file not found at:', envPath);
    process.exit(1);
  }
  
  const envContent = fs.readFileSync(envPath, 'utf8');
  const env = {};
  
  envContent.split('\n').forEach(line => {
    line = line.trim();
    if (line && !line.startsWith('#')) {
      const [key, ...values] = line.split('=');
      if (key && values.length > 0) {
        env[key] = values.join('=').replace(/^["']|["']$/g, ''); // Remove quotes
      }
    }
  });
  
  return env;
}

async function listAllGames() {
  try {
    const env = loadEnv();
    console.log('📂 Loaded environment from backend/.env');
    
    const connection = await mysql.createConnection({
      host: env.DB_HOST || 'localhost',
      user: env.DB_USER || 'root',
      password: env.DB_PASSWORD || 'password',
      database: env.DB_NAME || 'clann_ai',
      port: env.DB_PORT || 3306
    });

    console.log('🔌 Connected to database:', env.DB_NAME);
    console.log('🎮 All Games in Database:\n');

    const [games] = await connection.execute(`
      SELECT 
        id, 
        title, 
        team_name,
        status,
        created_at,
        video_url,
        CASE 
          WHEN ai_analysis IS NULL THEN 0
          WHEN JSON_LENGTH(ai_analysis) = 0 THEN 0
          ELSE JSON_LENGTH(ai_analysis)
        END as events_count
      FROM games 
      ORDER BY created_at DESC
    `);

    games.forEach((game, index) => {
      console.log(`${index + 1}. "${game.team_name}" - ${game.title}`);
      console.log(`   🆔 ID: ${game.id}`);
      console.log(`   📊 Status: ${game.status}`);
      console.log(`   🎯 Events: ${game.events_count}`);
      console.log(`   📅 Created: ${new Date(game.created_at).toLocaleDateString()}`);
      if (game.video_url.includes('20250523-match-23-may-2025-3fc1de88')) {
        console.log(`   🎬 Video: LONDON MATCH (20250523-match-23-may-2025-3fc1de88)`);
      } else if (game.video_url.includes('edinburgh')) {
        console.log(`   🎬 Video: EDINBURGH MATCH`);
      } else {
        console.log(`   🎬 Video: ${game.video_url.slice(0, 60)}...`);
      }
      console.log('');
    });

    console.log(`📈 Total games: ${games.length}`);
    
    // Show matching games for our pipeline outputs
    console.log('\n🔍 Pipeline Output Matches:');
    const londonGame = games.find(g => g.video_url.includes('20250523-match-23-may-2025-3fc1de88'));
    if (londonGame) {
      console.log(`✅ London match found: ${londonGame.id} (${londonGame.team_name})`);
    }
    
    const edinburghGame = games.find(g => g.video_url.includes('edinburgh') || g.team_name.toLowerCase().includes('edinburgh'));
    if (edinburghGame) {
      console.log(`✅ Edinburgh match found: ${edinburghGame.id} (${edinburghGame.team_name})`);
    }

    await connection.end();
  } catch (error) {
    console.error('❌ Database error:', error.message);
    console.error('💡 Make sure the backend/.env file has correct DB credentials');
  }
}

listAllGames();