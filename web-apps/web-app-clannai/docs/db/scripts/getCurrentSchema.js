const { Pool } = require('pg');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../../server/.env') });

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT,
    ssl: {
        rejectUnauthorized: false
    }
});

async function getCurrentSchema() {
    try {
        // Get tables in correct order
        const tables = await pool.query(`
            SELECT tablename as table_name
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        `);

        console.log('-- Current Database Schema\n');
        console.log('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";\n');

        for (const table of tables.rows) {
            const tableName = table.table_name;

            // Get columns
            const columns = await pool.query(`
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    column_default,
                    is_nullable
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position;
            `, [tableName]);

            // Get constraints
            const constraints = await pool.query(`
                SELECT pg_get_constraintdef(c.oid) as constraint_def
                FROM pg_constraint c
                JOIN pg_class t ON c.conrelid = t.oid
                WHERE t.relname = $1;
            `, [tableName]);

            console.log(`-- Table: ${tableName}`);
            console.log(`CREATE TABLE ${tableName} (`);
            
            // Format columns
            const columnDefs = columns.rows.map(col => {
                let def = `    ${col.column_name} ${col.data_type}`;
                if (col.character_maximum_length) {
                    def += `(${col.character_maximum_length})`;
                }
                if (col.is_nullable === 'NO') {
                    def += ' NOT NULL';
                }
                if (col.column_default) {
                    def += ` DEFAULT ${col.column_default}`;
                }
                return def;
            }).join(',\n');
            
            console.log(columnDefs);

            // Add constraints if they exist
            if (constraints.rows.length > 0) {
                console.log('    -- Constraints');
                console.log('    ' + constraints.rows.map(c => c.constraint_def).join(',\n    '));
            }
            console.log(');\n');
        }

    } catch (error) {
        console.error('Error getting schema:', error);
    } finally {
        await pool.end();
    }
}

getCurrentSchema(); 