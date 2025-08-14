const express = require('express');
const { authenticateToken } = require('../middleware/auth');
const { getGameById } = require('../utils/database');
const { uploadToS3 } = require('../utils/s3');
const { PutObjectCommand } = require('@aws-sdk/client-s3');
const { S3Client, GetObjectCommand } = require('@aws-sdk/client-s3');
const { exec } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const router = express.Router();

const s3Client = new S3Client({
    region: process.env.AWS_REGION || 'eu-west-1',
    credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
    }
});

const BUCKET_NAME = process.env.AWS_BUCKET_NAME || 'clannai-uploads';

// Create highlight reel from selected events
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

        // Create temporary directories
        const tempDir = path.join(__dirname, '../temp', uuidv4());
        const clipsDir = path.join(tempDir, 'clips');
        await fs.mkdir(tempDir, { recursive: true });
        await fs.mkdir(clipsDir, { recursive: true });

        try {
            // Use video directly from S3 URL (no download needed!)
            console.log('🎬 Using video directly from S3...');
            const videoUrl = game.s3_key.startsWith('https://') ? game.s3_key : 
                `https://${BUCKET_NAME}.s3.${process.env.AWS_REGION || 'eu-west-1'}.amazonaws.com/${game.s3_key}`;

            // Create individual clips
            console.log('✂️ Creating individual clips...');
            const clipPaths = [];
            
            for (let i = 0; i < events.length; i++) {
                const event = events[i];
                const clipPath = path.join(clipsDir, `clip_${i + 1}.mp4`);
                
                // Create 10-second clip (5 seconds before + 5 seconds after the event)
                const startTime = Math.max(0, event.timestamp - 5);
                const duration = 10;
                
                await createClip(videoUrl, clipPath, startTime, duration);
                clipPaths.push(clipPath);
                
                console.log(`✅ Created clip ${i + 1}: ${event.type} at ${event.timestamp}s`);
            }

            // Create file list for concatenation
            const fileListPath = path.join(tempDir, 'filelist.txt');
            const fileListContent = clipPaths.map(clip => `file '${clip}'`).join('\n');
            await fs.writeFile(fileListPath, fileListContent);

            // Concatenate all clips
            console.log('🔗 Concatenating clips...');
            const finalClipPath = path.join(tempDir, 'highlight_reel.mp4');
            await concatenateClips(fileListPath, finalClipPath);

            // Upload final clip to S3
            console.log('📤 Uploading final highlight reel to S3...');
            const finalClipBuffer = await fs.readFile(finalClipPath);
            const timestamp = Date.now();
            const clipFileName = `highlight_${gameId}_${timestamp}.mp4`;
            
            console.log('📤 Attempting to upload to S3...');
            console.log('📤 File size to upload:', finalClipBuffer.length, 'bytes');
            
            let uploadResult;
            try {
                uploadResult = await uploadToS3(finalClipBuffer, clipFileName, 'video/mp4');
                console.log('📤 Upload result:', uploadResult);
                console.log('📤 S3 Key:', uploadResult.s3Key);
            } catch (uploadError) {
                console.error('❌ S3 upload failed:', uploadError);
                throw new Error(`S3 upload failed: ${uploadError.message}`);
            }

            // Clean up temporary files
            console.log('🧹 Cleaning up temporary files...');
            await cleanupTempDir(tempDir);

            console.log('🎉 Highlight reel created successfully!');
            
            // Instead of returning S3 URL, return our backend download endpoint
            res.json({
                success: true,
                downloadUrl: `/api/clips/download/${uploadResult.s3Key}`,
                fileName: clipFileName,
                duration: events.length * 10, // 10 seconds per event
                eventCount: events.length
            });

        } catch (processingError) {
            // Make sure to clean up on error
            try {
                await cleanupTempDir(tempDir);
            } catch (cleanupError) {
                console.error('Error during cleanup:', cleanupError);
            }
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

// Download route - serves files from S3 through our backend
router.get('/download/:s3Key(*)', authenticateToken, async (req, res) => {
    try {
        const s3Key = req.params.s3Key;
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

// Helper function to download file from S3
async function downloadFromS3(s3Key, localPath) {
    // If s3Key is a full URL, extract just the key part
    let actualKey = s3Key;
    if (s3Key.startsWith('https://')) {
        const url = new URL(s3Key);
        actualKey = url.pathname.substring(1); // Remove leading slash
    }
    
    console.log(`📥 Downloading from bucket: ${BUCKET_NAME}, key: ${actualKey}`);
    
    const command = new GetObjectCommand({
        Bucket: BUCKET_NAME,
        Key: actualKey
    });

    const response = await s3Client.send(command);
    const fileStream = response.Body;
    
    const chunks = [];
    for await (const chunk of fileStream) {
        chunks.push(chunk);
    }
    
    const buffer = Buffer.concat(chunks);
    await fs.writeFile(localPath, buffer);
}

// Helper function to create a single clip using FFmpeg
function createClip(inputPath, outputPath, startTime, duration) {
    return new Promise((resolve, reject) => {
        console.log(`🔧 FFmpeg command: ffmpeg -ss ${startTime} -i "${inputPath}" -t ${duration} -c copy -avoid_negative_ts make_zero "${outputPath}"`);
        
        const command = `ffmpeg -ss ${startTime} -i "${inputPath}" -t ${duration} -c copy -avoid_negative_ts make_zero "${outputPath}"`;
        
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error('❌ FFmpeg error:', error);
                console.error('❌ FFmpeg stderr:', stderr);
                console.error('❌ FFmpeg stdout:', stdout);
                reject(new Error(`FFmpeg failed: ${error.message}`));
            } else {
                // Check if file was actually created and has content
                const fs = require('fs');
                if (fs.existsSync(outputPath)) {
                    const stats = fs.statSync(outputPath);
                    console.log(`✅ Clip created: ${outputPath} (${stats.size} bytes)`);
                    if (stats.size < 1000) {
                        console.error('⚠️  Warning: Clip file is very small, may be corrupted');
                    }
                } else {
                    console.error('❌ Error: Clip file was not created');
                    reject(new Error('Clip file was not created'));
                    return;
                }
                resolve();
            }
        });
    });
}

// Helper function to concatenate clips using FFmpeg
function concatenateClips(fileListPath, outputPath) {
    return new Promise((resolve, reject) => {
        const command = `ffmpeg -f concat -safe 0 -i "${fileListPath}" -c copy "${outputPath}"`;
        
        console.log(`🔧 Concatenation command: ${command}`);
        
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error('❌ FFmpeg concatenation error:', error);
                console.error('❌ FFmpeg stderr:', stderr);
                console.error('❌ FFmpeg stdout:', stdout);
                reject(new Error(`FFmpeg concatenation failed: ${error.message}`));
            } else {
                // Check if final file was created and has content
                const fs = require('fs');
                if (fs.existsSync(outputPath)) {
                    const stats = fs.statSync(outputPath);
                    console.log(`✅ Final clip created: ${outputPath} (${stats.size} bytes)`);
                    if (stats.size < 1000) {
                        console.error('⚠️  Warning: Final clip file is very small, may be corrupted');
                    }
                } else {
                    console.error('❌ Error: Final clip file was not created');
                    reject(new Error('Final clip file was not created'));
                    return;
                }
                resolve();
            }
        });
    });
}

// Helper function to upload file to S3 with public read access
async function uploadToS3Public(fileBuffer, fileName, fileType) {
    const timestamp = Date.now();
    const cleanFileName = fileName.replace(/[^a-zA-Z0-9.-]/g, '_');
    const key = `videos/${timestamp}-${cleanFileName}`;

    const command = new PutObjectCommand({
        Bucket: BUCKET_NAME,
        Key: key,
        Body: fileBuffer,
        ContentType: fileType,
        Metadata: {
            'original-filename': fileName,
            'upload-timestamp': timestamp.toString()
        }
    });

    await s3Client.send(command);
    const publicUrl = `https://${BUCKET_NAME}.s3.${process.env.AWS_REGION || 'eu-west-1'}.amazonaws.com/${key}`;

    return {
        s3Key: key,
        publicUrl: publicUrl,
        fileName: cleanFileName
    };
}

// Helper function to clean up temporary directory
async function cleanupTempDir(tempDir) {
    try {
        await fs.rmdir(tempDir, { recursive: true });
    } catch (error) {
        console.error('Cleanup error:', error);
        // Don't throw - cleanup errors shouldn't fail the main operation
    }
}

module.exports = router;