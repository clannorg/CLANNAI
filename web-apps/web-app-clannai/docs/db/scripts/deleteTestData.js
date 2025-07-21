const { Pool } = require('pg');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../../server/.env') });

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT,
    ssl: { rejectUnauthorized: false }
});

async function deleteTestData() {
    const client = await pool.connect();
    
    try {
        // First show test teams to be deleted
        const testTeams = await client.query(`
            SELECT name, team_code, created_at, subscription_status
            FROM Teams 
            WHERE name LIKE '%feb%'           -- 21feb, 19feb2, etc
               OR name = 'brazil'             -- test team
               OR name = 'brazil2'            -- test team
               OR name = 'tommy'              -- test team
               OR name = 'tommy eats'         -- test team
               OR name = '18febtest'          -- obvious test
               OR name = 'ahwaitthisteamstuffacworks'  -- obvious test
               OR name = 'CLANNNNNNNNNNN'     -- test team
               OR name = 'ClannAI demo'       -- demo/test team
               OR name = '19efbfehbwdf'       -- gibberish test
               OR name = 'rossteam'           -- test team
        `);

        console.log('\n🏃 Test teams to be deleted:', testTeams.rows.length);
        testTeams.rows.forEach(t => {
            console.log(`  - "${t.name}" (${t.subscription_status}) created: ${t.created_at}`);
        });

        // Show test users to be deleted
        const testUsers = await client.query(`
            SELECT email, created_at, role 
            FROM Users 
            WHERE email LIKE '%feb%@%'
               OR email LIKE 't%@test%'
               OR email LIKE '%hi%@clann%'
               OR email LIKE 'test%@%'
               OR email LIKE 'coach@team%'
               OR email LIKE 'newuser@%'
               OR email LIKE 'stripeuser@%'
               OR email LIKE 'terms@%'
               OR email LIKE 't1t1%@%'
               OR email LIKE 'tetst%@%'
               OR email LIKE 't_@clannai.com'
               OR email LIKE '4f%@clann.com'
               OR email LIKE '1t%@test.com'
               OR email LIKE '10t%@%'
               OR email LIKE '44%f%@clann.com'
               OR email LIKE 'brazil%@clann.com'
               OR email LIKE 'thomas@test.com'
               OR email LIKE 't@testy.com'
               OR email LIKE 'minas@clann.com'      -- test user
        `);

        console.log('\n👤 Test users to be deleted:', testUsers.rows.length);
        testUsers.rows.forEach(u => {
            console.log(`  - ${u.email} (${u.role}) created: ${u.created_at}`);
        });

        // Confirm before deleting
        console.log('\nPress Ctrl+C to cancel if this looks wrong...');
        await new Promise(resolve => setTimeout(resolve, 5000));

        // Delete test teams (cascade will handle sessions)
        const deletedTeams = await client.query(`
            DELETE FROM Teams 
            WHERE name LIKE '%feb%'
               OR name = 'brazil'
               OR name = 'brazil2'
               OR name = 'tommy'
               OR name = 'tommy eats'
               OR name = '18febtest'
               OR name = 'ahwaitthisteamstuffacworks'
               OR name = 'CLANNNNNNNNNNN'
               OR name = 'ClannAI demo'
               OR name = '19efbfehbwdf'
               OR name = 'rossteam'
            RETURNING name
        `);

        // Delete test users
        const deletedUsers = await client.query(`
            DELETE FROM Users 
            WHERE email LIKE '%feb%@%'
               OR email LIKE 't%@test%'
               OR email LIKE '%hi%@clann%'
               OR email LIKE 'test%@%'
               OR email LIKE 'coach@team%'
               OR email LIKE 'newuser@%'
               OR email LIKE 'stripeuser@%'
               OR email LIKE 'terms@%'
               OR email LIKE 't1t1%@%'
               OR email LIKE 'tetst%@%'
               OR email LIKE 't_@clannai.com'
               OR email LIKE '4f%@clann.com'
               OR email LIKE '1t%@test.com'
               OR email LIKE '10t%@%'
               OR email LIKE '44%f%@clann.com'
               OR email LIKE 'brazil%@clann.com'
               OR email LIKE 'thomas@test.com'
               OR email LIKE 't@testy.com'
               OR email LIKE 'minas@clann.com'
            RETURNING email
        `);

        console.log(`\n✅ Successfully deleted ${deletedTeams.rows.length} test teams`);
        console.log(`✅ Successfully deleted ${deletedUsers.rows.length} test users`);

    } catch (error) {
        console.error('❌ Error:', error);
    } finally {
        client.release();
        await pool.end();
    }
}

console.log('🚀 Starting test data cleanup...');
deleteTestData(); 