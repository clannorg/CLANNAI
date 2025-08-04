#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

async function uploadGreenIslandData() {
  try {
    console.log('🏈 UPLOADING GREEN ISLAND DATA VIA API');
    console.log('=====================================');
    
    // 1. Load the events JSON
    console.log('📊 Step 1: Loading AI analysis...');
    const eventsPath = path.join(__dirname, '../../../ai/veo-games/data/19-20250419/web_events_array.json');
    const eventsData = JSON.parse(fs.readFileSync(eventsPath, 'utf8'));
    console.log(`✅ Loaded ${eventsData.length} events`);
    
    // 2. Load S3 URLs
    console.log('📁 Step 2: Loading S3 locations...');
    const s3Path = path.join(__dirname, '../../../ai/veo-games/data/19-20250419/s3_locations.json');
    const s3Data = JSON.parse(fs.readFileSync(s3Path, 'utf8'));
    const videoUrl = s3Data.s3_urls['video.mp4'].url;
    
    console.log(`✅ Video URL: ${videoUrl}`);
    console.log(`✅ Events count: ${eventsData.length}`);
    
    // 3. Create the game via API (if available)
    console.log('🎮 Step 3: Creating game via API...');
    
    const gameData = {
      title: 'Green Island FC - Match Analysis (Apr 19, 2025)',
      description: 'Professional AI analysis of Green Island FC match footage',
      video_url: videoUrl,
      s3_key: s3Data.s3_urls['video.mp4'].s3_key,
      team_name: 'Green Island FC',
      ai_analysis: eventsData,
      status: 'analyzed'
    };
    
    // For now, just output the data that needs to be uploaded
    console.log('\n🎯 GREEN ISLAND GAME DATA READY:');
    console.log('===============================');
    console.log(`📹 Video: ${videoUrl}`);
    console.log(`⚽ Events: ${eventsData.length} detected`);
    console.log(`📊 File size: ${Math.round(s3Data.s3_urls['video.mp4'].file_size_mb)}MB`);
    
    console.log('\n📋 MANUAL STEPS TO COMPLETE:');
    console.log('============================');
    console.log('1. Go to your web app dashboard');
    console.log('2. Create new game with title: "Green Island FC - Match Analysis"');
    console.log('3. Paste video URL:', videoUrl);
    console.log('4. Upload the events JSON manually');
    console.log('5. Set status to "analyzed"');
    
    // Save a simplified JSON for manual upload
    const manualUpload = {
      title: gameData.title,
      description: gameData.description,
      video_url: videoUrl,
      events: eventsData,
      metadata: {
        total_events: eventsData.length,
        file_size_mb: s3Data.s3_urls['video.mp4'].file_size_mb,
        analysis_date: s3Data.upload_timestamp
      }
    };
    
    fs.writeFileSync('./green_island_upload.json', JSON.stringify(manualUpload, null, 2));
    console.log('\n💾 Saved manual upload data to: green_island_upload.json');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

uploadGreenIslandData();