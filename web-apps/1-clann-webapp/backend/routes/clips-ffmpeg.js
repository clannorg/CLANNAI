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
 * Create clips using FFmpeg (for multiple events/stitching)
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
        
        console.log(`🎬 Creating clips with FFmpeg for game ${gameId} with ${events.length} events`);
        
        // Get game details
        const game = await getGameById(gameId);
        if (!game) {
            return res.status(404).json({ success: false, error: 'Game not found' });
        }
        
        if (!game.s3_key) {
            return res.status(400).json({ success: false, error: 'Game video not found' });
        }
        
        // Construct S3 URL from s3_key
        const videoUrl = game.s3_key.startsWith('https://') ? game.s3_key : 
            `https://${process.env.AWS_BUCKET_NAME || 'end-nov-webapp-clann'}.s3.${process.env.AWS_REGION || 'eu-west-1'}.amazonaws.com/${game.s3_key}`;
        
        console.log(`📹 Using video: ${videoUrl}`);
        
        // Create temporary directory for processing
        const jobId = uuidv4();
        const tempDir = path.join(os.tmpdir(), `clip-job-${jobId}`);
        fs.mkdirSync(tempDir, { recursive: true });
        
        try {
            const clipPaths = [];
            const totalDuration = events.reduce((sum, event) => {
                const beforePadding = event.beforePadding || 5;
                const afterPadding = event.afterPadding || 3;
                return sum + beforePadding + afterPadding;
            }, 0);
            
            // Create individual clips
            for (let i = 0; i < events.length; i++) {
                const event = events[i];
                const beforePadding = event.beforePadding || 5;
                const afterPadding = event.afterPadding || 3;
                const startTime = Math.max(0, event.timestamp - beforePadding);
                const duration = beforePadding + afterPadding;
                
                const clipPath = path.join(tempDir, `clip_${i + 1}.mp4`);
                
                console.log(`📹 Creating clip ${i + 1}: ${startTime}s for ${duration}s`);
                
                // Use FFmpeg to extract clip segment
                const ffmpegCmd = [
                    'ffmpeg',
                    '-y', // Overwrite output files
                    '-ss', startTime.toString(),
                    '-i', videoUrl,
                    '-t', duration.toString(),
                    '-c', 'copy', // Copy streams without re-encoding (faster)
                    '-avoid_negative_ts', 'make_zero',
                    clipPath
                ].join(' ');
                
                console.log(`🔧 Running: ${ffmpegCmd}`);
                execSync(ffmpegCmd, { stdio: 'pipe' });
                clipPaths.push(clipPath);
            }
            
            if (events.length === 1) {
                // Single clip - return directly
                const clipPath = clipPaths[0];
                const fileName = `clip_${Math.floor(events[0].timestamp)}.mp4`;
                
                res.setHeader('Content-Type', 'video/mp4');
                res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
                
                const fileStream = fs.createReadStream(clipPath);
                fileStream.pipe(res);
                
                fileStream.on('end', () => {
                    // Cleanup
                    fs.rmSync(tempDir, { recursive: true, force: true });
                });
                
            } else {
                // Multiple clips - concatenate them
                const finalClipPath = path.join(tempDir, 'highlight_reel.mp4');
                const concatListPath = path.join(tempDir, 'concat_list.txt');
                
                // Create concat list file
                const concatList = clipPaths.map(clipPath => `file '${path.basename(clipPath)}'`).join('\n');
                fs.writeFileSync(concatListPath, concatList);
                
                console.log(`🔗 Concatenating ${clipPaths.length} clips...`);
                
                // Concatenate clips
                const concatCmd = [
                    'ffmpeg',
                    '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concatListPath,
                    '-c', 'copy',
                    finalClipPath
                ].join(' ');
                
                console.log(`🔧 Running: ${concatCmd}`);
                execSync(concatCmd, { stdio: 'pipe' });
                
                // Return the concatenated file
                const fileName = `highlight_reel_${Date.now()}.mp4`;
                
                res.setHeader('Content-Type', 'video/mp4');
                res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
                
                const fileStream = fs.createReadStream(finalClipPath);
                fileStream.pipe(res);
                
                fileStream.on('end', () => {
                    // Cleanup
                    fs.rmSync(tempDir, { recursive: true, force: true });
                });
            }
            
        } catch (error) {
            // Cleanup on error
            fs.rmSync(tempDir, { recursive: true, force: true });
            throw error;
        }
        
    } catch (error) {
        console.error('❌ FFmpeg clip creation error:', error);
        
        if (error.message.includes('ffmpeg')) {
            return res.status(500).json({
                success: false,
                error: 'FFmpeg not available on server. Please install FFmpeg or use MediaConvert fallback.',
                details: error.message
            });
        }
        
        res.status(500).json({
            success: false,
            error: 'Failed to create clips',
            details: error.message
        });
    }
});

module.exports = router;