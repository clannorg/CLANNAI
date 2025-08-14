const { Pool } = require('pg');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../backend/.env') });

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT || 5432,
  ssl: { rejectUnauthorized: false }
});

async function checkCompanyTeamMembership() {
  try {
    // Get all teams
    const allTeams = await pool.query('SELECT id, name, team_code FROM teams ORDER BY name');
    console.log('📊 ALL TEAMS IN DATABASE:');
    console.table(allTeams.rows);
    
    // Get company user (thomas@clann.ai)
    const companyUser = await pool.query('SELECT id, email, role FROM users WHERE email = $1', ['thomas@clann.ai']);
    
    if (companyUser.rows.length > 0) {
      const userId = companyUser.rows[0].id;
      console.log('\n👤 Company User:', companyUser.rows[0]);
      
      // Get teams this user is member of
      const userTeams = await pool.query('SELECT team_id FROM team_members WHERE user_id = $1', [userId]);
      const memberTeamIds = userTeams.rows.map(row => row.team_id);
      
      console.log('\n✅ Teams user is MEMBER of (IDs):', memberTeamIds);
      
      // Find teams user is NOT member of
      const nonMemberTeams = allTeams.rows.filter(team => !memberTeamIds.includes(team.id));
      
      console.log('\n❌ Teams user is NOT member of:');
      console.table(nonMemberTeams);
      
      return { allTeams: allTeams.rows, userId, nonMemberTeams };
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  } finally {
    await pool.end();
  }
}

checkCompanyTeamMembership();