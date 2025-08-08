#!/usr/bin/env node

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

// Load environment variables from the backend
dotenv.config({ path: '../../web-apps/1-clann-webapp/backend/.env' });

console.log('🔗 Connecting to database...');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL && process.env.DATABASE_URL.includes('rds.amazonaws.com') ? { 
    rejectUnauthorized: false,
    require: true 
  } : false
});

async function insertGreenIslandGame() {
  try {
    console.log('\n🏈 INSERTING GREEN ISLAND GAME');
    console.log('================================');
    
    // 1. First, create/find Green Island team
    console.log('📋 Step 1: Creating Green Island team...');
    const teamResult = await pool.query(`
      INSERT INTO teams (name, description, team_code, color)
      VALUES ($1, $2, $3, $4)
      ON CONFLICT (team_code) DO UPDATE SET 
        name = EXCLUDED.name,
        description = EXCLUDED.description
      RETURNING id, name
    `, [
      'Green Island FC',
      'Green Island Football Club - Customer Analysis',
      'GREEN_ISLAND',
      '#00FF00'
    ]);
    
    const teamId = teamResult.rows[0].id;
    console.log(`✅ Team created/found: ${teamResult.rows[0].name} (${teamId})`);
    
    // 2. Load the events JSON
    console.log('📊 Step 2: Loading AI analysis...');
    const eventsPath = path.join(__dirname, 'data/19-20250419/web_events_array.json');
    const eventsData = JSON.parse(fs.readFileSync(eventsPath, 'utf8'));
    console.log(`✅ Loaded ${eventsData.length} events`);
    
    // 3. Load S3 URLs
    console.log('📁 Step 3: Loading S3 locations...');
    const s3Path = path.join(__dirname, 'data/19-20250419/s3_locations.json');
    const s3Data = JSON.parse(fs.readFileSync(s3Path, 'utf8'));
    const videoUrl = s3Data.s3_urls['video.mp4'].url;
    const videoS3Key = s3Data.s3_urls['video.mp4'].s3_key;
    console.log(`✅ Video URL: ${videoUrl}`);
    
    // 4. Insert the game
    console.log('🎮 Step 4: Creating game record...');
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
        metadata
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
      RETURNING id, title, status
    `, [
      'Green Island FC - Match Analysis (Apr 19, 2025)',
      'Professional AI analysis of Green Island FC match footage',
      videoUrl,
      videoS3Key,
      'veo',
      'analyzed',
      teamId,
      JSON.stringify(eventsData),
      Math.round(s3Data.s3_urls['video.mp4'].file_size_mb * 1024 * 1024), // Convert MB to bytes
      1800, // 30 minutes estimated
      JSON.stringify({
        analysis_date: s3Data.upload_timestamp,
        total_events: eventsData.length,
        source_veo_url: 'https://app.veo.co/matches/20250419-19-apr-2025-224536-01ff86a0/',
        ai_model: 'clann-v1'
      })
    ]);
    
    const gameId = gameResult.rows[0].id;
    
    console.log('\n🎉 SUCCESS!');
    console.log('===========');
    console.log(`✅ Game created: ${gameResult.rows[0].title}`);
    console.log(`✅ Game ID: ${gameId}`);
    console.log(`✅ Status: ${gameResult.rows[0].status}`);
    console.log(`✅ Events: ${eventsData.length} detected`);
    console.log(`✅ Video: ${Math.round(s3Data.s3_urls['video.mp4'].file_size_mb)}MB`);
    
    console.log('\n🌐 Green Island can now access their analysis at:');
    console.log(`   https://your-webapp.com/games/${gameId}`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error(error);
  } finally {
    await pool.end();
  }
}

insertGreenIslandGame();