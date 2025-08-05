const { Pool } = require("pg");
const path = require('path');
require("dotenv").config({ path: path.join(__dirname, '../../backend/.env') });

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT || 5432,
    ssl: { rejectUnauthorized: false }  // Required for AWS RDS
});

async function printSchema() {
    try {
        console.log('📋 DATABASE SCHEMA');
        console.log('==================\n');

        // Show all tables
        const tables = await pool.query(`
            SELECT 
                table_name,
                (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            ORDER BY table_name;
        `);
        
        console.log('📊 TABLES OVERVIEW');
        console.log('------------------');
        console.table(tables.rows);

        // Show detailed columns for each table
        for (const table of tables.rows) {
            console.log(`\n🔧 TABLE: ${table.table_name.toUpperCase()}`);
            console.log(''.padEnd(50, '-'));
            
            const columns = await pool.query(`
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position;
            `, [table.table_name]);
            
            console.table(columns.rows);
        }

        // Show row counts
        console.log('\n📈 ROW COUNTS');
        console.log('-------------');
        const counts = [];
        for (const table of tables.rows) {
            try {
                const count = await pool.query(`SELECT COUNT(*) as count FROM ${table.table_name}`);
                counts.push({
                    table: table.table_name,
                    rows: parseInt(count.rows[0].count)
                });
            } catch (err) {
                counts.push({
                    table: table.table_name,
                    rows: 'ERROR'
                });
            }
        }
        console.table(counts);

    } catch (err) {
        console.error('❌ Error:', err.message);
    } finally {
        await pool.end();
    }
}

printSchema();