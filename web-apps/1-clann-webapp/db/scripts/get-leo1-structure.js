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

async function getLeo1Structure() {
    try {
        console.log('🔍 LEO1 GAME STRUCTURE');
        console.log('======================\n');

        // Find the leo1 game (Clann vs Lostthehead)
        const query = `
            SELECT 
                g.id,
                g.title,
                g.ai_analysis,
                g.metadata,
                jsonb_array_length(g.ai_analysis) as event_count
            FROM games g
            WHERE g.title LIKE '%Clann vs Lostthehead%'
            OR g.title LIKE '%Flagship%'
            LIMIT 1
        `;

        const result = await pool.query(query);
        
        if (result.rows.length === 0) {
            console.log('❌ Leo1 game not found');
            return;
        }

        const game = result.rows[0];
        console.log(`📋 Game: ${game.title}`);
        console.log(`🆔 ID: ${game.id}`);
        console.log(`📊 Events: ${game.event_count || 'No events'}\n`);

        if (game.ai_analysis) {
            console.log('🤖 AI_ANALYSIS STRUCTURE:');
            console.log('=========================');
            
            // Show first few events to understand structure
            const events = game.ai_analysis;
            if (Array.isArray(events) && events.length > 0) {
                console.log(`Total events: ${events.length}\n`);
                
                // Show first 3 events
                console.log('📝 SAMPLE EVENTS (first 3):');
                events.slice(0, 3).forEach((event, i) => {
                    console.log(`\n[${i + 1}] Event Structure:`);
                    console.log(JSON.stringify(event, null, 2));
                });

                // Show event types distribution
                const eventTypes = {};
                events.forEach(event => {
                    const type = event.type || event.event_type || 'unknown';
                    eventTypes[type] = (eventTypes[type] || 0) + 1;
                });
                
                console.log('\n📊 EVENT TYPES DISTRIBUTION:');
                Object.entries(eventTypes).forEach(([type, count]) => {
                    console.log(`   ${type}: ${count}`);
                });
            }
        } else {
            console.log('❌ No ai_analysis found');
        }

        if (game.metadata) {
            console.log('\n📋 METADATA STRUCTURE:');
            console.log('======================');
            console.log(JSON.stringify(game.metadata, null, 2));
        }

    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        await pool.end();
    }
}

getLeo1Structure();
