const { S3Client, GetObjectCommand, PutObjectCommand } = require('@aws-sdk/client-s3');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

/**
 * Use FFmpeg from Lambda layer (simpler approach)
 */
async function ensureFFmpeg() {
    // Try common FFmpeg locations in Lambda layers
    const possiblePaths = [
        '/opt/bin/ffmpeg',
        '/opt/ffmpeg/ffmpeg', 
        '/usr/bin/ffmpeg',
        'ffmpeg' // system PATH
    ];
    
    for (const path of possiblePaths) {
        try {
            execSync(`${path} -version`, { stdio: 'pipe' });
            console.log(`✅ Found FFmpeg at: ${path}`);
            return path;
        } catch (error) {
            // Continue to next path
        }
    }
    
    throw new Error('FFmpeg not found in any expected location. Please add an FFmpeg layer to this Lambda function.');
}

// Initialize S3 client
const s3Client = new S3Client({
    region: process.env.AWS_REGION || 'eu-west-1'
});

const BUCKET_NAME = process.env.AWS_BUCKET_NAME || 'end-nov-webapp-clann';
const TMP_DIR = '/tmp';

/**
 * Main Lambda handler for clip processing
 */
exports.handler = async (event) => {
    console.log('🚀 Lambda clip processor started');
    console.log('📥 Event:', JSON.stringify(event, null, 2));
    
    try {
        // Parse input - handle both API Gateway and direct invocation
        let body;
        if (event.body) {
            // API Gateway format
            body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
        } else {
            // Direct invocation format
            body = event;
        }
        
        const { gameId, events, s3VideoUrl } = body;
        
        // Validate input
        if (!gameId || !events || !Array.isArray(events) || events.length === 0) {
            throw new Error('gameId and events array are required');
        }
        
        if (!s3VideoUrl) {
            throw new Error('s3VideoUrl is required');
        }
        
        console.log(`📊 Processing ${events.length} events for game ${gameId}`);
        
        // Generate unique job ID
        const jobId = uuidv4();
        const workDir = path.join(TMP_DIR, `clip-job-${jobId}`);
        
        // Create working directory
        fs.mkdirSync(workDir, { recursive: true });
        console.log(`📁 Working directory: ${workDir}`);
        
        // Process clips
        const clipPaths = [];
        
        for (let i = 0; i < events.length; i++) {
            const event = events[i];
            const beforePadding = event.beforePadding || 5;
            const afterPadding = event.afterPadding || 3;
            
            const startTime = Math.max(0, event.timestamp - beforePadding);
            const duration = beforePadding + afterPadding;
            
            console.log(`🎬 Processing event ${i + 1}: timestamp=${event.timestamp}s, start=${startTime}s, duration=${duration}s`);
            
            const clipPath = path.join(workDir, `clip_${i + 1}.mp4`);
            
            // Download FFmpeg if not available
            const ffmpegPath = await ensureFFmpeg();
            
            // Use FFmpeg to extract clip segment
            const ffmpegCmd = [
                ffmpegPath,
                '-y', // Overwrite output files
                '-ss', startTime.toString(),
                '-i', s3VideoUrl,
                '-t', duration.toString(),
                '-c', 'copy', // Copy streams without re-encoding (faster)
                '-avoid_negative_ts', 'make_zero',
                clipPath
            ].join(' ');
            
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
                throw new Error(`Failed to create clip ${i + 1}: ${ffmpegError.message}`);
            }
        }
        
        // Combine clips if multiple
        let finalClipPath;
        
        if (clipPaths.length === 1) {
            finalClipPath = clipPaths[0];
            console.log('📹 Single clip, no concatenation needed');
        } else {
            console.log(`🔗 Concatenating ${clipPaths.length} clips`);
            
            // Create concat file list
            const concatListPath = path.join(workDir, 'concat_list.txt');
            const concatContent = clipPaths.map(p => `file '${p}'`).join('\n');
            fs.writeFileSync(concatListPath, concatContent);
            
            finalClipPath = path.join(workDir, 'final_highlight_reel.mp4');
            
            const concatCmd = [
                ffmpegPath, // Use the same FFmpeg path
                '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concatListPath,
                '-c', 'copy',
                finalClipPath
            ].join(' ');
            
            console.log(`🔗 Concat command: ${concatCmd}`);
            
            try {
                execSync(concatCmd, { 
                    stdio: 'pipe',
                    timeout: 60000 // 1 minute timeout for concat
                });
                
                if (fs.existsSync(finalClipPath)) {
                    const stats = fs.statSync(finalClipPath);
                    console.log(`✅ Final clip created: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
                } else {
                    throw new Error('Final clip file not created');
                }
            } catch (concatError) {
                console.error('❌ Concatenation error:', concatError.message);
                throw new Error(`Failed to concatenate clips: ${concatError.message}`);
            }
        }
        
        // Upload final clip to S3
        const outputKey = `clips/${gameId}/${Date.now()}/highlight_reel.mp4`;
        const fileBuffer = fs.readFileSync(finalClipPath);
        
        console.log(`📤 Uploading to S3: ${outputKey}`);
        
        await s3Client.send(new PutObjectCommand({
            Bucket: BUCKET_NAME,
            Key: outputKey,
            Body: fileBuffer,
            ContentType: 'video/mp4'
        }));
        
        const downloadUrl = `https://${BUCKET_NAME}.s3.amazonaws.com/${outputKey}`;
        
        // Calculate total duration
        const totalDuration = events.reduce((total, event) => {
            const beforePadding = event.beforePadding || 5;
            const afterPadding = event.afterPadding || 3;
            return total + beforePadding + afterPadding;
        }, 0);
        
        // Cleanup temp files
        try {
            execSync(`rm -rf ${workDir}`, { stdio: 'pipe' });
            console.log('🧹 Cleanup completed');
        } catch (cleanupError) {
            console.warn('⚠️ Cleanup warning:', cleanupError.message);
        }
        
        console.log('🎉 Clip processing completed successfully');
        
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                success: true,
                downloadUrl: downloadUrl,
                fileName: 'highlight_reel.mp4',
                duration: totalDuration,
                eventCount: events.length,
                outputKey: outputKey,
                message: 'Clip created successfully with Lambda + FFmpeg!'
            })
        };
        
    } catch (error) {
        console.error('❌ Lambda error:', error);
        
        return {
            statusCode: 500,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                success: false,
                error: error.message,
                message: 'Clip processing failed'
            })
        };
    }
};