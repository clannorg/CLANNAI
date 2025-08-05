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

async function checkGreenislandAnalysis() {
    try {
        console.log('🔍 GREENISLAND ANALYSIS DEEP DIVE');
        console.log('================================\n');

        // Get Greenisland's game with all analysis fields
        const gameQuery = `
            SELECT 
                g.id,
                g.title,
                t.name as team_name,
                g.status,
                g.ai_analysis IS NOT NULL as has_ai_analysis,
                g.tactical_analysis IS NOT NULL as has_tactical_analysis,
                LENGTH(g.ai_analysis::text) as ai_analysis_size,
                LENGTH(g.tactical_analysis::text) as tactical_analysis_size,
                g.video_url,
                g.created_at
            FROM games g
            JOIN teams t ON g.team_id = t.id 
            WHERE t.name = 'greenisland' 
            ORDER BY g.created_at DESC
        `;

        const games = await pool.query(gameQuery);
        
        console.log('🎮 GREENISLAND GAMES:');
        console.log('--------------------');
        games.rows.forEach((game, i) => {
            console.log(`\n${i + 1}. ${game.title}`);
            console.log(`   ID: ${game.id}`);
            console.log(`   Status: ${game.status}`);
            console.log(`   Has AI Analysis: ${game.has_ai_analysis} (${game.ai_analysis_size || 0} chars)`);
            console.log(`   Has Tactical Analysis: ${game.has_tactical_analysis} (${game.tactical_analysis_size || 0} chars)`);
            console.log(`   Video URL: ${game.video_url || 'None'}`);
        });

        if (games.rows.length > 0) {
            const mainGame = games.rows[0]; // Most recent
            console.log(`\n📊 DETAILED ANALYSIS FOR: "${mainGame.title}"`);
            console.log('=' .repeat(50));

            // Get the actual analysis content
            const detailQuery = `
                SELECT 
                    ai_analysis,
                    tactical_analysis
                FROM games 
                WHERE id = $1
            `;
            
            const detail = await pool.query(detailQuery, [mainGame.id]);
            if (detail.rows.length > 0) {
                const analysis = detail.rows[0];
                
                console.log('\n🤖 AI ANALYSIS PREVIEW:');
                if (analysis.ai_analysis) {
                    const aiPreview = JSON.stringify(analysis.ai_analysis, null, 2).substring(0, 500);
                    console.log(aiPreview + '...');
                } else {
                    console.log('   None');
                }

                console.log('\n🎯 TACTICAL ANALYSIS PREVIEW:');
                if (analysis.tactical_analysis) {
                    const tacticalPreview = JSON.stringify(analysis.tactical_analysis, null, 2).substring(0, 500);
                    console.log(tacticalPreview + '...');
                } else {
                    console.log('   None');
                }
            }
        }

        console.log('\n💡 ANALYSIS SYSTEM SUMMARY:');
        console.log('---------------------------');
        console.log('• has_analysis = (ai_analysis IS NOT NULL)');
        console.log('• has_tactical = (tactical_analysis IS NOT NULL)');
        console.log('• Marc sees "AI descriptions" = ai_analysis content');
        console.log('• "Proper analysis & insights" = tactical_analysis content');
        console.log('\n🎯 TO FIX: Need to populate tactical_analysis field!');

    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        await pool.end();
    }
}

checkGreenislandAnalysis();