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

async function findCookstownGame() {
    try {
        console.log('🔍 SEARCHING FOR COOKSTOWN GAME');
        console.log('==============================\n');

        // First, list all games to see what we have
        console.log('📋 ALL GAMES IN DATABASE:');
        const allGames = await pool.query(`
            SELECT 
                g.id,
                g.title,
                t.name as team_name,
                g.status,
                g.created_at,
                g.video_url,
                CASE 
                    WHEN g.ai_analysis IS NOT NULL THEN jsonb_array_length(g.ai_analysis) 
                    ELSE 0 
                END as events_count,
                CASE 
                    WHEN g.tactical_analysis IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END as has_tactical
            FROM games g
            LEFT JOIN teams t ON g.team_id = t.id
            ORDER BY g.created_at DESC;
        `);

        allGames.rows.forEach((game, index) => {
            console.log(`${index + 1}. "${game.team_name}" - ${game.title}`);
            console.log(`   🆔 ID: ${game.id}`);
            console.log(`   📊 Status: ${game.status}`);
            console.log(`   🎯 Events: ${game.events_count}`);
            console.log(`   🧠 Tactical: ${game.has_tactical}`);
            console.log(`   📅 Created: ${new Date(game.created_at).toLocaleDateString()}`);
            if (game.video_url) {
                if (game.video_url.includes('cookstown')) {
                    console.log(`   🎬 Video: 🏴󠁧󠁢󠁳󠁣󠁴󠁿 COOKSTOWN MATCH`);
                } else if (game.video_url.includes('20250523-match-23-may-2025-3fc1de88')) {
                    console.log(`   🎬 Video: 🏴󠁧󠁢󠁥󠁮󠁧󠁿 LONDON MATCH`);
                } else if (game.video_url.includes('edinburgh')) {
                    console.log(`   🎬 Video: 🏴󠁧󠁢󠁳󠁣󠁴󠁿 EDINBURGH MATCH`);
                } else {
                    console.log(`   🎬 Video: ${game.video_url.slice(0, 60)}...`);
                }
            } else {
                console.log(`   🎬 Video: None`);
            }
            console.log('');
        });

        console.log(`📈 Total games: ${allGames.rows.length}\n`);

        // Now specifically search for Cookstown
        console.log('🏴󠁧󠁢󠁳󠁣󠁴󠁿 COOKSTOWN SEARCH RESULTS:');
        console.log('============================');
        
        const cookstownSearch = await pool.query(`
            SELECT 
                g.id,
                g.title,
                g.description,
                t.name as team_name,
                g.status,
                g.video_url,
                g.s3_key,
                g.created_at
            FROM games g
            LEFT JOIN teams t ON g.team_id = t.id
            WHERE 
                LOWER(g.title) LIKE '%cookstown%' 
                OR LOWER(t.name) LIKE '%cookstown%'
                OR LOWER(g.description) LIKE '%cookstown%'
                OR LOWER(g.video_url) LIKE '%cookstown%'
            ORDER BY g.created_at DESC;
        `);

        if (cookstownSearch.rows.length === 0) {
            console.log('❌ No Cookstown games found');
            
            // Check for Bourneview as backup
            console.log('\n🔍 Searching for "Bourneview" as backup...');
            const bourneviewSearch = await pool.query(`
                SELECT 
                    g.id,
                    g.title,
                    t.name as team_name,
                    g.status,
                    g.video_url
                FROM games g
                LEFT JOIN teams t ON g.team_id = t.id
                WHERE 
                    LOWER(g.title) LIKE '%bourneview%' 
                    OR LOWER(t.name) LIKE '%bourneview%'
                    OR LOWER(g.video_url) LIKE '%bourneview%'
                ORDER BY g.created_at DESC;
            `);
            
            if (bourneviewSearch.rows.length > 0) {
                console.log('✅ Found Bourneview matches:');
                console.table(bourneviewSearch.rows);
            } else {
                console.log('❌ No Bourneview games found either');
            }
        } else {
            console.log(`✅ Found ${cookstownSearch.rows.length} Cookstown game(s):`);
            console.table(cookstownSearch.rows);
            
            // Return the first (most recent) Cookstown game for follow-up analysis
            return cookstownSearch.rows[0];
        }

    } catch (err) {
        console.error('❌ Error:', err.message);
    } finally {
        await pool.end();
    }
}

// Run the search
findCookstownGame().then(game => {
    if (game) {
        console.log(`\n🎯 FOUND COOKSTOWN GAME: ${game.id}`);
        console.log('Use this ID in the next script to analyze S3 files');
    }
});