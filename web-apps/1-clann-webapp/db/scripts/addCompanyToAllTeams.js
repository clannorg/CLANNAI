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

async function addCompanyToAllTeams() {
  try {
    // Get company user
    const companyUser = await pool.query('SELECT id, email, role FROM users WHERE email = $1', ['thomas@clann.ai']);
    
    if (companyUser.rows.length === 0) {
      console.log('❌ Company user thomas@clann.ai not found');
      return;
    }
    
    const userId = companyUser.rows[0].id;
    console.log('👤 Found company user:', companyUser.rows[0]);
    
    // Get all teams
    const allTeams = await pool.query('SELECT id, name, team_code FROM teams ORDER BY name');
    console.log(`\n📊 Found ${allTeams.rows.length} teams total`);
    
    // Get current memberships
    const currentMemberships = await pool.query('SELECT team_id FROM team_members WHERE user_id = $1', [userId]);
    const memberTeamIds = currentMemberships.rows.map(row => row.team_id);
    
    console.log(`✅ Currently member of ${memberTeamIds.length} teams`);
    
    // Add to missing teams
    let addedCount = 0;
    
    for (const team of allTeams.rows) {
      if (!memberTeamIds.includes(team.id)) {
        try {
          await pool.query(
            'INSERT INTO team_members (user_id, team_id, joined_at) VALUES ($1, $2, NOW()) ON CONFLICT (user_id, team_id) DO NOTHING',
            [userId, team.id]
          );
          
          console.log(`➕ Added to team: ${team.name} (${team.team_code})`);
          addedCount++;
        } catch (error) {
          console.error(`❌ Failed to add to team ${team.name}:`, error.message);
        }
      } else {
        console.log(`✅ Already member of: ${team.name} (${team.team_code})`);
      }
    }
    
    console.log(`\n🎉 SUCCESS! Added company user to ${addedCount} new teams`);
    
    // Verify final membership count
    const finalMemberships = await pool.query('SELECT team_id FROM team_members WHERE user_id = $1', [userId]);
    console.log(`🏆 Final membership count: ${finalMemberships.rows.length}/${allTeams.rows.length} teams`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    throw error;
  } finally {
    await pool.end();
  }
}

addCompanyToAllTeams();