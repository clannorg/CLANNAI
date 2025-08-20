const { Pool } = require('pg');

// Database configuration (hardcoded like other migration scripts)
const pool = new Pool({
  host: 'clann-webapp-prod.cfcgo2cma4or.eu-west-1.rds.amazonaws.com',
  user: 'postgres',
  password: 'ClannWebApp2024!',
  database: 'postgres',
  port: 5432,
  ssl: {
    rejectUnauthorized: false
  }
});

async function runMigration() {
  try {
    console.log('🔄 Running chunks base URL migration...');
    
    const migrationSQL = `
      -- Add chunks_base_url column to games table for pre-chunked video clips
      ALTER TABLE games 
      ADD COLUMN IF NOT EXISTS chunks_base_url TEXT;
      
      -- Add comment to document the column purpose
      COMMENT ON COLUMN games.chunks_base_url IS 'Base URL for pre-chunked video segments (e.g., https://bucket.s3.amazonaws.com/clips/game-id/)';
    `;
    
    await pool.query(migrationSQL);
    console.log('✅ Migration completed successfully!');
    console.log('📋 Added chunks_base_url column to games table');
    
  } catch (error) {
    console.error('❌ Migration failed:', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

runMigration();