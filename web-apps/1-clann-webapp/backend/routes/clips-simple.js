const express = require('express');
const router = express.Router();
const { authenticateToken } = require('../middleware/auth');
const { getGameById } = require('../utils/database');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { v4: uuidv4 } = require('uuid');

/**
 * Ensure FFmpeg is available (download static binary if needed)
 */
async function ensureFFmpeg() {
    const ffmpegPath = '/tmp/ffmpeg';
    
    // Check if ffmpeg exists in system PATH
    try {
        execSync('which ffmpeg', { stdio: 'pipe' });
        console.log('✅ Using system FFmpeg');
        return 'ffmpeg'; // Use system ffmpeg
    } catch (error) {
        console.log('System FFmpeg not found, checking for static binary...');
    }
    
    // Check if we have a static binary
    if (fs.existsSync(ffmpegPath)) {
        console.log('✅ Using cached static FFmpeg binary');
        return ffmpegPath;
    }
    
    // Download static FFmpeg binary
    console.log('📥 Downloading static FFmpeg binary...');
    try {
        execSync(`curl -L -o ${ffmpegPath} "https://johnvansickle.com/ffmpeg/builds/linux64-static/bin/ffmpeg"`, { stdio: 'pipe' });
        execSync(`chmod +x ${ffmpegPath}`, { stdio: 'pipe' });
        console.log('✅ FFmpeg binary downloaded and ready');
        return ffmpegPath;
    } catch (error) {
        throw new Error(`Failed to download FFmpeg: ${error.message}`);
    }
}

/**
 * Create clips using direct FFmpeg processing
 */
