require('dotenv').config();
const { Pool } = require('pg');
const axios = require('axios');

const isAWSRDS = process.env.DATABASE_URL && process.env.DATABASE_URL.includes('rds.amazonaws.com');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || `postgresql://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`,
  ssl: isAWSRDS ? { rejectUnauthorized: false } : false
});

async function fixEdinburghTactical() {
  try {
    console.log('🔧 Fixing Edinburgh tactical analysis...');
    
    // Get the Edinburgh game
    const gameResult = await pool.query('SELECT id, title, metadata FROM games WHERE id = \'0f969bda-b953-473e-a34f-41b4742b5380\'');
    
    if (gameResult.rows.length === 0) {
      console.log('❌ Game not found');
      return;
    }
    
    const game = gameResult.rows[0];
    console.log(`📊 Processing game: ${game.title}`);
    
    // Get the tactical file URL from metadata
    const tacticalFileUrl = game.metadata?.tactical_files?.coaching_insights?.url;
    
    if (!tacticalFileUrl) {
      console.log('❌ No tactical file URL found in metadata');
      return;
    }
    
    console.log(`📥 Fetching tactical data from: ${tacticalFileUrl}`);
    
    // Fetch the tactical analysis from S3
    const response = await axios.get(tacticalFileUrl, {
      responseType: 'text'
    });
    
    let analysisData = response.data;
    
    // Parse JSON if it's a string
    if (typeof analysisData === 'string') {
      try {
        analysisData = JSON.parse(analysisData);
      } catch (parseError) {
        console.error('❌ Failed to parse JSON:', parseError);
        return;
      }
    }
    
    console.log('📊 Fetched tactical analysis with keys:', Object.keys(analysisData));
    
    // Transform the data to match the expected format
    const transformedData = {
      tactical: {},
      analysis: {}
    };
    
    // If the S3 data has tactical_analysis.red_team, transform it
    if (analysisData.tactical_analysis) {
      const tactical = analysisData.tactical_analysis;
      
      if (tactical.red_team) {
        transformedData.tactical.red_team = {
          content: JSON.stringify(tactical.red_team, null, 2)
        };
      }
      
      if (tactical.blue_team) {
        transformedData.tactical.blue_team = {
          content: JSON.stringify(tactical.blue_team, null, 2)
        };
      }
    }
    
    // Include other analysis data
    if (analysisData.match_overview) {
      transformedData.analysis.match_overview = analysisData.match_overview;
    }
    
    if (analysisData.key_moments) {
      transformedData.analysis.key_moments = analysisData.key_moments;
    }
    
    if (analysisData.manager_recommendations) {
      transformedData.analysis.manager_recommendations = analysisData.manager_recommendations;
    }
    
    console.log('🔄 Transformed data structure:', Object.keys(transformedData));
    console.log('🔄 Tactical keys:', Object.keys(transformedData.tactical));
    console.log('🔄 Analysis keys:', Object.keys(transformedData.analysis));
    
    // Update the game with the processed tactical analysis
    await pool.query(
      'UPDATE games SET tactical_analysis = $1 WHERE id = $2',
      [transformedData, game.id]
    );
    
    console.log('✅ Edinburgh tactical analysis fixed!');
    
  } catch (error) {
    console.error('❌ Error fixing Edinburgh tactical analysis:', error);
  } finally {
    await pool.end();
  }
}

fixEdinburghTactical(); 