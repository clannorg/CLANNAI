const { Pool } = require('pg')
require('dotenv').config({ path: '../../backend/.env' })

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
  ssl: { rejectUnauthorized: false }
})

async function addCompanyUsersToAllTeams() {
  try {
    console.log('🏢 Adding all company users to all teams...\n')
    
    // Get all company users
    const companyUsersQuery = `
      SELECT id, name, email 
      FROM users 
      WHERE role = 'company'
    `
    const companyUsers = await pool.query(companyUsersQuery)
    console.log(`Found ${companyUsers.rows.length} company users:`)
    companyUsers.rows.forEach(user => {
      console.log(`  - ${user.name} (${user.email})`)
    })
    
    // Get all teams
    const teamsQuery = `
      SELECT id, name, team_code 
      FROM teams
    `
    const teams = await pool.query(teamsQuery)
    console.log(`\nFound ${teams.rows.length} teams:`)
    teams.rows.forEach(team => {
      console.log(`  - ${team.name} (${team.team_code})`)
    })
    
    // Add each company user to each team (if not already member)
    let addedCount = 0
    for (const user of companyUsers.rows) {
      for (const team of teams.rows) {
        const insertQuery = `
          INSERT INTO team_members (team_id, user_id)
          VALUES ($1, $2)
          ON CONFLICT (team_id, user_id) DO NOTHING
          RETURNING id
        `
        const result = await pool.query(insertQuery, [team.id, user.id])
        if (result.rows.length > 0) {
          console.log(`✅ Added ${user.name} to ${team.name}`)
          addedCount++
        }
      }
    }
    
    console.log(`\n🎉 Successfully added ${addedCount} new team memberships!`)
    
    // Verify results
    console.log('\n📊 Verification - Company users per team:')
    for (const team of teams.rows) {
      const membersQuery = `
        SELECT u.name, u.role
        FROM team_members tm
        JOIN users u ON tm.user_id = u.id
        WHERE tm.team_id = $1 AND u.role = 'company'
      `
      const members = await pool.query(membersQuery, [team.id])
      console.log(`  ${team.name}: ${members.rows.length} company members`)
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message)
  } finally {
    await pool.end()
  }
}

addCompanyUsersToAllTeams()
