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

async function toggleTeamPremium(teamId, setPremium = false) {
    try {
        // First get current status
        const beforeStatus = await pool.query(`
            SELECT name, is_premium, subscription_status 
            FROM Teams 
            WHERE id = $1`,
            [teamId]
        );

        if (beforeStatus.rows.length === 0) {
            console.log(`❌ No team found with ID ${teamId}`);
            return;
        }

        console.log('Current status:', beforeStatus.rows[0]);

        // Update team status
        const result = await pool.query(`
            UPDATE Teams 
            SET is_premium = $1,
                subscription_status = $2,
                subscription_id = $3,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $4
            RETURNING *`,
            [
                setPremium,
                setPremium ? 'PREMIUM' : 'FREE',
                setPremium ? 'manual_override' : null,
                teamId
            ]
        );

        if (result.rows.length > 0) {
            console.log(`✅ Successfully ${setPremium ? 'enabled' : 'disabled'} premium for team ${result.rows[0].name}`);
            console.log('New status:', {
                name: result.rows[0].name,
                is_premium: result.rows[0].is_premium,
                subscription_status: result.rows[0].subscription_status
            });
        }
    } catch (error) {
        console.error('Error updating team status:', error);
    } finally {
        await pool.end();
    }
}

async function checkAllTeamsPremiumStatus() {
    try {
        const result = await pool.query(`
            SELECT 
                id,
                name,
                is_premium,
                subscription_status,
                subscription_id
            FROM Teams
            ORDER BY name;
        `);

        console.log('\n=== TEAMS PREMIUM STATUS ===');
        console.table(result.rows);
    } catch (error) {
        console.error('Error checking teams status:', error);
    } finally {
        await pool.end();
    }
}

// Check command line arguments
if (process.argv.length < 3) {
    console.log('Usage: node toggleTeamPremium.js <teamId> [true|false]');
    console.log('Example: node toggleTeamPremium.js 18f994d0-6eeb-4285-a453-a8aa176b1dce true');
    process.exit(1);
}

// Add this to handle the 'check' command
if (process.argv[2] === 'check') {
    checkAllTeamsPremiumStatus();
} else {
    const teamId = process.argv[2];
    const setPremium = process.argv[3] === 'true';
    toggleTeamPremium(teamId, setPremium);
}
