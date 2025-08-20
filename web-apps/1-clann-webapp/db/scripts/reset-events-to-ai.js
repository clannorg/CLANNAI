#!/usr/bin/env node

/**
 * Reset Events to AI Analysis
 * 
 * Clears user-modified events for a game, reverting back to showing
 * the original AI analysis. Useful when AI analysis has been regenerated
 * and you want users to see the fresh AI events instead of old edits.
 * 
 * Usage:
 *   node reset-events-to-ai.js <game-id>
 *   node reset-events-to-ai.js all  # Reset ALL games
 */

const { Pool } = require('pg')
const path = require('path')
require('dotenv').config({ path: path.join(__dirname, '../../backend/.env') })

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT || 5432,
  ssl: {
    rejectUnauthorized: false
  }
})

async function resolveGameId(input) {
  // If it's a number, treat it as game index from list-games.js
  if (/^\d+$/.test(input)) {
    const gameNumber = parseInt(input)
    const result = await pool.query(`
      SELECT id, title FROM games 
      ORDER BY created_at DESC
    `)
    
    if (gameNumber < 1 || gameNumber > result.rows.length) {
      throw new Error(`Game number ${gameNumber} not found. Use 1-${result.rows.length}`)
    }
    
    const game = result.rows[gameNumber - 1]
    console.log(`🎯 Game ${gameNumber}: "${game.title}"`)
    return game.id
  }
  
  // Otherwise treat as direct game ID
  return input
}

async function resetGameEvents(gameInput) {
  try {
    const gameId = await resolveGameId(gameInput)
    console.log(`🔄 Resetting events for game ${gameId}...`)
    
    // Get current state
    const gameResult = await pool.query(
      'SELECT title, events_modified, ai_analysis FROM games WHERE id = $1',
      [gameId]
    )
    
    if (gameResult.rows.length === 0) {
      console.log(`❌ Game not found`)
      return false
    }
    
    const game = gameResult.rows[0]
    console.log(`📋 Game: "${game.title}"`)
    
    const hasModified = !!game.events_modified
    const aiEventsCount = game.ai_analysis ? game.ai_analysis.length : 0
    const modifiedEventsCount = game.events_modified ? game.events_modified.length : 0
    
    console.log(`   AI Events: ${aiEventsCount}`)
    console.log(`   Modified Events: ${modifiedEventsCount} ${hasModified ? '(ACTIVE)' : '(none)'}`)
    
    if (!hasModified) {
      console.log(`✅ Game ${gameId} already showing AI events (no reset needed)`)
      return true
    }
    
    // Clear the modified events
    await pool.query(`
      UPDATE games 
      SET 
        events_modified = NULL,
        events_last_modified_by = NULL,
        events_last_modified_at = NULL
      WHERE id = $1
    `, [gameId])
    
    console.log(`✅ Reset complete! Game ${gameId} will now show ${aiEventsCount} AI events`)
    return true
    
  } catch (error) {
    console.error(`❌ Error resetting game ${gameId}:`, error.message)
    return false
  }
}

async function resetAllGames() {
  try {
    console.log('🔄 Resetting ALL games to AI events...')
    
    // Get all games with modified events
    const result = await pool.query(`
      SELECT id, title, 
             CASE WHEN events_modified IS NOT NULL THEN array_length(events_modified, 1) ELSE 0 END as modified_count,
             CASE WHEN ai_analysis IS NOT NULL THEN array_length(ai_analysis, 1) ELSE 0 END as ai_count
      FROM games 
      WHERE events_modified IS NOT NULL
      ORDER BY title
    `)
    
    if (result.rows.length === 0) {
      console.log('✅ No games have modified events - nothing to reset')
      return
    }
    
    console.log(`\n📊 Found ${result.rows.length} games with modified events:`)
    result.rows.forEach(game => {
      console.log(`   ${game.id}: "${game.title}" (${game.modified_count} modified → ${game.ai_count} AI)`)
    })
    
    console.log('\n🔄 Resetting all...')
    
    // Reset all at once
    const updateResult = await pool.query(`
      UPDATE games 
      SET 
        events_modified = NULL,
        events_last_modified_by = NULL,
        events_last_modified_at = NULL
      WHERE events_modified IS NOT NULL
    `)
    
    console.log(`✅ Reset ${updateResult.rowCount} games to show AI events`)
    
  } catch (error) {
    console.error('❌ Error resetting all games:', error.message)
  }
}

async function main() {
  const gameInput = process.argv[2]
  
  if (!gameInput) {
    console.log('❌ Usage: node reset-events-to-ai.js <game-number>')
    console.log('   Or: node reset-events-to-ai.js <game-id>')
    console.log('   Or: node reset-events-to-ai.js all')
    console.log('')
    console.log('💡 First run: node list-games.js')
    console.log('   Then use the game number: node reset-events-to-ai.js 3')
    process.exit(1)
  }
  
  try {
    if (gameInput.toLowerCase() === 'all') {
      await resetAllGames()
    } else {
      await resetGameEvents(gameInput)
    }
  } catch (error) {
    console.error('❌ Script error:', error.message)
  } finally {
    await pool.end()
  }
}

if (require.main === module) {
  main()
}