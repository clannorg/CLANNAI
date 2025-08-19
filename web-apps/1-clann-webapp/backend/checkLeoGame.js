require('dotenv').config();
const { pool } = require('./utils/database');

async function checkLeoGame() {
  try {
    console.log('🔍 Searching for Leo game...');
    
    // Search for Leo game
    const leoResult = await pool.query(`
      SELECT id, team_name, team_color, status, created_at, metadata 
      FROM games 
      WHERE LOWER(team_name) LIKE '%leo%' 
      ORDER BY created_at DESC 
      LIMIT 1
    `);
    
    if (leoResult.rows.length > 0) {
      const game = leoResult.rows[0];
      console.log('=== LEO GAME FOUND ===');
      console.log('ID:', game.id);
      console.log('Team Name:', game.team_name);
      console.log('Team Color:', game.team_color);
      console.log('Status:', game.status);
      console.log('Created:', game.created_at);
      
      if (game.metadata) {
        console.log('\n=== METADATA ===');
        const meta = JSON.parse(game.metadata);
        console.log('Teams:', JSON.stringify(meta.teams, null, 2));
        console.log('Files:', Object.keys(meta.files || {}));
      } else {
        console.log('❌ No metadata found');
      }
    } else {
      console.log('❌ No Leo game found');
      
      // Show recent games instead
      const recentResult = await pool.query(`
        SELECT id, team_name, status, created_at 
        FROM games 
        ORDER BY created_at DESC 
        LIMIT 5
      `);
      
      console.log('\n=== RECENT GAMES ===');
      recentResult.rows.forEach(game => {
        console.log(`${game.id}: ${game.team_name} (${game.status})`);
      });
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    process.exit(0);
  }
}

checkLeoGame();