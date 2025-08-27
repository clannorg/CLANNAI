const { Pool } = require('pg');

const pool = new Pool({
  connectionString: "postgresql://postgres:ClannWebApp2024!@clann-webapp-prod.cfcgo2cma4or.eu-west-1.rds.amazonaws.com:5432/postgres",
  ssl: { rejectUnauthorized: false }
});

async function checkTraining() {
  const client = await pool.connect();
  
  try {
    console.log('🔍 Checking training_url in database...');
    
    // First check the table structure
    const structure = await client.query(
      "SELECT column_name FROM information_schema.columns WHERE table_name = 'games'"
    );
    console.log('📋 Table columns:', structure.rows.map(r => r.column_name));
    
    const result = await client.query(
      'SELECT id, title, training_url FROM games WHERE id = $1',
      ['50ce15ae-b083-4e93-a831-d9f950c39ee8']
    );
    
    console.log('📊 Results:', result.rows);
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    client.release();
    await pool.end();
  }
}

checkTraining();
