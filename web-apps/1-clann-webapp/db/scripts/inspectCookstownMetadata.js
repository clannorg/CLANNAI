const { Pool } = require("pg");
const path = require('path');
require("dotenv").config({ path: path.join(__dirname, '../../backend/.env') });

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT || 5432,
    ssl: { rejectUnauthorized: false }
});

async function inspectCookstownMetadata() {
    try {
        console.log('🔍 DETAILED COOKSTOWN METADATA INSPECTION');
        console.log('=========================================\n');

        const gameData = await pool.query(`
            SELECT 
                id,
                title,
                video_url,
                s3_key,
                status,
                ai_analysis,
                tactical_analysis,
                metadata
            FROM games 
            WHERE id = $1
        `, ['101776e8-b14b-471d-b7de-1f5354414d48']);

        if (gameData.rows.length === 0) {
            console.log('❌ Game not found');
            return;
        }

        const game = gameData.rows[0];

        console.log('🎮 GAME BASIC INFO:');
        console.log(`Title: ${game.title}`);
        console.log(`Status: ${game.status}`);
        console.log(`Video URL: ${game.video_url}`);
        console.log(`S3 Key: ${game.s3_key}\n`);

        console.log('📊 AI EVENTS SAMPLE:');
        console.log('===================');
        if (game.ai_analysis && game.ai_analysis.length > 0) {
            console.log(`Total events: ${game.ai_analysis.length}`);
            console.log('First 3 events:');
            game.ai_analysis.slice(0, 3).forEach((event, i) => {
                console.log(`${i+1}. ${event.type} at ${event.timestamp}s (${event.team}): ${event.description || 'No description'}`);
            });

            // Event type breakdown
            const eventTypes = {};
            game.ai_analysis.forEach(event => {
                eventTypes[event.type] = (eventTypes[event.type] || 0) + 1;
            });
            console.log('\nEvent breakdown:');
            Object.entries(eventTypes).forEach(([type, count]) => {
                console.log(`  ${type}: ${count}`);
            });
        } else {
            console.log('❌ No AI events found');
        }

        console.log('\n🧠 TACTICAL ANALYSIS:');
        console.log('====================');
        if (game.tactical_analysis) {
            console.log(`Full tactical structure:`, JSON.stringify(game.tactical_analysis, null, 2));
        } else {
            console.log('❌ No tactical analysis found');
        }

        console.log('\n📋 METADATA DETAILS:');
        console.log('====================');
        if (game.metadata) {
            console.log(`Full metadata structure:`, JSON.stringify(game.metadata, null, 2));
        } else {
            console.log('❌ No metadata found');
        }

    } catch (err) {
        console.error('❌ Error:', err.message);
    } finally {
        await pool.end();
    }
}

inspectCookstownMetadata();