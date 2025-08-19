const { Pool } = require("pg");
const path = require('path');
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

async function listGames() {
    try {
        const query = `
            SELECT 
                g.id,
                g.title,
                g.status,
                g.created_at,
                t.name as team_name,
                u.name as uploaded_by_name,
                CASE 
                    WHEN g.ai_analysis IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END as has_analysis
            FROM games g
            LEFT JOIN teams t ON g.team_id = t.id
            LEFT JOIN users u ON g.uploaded_by = u.id
            ORDER BY g.created_at DESC
        `;

        const result = await pool.query(query);
        
        console.log('🎮 ALL GAMES');
        console.log('============\n');

        if (result.rows.length === 0) {
            console.log('No games found.');
            return;
        }

        result.rows.forEach((game, index) => {
            const date = new Date(game.created_at).toISOString().split('T')[0];
            const shortId = game.id.split('-')[0];
            const gameNumber = index + 1;
            
            console.log(`[${gameNumber}] ${game.title} (${game.team_name || 'No Team'})`);
            console.log(`    📅 ${date} | 📊 ${game.status} | 🤖 AI: ${game.has_analysis}`);
            console.log(`    👤 ${game.uploaded_by_name || 'Unknown'}`);
            console.log(`    🆔 ${shortId}... (Full: ${game.id})`);
            console.log(`    🔗 node inspect-game-urls.js ${gameNumber}`);
            console.log('');
        });

        console.log(`\n📋 Total: ${result.rows.length} games`);
        console.log('\n💡 Usage:');
        console.log('   node inspect-game-urls.js <game-number>    # e.g. node inspect-game-urls.js 2');
        console.log('   node inspect-game-urls.js "<title>"        # e.g. node inspect-game-urls.js "Bourneview YM"');
        console.log('   node inspect-game-urls.js <full-id>        # e.g. node inspect-game-urls.js 09e614b8-...');

    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        await pool.end();
    }
}

listGames();