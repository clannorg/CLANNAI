require('dotenv').config({ path: '../../.env' });
const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

async function checkGreenislandEvents() {
  try {
    console.log('🔍 Checking Greenisland game events...');
    
    // Get the Greenisland game
    const gameQuery = `
      SELECT g.id, g.title, g.ai_analysis, t.name as team_name
      FROM games g 
      JOIN teams t ON g.team_id = t.id 
      WHERE t.name = 'greenisland' 
      AND g.status = 'analyzed'
      LIMIT 1
    `;
    
    const gameResult = await pool.query(gameQuery);
    
    if (gameResult.rows.length === 0) {
      console.log('❌ No analyzed Greenisland games found');
      return;
    }
    
    const game = gameResult.rows[0];
    console.log(`📊 Game: ${game.title} (ID: ${game.id})`);
    
    if (!game.ai_analysis) {
      console.log('❌ No ai_analysis data found');
      return;
    }
    
    const events = game.ai_analysis;
    console.log(`📋 Total events: ${events.length}`);
    
    // Count event types
    const eventTypes = {};
    events.forEach(event => {
      eventTypes[event.type] = (eventTypes[event.type] || 0) + 1;
    });
    
    console.log('\n📊 Event breakdown:');
    Object.entries(eventTypes).sort((a,b) => b[1] - a[1]).forEach(([type, count]) => {
      console.log(`  ${type}: ${count}`);
    });
    
    // Show turnover samples
    if (eventTypes.turnover) {
      console.log('\n✅ TURNOVER SAMPLES:');
      const turnovers = events.filter(e => e.type === 'turnover').slice(0, 5);
      turnovers.forEach(t => {
        console.log(`  ${t.timestamp}s [${t.team}]: ${t.description}`);
      });
    } else {
      console.log('\n❌ NO TURNOVERS FOUND');
      console.log('\n🔍 All event types found:');
      Object.keys(eventTypes).forEach(type => console.log(`  - ${type}`));
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await pool.end();
  }
}

checkGreenislandEvents();