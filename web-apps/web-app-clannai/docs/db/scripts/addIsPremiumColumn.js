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

async function addIsPremiumColumn() {
    try {
        await pool.query(`
            ALTER TABLE Teams 
            ADD COLUMN is_premium BOOLEAN DEFAULT FALSE;
        `);
    } catch (error) {
        process.exit(1);
    } finally {
        await pool.end();
    }
}

const addTrialColumn = async () => {
    await pool.query(`
        ALTER TABLE Teams 
        ADD COLUMN trial_ends_at TIMESTAMP,
        ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'FREE'
        CHECK (subscription_status IN ('FREE', 'TRIAL', 'PREMIUM'));
    `);
};

addIsPremiumColumn();
addTrialColumn();