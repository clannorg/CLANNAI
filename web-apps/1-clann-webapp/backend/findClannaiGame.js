require('dotenv').config();
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || `postgresql://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`,
  ssl: process.env.DATABASE_URL && process.env.DATABASE_URL.includes('rds.amazonaws.com') ? { 
    rejectUnauthorized: false,
    require: true 
  } : false
});

async function findGame() {
  try {
    console.log('🔍 Searching for clannai game...');
    
    const result = await pool.query(`
      SELECT id, team_name, team_color, status, metadata, events 
      FROM games 
      WHERE LOWER(team_name) LIKE '%clannai%' OR LOWER(team_name) LIKE '%lost%'
      ORDER BY created_at DESC 
      LIMIT 3
    `);
    
    if (result.rows.length > 0) {
      result.rows.forEach((game, i) => {
        console.log(`\n=== GAME ${i + 1} ===`);
        console.log('ID:', game.id);
        console.log('Team Name:', game.team_name);
        console.log('Status:', game.status);
        
        if (game.metadata) {
          const meta = JSON.parse(game.metadata);
          console.log('\n📋 METADATA TEAMS:');
          if (meta.teams) {
            console.log('Red Team:', meta.teams.red_team?.name, '(', meta.teams.red_team?.jersey_color, ')');
            console.log('Blue Team:', meta.teams.blue_team?.name, '(', meta.teams.blue_team?.jersey_color, ')');
          } else {
            console.log('❌ No teams in metadata');
          }
        }
        
        if (game.events) {
          const events = JSON.parse(game.events);
          console.log('\n🎯 EVENT ANALYSIS:');
          console.log('Total events:', events.length);
          
          // Check team distribution
          const teamCounts = {};
          events.forEach(e => {
            teamCounts[e.team || 'undefined'] = (teamCounts[e.team || 'undefined'] || 0) + 1;
          });
          console.log('Team distribution:', teamCounts);
          
          // Show sample events
          console.log('\n📝 SAMPLE EVENTS:');
          events.slice(0, 3).forEach(event => {
            console.log(`- ${event.type}: team="${event.team}", desc="${event.description}"`);
          });
        }
      });
    } else {
      console.log('❌ No matching games found');
      
      // Show all recent games
      const allGames = await pool.query('SELECT id, team_name, status FROM games ORDER BY created_at DESC LIMIT 5');
      console.log('\n=== ALL RECENT GAMES ===');
      allGames.rows.forEach(g => console.log(`${g.id}: ${g.team_name} (${g.status})`));
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await pool.end();
  }
}

findGame();