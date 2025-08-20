const express = require('express');
const { authenticateToken } = require('../middleware/auth');
const { getGameById } = require('../utils/database');
const { createClipsJob, getJobStatus } = require('../utils/mediaconvert');
const { S3Client, GetObjectCommand, PutObjectCommand } = require('@aws-sdk/client-s3');
const path = require('path');

const router = express.Router();

const s3Client = new S3Client({
    region: process.env.AWS_REGION || 'eu-west-1',
    credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
    }
});

const BUCKET_NAME = process.env.AWS_BUCKET_NAME || 'clannai-uploads';

// Helper function to check if FFmpeg is available
const checkFFmpegAvailable = async () => {
    try {
        const { exec } = require('child_process');
        return new Promise((resolve) => {
            exec('ffmpeg -version', (error) => {
                resolve(!error);
            });
        });
    } catch (error) {
        return false;
    }
};

// Helper function to create clips using FFmpeg (local fallback)
const createClipsWithFFmpeg = async (videoUrl, events, gameId) => {
    const { exec } = require('child_process');
    const fs = require('fs').promises;
    const os = require('os');
    
    // Create temp directory
    const tempDir = path.join(os.tmpdir(), `clips-${gameId}-${Date.now()}`);
    await fs.mkdir(tempDir, { recursive: true });
    
    try {
        console.log('🎬 Using FFmpeg fallback for local development...');
        
        // No need to download! FFmpeg can stream directly from HTTPS URLs
        console.log('🎯 Using direct streaming from S3 (no download needed)');
        const inputUrl = videoUrl;
        
        // Create individual clips
        const clipPaths = [];
        for (let i = 0; i < events.length; i++) {
            const event = events[i];
            const clipPath = path.join(tempDir, `clip_${i + 1}.mp4`);
            
            const beforePadding = event.beforePadding || 5;
            const afterPadding = event.afterPadding || 5;
            const startTime = Math.max(0, event.timestamp - beforePadding);
            const duration = beforePadding + afterPadding;
            
            await new Promise((resolve, reject) => {
                // EFFICIENT: Seek BEFORE reading input (streams only the needed segment)
                const cmd = `ffmpeg -ss ${startTime} -i "${inputUrl}" -t ${duration} -c copy -avoid_negative_ts make_zero "${clipPath}"`;
                console.log(`🎬 Creating clip ${i + 1}: ${cmd}`);
                exec(cmd, { timeout: 60000 }, (error, stdout, stderr) => {
                    if (error) {
                        console.error(`❌ FFmpeg error for clip ${i + 1}:`, error.message);
                        console.error(`❌ FFmpeg stderr:`, stderr);
                        reject(error);
                    } else {
                        console.log(`✅ Clip ${i + 1} created successfully`);
                        resolve();
                    }
                });
            });
            
            clipPaths.push(clipPath);
            console.log(`✅ Created clip ${i + 1}: ${event.type} at ${event.timestamp}s (${duration}s total)`);
        }
        
        // Concatenate clips
        console.log('🔗 Concatenating clips...');
        const concatListPath = path.join(tempDir, 'concat_list.txt');
        const concatContent = clipPaths.map(p => `file '${p}'`).join('\n');
        await fs.writeFile(concatListPath, concatContent);
        console.log('📝 Concat list created:', concatContent);
        
        const finalClipPath = path.join(tempDir, 'highlight_reel.mp4');
        await new Promise((resolve, reject) => {
            const cmd = `ffmpeg -f concat -safe 0 -i "${concatListPath}" -c copy "${finalClipPath}"`;
            console.log('🎬 Concatenating:', cmd);
            exec(cmd, { timeout: 120000 }, (error, stdout, stderr) => {
                if (error) {
                    console.error('❌ Concatenation error:', error.message);
                    console.error('❌ Concatenation stderr:', stderr);
                    reject(error);
                } else {
                    console.log('✅ Concatenation completed successfully');
                    resolve();
                }
            });
        });
        
        // Upload to S3
        console.log('☁️ Uploading final clip to S3...');
        const clipBuffer = await fs.readFile(finalClipPath);
        const s3Key = `clips/${gameId}/${Date.now()}/highlight_reel.mp4`;
        console.log(`📤 Upload size: ${Math.round(clipBuffer.length / 1024 / 1024)}MB`);
        console.log(`📍 S3 key: ${s3Key}`);
        
        const uploadCommand = new PutObjectCommand({
            Bucket: BUCKET_NAME,
            Key: s3Key,
            Body: clipBuffer,
            ContentType: 'video/mp4'
        });
        
        await s3Client.send(uploadCommand);
        console.log('✅ S3 upload completed');
        
        // Clean up temp files
        await fs.rm(tempDir, { recursive: true, force: true });
        
        return {
            success: true,
            downloadUrl: `/api/clips/download/${s3Key}`,
            s3Key: s3Key,
            message: 'Clips created successfully using FFmpeg'
        };
        
    } catch (error) {
        // Clean up temp files on error
        try {
            await fs.rm(tempDir, { recursive: true, force: true });
        } catch (cleanupError) {
            console.error('Error cleaning up temp files:', cleanupError);
        }
        throw error;
    }
};

