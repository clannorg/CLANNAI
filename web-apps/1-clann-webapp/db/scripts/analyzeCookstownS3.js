const { Pool } = require("pg");
const https = require('https');
const http = require('http');
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

// Function to fetch S3 file content
function fetchS3Content(url, maxSize = 5000) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https') ? https : http;
        
        client.get(url, (res) => {
            if (res.statusCode !== 200) {
                resolve({ error: `HTTP ${res.statusCode}`, content: null });
                return;
            }
            
            let data = '';
            let bytesReceived = 0;
            
            res.on('data', (chunk) => {
                bytesReceived += chunk.length;
                if (bytesReceived > maxSize) {
                    res.destroy();
                    resolve({ content: data + `... [TRUNCATED - File too large, showing first ${maxSize} bytes]`, truncated: true });
                    return;
                }
                data += chunk;
            });
            
            res.on('end', () => {
                resolve({ content: data, size: bytesReceived });
            });
            
        }).on('error', (err) => {
            resolve({ error: err.message, content: null });
        });
    });
}

async function analyzeCookstownS3() {
    try {
        console.log('📁 COOKSTOWN S3 FILES ANALYSIS');
        console.log('==============================\n');

        // Get the Cookstown game (you can pass game ID as argument)
        const gameId = process.argv[2];
        
        let gameQuery;
        if (gameId) {
            console.log(`🎯 Analyzing specific game ID: ${gameId}`);
            gameQuery = await pool.query('SELECT * FROM games WHERE id = $1', [gameId]);
        } else {
            console.log('🔍 Searching for Cookstown game...');
            gameQuery = await pool.query(`
                SELECT * FROM games g
                LEFT JOIN teams t ON g.team_id = t.id
                WHERE 
                    LOWER(g.title) LIKE '%cookstown%' 
                    OR LOWER(t.name) LIKE '%cookstown%'
                    OR LOWER(g.description) LIKE '%cookstown%'
                    OR LOWER(g.video_url) LIKE '%cookstown%'
                ORDER BY g.created_at DESC
                LIMIT 1
            `);
        }

        if (gameQuery.rows.length === 0) {
            console.log('❌ No Cookstown game found');
            return;
        }

        const game = gameQuery.rows[0];
        console.log(`✅ Found game: "${game.title}"`);
        console.log(`📅 Created: ${game.created_at}`);
        console.log(`📊 Status: ${game.status}`);
        console.log(`🆔 ID: ${game.id}\n`);

        // Analyze S3 URLs from different sources
        const s3Sources = [];

        // 1. Direct video URL
        if (game.video_url) {
            s3Sources.push({ name: 'Video URL', url: game.video_url, type: 'video' });
        }

        // 2. S3 Key 
        if (game.s3_key) {
            s3Sources.push({ name: 'S3 Key', url: game.s3_key, type: 'key' });
        }

        // 3. Metadata S3 URLs
        if (game.metadata) {
            // Check events_files
            if (game.metadata.events_files) {
                Object.entries(game.metadata.events_files).forEach(([key, fileInfo]) => {
                    if (fileInfo && fileInfo.url) {
                        s3Sources.push({ name: `Events: ${key}`, url: fileInfo.url, type: 'data' });
                    }
                });
            }
            
            // Check tactical_files  
            if (game.metadata.tactical_files) {
                Object.entries(game.metadata.tactical_files).forEach(([key, fileInfo]) => {
                    if (fileInfo && fileInfo.url) {
                        s3Sources.push({ name: `Tactical: ${key}`, url: fileInfo.url, type: 'data' });
                    }
                });
            }
            
            // Check analysis_files
            if (game.metadata.analysis_files) {
                Object.entries(game.metadata.analysis_files).forEach(([key, fileInfo]) => {
                    if (fileInfo && fileInfo.url) {
                        s3Sources.push({ name: `Analysis: ${key}`, url: fileInfo.url, type: 'data' });
                    }
                });
            }
            
            // Legacy: check direct files object
            if (game.metadata.files) {
                Object.entries(game.metadata.files).forEach(([key, url]) => {
                    if (url) {
                        s3Sources.push({ name: `Legacy: ${key}`, url: url, type: 'data' });
                    }
                });
            }
        }

        console.log('📋 S3 SOURCES FOUND:');
        console.log('===================');
        s3Sources.forEach((source, index) => {
            console.log(`${index + 1}. ${source.name}`);
            console.log(`   🔗 URL: ${source.url}`);
            console.log(`   📁 Type: ${source.type}\n`);
        });

        // Analyze file contents for data files (not video)
        console.log('🔍 ANALYZING FILE CONTENTS:');
        console.log('===========================\n');

        for (const source of s3Sources) {
            if (source.type === 'video') {
                console.log(`📺 ${source.name}: Skipping video file (too large)`);
                continue;
            }
            
            if (source.type === 'key') {
                console.log(`🔑 ${source.name}: ${source.url}`);
                continue;
            }

            console.log(`📄 Fetching: ${source.name}`);
            console.log(`🔗 URL: ${source.url}`);
            
            const result = await fetchS3Content(source.url);
            
            if (result.error) {
                console.log(`❌ Error: ${result.error}\n`);
                continue;
            }

            console.log(`✅ Size: ${result.size} bytes`);
            
            // Try to parse as JSON
            try {
                const jsonData = JSON.parse(result.content);
                console.log(`📊 JSON Structure:`);
                
                if (Array.isArray(jsonData)) {
                    console.log(`   📋 Array with ${jsonData.length} items`);
                    if (jsonData.length > 0) {
                        console.log(`   🏷️  First item keys: ${Object.keys(jsonData[0]).join(', ')}`);
                        
                        // Show first few items if it's events
                        if (jsonData[0].type && jsonData[0].timestamp) {
                            console.log(`   🎯 Event types: ${[...new Set(jsonData.map(e => e.type))].join(', ')}`);
                            console.log(`   ⏱️  Time range: ${jsonData[0].timestamp}s - ${jsonData[jsonData.length-1].timestamp}s`);
                        }
                    }
                } else {
                    console.log(`   🏷️  Object keys: ${Object.keys(jsonData).join(', ')}`);
                    
                    // Special handling for tactical analysis
                    if (jsonData.red_team || jsonData.blue_team) {
                        console.log(`   ⚽ Red team: ${jsonData.red_team?.team_name || 'Unknown'}`);
                        console.log(`   ⚽ Blue team: ${jsonData.blue_team?.team_name || 'Unknown'}`);
                    }
                    
                    // Special handling for metadata
                    if (jsonData.teams) {
                        console.log(`   👥 Teams: ${JSON.stringify(jsonData.teams, null, 2)}`);
                    }
                }
                
            } catch (parseError) {
                console.log(`📝 Text content (first 200 chars):`);
                console.log(`   "${result.content.substring(0, 200)}${result.content.length > 200 ? '...' : ''}"`);
            }
            
            console.log(''); // Empty line between files
        }

        // Analyze database stored data
        console.log('💾 DATABASE STORED DATA:');
        console.log('========================\n');

        if (game.ai_analysis) {
            console.log(`📊 AI Events: ${game.ai_analysis.length} events stored in database`);
            if (game.ai_analysis.length > 0) {
                const eventTypes = {};
                game.ai_analysis.forEach(event => {
                    eventTypes[event.type] = (eventTypes[event.type] || 0) + 1;
                });
                console.log(`🏷️  Event types: ${Object.entries(eventTypes).map(([type, count]) => `${type}(${count})`).join(', ')}`);
            }
        } else {
            console.log('❌ No AI events in database');
        }

        if (game.tactical_analysis) {
            console.log(`🧠 Tactical Analysis: Available in database`);
            const keys = Object.keys(game.tactical_analysis);
            console.log(`🏷️  Keys: ${keys.join(', ')}`);
        } else {
            console.log('❌ No tactical analysis in database');
        }

        if (game.metadata) {
            console.log(`📋 Metadata: Available in database`);
            const keys = Object.keys(game.metadata);
            console.log(`🏷️  Keys: ${keys.join(', ')}`);
        } else {
            console.log('❌ No metadata in database');
        }

    } catch (err) {
        console.error('❌ Error:', err.message);
    } finally {
        await pool.end();
    }
}

analyzeCookstownS3();