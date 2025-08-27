const AWS = require('aws-sdk');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const s3 = new AWS.S3();

exports.handler = async (event) => {
    console.log('🎬 Lambda clip processor started');
    console.log('📝 Event:', JSON.stringify(event, null, 2));
    
    const { gameId, events, s3VideoUrl, bucketName } = event;
    
    try {
        // Create temp directory
        const tempDir = '/tmp/clips';
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir, { recursive: true });
        }
        
        const clipPaths = [];
        
        // Create individual clips
        for (let i = 0; i < events.length; i++) {
            const event = events[i];
            const clipPath = path.join(tempDir, `clip_${i + 1}.mp4`);
            
            const beforePadding = event.beforePadding || 5;
            const afterPadding = event.afterPadding || 5;
            const startTime = Math.max(0, event.timestamp - beforePadding);
            const duration = beforePadding + afterPadding;
            
            console.log(`📹 Creating clip ${i + 1}: ${startTime}s for ${duration}s`);
            
            // Use FFmpeg from layer
            const ffmpegCmd = `/opt/bin/ffmpeg -ss ${startTime} -i "${s3VideoUrl}" -t ${duration} -c copy -avoid_negative_ts make_zero "${clipPath}"`;
            
            try {
                execSync(ffmpegCmd, { stdio: 'inherit' });
                clipPaths.push(clipPath);
                console.log(`✅ Created clip ${i + 1}`);
            } catch (error) {
                console.error(`❌ Error creating clip ${i + 1}:`, error);
                throw error;
            }
        }
        
        // Create file list for concatenation
        const fileListPath = path.join(tempDir, 'filelist.txt');
        const fileListContent = clipPaths.map(clip => `file '${clip}'`).join('\n');
        fs.writeFileSync(fileListPath, fileListContent);
        
        // Concatenate clips
        const finalClipPath = path.join(tempDir, 'highlight_reel.mp4');
        const concatCmd = `/opt/bin/ffmpeg -f concat -safe 0 -i "${fileListPath}" -c copy "${finalClipPath}"`;
        
        console.log('🔗 Concatenating clips...');
        execSync(concatCmd, { stdio: 'inherit' });
        
        // Upload to S3
        const finalClipBuffer = fs.readFileSync(finalClipPath);
        const timestamp = Date.now();
        const clipFileName = `highlight_${gameId}_${timestamp}.mp4`;
        
        const uploadParams = {
            Bucket: bucketName,
            Key: clipFileName,
            Body: finalClipBuffer,
            ContentType: 'video/mp4'
        };
        
        console.log('📤 Uploading to S3...');
        const uploadResult = await s3.upload(uploadParams).promise();
        
        // Clean up temp files
        clipPaths.forEach(clipPath => {
            if (fs.existsSync(clipPath)) {
                fs.unlinkSync(clipPath);
            }
        });
        if (fs.existsSync(finalClipPath)) {
            fs.unlinkSync(finalClipPath);
        }
        if (fs.existsSync(fileListPath)) {
            fs.unlinkSync(fileListPath);
        }
        
        console.log('✅ Clip processing complete!');
        
        return {
            statusCode: 200,
            body: JSON.stringify({
                success: true,
                s3Key: clipFileName,
                location: uploadResult.Location,
                eventCount: events.length
            })
        };
        
    } catch (error) {
        console.error('❌ Lambda error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                error: 'Failed to process clips',
                details: error.message
            })
        };
    }
};
