const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
require("dotenv").config({ path: path.join(__dirname, '../../backend/.env') });

async function backupDatabase() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
    const backupDir = path.join(__dirname, '../backups');
    const backupFile = path.join(backupDir, `clannai-backup-${timestamp}.sql`);
    
    // Create backups directory if it doesn't exist
    if (!fs.existsSync(backupDir)) {
        fs.mkdirSync(backupDir, { recursive: true });
        console.log('📁 Created backups directory');
    }

    console.log('🔄 Starting database backup...');
    console.log(`📅 Backup file: ${backupFile}`);
    
    // Build pg_dump command with version compatibility flags
    const connectionString = `postgresql://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`;
    const command = `pg_dump --no-sync --no-tablespaces '${connectionString}' > '${backupFile}'`;
    
    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error('❌ Backup failed:', error.message);
                if (stderr) console.error('stderr:', stderr);
                reject(error);
                return;
            }
            
            // Check if backup file was created and has content
            if (fs.existsSync(backupFile)) {
                const stats = fs.statSync(backupFile);
                const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
                
                console.log('✅ Backup completed successfully!');
                console.log(`📊 Backup size: ${sizeMB} MB`);
                console.log(`📁 Location: ${backupFile}`);
                
                // Show recent backups
                const backups = fs.readdirSync(backupDir)
                    .filter(file => file.endsWith('.sql'))
                    .map(file => {
                        const filePath = path.join(backupDir, file);
                        const stats = fs.statSync(filePath);
                        return {
                            name: file,
                            size: (stats.size / 1024 / 1024).toFixed(2),
                            date: stats.mtime.toISOString().split('T')[0]
                        };
                    })
                    .sort((a, b) => b.date.localeCompare(a.date));
                
                if (backups.length > 1) {
                    console.log('\n📋 Recent backups:');
                    backups.slice(0, 5).forEach(backup => {
                        console.log(`   ${backup.name} (${backup.size} MB) - ${backup.date}`);
                    });
                }
                
                resolve(backupFile);
            } else {
                reject(new Error('Backup file was not created'));
            }
        });
    });
}

// Run backup if called directly
if (require.main === module) {
    backupDatabase()
        .then(() => {
            console.log('\n💡 To restore this backup:');
            console.log('   psql "your-connection-string" < backup-file.sql');
            process.exit(0);
        })
        .catch(error => {
            console.error('❌ Backup failed:', error.message);
            process.exit(1);
        });
}

module.exports = { backupDatabase };