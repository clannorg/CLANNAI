const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../backend/.env') });
const { Pool } = require('pg');

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT || 5432,
  ssl: { rejectUnauthorized: false }  // Required for AWS RDS
});

async function checkEvents() {
  try {
    console.log('🔍 Checking Greenisland Events Content...\n');
    
    const query = `
      SELECT 
        g.id, g.title, g.status,
        CASE 
          WHEN g.ai_analysis IS NOT NULL THEN jsonb_array_length(g.ai_analysis)
          ELSE 0 
        END as event_count,
        g.ai_analysis
      FROM games g 
      JOIN teams t ON g.team_id = t.id 
      WHERE t.name = 'greenisland' 
      AND g.status = 'analyzed'
      LIMIT 1
    `;
    
    const result = await pool.query(query);
    
    if (result.rows.length === 0) {
      console.log('❌ No Greenisland games found');
      return;
    }
    
    const game = result.rows[0];
    console.log(`📊 Game: "${game.title}"`);
    console.log(`📋 Total Events: ${game.event_count}`);
    
    if (game.ai_analysis && game.ai_analysis.length > 0) {
      // Count event types
      const eventTypes = {};
      game.ai_analysis.forEach(event => {
        eventTypes[event.type] = (eventTypes[event.type] || 0) + 1;
      });
      
      console.log('\n📊 Event Type Breakdown:');
      Object.entries(eventTypes)
        .sort((a,b) => b[1] - a[1])
        .forEach(([type, count]) => {
          console.log(`  ${type}: ${count}`);
        });
      
      // Check specifically for turnovers
      if (eventTypes.turnover) {
        console.log('\n✅ TURNOVER EVENTS FOUND!');
        const turnovers = game.ai_analysis
          .filter(e => e.type === 'turnover')
          .slice(0, 3);
        
        console.log('\nSample turnovers:');
        turnovers.forEach((t, i) => {
          console.log(`  ${i+1}. ${t.timestamp}s [${t.team}]: ${t.description.substring(0, 60)}...`);
        });
      } else {
        console.log('\n❌ NO TURNOVER EVENTS FOUND');
        console.log('\nActual event types:', Object.keys(eventTypes).join(', '));
      }
    } else {
      console.log('❌ No events data found');
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await pool.end();
  }
}

checkEvents();