// Create highlight reel from selected events - HYBRID APPROACH
router.post('/create', authenticateToken, async (req, res) => {
    const { gameId, events } = req.body;
    
    try {
        console.log('🎬 Creating highlight reel for game:', gameId);
        console.log('📝 Selected events:', events);

        // Validate input
        if (!gameId || !events || !Array.isArray(events) || events.length === 0) {
            return res.status(400).json({ error: 'Game ID and events array are required' });
        }

        if (events.length > 5) {
            return res.status(400).json({ error: 'Maximum 5 events allowed' });
        }

        // Get game details
        const game = await getGameById(gameId);
        if (!game) {
            return res.status(404).json({ error: 'Game not found' });
        }

        if (!game.s3_key) {
            return res.status(400).json({ error: 'Game video not found' });
        }

        const videoUrl = game.s3_key.startsWith('https://') ? game.s3_key : 
            `https://${BUCKET_NAME}.s3.amazonaws.com/${game.s3_key}`;

        // Calculate total duration from individual padding
        const totalDuration = events.reduce((total, event) => {
            const beforePadding = event.beforePadding || 5;
            const afterPadding = event.afterPadding || 5;
            return total + beforePadding + afterPadding;
        }, 0);

        // HYBRID APPROACH: Try MediaConvert first, fallback to FFmpeg
        try {
            console.log('🚀 Attempting MediaConvert (production method)...');
            const s3VideoUrl = game.s3_key.startsWith('s3://') ? game.s3_key : 
                `s3://${BUCKET_NAME}/${game.s3_key}`;
            
            // Create MediaConvert job with individual padding
            const mediaConvertResult = await createClipsJob(s3VideoUrl, events, gameId);
            
            console.log('✅ MediaConvert job started:', mediaConvertResult.jobId);
            
            // Return job info - frontend will need to poll for completion
            return res.json({
                success: true,
                jobId: mediaConvertResult.jobId,
                status: mediaConvertResult.status,
                message: 'Clip processing started using MediaConvert. This may take a few minutes.',
                duration: totalDuration,
                eventCount: events.length,
                outputPath: mediaConvertResult.outputPath
            });

        } catch (mediaConvertError) {
            console.error('❌ MediaConvert failed:', mediaConvertError.message);
            
            // Check if we're in development and FFmpeg is available
            const isLocal = process.env.NODE_ENV !== 'production';
            const ffmpegAvailable = await checkFFmpegAvailable();
            
            if (isLocal && ffmpegAvailable) {
                console.log('🔄 Falling back to FFmpeg for local development...');
                
                try {
                    const ffmpegResult = await createClipsWithFFmpeg(videoUrl, events, gameId);
                    
                    return res.json({
                        success: true,
                        downloadUrl: ffmpegResult.downloadUrl,
                        fileName: 'highlight_reel.mp4',
                        duration: totalDuration,
                        eventCount: events.length,
                        message: 'Clips created successfully using FFmpeg (local development)'
                    });
                    
                } catch (ffmpegError) {
                    console.error('❌ FFmpeg fallback also failed:', ffmpegError);
                    throw ffmpegError;
                }
            } else {
                // Neither MediaConvert nor FFmpeg available
                if (!isLocal) {
                    throw new Error('MediaConvert failed in production environment');
                } else {
                    throw new Error('MediaConvert failed and FFmpeg not available for fallback');
                }
            }
        }

    } catch (error) {
        console.error('❌ Error creating highlight reel:', error);
        res.status(500).json({ 
            error: 'Failed to create highlight reel', 
            details: error.message 
        });
    }
});

// Check job status
router.get('/status/:jobId', authenticateToken, async (req, res) => {
    try {
        const { jobId } = req.params;
        console.log('📊 Checking job status:', jobId);
        
        const status = await getJobStatus(jobId);
        
        res.json({
            success: true,
            jobId: jobId,
            status: status.status,
            progress: status.progress,
            createdAt: status.createdAt,
            finishedAt: status.finishedAt
        });
        
    } catch (error) {
        console.error('❌ Error checking job status:', error);
        res.status(500).json({ 
            error: 'Failed to check job status',
            details: error.message 
        });
    }
});

// Download route - serves files from S3 through our backend
router.get('/download/*', authenticateToken, async (req, res) => {
    try {
        // Extract S3 key from the full path (remove '/download/' prefix)
        const s3Key = req.params[0];
        console.log(`📥 Serving download for: ${s3Key}`);
        
        const command = new GetObjectCommand({
            Bucket: BUCKET_NAME,
            Key: s3Key
        });

        const response = await s3Client.send(command);
        
        // Set headers for download
        res.setHeader('Content-Type', 'video/mp4');
        res.setHeader('Content-Disposition', `attachment; filename="${path.basename(s3Key)}"`);
        
        // Stream the file
        response.Body.pipe(res);
        
    } catch (error) {
        console.error('❌ Download error:', error);
        res.status(404).json({ error: 'File not found' });
    }
});

module.exports = router;