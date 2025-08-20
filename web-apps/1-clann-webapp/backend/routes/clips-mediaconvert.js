const express = require('express');
const { authenticateToken } = require('../middleware/auth');
const { getGameById } = require('../utils/database');
const { createClipsJob, getJobStatus } = require('../utils/mediaconvert');
const { S3Client, GetObjectCommand } = require('@aws-sdk/client-s3');
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

// Create highlight reel from selected events using MediaConvert
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

        try {
            // Use video directly from S3 URL
            console.log('🎬 Using video directly from S3...');
            const videoUrl = game.s3_key.startsWith('https://') ? game.s3_key : 
                `s3://${BUCKET_NAME}/${game.s3_key}`;

            console.log('🚀 Starting MediaConvert job for clips...');
            
            // Create MediaConvert job with individual padding
            const mediaConvertResult = await createClipsJob(videoUrl, events, gameId);
            
            console.log('✅ MediaConvert job started:', mediaConvertResult.jobId);
            
            // Calculate total duration from individual padding
            const totalDuration = events.reduce((total, event) => {
                const beforePadding = event.beforePadding || 5;
                const afterPadding = event.afterPadding || 5;
                return total + beforePadding + afterPadding;
            }, 0);
            
            // Return job info - frontend will need to poll for completion
            res.json({
                success: true,
                jobId: mediaConvertResult.jobId,
                status: mediaConvertResult.status,
                message: 'Clip processing started. This may take a few minutes.',
                duration: totalDuration,
                eventCount: events.length,
                outputPath: mediaConvertResult.outputPath
            });

        } catch (processingError) {
            console.error('❌ MediaConvert processing error:', processingError);
            throw processingError;
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