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
        const { gameId, events, includeScoreline = false } = req.body;
        
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
        
        // Get team information and calculate scores if scoreline is requested
        let teamInfo = null;
        let allGameEvents = [];
        
        if (includeScoreline) {
            // Parse team metadata
            const metadata = game.metadata ? JSON.parse(game.metadata) : null;
            teamInfo = {
                redTeam: metadata?.teams?.red_team || { name: 'Team A', jersey_color: 'red' },
                blueTeam: metadata?.teams?.blue_team || { name: 'Team B', jersey_color: 'blue' }
            };
            
            // Parse all game events for score calculation
            allGameEvents = game.ai_analysis ? JSON.parse(game.ai_analysis) : [];
            console.log(`📊 Team info: ${teamInfo.redTeam.name} vs ${teamInfo.blueTeam.name}`);
        }
        
        // Create temporary directory for processing
        const jobId = uuidv4();
        const tempDir = path.join(os.tmpdir(), `clip-job-${jobId}`);
        fs.mkdirSync(tempDir, { recursive: true });
        
        // Helper function to calculate scores at a given timestamp
        const calculateScoresAtTime = (timestamp) => {
            if (!includeScoreline || !allGameEvents.length) return { red: 0, blue: 0 };
            
            const goalsUpToTime = allGameEvents.filter(event => 
                event.type === 'goal' && event.timestamp <= timestamp
            );
            
            let redScore = 0, blueScore = 0;
            
            goalsUpToTime.forEach(goal => {
                const goalTeam = (goal.team || '').toLowerCase();
                const redTeamName = teamInfo.redTeam.name.toLowerCase();
                const blueTeamName = teamInfo.blueTeam.name.toLowerCase();
                
                if (goalTeam === redTeamName || 
                    goalTeam.includes(redTeamName) || 
                    redTeamName.includes(goalTeam)) {
                    redScore++;
                } else if (goalTeam === blueTeamName || 
                          goalTeam.includes(blueTeamName) || 
                          blueTeamName.includes(goalTeam)) {
                    blueScore++;
                }
            });
            
            return { red: redScore, blue: blueScore };
        };

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
                
                let ffmpegCmd;
                
                if (includeScoreline && teamInfo) {
                    // Calculate scores at the event timestamp
                    const scores = calculateScoresAtTime(event.timestamp);
                    const minutes = Math.floor(event.timestamp / 60);
                    const seconds = Math.floor(event.timestamp % 60);
                    const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                    
                    // Create scoreline text
                    const redTeamShort = teamInfo.redTeam.name.split(' ')[0].toUpperCase();
                    const blueTeamShort = teamInfo.blueTeam.name.split(' ')[0].toUpperCase();
                    const scorelineText = `${redTeamShort} ${scores.red} - ${scores.blue} ${blueTeamShort}    ${timeStr}`;
                    
                    console.log(`📊 Adding scoreline: ${scorelineText}`);
                    
                    // Use FFmpeg with text overlay for scoreline
                    ffmpegCmd = [
                        'ffmpeg',
                        '-y',
                        '-ss', startTime.toString(),
                        '-i', videoUrl,
                        '-t', duration.toString(),
                        '-vf', `drawtext=text='${scorelineText}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.7:boxborderw=5:x=20:y=20`,
                        '-c:a', 'copy', // Copy audio without re-encoding
                        '-avoid_negative_ts', 'make_zero',
                        clipPath
                    ].join(' ');
                } else {
                    // Use FFmpeg to extract clip segment without overlay
                    ffmpegCmd = [
                        'ffmpeg',
                        '-y', // Overwrite output files
                        '-ss', startTime.toString(),
                        '-i', videoUrl,
                        '-t', duration.toString(),
                        '-c', 'copy', // Copy streams without re-encoding (faster)
                        '-avoid_negative_ts', 'make_zero',
                        clipPath
                    ].join(' ');
                }
                
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