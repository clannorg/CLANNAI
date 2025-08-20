const { Pool } = require("pg");
const path = require('path');
const https = require('https');
const http = require('http');
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

// Function to check if URL is accessible
function checkUrl(url) {
    return new Promise((resolve) => {
        if (!url) {
            resolve({ status: 'empty', code: null });
            return;
        }

        const client = url.startsWith('https:') ? https : http;
        const request = client.request(url, { method: 'HEAD', timeout: 5000 }, (res) => {
            resolve({ status: res.statusCode < 400 ? 'ok' : 'error', code: res.statusCode });
        });

        request.on('error', () => {
            resolve({ status: 'error', code: 'timeout' });
        });

        request.on('timeout', () => {
            request.destroy();
            resolve({ status: 'error', code: 'timeout' });
        });

        request.end();
    });
}

async function findGame(identifier) {
    let query, params;

    // Check if it's a number (list index)
    if (/^\d+$/.test(identifier)) {
        const index = parseInt(identifier) - 1;
        query = `
            SELECT * FROM games g
            LEFT JOIN teams t ON g.team_id = t.id
            LEFT JOIN users u ON g.uploaded_by = u.id
            ORDER BY g.created_at DESC
            LIMIT 1 OFFSET $1
        `;
        params = [index];
    }
    // Check if it's a UUID
    else if (/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(identifier)) {
        query = `
            SELECT g.*, t.name as team_name, u.name as uploaded_by_name
            FROM games g
            LEFT JOIN teams t ON g.team_id = t.id
            LEFT JOIN users u ON g.uploaded_by = u.id
            WHERE g.id = $1
        `;
        params = [identifier];
    }
    // Otherwise treat as title search
    else {
        query = `
            SELECT g.*, t.name as team_name, u.name as uploaded_by_name
            FROM games g
            LEFT JOIN teams t ON g.team_id = t.id
            LEFT JOIN users u ON g.uploaded_by = u.id
            WHERE g.title ILIKE $1
        `;
        params = [`%${identifier}%`];
    }

    const result = await pool.query(query, params);
    return result.rows[0];
}

function extractUrlsFromMetadata(metadata) {
    const urls = [];
    
    if (!metadata) return urls;

    // Helper function to recursively find URLs
    function findUrls(obj, path = '') {
        if (typeof obj === 'string' && (obj.startsWith('http://') || obj.startsWith('https://'))) {
            urls.push({ path, url: obj });
        } else if (typeof obj === 'object' && obj !== null) {
            for (const [key, value] of Object.entries(obj)) {
                const newPath = path ? `${path}.${key}` : key;
                findUrls(value, newPath);
            }
        }
    }

    findUrls(metadata);
    return urls;
}

async function inspectGameUrls() {
    const identifier = process.argv[2];
    
    if (!identifier) {
        console.log('❌ Please provide a game identifier:');
        console.log('   node inspect-game-urls.js <game-number>    # e.g. 2');
        console.log('   node inspect-game-urls.js "<title>"        # e.g. "Bourneview YM"');
        console.log('   node inspect-game-urls.js <full-id>        # e.g. 09e614b8-...');
        console.log('\n💡 Run "node list-games.js" to see all games');
        process.exit(1);
    }

    try {
        const game = await findGame(identifier);
        
        if (!game) {
            console.log(`❌ Game not found: "${identifier}"`);
            console.log('\n💡 Run "node list-games.js" to see all available games');
            process.exit(1);
        }

        console.log(`🎮 GAME: "${game.title}" (${game.team_name || 'No Team'})`);
        console.log('='.repeat(50));
        console.log(`📅 Created: ${new Date(game.created_at).toLocaleDateString()}`);
        console.log(`👤 Uploaded by: ${game.uploaded_by_name || 'Unknown'}`);
        console.log(`📊 Status: ${game.status}`);
        console.log(`🆔 ID: ${game.id}\n`);

        // Collect all URLs
        const allUrls = [];

        // Direct URL fields
        if (game.video_url) allUrls.push({ type: 'VEO Source', url: game.video_url });
        if (game.s3_key) {
            const s3Url = game.s3_key.startsWith('https://') ? game.s3_key : 
                `https://end-nov-webapp-clann.s3.amazonaws.com/${game.s3_key}`;
            allUrls.push({ type: 'Main Video (S3)', url: s3Url });
        }
        if (game.thumbnail_url) allUrls.push({ type: 'Thumbnail', url: game.thumbnail_url });
        if (game.metadata_url) allUrls.push({ type: 'Metadata File', url: game.metadata_url });

        // URLs from metadata JSONB
        const metadataUrls = extractUrlsFromMetadata(game.metadata);
        metadataUrls.forEach(item => {
            allUrls.push({ type: `Metadata: ${item.path}`, url: item.url });
        });

        if (allUrls.length === 0) {
            console.log('❌ No URLs found for this game');
            return;
        }

        console.log(`🔗 FOUND ${allUrls.length} URLs:\n`);

        // Check each URL
        for (const item of allUrls) {
            const status = await checkUrl(item.url);
            let statusIcon;
            
            switch (status.status) {
                case 'ok': statusIcon = '✅'; break;
                case 'error': statusIcon = '❌'; break;
                case 'empty': statusIcon = '⚪'; break;
                default: statusIcon = '❓';
            }

            console.log(`${statusIcon} ${item.type}`);
            console.log(`   ${item.url}`);
            if (status.code && status.code !== 'timeout') {
                console.log(`   Status: ${status.code}`);
            } else if (status.code === 'timeout') {
                console.log(`   Status: Timeout/Error`);
            }
            console.log('');
        }

        // Summary
        const okCount = allUrls.filter(async (item) => (await checkUrl(item.url)).status === 'ok').length;
        console.log(`📊 Summary: ${allUrls.length} total URLs`);

    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        await pool.end();
    }
}

inspectGameUrls();