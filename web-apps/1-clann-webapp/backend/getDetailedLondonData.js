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

async function getDetailedLondonData() {
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
    const gameId = 'd8e8ec0a-bda1-4f8c-baeb-61c51e36a346';
    
    const query = `
      SELECT 
        id, title, video_url, s3_key, status, created_at,
        metadata, ai_analysis, tactical_analysis
      FROM games 
      WHERE id = $1
    `;
    
    const result = await pool.query(query, [gameId]);
    
    if (result.rows.length > 0) {
      const game = result.rows[0];
      console.log('🎮 DETAILED EAST LONDON BALLER GAME DATA:\n');
      
      console.log('📋 Basic Info:');
      console.log(`  ID: ${game.id}`);
      console.log(`  Title: ${game.title}`);
      console.log(`  Status: ${game.status}`);
      console.log(`  VEO URL: ${game.video_url}`);
      console.log(`  S3 Key: ${game.s3_key}`);
      console.log(`  Created: ${game.created_at}\n`);
      
      console.log('📊 METADATA CONTENT:');
      if (game.metadata) {
        console.log(JSON.stringify(game.metadata, null, 2));
      } else {
        console.log('  No metadata found');
      }
      
      console.log('\n🤖 AI ANALYSIS:');
      if (game.ai_analysis) {
        console.log(`  Type: ${typeof game.ai_analysis}`);
        console.log(`  Is Array: ${Array.isArray(game.ai_analysis)}`);
        if (Array.isArray(game.ai_analysis)) {
          console.log(`  Events Count: ${game.ai_analysis.length}`);
          console.log(`  Sample Events:`);
          game.ai_analysis.slice(0, 3).forEach((event, i) => {
            console.log(`    ${i+1}. ${event.type} at ${Math.floor(event.timestamp/60)}:${(event.timestamp%60).toString().padStart(2,'0')}`);
          });
        } else {
          console.log('  Structure:', Object.keys(game.ai_analysis));
        }
      } else {
        console.log('  No AI analysis found');
      }
      
      console.log('\n⚽ TACTICAL ANALYSIS:');
      if (game.tactical_analysis) {
        console.log(`  Type: ${typeof game.tactical_analysis}`);
        console.log(`  Keys: ${Object.keys(game.tactical_analysis).join(', ')}`);
        
        if (game.tactical_analysis.tactical) {
          console.log(`  Tactical Files: ${Object.keys(game.tactical_analysis.tactical).join(', ')}`);
        }
        if (game.tactical_analysis.analysis) {
          console.log(`  Analysis Files: ${Object.keys(game.tactical_analysis.analysis).join(', ')}`);
        }
      } else {
        console.log('  No tactical analysis found');
      }
      
    } else {
      console.log('❌ Game not found');
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await pool.end();
  }
}

getDetailedLondonData().catch(console.error);