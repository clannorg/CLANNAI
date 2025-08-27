const { Pool } = require('pg');

const pool = new Pool({
  connectionString: "postgresql://postgres:ClannWebApp2024!@clann-webapp-prod.cfcgo2cma4or.eu-west-1.rds.amazonaws.com:5432/postgres",
  ssl: { rejectUnauthorized: false }
});

async function addTrainingUrl() {
  const client = await pool.connect();
  
  try {
    console.log('🏋️ Adding training_url column...');
    
    // Add training_url column if it doesn't exist
    await client.query(`
      ALTER TABLE games 
      ADD COLUMN IF NOT EXISTS training_url TEXT;
    `);
    
    console.log('✅ training_url column added');
    
    // Update the Dalkey game with training URL
    const trainingUrl = "https://end-nov-webapp-clann.s3.amazonaws.com/analysis-data/20250427-match-apr-27-2025-9bd1cf29-3-3_training_recommendations-json.json";
    const gameId = "50ce15ae-b083-4e93-a831-d9f950c39ee8";
    
    await client.query(
      'UPDATE games SET training_url = $1 WHERE id = $2',
      [trainingUrl, gameId]
    );
    
    console.log('✅ Updated Dalkey game with training URL');
    console.log('🔗 Training URL:', trainingUrl);
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    client.release();
    await pool.end();
  }
}

addTrainingUrl();
