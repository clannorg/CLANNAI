const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL && process.env.DATABASE_URL.includes('rds.amazonaws.com') ? { 
    rejectUnauthorized: false 
  } : false
});

async function runTrainingMigration() {
  const client = await pool.connect();
  
  try {
    console.log('🏋️ Running training_url migration...');
    
    // Add training_url column
    await client.query(`
      -- Add training_url column to games table for training recommendations
      ALTER TABLE games 
      ADD COLUMN IF NOT EXISTS training_url TEXT;
    `);
    
    // Add comment
    await client.query(`
      COMMENT ON COLUMN games.training_url IS 'URL for training recommendations JSON file (e.g., https://bucket.s3.amazonaws.com/analysis-data/game-id-training.json)';
    `);
    
    console.log('✅ Added training_url column to games table');
    console.log('🏋️ Training recommendations migration completed successfully!');
    
  } catch (error) {
    console.error('❌ Migration failed:', error);
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

// Run the migration
runTrainingMigration()
  .then(() => {
    console.log('🎯 Migration completed successfully');
    process.exit(0);
  })
  .catch((error) => {
    console.error('💥 Migration failed:', error);
    process.exit(1);
  });
