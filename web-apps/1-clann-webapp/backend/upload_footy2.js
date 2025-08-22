#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');
require('dotenv').config();

console.log('🔗 Connecting to database...');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL && process.env.DATABASE_URL.includes('rds.amazonaws.com') ? { 
    rejectUnauthorized: false,
    require: true 
  } : false
});

async function uploadFooty2Game() {
  try {
    console.log('\n⚽ UPLOADING FOOTY2 MATCH WITH CORRECTED EVENTS');
    console.log('===============================================');
    
    // 1. First, create/find Footy2 team
    console.log('📋 Step 1: Creating Footy2 teams...');
    
    // Create Clann team
    const clannTeamResult = await pool.query(`
      INSERT INTO teams (name, description, team_code, color)
      VALUES ($1, $2, $3, $4)
      ON CONFLICT (team_code) DO UPDATE SET 
        name = EXCLUDED.name,
        description = EXCLUDED.description
      RETURNING id, name
    `, [
      'Clann',
      'Clann FC - Footy2 Match Analysis',
      'CLANN_FC',
      '#FFFFFF'  // White/no bibs
    ]);
    
    const clannTeamId = clannTeamResult.rows[0].id;
    console.log(`✅ Clann team created/found: ${clannTeamResult.rows[0].name} (${clannTeamId})`);
    
    // Create Lostthehead team
    const losttheheadTeamResult = await pool.query(`
      INSERT INTO teams (name, description, team_code, color)
      VALUES ($1, $2, $3, $4)
      ON CONFLICT (team_code) DO UPDATE SET 
        name = EXCLUDED.name,
        description = EXCLUDED.description
      RETURNING id, name
    `, [
      'Lostthehead',
      'Lostthehead FC - Footy2 Match Analysis',
      'LOSTTHEHEAD_FC',
      '#FFA500'  // Orange bibs
    ]);
    
    const losttheheadTeamId = losttheheadTeamResult.rows[0].id;
    console.log(`✅ Lostthehead team created/found: ${losttheheadTeamResult.rows[0].name} (${losttheheadTeamId})`);
    
    // 2. Load the corrected events JSON
    console.log('📊 Step 2: Loading corrected AI analysis...');
    const eventsPath = path.join(__dirname, '../../../ai/footy2/outputs/leo1/web_events_array.json');
    const eventsData = JSON.parse(fs.readFileSync(eventsPath, 'utf8'));
    console.log(`✅ Loaded ${eventsData.length} corrected events`);
    
    // 3. Load match metadata
    console.log('📁 Step 3: Loading match metadata...');
    const metadataPath = path.join(__dirname, '../../../ai/footy2/outputs/leo1/match_metadata.json');
    const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
    console.log(`✅ Match metadata loaded`);
    
    // 4. Check if S3 locations exist
    let videoUrl = null;
    let videoS3Key = null;
    let fileSize = 0;
    
    const s3LocationsPath = path.join(__dirname, '../../../ai/footy2/outputs/leo1/s3_locations.json');
    if (fs.existsSync(s3LocationsPath)) {
      console.log('📁 Step 4: Loading S3 locations...');
      const s3Data = JSON.parse(fs.readFileSync(s3LocationsPath, 'utf8'));
      if (s3Data.s3_urls && s3Data.s3_urls['video.mp4']) {
        videoUrl = s3Data.s3_urls['video.mp4'].url;
        videoS3Key = s3Data.s3_urls['video.mp4'].s3_key;
        fileSize = Math.round(s3Data.s3_urls['video.mp4'].file_size_mb * 1024 * 1024);
        console.log(`✅ Video URL: ${videoUrl}`);
      }
    } else {
      console.log('⚠️  Step 4: No S3 locations found - using local video reference');
      videoUrl = 'local://footy2/leo1.mp4';
      videoS3Key = 'footy2/leo1.mp4';
      fileSize = 100 * 1024 * 1024; // Estimate 100MB
    }
    
    // 5. Insert the game (using Clann as primary team)
    console.log('🎮 Step 5: Creating game record...');
    const gameResult = await pool.query(`
      INSERT INTO games (
        title, 
        description,
        video_url,
        s3_key,
        file_type,
        status,
        team_id,
        ai_analysis,
        file_size,
        duration,
        metadata,
        is_demo
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
      RETURNING id, title, status
    `, [
      'Footy2 Match: Clann vs Lostthehead (Corrected Events)',
      'Professional AI analysis with manually corrected goal events. Final Score: Clann 14 - 9 Lostthehead',
      videoUrl,
      videoS3Key,
      'analysis',
      'analyzed',
      clannTeamId,
      JSON.stringify(eventsData),
      fileSize,
      3120, // 52 minutes (based on last event at 51:57)
      JSON.stringify({
        analysis_date: new Date().toISOString(),
        total_events: eventsData.length,
        total_goals: metadata.total_goals || eventsData.length,
        team_scores: metadata.team_scores || { clann: 14, lostthehead: 9 },
        teams: {
          clann: { id: clannTeamId, name: 'Clann', colors: 'no bibs/colours' },
          lostthehead: { id: losttheheadTeamId, name: 'Lostthehead', colors: 'orange bibs' }
        },
        match_type: '5-a-side',
        ai_model: 'clann-v4-corrected',
        correction_notes: 'Events manually corrected based on actual match detection',
        original_events_count: 23,
        corrected_events_count: eventsData.length
      }),
      true  // is_demo - make it accessible to all users
    ]);
    
    const gameId = gameResult.rows[0].id;
    
    // 6. Calculate and display final statistics
    const teamStats = { clann: 0, lostthehead: 0 };
    eventsData.forEach(event => {
      if (event.type === 'goal') {
        teamStats[event.team] = (teamStats[event.team] || 0) + 1;
      }
    });
    
    console.log('\n🎉 SUCCESS!');
    console.log('===========');
    console.log(`✅ Game created: ${gameResult.rows[0].title}`);
    console.log(`✅ Game ID: ${gameId}`);
    console.log(`✅ Status: ${gameResult.rows[0].status}`);
    console.log(`✅ Events: ${eventsData.length} corrected goals`);
    console.log(`✅ Final Score: Clann ${teamStats.clann} - ${teamStats.lostthehead} Lostthehead`);
    console.log(`✅ Duration: ${Math.floor(3120/60)}:${String(3120%60).padStart(2,'0')} minutes`);
    console.log(`✅ Demo Access: Enabled (accessible to all users)`);
    
    if (videoUrl.startsWith('http')) {
      console.log(`✅ Video: Available on S3`);
    } else {
      console.log(`⚠️  Video: Local reference (${videoUrl})`);
      console.log(`   📝 Note: Upload video to S3 and update s3_key for full functionality`);
    }
    
    console.log('\n🌐 Footy2 match is now accessible at:');
    console.log(`   https://your-webapp.com/games/${gameId}`);
    
    console.log('\n📊 Event Summary:');
    console.log('================');
    console.log(`   Total Goals: ${eventsData.length}`);
    console.log(`   Clann Goals: ${teamStats.clann}`);
    console.log(`   Lostthehead Goals: ${teamStats.lostthehead}`);
    console.log(`   First Goal: ${Math.floor(eventsData[0].timestamp/60)}:${String(eventsData[0].timestamp%60).padStart(2,'0')}`);
    console.log(`   Last Goal: ${Math.floor(eventsData[eventsData.length-1].timestamp/60)}:${String(eventsData[eventsData.length-1].timestamp%60).padStart(2,'0')}`);
    
    return gameId;
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error(error);
    throw error;
  } finally {
    await pool.end();
  }
}

