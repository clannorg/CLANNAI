const { Pool } = require("pg");
const path = require('path');
require("dotenv").config({ path: path.join(__dirname, '../../../server/.env') });

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT,
    ssl: { rejectUnauthorized: false }
});

async function printDbDefinition() {
    try {
        // 1. List all tables
        const tables = await pool.query(`
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        `);
        console.log('\n=== ALL TABLES ===');
        console.table(tables.rows);

        // 2. For each table, get its complete structure
        for (let table of tables.rows) {
            const tableName = table.table_name;
            
            // Get columns
            const columns = await pool.query(`
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position;
            `, [tableName]);
            
            // Get constraints
            const constraints = await pool.query(`
                SELECT
                    con.conname as constraint_name,
                    con.contype as constraint_type,
                    pg_get_constraintdef(con.oid) as definition
                FROM pg_constraint con
                JOIN pg_class rel ON rel.oid = con.conrelid
                WHERE rel.relname = $1;
            `, [tableName]);
            
            console.log(`\n=== TABLE: ${tableName.toUpperCase()} ===`);
            console.log('\nColumns:');
            console.table(columns.rows);
            console.log('\nConstraints:');
            console.table(constraints.rows);
        }

    } catch (error) {
        console.error('Error:', error);
    } finally {
        await pool.end();
    }
}

printDbDefinition();
