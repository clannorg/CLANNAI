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

async function checkAndAddCascadeDelete() {
    try {
        // First check current constraints
        const currentConstraints = await pool.query(`
            SELECT 
                tc.constraint_name, 
                tc.table_name, 
                kcu.column_name,
                rc.delete_rule
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.referential_constraints rc
              ON tc.constraint_name = rc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_name IN ('teammembers', 'sessions');
        `);

        console.log('\nCurrent constraints:');
        console.table(currentConstraints.rows);

        // Now try to add CASCADE
        console.log('\nAttempting to add CASCADE constraints...');
        await pool.query(`
            ALTER TABLE TeamMembers 
            DROP CONSTRAINT IF EXISTS teammembers_user_id_fkey,
            ADD CONSTRAINT teammembers_user_id_fkey 
                FOREIGN KEY (user_id) 
                REFERENCES Users(id) 
                ON DELETE CASCADE;

            ALTER TABLE Sessions
            DROP CONSTRAINT IF EXISTS sessions_uploaded_by_fkey,
            ADD CONSTRAINT sessions_uploaded_by_fkey 
                FOREIGN KEY (uploaded_by) 
                REFERENCES Users(id) 
                ON DELETE CASCADE;
        `);

        // Check constraints again
        const newConstraints = await pool.query(`
            SELECT 
                tc.constraint_name, 
                tc.table_name, 
                kcu.column_name,
                rc.delete_rule
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.referential_constraints rc
              ON tc.constraint_name = rc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_name IN ('teammembers', 'sessions');
        `);

        console.log('\nNew constraints:');
        console.table(newConstraints.rows);

    } catch (error) {
        console.error('Error:', error);
    } finally {
        await pool.end();
    }
}

checkAndAddCascadeDelete(); 