// Check if we need to upload to S3 first
async function checkS3Upload() {
  console.log('\n🔍 CHECKING S3 UPLOAD STATUS');
  console.log('============================');
  
  const s3LocationsPath = path.join(__dirname, '../../../ai/footy2/outputs/leo1/s3_locations.json');
  
  if (!fs.existsSync(s3LocationsPath)) {
    console.log('⚠️  No S3 locations found. Video needs to be uploaded to S3 first.');
    console.log('\n📋 TO UPLOAD TO S3:');
    console.log('==================');
    console.log('1. Run the S3 uploader script:');
    console.log('   cd /home/ubuntu/CLANNAI/ai/footy2');
    console.log('   python pipeline/6_s3_uploader.py leo1');
    console.log('');
    console.log('2. Then run this script again to create the webapp entry');
    console.log('');
    return false;
  }
  
  const s3Data = JSON.parse(fs.readFileSync(s3LocationsPath, 'utf8'));
  if (!s3Data.s3_urls || !s3Data.s3_urls['video.mp4']) {
    console.log('⚠️  S3 data incomplete. Video upload may have failed.');
    return false;
  }
  
  console.log('✅ S3 upload completed. Video available at:');
  console.log(`   ${s3Data.s3_urls['video.mp4'].url}`);
  return true;
}

async function main() {
  try {
    const s3Ready = await checkS3Upload();
    
    if (!s3Ready) {
      console.log('\n🚀 PROCEEDING WITH LOCAL REFERENCE');
      console.log('==================================');
      console.log('Creating webapp entry with local video reference.');
      console.log('You can upload to S3 later and update the video URL.');
    }
    
    const gameId = await uploadFooty2Game();
    
    console.log('\n🎯 NEXT STEPS:');
    console.log('=============');
    if (!s3Ready) {
      console.log('1. Upload video to S3 using: python pipeline/6_s3_uploader.py leo1');
      console.log('2. Update the game record with the S3 video URL');
    }
    console.log(`3. Access the match analysis at: /games/${gameId}`);
    console.log('4. Verify the corrected events display properly in the timeline');
    
  } catch (error) {
    console.error('❌ Upload failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { uploadFooty2Game, checkS3Upload };
