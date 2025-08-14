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

async function checkCookstownData() {
    try {
        console.log('🏴󠁧󠁢󠁳󠁣󠁴󠁿 COOKSTOWN GAME DATA ANALYSIS');
        console.log('====================================\n');

        // 1. Find Cookstown game
        console.log('🔍 FINDING COOKSTOWN GAME...');
        const cookstownGame = await pool.query(`
            SELECT 
                g.id,
                g.title,
                g.description,
                g.video_url,
                g.s3_key,
                g.status,
                t.name as team_name,
                u.email as uploaded_by,
                g.created_at,
                CASE 
                    WHEN g.ai_analysis IS NOT NULL THEN jsonb_array_length(g.ai_analysis) 
                    ELSE NULL 
                END as events_count,
                CASE 
                    WHEN g.tactical_analysis IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END as has_tactical,
                CASE 
                    WHEN g.metadata IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END as has_metadata
            FROM games g
            JOIN teams t ON g.team_id = t.id
            JOIN users u ON g.uploaded_by = u.id
            WHERE LOWER(g.title) LIKE '%cookstown%' 
               OR LOWER(t.name) LIKE '%cookstown%'
               OR LOWER(g.description) LIKE '%cookstown%'
            ORDER BY g.created_at DESC;
        `);

        if (cookstownGame.rows.length === 0) {
            console.log('❌ No Cookstown game found in database');
            return;
        }

        console.table(cookstownGame.rows);

        // 2. Detailed analysis for each Cookstown game
        for (const game of cookstownGame.rows) {
            console.log(`\n🎮 DETAILED ANALYSIS FOR: ${game.title}`);
            console.log('================================================');
            
            // Get the full record
            const fullGame = await pool.query(`
                SELECT 
                    *
                FROM games 
                WHERE id = $1;
            `, [game.id]);

            const gameData = fullGame.rows[0];

            // Analyze S3 URLs and file contents
            console.log('\n📁 S3 FILES & URLS:');
            console.log('-------------------');
            console.log('Video URL:', gameData.video_url || 'None');
            console.log('S3 Key:', gameData.s3_key || 'None');

            // Analyze AI Events
            console.log('\n⚡ AI EVENTS ANALYSIS:');
            console.log('---------------------');
            if (gameData.ai_analysis) {
                const events = gameData.ai_analysis;
                console.log('Total Events:', events.length);
                
                // Count event types
                const eventTypes = {};
                events.forEach(event => {
                    eventTypes[event.type] = (eventTypes[event.type] || 0) + 1;
                });
                
                console.log('\nEvent Types Breakdown:');
                console.table(eventTypes);

                console.log('\nFirst 5 Events:');
                console.table(events.slice(0, 5));
            } else {
                console.log('❌ No AI events data found');
            }

            // Analyze Tactical Data
            console.log('\n🧠 TACTICAL ANALYSIS:');
            console.log('--------------------');
            if (gameData.tactical_analysis) {
                const tactical = gameData.tactical_analysis;
                console.log('Tactical Analysis Structure:');
                console.log('Keys:', Object.keys(tactical));
                
                if (tactical.red_team) {
                    console.log('\nRed Team:', tactical.red_team.team_name || 'Unknown');
                    console.log('Red Strengths:', tactical.red_team.strengths?.length || 0);
                }
                
                if (tactical.blue_team) {
                    console.log('Blue Team:', tactical.blue_team.team_name || 'Unknown');
                    console.log('Blue Strengths:', tactical.blue_team.strengths?.length || 0);
                }
            } else {
                console.log('❌ No tactical analysis data found');
            }

            // Analyze Metadata
            console.log('\n📊 METADATA:');
            console.log('------------');
            if (gameData.metadata) {
                const metadata = gameData.metadata;
                console.log('Metadata Keys:', Object.keys(metadata));
                
                if (metadata.teams) {
                    console.log('\nTeam Info:');
                    console.table(metadata.teams);
                }
                
                if (metadata.files) {
                    console.log('\nS3 File URLs:');
                    Object.entries(metadata.files).forEach(([key, url]) => {
                        console.log(`${key}:`, url);
                    });
                }
            } else {
                console.log('❌ No metadata found');
            }
        }

    } catch (err) {
        console.error('❌ Error:', err.message);
        console.error('Stack:', err.stack);
    } finally {
        await pool.end();
    }
}

checkCookstownData();