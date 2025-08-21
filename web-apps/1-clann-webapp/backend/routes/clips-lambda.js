const express = require('express');
const router = express.Router();
const { authenticateToken } = require('../middleware/auth');
const { getGameById } = require('../utils/database');
const { invokeClipProcessor } = require('../utils/lambda');
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
        return 'ffmpeg'; // Use system ffmpeg
    } catch (error) {
        console.log('System FFmpeg not found, checking for static binary...');
    }
    
    // Check if we have a static binary
    if (fs.existsSync(ffmpegPath)) {
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
        
        // Validate game has video
        if (!game.s3_key) {
            return res.status(400).json({ 
                success: false,
                error: 'Game does not have a video file' 
            });
        }
        
        // Prepare S3 video URL for Lambda
        let s3VideoUrl = game.s3_key;
        if (s3VideoUrl.startsWith('https://')) {
            // Extract key from https://bucket.s3.amazonaws.com/path/file.mp4
            const urlParts = s3VideoUrl.split('.s3.amazonaws.com/');
            const s3Key = urlParts.length > 1 ? urlParts[1] : s3VideoUrl;
            s3VideoUrl = `s3://${process.env.AWS_BUCKET_NAME}/${s3Key}`;
        } else if (!s3VideoUrl.startsWith('s3://')) {
            s3VideoUrl = `s3://${process.env.AWS_BUCKET_NAME}/${s3VideoUrl}`;
        }
        
        console.log('📹 Video URL for Lambda:', s3VideoUrl);
        
        // Validate events have required fields
        const validatedEvents = events.map((event, index) => {
            if (typeof event.timestamp !== 'number') {
                throw new Error(`Event ${index + 1} missing valid timestamp`);
            }
            
            return {
                timestamp: event.timestamp,
                beforePadding: event.beforePadding || 5,
                afterPadding: event.afterPadding || 3
            };
        });
        
        console.log('✅ Events validated:', validatedEvents);
        
        // Invoke Lambda function
        const result = await invokeClipProcessor(gameId, validatedEvents, s3VideoUrl);
        
        // Return success response
        res.json({
            success: true,
            method: 'lambda',
            downloadUrl: result.downloadUrl,
            fileName: result.fileName,
            duration: result.duration,
            eventCount: result.eventCount,
            message: result.message
        });
        
    } catch (error) {
        console.error('❌ Clip creation error:', error);
        res.status(500).json({ 
            success: false,
            error: error.message,
            message: 'Failed to create clips using Lambda'
        });
    }
});

/**
 * Health check endpoint
 */
router.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy',
        service: 'clips-lambda',
        timestamp: new Date().toISOString()
    });
});

module.exports = router;