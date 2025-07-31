#!/usr/bin/env node

/**
 * Delete Demo Games from ClannAI Dashboard
 * Removes the specific fake games that are cluttering the dashboard
 */

const { Pool } = require('pg');
const path = require('path');

// Try to find database configuration
const possibleEnvPaths = [
    path.join(__dirname, 'web-apps/web-app-clannai/server/.env'),
    path.join(__dirname, 'web-apps/1-clann-webapp/backend/.env'),
    path.join(__dirname, 'web-apps/clannai-frontend/.env'),
    path.join(__dirname, '.env')
];

// Try to load environment variables from possible locations
let envLoaded = false;
for (const envPath of possibleEnvPaths) {
    try {
        require('dotenv').config({ path: envPath });
        const fs = require('fs');
        if (fs.existsSync(envPath)) {
            console.log(`📋 Loading config from: ${envPath}`);
            envLoaded = true;
            break;
        }
    } catch (error) {
        // Continue trying other paths
    }
}

if (!envLoaded) {
    console.log('⚠️  No .env file found. You may need to set DATABASE_URL manually.');
}

// Database connection
const pool = new Pool({
    connectionString: process.env.DATABASE_URL || `postgresql://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`,
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

async function deleteDemoGames() {
    const client = await pool.connect();
    
    try {
        console.log('🎯 Targeting specific demo games for deletion...\n');

        // First, show the demo games that will be deleted
        const demoGames = await client.query(`
            SELECT title, video_url, status, created_at
            FROM games 
            WHERE title LIKE '%United U21s vs Tottenham Development%'
               OR title LIKE '%City Development vs Newcastle Academy%'
               OR title LIKE '%Liverpool Reserves vs Everton U21%'
               OR title LIKE '%Chelsea Youth vs Brighton Academy%'
               OR title LIKE '%Arsenal vs Local Academy%'
               OR video_url LIKE '%demo-videos.clann.ai%'
               OR video_url LIKE '%game269_0511.mp4%'
               OR video_url LIKE '%game277_0526.mp4%'
               OR video_url LIKE '%game297_0616.mp4%'
               OR video_url LIKE '%game298_0601.mp4%'
               OR video_url LIKE '%game304_0618.mp4%'
        `);

        console.log(`🗑️  Found ${demoGames.rows.length} demo games to delete:`);
        demoGames.rows.forEach((game, index) => {
            console.log(`${index + 1}. "${game.title}" (${game.status}) - ${game.video_url}`);
        });

        if (demoGames.rows.length === 0) {
            console.log('✅ No demo games found. Dashboard might already be clean!');
            return;
        }

        // Ask for confirmation
        console.log('\n⚠️  This will permanently delete these demo games from your dashboard.');
        console.log('Press Ctrl+C in the next 5 seconds to cancel...\n');
        
        await new Promise(resolve => setTimeout(resolve, 5000));

        // Delete the demo games
        const deleteResult = await client.query(`
            DELETE FROM games 
            WHERE title LIKE '%United U21s vs Tottenham Development%'
               OR title LIKE '%City Development vs Newcastle Academy%'
               OR title LIKE '%Liverpool Reserves vs Everton U21%'
               OR title LIKE '%Chelsea Youth vs Brighton Academy%'
               OR title LIKE '%Arsenal vs Local Academy%'
               OR video_url LIKE '%demo-videos.clann.ai%'
               OR video_url LIKE '%game269_0511.mp4%'
               OR video_url LIKE '%game277_0526.mp4%'
               OR video_url LIKE '%game297_0616.mp4%'
               OR video_url LIKE '%game298_0601.mp4%'
               OR video_url LIKE '%game304_0618.mp4%'
            RETURNING title
        `);

        console.log(`✅ Successfully deleted ${deleteResult.rows.length} demo games!`);
        
        // Clean up associated demo teams if they're empty
        console.log('\n🧹 Checking for empty demo teams...');
        
        const emptyDemoTeams = await client.query(`
            DELETE FROM teams 
            WHERE (name LIKE '%United U21s%' 
                OR name LIKE '%City Development%'
                OR name LIKE '%Liverpool Reserves%'
                OR name LIKE '%Chelsea Youth%'
                OR name LIKE '%Arsenal%Academy%'
                OR name LIKE '%Demo%')
            AND id NOT IN (SELECT DISTINCT team_id FROM games WHERE team_id IS NOT NULL)
            RETURNING name
        `);

        if (emptyDemoTeams.rows.length > 0) {
            console.log(`🗑️  Removed ${emptyDemoTeams.rows.length} empty demo teams`);
        }

        // Clean up demo users if they have no teams
        const emptyDemoUsers = await client.query(`
            DELETE FROM users 
            WHERE (email LIKE '%@demo.com%' 
                OR email LIKE '%coach@%'
                OR email LIKE '%demo%')
            AND id NOT IN (SELECT DISTINCT uploaded_by FROM games WHERE uploaded_by IS NOT NULL)
            AND id NOT IN (SELECT DISTINCT owner_id FROM teams WHERE owner_id IS NOT NULL)
            RETURNING email
        `);

        if (emptyDemoUsers.rows.length > 0) {
            console.log(`👤 Removed ${emptyDemoUsers.rows.length} orphaned demo users`);
        }

        console.log('\n🎉 Demo data cleanup complete!');
        console.log('Your ClannAI dashboard should now be clean of fake data.');

    } catch (error) {
        console.error('❌ Error cleaning up demo data:', error.message);
        console.log('\n💡 If you need to set database credentials manually:');
        console.log('   export DATABASE_URL="postgresql://user:password@host:port/database"');
        console.log('   or set DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD environment variables');
    } finally {
        client.release();
        await pool.end();
    }
}

console.log('🚀 ClannAI Demo Data Cleanup Tool');
console.log('==================================\n');
deleteDemoGames().catch(console.error); 