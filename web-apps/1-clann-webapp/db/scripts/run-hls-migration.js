#!/usr/bin/env node

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

// Database configuration
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

async function runHlsMigration() {
  const client = await pool.connect();
  
  try {
    console.log('🚀 Running HLS migration...');
    
    // Read the migration file
    const migrationPath = path.join(__dirname, '../migrations/006_add_hls_conversions.sql');
    const migrationSQL = fs.readFileSync(migrationPath, 'utf8');
    
    // Execute the migration
    await client.query(migrationSQL);
    
    console.log('✅ HLS migration completed successfully!');
    
    // Verify the new tables exist
    const result = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      AND table_name IN ('hls_conversions', 'hls_conversion_jobs')
      ORDER BY table_name;
    `);
    
    console.log('📋 New tables created:');
    result.rows.forEach(row => {
      console.log(`  - ${row.table_name}`);
    });
    
  } catch (error) {
    console.error('❌ Migration failed:', error.message);
    process.exit(1);
  } finally {
    client.release();
    await pool.end();
  }
}

runHlsMigration();