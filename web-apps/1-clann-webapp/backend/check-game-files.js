const { Pool } = require('pg');

const pool = new Pool({
  connectionString: "postgresql://postgres:ClannWebApp2024!@clann-webapp-prod.cfcgo2cma4or.eu-west-1.rds.amazonaws.com:5432/postgres",
  ssl: { rejectUnauthorized: false }
});

async function checkGameFiles() {
  const client = await pool.connect();
  
  try {
    console.log('🔍 Checking all files for Dalkey vs Corduff game...');
    
    const result = await client.query(
      `SELECT 
        id, 
        title,
        video_url,
        metadata_url,
        training_url,
        tactical_analysis,
        ai_analysis,
        status
      FROM games 
      WHERE id = $1`,
      ['50ce15ae-b083-4e93-a831-d9f950c39ee8']
    );
    
    if (result.rows.length === 0) {
      console.log('❌ Game not found');
      return;
    }
    
    const game = result.rows[0];
    console.log('🎯 Game:', game.title);
    console.log('📊 Status:', game.status);
    console.log('\n📁 FILES STORED:');
    
    if (game.video_url) {
      console.log('🎥 Video URL:', game.video_url);
    } else {
      console.log('🎥 Video URL: ❌ Not set');
    }
    
    if (game.metadata_url) {
      console.log('📋 Metadata URL:', game.metadata_url);
    } else {
      console.log('📋 Metadata URL: ❌ Not set');
    }
    
    if (game.training_url) {
      console.log('🏋️ Training URL:', game.training_url);
    } else {
      console.log('🏋️ Training URL: ❌ Not set');
    }
    
    if (game.tactical_analysis) {
      console.log('⚽ Tactical Analysis: ✅ Stored in database (JSON object)');
      console.log('   Keys:', Object.keys(game.tactical_analysis));
    } else {
      console.log('⚽ Tactical Analysis: ❌ Not set');
    }
    
    if (game.ai_analysis && game.ai_analysis.length > 0) {
      console.log('🤖 AI Analysis: ✅ Stored in database');
      console.log('   Events count:', game.ai_analysis.length);
      console.log('   Sample event:', game.ai_analysis[0]);
    } else {
      console.log('🤖 AI Analysis: ❌ Not set');
    }
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    client.release();
    await pool.end();
  }
}

checkGameFiles();