router.post('/create', authenticateToken, async (req, res) => {
    try {
        const { gameId, events } = req.body;
        
        // Validate input
        if (!gameId || !events || !Array.isArray(events) || events.length === 0) {
            return res.status(400).json({ 
                success: false,
                error: 'gameId and events array are required' 
            });
        }
        
        console.log(`🎬 Creating clips for game ${gameId} with ${events.length} events`);
        
        // Get game details
        const game = await getGameById(gameId);
        if (!game) {
            return res.status(404).json({ 
                success: false,
                error: 'Game not found' 
            });
        }
        
        // Check for chunks first (fastest option)
        if (game.chunks_base_url) {
            console.log('📦 Using chunk-based clip creation (direct serving)...');
            const chunks = events.map(event => {
                const chunkTime = Math.floor(event.timestamp / 15) * 15; // Round to 15s boundary
                const chunkFileName = `clip_${Math.floor(chunkTime / 60)}m${(chunkTime % 60).toString().padStart(2, '0')}s.mp4`;
                return {
                    eventTime: event.timestamp,
                    downloadUrl: `${game.chunks_base_url}${chunkFileName}`,
                    fileName: chunkFileName
                };
            });

            return res.json({
                success: true,
                method: 'chunks',
                message: 'Chunk-based clips ready for download',
                chunks: chunks
            });
        }
        
        // Validate game has video
        if (!game.s3_url && !game.s3_key) {
            return res.status(400).json({ 
                success: false,
                error: 'Game does not have a video file' 
            });
        }
        
        // Use direct FFmpeg processing
        console.log('🎬 Using direct FFmpeg for clip processing...');
        
        // Ensure FFmpeg is available
        const ffmpegPath = await ensureFFmpeg();
        console.log(`✅ FFmpeg ready at: ${ffmpegPath}`);
        
        // Create working directory
        const workDir = path.join(os.tmpdir(), `clips-${uuidv4()}`);
        fs.mkdirSync(workDir, { recursive: true });
        
        const clipPaths = [];
        const videoUrl = game.s3_url || `https://end-nov-webapp-clann.s3.eu-west-1.amazonaws.com/${game.s3_key}`;
        
        // Process each event
        for (let i = 0; i < events.length; i++) {
            const event = events[i];
            const beforePadding = event.beforePadding || 5;
            const afterPadding = event.afterPadding || 3;
            
            const startTime = Math.max(0, event.timestamp - beforePadding);
            const duration = beforePadding + afterPadding;
            
            console.log(`🎬 Processing event ${i + 1}: timestamp=${event.timestamp}s, start=${startTime}s, duration=${duration}s`);
            
            const clipPath = path.join(workDir, `clip_${i + 1}.mp4`);
            
            // Use FFmpeg to extract clip segment (optimized for speed)
            const ffmpegCmd = `${ffmpegPath} -y -ss ${startTime} -i "${videoUrl}" -t ${duration} -c copy -avoid_negative_ts make_zero "${clipPath}"`;
            
            console.log(`⚡ FFmpeg command: ${ffmpegCmd}`);
            
            try {
                execSync(ffmpegCmd, { 
                    stdio: 'pipe',
                    timeout: 120000 // 2 minute timeout per clip
                });
                
                if (fs.existsSync(clipPath)) {
                    const stats = fs.statSync(clipPath);
                    console.log(`✅ Clip ${i + 1} created: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
                    clipPaths.push(clipPath);
                } else {
                    throw new Error(`Clip file not created: ${clipPath}`);
                }
            } catch (ffmpegError) {
                console.error(`❌ FFmpeg error for clip ${i + 1}:`, ffmpegError.message);
                
                // Clean up on error
                try {
                    fs.rmSync(workDir, { recursive: true, force: true });
                } catch (cleanupError) {
                    console.error('⚠️ Cleanup error:', cleanupError.message);
                }
                
                throw new Error(`Failed to create clip ${i + 1}: ${ffmpegError.message}`);
            }
        }
        
        // Handle single vs multiple clips
        let finalClipPath;
        let fileName;
        
        if (clipPaths.length === 1) {
            finalClipPath = clipPaths[0];
            fileName = `clip_${Date.now()}.mp4`;
            console.log('📹 Single clip ready');
        } else {
            console.log(`🔗 Concatenating ${clipPaths.length} clips`);
            
            // Create concat file list
            const concatListPath = path.join(workDir, 'concat_list.txt');
            const concatContent = clipPaths.map(p => `file '${p}'`).join('\n');
            fs.writeFileSync(concatListPath, concatContent);
            
            finalClipPath = path.join(workDir, 'final_highlight_reel.mp4');
            fileName = `highlight_reel_${Date.now()}.mp4`;
            
            const concatCmd = `${ffmpegPath} -y -f concat -safe 0 -i "${concatListPath}" -c copy "${finalClipPath}"`;
            
            console.log(`🔗 Concat command: ${concatCmd}`);
            
            try {
                execSync(concatCmd, { 
                    stdio: 'pipe',
                    timeout: 60000 // 1 minute timeout for concat
                });
                
                if (!fs.existsSync(finalClipPath)) {
                    throw new Error('Final concatenated clip not created');
                }
                
                const stats = fs.statSync(finalClipPath);
                console.log(`✅ Final clip created: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
            } catch (concatError) {
                console.error('❌ Concatenation error:', concatError.message);
                
                // Clean up on error
                try {
                    fs.rmSync(workDir, { recursive: true, force: true });
                } catch (cleanupError) {
                    console.error('⚠️ Cleanup error:', cleanupError.message);
                }
                
                throw new Error(`Failed to concatenate clips: ${concatError.message}`);
            }
        }
        
        console.log(`🎉 Clip processing complete: ${finalClipPath}`);
        
        // For now, read the file and send it directly
        // In production, you might want to upload to S3 or serve via static file server
        const fileBuffer = fs.readFileSync(finalClipPath);
        
        // Clean up working directory after sending response
        setTimeout(() => {
            try {
                fs.rmSync(workDir, { recursive: true, force: true });
                console.log(`🧹 Cleaned up working directory: ${workDir}`);
            } catch (cleanupError) {
                console.error('⚠️ Cleanup error:', cleanupError.message);
            }
        }, 5000); // 5 seconds delay
        
        // Send file directly
        res.setHeader('Content-Type', 'video/mp4');
        res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
        res.setHeader('Content-Length', fileBuffer.length);
        res.send(fileBuffer);
        
    } catch (error) {
        console.error('❌ Clip creation error:', error);
        res.status(500).json({ 
            success: false,
            error: error.message 
        });
    }
});

module.exports = router;