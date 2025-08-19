const { Pool } = require("pg");
const path = require('path');
const fs = require('fs');
require("dotenv").config({ path: path.join(__dirname, '../../backend/.env') });

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT || 5432,
    ssl: {
        rejectUnauthorized: false
    }
});

async function backupGamesTable() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
    const backupDir = path.join(__dirname, '../backups');
    const backupFile = path.join(backupDir, `games-backup-${timestamp}.json`);
    
    // Create backups directory if it doesn't exist
    if (!fs.existsSync(backupDir)) {
        fs.mkdirSync(backupDir, { recursive: true });
        console.log('📁 Created backups directory');
    }

    console.log('🔄 Starting games table backup...');
    console.log(`📅 Backup file: ${backupFile}`);
    
    try {
        // Get all games data
        const query = `
            SELECT 
                g.*,
                t.name as team_name,
                u.name as uploaded_by_name,
                u.email as uploaded_by_email
            FROM games g
            LEFT JOIN teams t ON g.team_id = t.id
            LEFT JOIN users u ON g.uploaded_by = u.id
            ORDER BY g.created_at DESC
        `;
        
        const result = await pool.query(query);
        
        const backupData = {
            backup_date: new Date().toISOString(),
            backup_type: 'games_table_with_relationships',
            total_games: result.rows.length,
            games: result.rows
        };
        
        // Write to JSON file
        fs.writeFileSync(backupFile, JSON.stringify(backupData, null, 2));
        
        const stats = fs.statSync(backupFile);
        const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
        
        console.log('✅ Games table backup completed!');
        console.log(`📊 Backed up ${result.rows.length} games`);
        console.log(`📊 Backup size: ${sizeMB} MB`);
        console.log(`📁 Location: ${backupFile}`);
        
        // Show what we backed up
        console.log('\n📋 Backed up games:');
        result.rows.slice(0, 5).forEach((game, index) => {
            console.log(`   [${index + 1}] ${game.title} (${game.team_name || 'No Team'}) - ${game.status}`);
        });
        
        if (result.rows.length > 5) {
            console.log(`   ... and ${result.rows.length - 5} more games`);
        }
        
        return backupFile;
        
    } catch (error) {
        console.error('❌ Backup failed:', error.message);
        throw error;
    } finally {
        await pool.end();
    }
}

// Run backup if called directly
if (require.main === module) {
    backupGamesTable()
        .then(() => {
            console.log('\n💡 This backup contains all games data including:');
            console.log('   - Game metadata and analysis');
            console.log('   - Team and user relationships');
            console.log('   - All JSONB fields (ai_analysis, metadata, etc.)');
            console.log('\n🔒 Safe to proceed with migration!');
            process.exit(0);
        })
        .catch(error => {
            console.error('❌ Backup failed:', error.message);
            process.exit(1);
        });
}

module.exports = { backupGamesTable };