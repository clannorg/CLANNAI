const { Pool } = require('pg');

const pool = new Pool({
  connectionString: "postgresql://postgres:ClannWebApp2024!@clann-webapp-prod.cfcgo2cma4or.eu-west-1.rds.amazonaws.com:5432/postgres",
  ssl: { rejectUnauthorized: false }
});

async function checkTactical() {
  const client = await pool.connect();
  
  try {
    const result = await client.query(
      'SELECT tactical_analysis FROM games WHERE id = $1',
      ['50ce15ae-b083-4e93-a831-d9f950c39ee8']
    );
    
    if (result.rows[0]?.tactical_analysis) {
      console.log('⚽ TACTICAL ANALYSIS CONTENT:');
      console.log(JSON.stringify(result.rows[0].tactical_analysis, null, 2));
    }
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    client.release();
    await pool.end();
  }
}

checkTactical();
