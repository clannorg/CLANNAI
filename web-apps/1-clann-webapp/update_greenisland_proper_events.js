const { Pool } = require('pg');

// Database connection
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://postgres:ClannWebApp2024!@clann-webapp-prod.cfcgo2cma4or.eu-west-1.rds.amazonaws.com:5432/postgres',
  ssl: { rejectUnauthorized: false }
});

async function updateGreenislandEvents() {
  console.log('🔄 Updating Greenisland events with enhanced S3 data...');
  
  try {
    // Fetch enhanced events from S3
    const response = await fetch('https://end-nov-webapp-clann.s3.amazonaws.com/analysis-data/19-20250419-web_events_array-json.json');
    const enhancedEvents = await response.json();
    
    console.log(`📥 Fetched ${enhancedEvents.length} enhanced events from S3`);
    
    // Find Greenisland game by VEO URL (since that's what identifies it)
    const gameQuery = `
      SELECT id, title, ai_analysis 
      FROM games 
      WHERE video_url LIKE '%20250111-ballyclare%' 
      AND team_id IN (
        SELECT id FROM teams WHERE LOWER(name) LIKE '%greenisland%'
      )
    `;
    
    const gameResult = await pool.query(gameQuery);
    
    if (gameResult.rows.length === 0) {
      console.log('❌ No Greenisland game found');
      return;
    }
    
    const game = gameResult.rows[0];
    console.log(`🎮 Found game: "${game.title}" (ID: ${game.id})`);
    console.log(`📊 Current events: ${Array.isArray(game.ai_analysis) ? game.ai_analysis.length : 'Not array'}`);
    
    // Update the game with enhanced events
    const updateQuery = `
      UPDATE games 
      SET ai_analysis = $1::jsonb,
          updated_at = NOW()
      WHERE id = $2
    `;
    
    await pool.query(updateQuery, [JSON.stringify(enhancedEvents), game.id]);
    
    console.log(`✅ Updated game ${game.id} with ${enhancedEvents.length} enhanced events!`);
    
    // Verify the update
    const verifyQuery = `
      SELECT 
        title,
        jsonb_array_length(ai_analysis) as event_count,
        ai_analysis->0 as sample_event
      FROM games 
      WHERE id = $1
    `;
    
    const verifyResult = await pool.query(verifyQuery, [game.id]);
    const updated = verifyResult.rows[0];
    
    console.log(`🔍 Verification:`);
    console.log(`   Game: ${updated.title}`);
    console.log(`   Events: ${updated.event_count}`);
    console.log(`   Sample: ${JSON.stringify(updated.sample_event, null, 2)}`);
    
  } catch (error) {
    console.error('❌ Error updating events:', error);
  } finally {
    await pool.end();
  }
}

updateGreenislandEvents();