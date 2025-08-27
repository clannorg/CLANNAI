#!/usr/bin/env node

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL && process.env.DATABASE_URL.includes('rds.amazonaws.com') ? { 
    rejectUnauthorized: false,
    require: true 
  } : false
});

async function updateDalkeyV5() {
  try {
    // Get game ID from environment or use default Dalkey game
    const gameId = process.env.GAME_ID || '50ce15ae-b083-4e93-a831-d9f950c39ee8';
    const matchId = process.env.MATCH_ID || '20250427-match-apr-27-2025-9bd1cf29';
    
    console.log(`🎯 Updating game ${gameId} with VEO-Games-V5 analysis for match ${matchId}...`);
    
    // Load our S3 data
    const s3LocationsPath = `../../../ai/veo-games-v5/outputs/${matchId}/s3_core_locations.json`;
    const s3Locations = JSON.parse(fs.readFileSync(s3LocationsPath, 'utf8'));
    
    // Load our events
    const eventsUrl = s3Locations['web_events_array.json'].url;
    console.log('📄 Events URL:', eventsUrl);
    
    // Create metadata with S3 URLs
    const metadata = {
      "teams": {
        "red_team": {
          "name": "Dalkey",
          "jersey_color": "white jerseys"
        },
        "blue_team": {
          "name": "Corduff", 
          "jersey_color": "red and black jerseys"
        }
      },
      "match_id": "20250427-match-apr-27-2025-9bd1cf29",
      "final_score": "Dalkey 0 - 2 Corduff",
      "v5_analysis": true,
      "s3_files": s3Locations,
      "tactical_files": {
        "web_events_array_json": eventsUrl,
        "match_metadata_json": s3Locations['match_metadata.json'].url,
        "team_config_json": s3Locations['1_team_config.json'].url
      }
    };
    
    // Simple events array (webapp will load from S3)
    const events = [
      {
        "type": "goal",
        "timestamp": 2205,
        "team": "Corduff",
        "description": "First VEO-verified goal"
      },
      {
        "type": "goal", 
        "timestamp": 5111,
        "team": "Corduff",
        "description": "Second VEO-verified goal"
      }
    ];
    
    const tactical = {
      "dalkey": {
        "strengths": ["Strong possession play", "Good set pieces"],
        "weaknesses": ["Poor finishing", "Defensive lapses"]
      },
      "corduff": {
        "strengths": ["Clinical finishing", "Strong defense"],
        "weaknesses": ["Prone to fouls", "Inconsistent possession"]
      }
    };
    
    const result = await pool.query(
      'UPDATE games SET ai_analysis = $1, tactical_analysis = $2, metadata = $3, status = $4 WHERE id = $5 RETURNING title',
      [JSON.stringify(events), JSON.stringify(tactical), JSON.stringify(metadata), 'analyzed', gameId]
    );
    
    if (result.rows.length > 0) {
      console.log('✅ Successfully updated Dalkey game!');
      console.log('📊 Game:', result.rows[0].title);
      console.log('🎯 Status: analyzed');
      console.log('📄 Events URL:', eventsUrl);
      console.log('\n🌐 Game should now be visible on the website!');
    } else {
      console.log('❌ Game not found with ID:', gameId);
    }
    
  } catch (error) {
    console.error('❌ Database error:', error.message);
  } finally {
    await pool.end();
  }
}

if (require.main === module) {
  updateDalkeyV5();
}

module.exports = { updateDalkeyV5 };
