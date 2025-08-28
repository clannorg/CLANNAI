const express = require('express')
const router = express.Router()
const { GoogleGenerativeAI } = require('@google/generative-ai')
const { authenticateToken } = require('../middleware/auth')
const { getGameById } = require('../utils/database')

// Initialize Gemini client
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY)

// Debug endpoint to check server status
router.get('/debug', (req, res) => {
  try {
    const fs = require('fs');
    const path = require('path');
    
    // Try to find .env files
    let envFileInfo = {};
    const possibleEnvPaths = [
      '.env',
      '../.env', 
      '../../.env',
      '/app/.env',
      '/app/backend/.env',
      process.cwd() + '/.env'
    ];
    
    possibleEnvPaths.forEach(envPath => {
      try {
        const fullPath = path.resolve(envPath);
        if (fs.existsSync(fullPath)) {
          const content = fs.readFileSync(fullPath, 'utf8');
          envFileInfo[fullPath] = {
            exists: true,
            size: content.length,
            lines: content.split('\n').length,
            // Show first few chars of each line for debugging (hide sensitive values)
            preview: content.split('\n').slice(0, 10).map(line => {
              if (line.includes('=')) {
                const [key, value] = line.split('=', 2);
                return `${key}=${value ? value.substring(0, 10) + '...' : ''}`;
              }
              return line;
            })
          };
        }
      } catch (e) {
        envFileInfo[envPath] = { error: e.message };
      }
    });

    res.json({
      timestamp: new Date().toISOString(),
      server_status: 'running',
      process_info: {
        cwd: process.cwd(),
        node_version: process.version,
        platform: process.platform
      },
      environment: {
        node_env: process.env.NODE_ENV,
        gemini_key_exists: !!process.env.GEMINI_API_KEY,
        gemini_key_length: process.env.GEMINI_API_KEY?.length,
        gemini_key_start: process.env.GEMINI_API_KEY?.substring(0, 10),
        cors_origin: process.env.CORS_ORIGIN,
        port: process.env.PORT
      },
      env_files_found: envFileInfo,
      dependencies: {
        google_ai_loaded: !!require('@google/generative-ai'),
        express_loaded: !!require('express')
      }
    });
  } catch (error) {
    res.status(500).json({
      error: 'Debug endpoint failed',
      message: error.message,
      stack: error.stack
    });
  }
})

// Chat with AI about a specific game
router.post('/game/:gameId', authenticateToken, async (req, res) => {
  console.log(`🤖 AI Chat request for game: ${req.params.gameId}`)
  
  try {
    const { gameId } = req.params
    const { message, chatHistory = [], systemPrompt } = req.body

    console.log(`🤖 Message received: ${message}`)
    console.log(`🤖 Chat history length: ${chatHistory.length}`)

    if (!message) {
      console.log('❌ No message provided')
      return res.status(400).json({ error: 'Message is required' })
    }

    // Get game details with events
    console.log(`🎮 Fetching game data for: ${gameId}`)
    const game = await getGameById(gameId)
    
    if (!game) {
      console.log('❌ Game not found in database')
      return res.status(404).json({ error: 'Game not found' })
    }
    console.log(`✅ Game found: ${game.team_name} vs ${game.opponent_name}`)
    
    // Parse events from ai_analysis
    let events = []
    if (game.ai_analysis) {
      events = Array.isArray(game.ai_analysis) 
        ? game.ai_analysis 
        : (game.ai_analysis.events || [])
    }
    console.log(`📊 Events parsed: ${events.length} events`)

    // Parse tactical analysis
    let tacticalAnalysis = null
    let tacticalContext = ''
    if (game.tactical_analysis) {
      tacticalAnalysis = game.tactical_analysis
      
      // Enhanced tactical context for AI
      if (tacticalAnalysis.analysis) {
        if (tacticalAnalysis.analysis.match_overview) {
          const overview = tacticalAnalysis.analysis.match_overview
          tacticalContext += `\n\nMatch Overview:
- Final Score: ${overview.final_score}
- Total Goals: ${overview.total_goals}
- Total Shots: ${overview.total_shots}
- Winning Team: ${overview.winning_team}
- Key Story: ${overview.key_tactical_story}`
        }

        if (tacticalAnalysis.analysis.manager_recommendations?.red_team) {
          tacticalContext += `\n\nCoach Recommendations for Red Team:`
          tacticalAnalysis.analysis.manager_recommendations.red_team.forEach((rec, i) => {
            tacticalContext += `\n${i + 1}. ${rec}`
          })
        }

        if (tacticalAnalysis.analysis.key_moments) {
          tacticalContext += `\n\nKey Moments:`
          tacticalAnalysis.analysis.key_moments.forEach((moment, i) => {
            tacticalContext += `\n${i + 1}. ${Math.floor(moment.timestamp / 60)}:${(moment.timestamp % 60).toString().padStart(2, '0')} - ${moment.description}`
            if (moment.tactical_significance) {
              tacticalContext += `\n   Tactical Significance: ${moment.tactical_significance}`
            }
          })
        }
      }

      // Include team-specific tactical analysis  
      if (tacticalAnalysis.tactical?.red_team) {
        try {
          const redTeamData = JSON.parse(tacticalAnalysis.tactical.red_team.content)
          tacticalContext += `\n\nRed Team Analysis:`
          if (redTeamData.strengths) {
            tacticalContext += `\nStrengths: ${redTeamData.strengths.join(', ')}`
          }
          if (redTeamData.weaknesses) {
            tacticalContext += `\nAreas for Improvement: ${redTeamData.weaknesses.join(', ')}`
          }
          if (redTeamData.shot_accuracy) {
            tacticalContext += `\nShooting Analysis: ${redTeamData.shot_accuracy}`
          }
        } catch (e) {
          // Fallback to raw content if parsing fails
          tacticalContext += `\n\nRed Team Analysis: ${tacticalAnalysis.tactical.red_team.content.slice(0, 300)}...`
        }
      }
    }

    // Calculate game statistics
    const stats = {
      totalEvents: events.length,
      goals: events.filter(e => e.type === 'goal').length,
      shots: events.filter(e => e.type === 'shot').length,
      fouls: events.filter(e => e.type === 'foul').length,
      cards: events.filter(e => e.type === 'yellow_card' || e.type === 'red_card').length,
      redTeamGoals: events.filter(e => e.type === 'goal' && e.team === 'red').length,
      blackTeamGoals: events.filter(e => e.type === 'goal' && e.team === 'black').length,
    }

    // Tactical context is already built above - use the enhanced version

    // Build context for AI
    const gameContext = `
Game Information:
- Title: ${game.title}
- Team: ${game.team_name}
- Duration: ${Math.floor(game.duration / 60)} minutes
- Status: ${game.status}

Match Statistics:
- Total Events: ${stats.totalEvents}
- Goals: ${stats.goals} (Red: ${stats.redTeamGoals}, Black: ${stats.blackTeamGoals})
- Shots: ${stats.shots}
- Fouls: ${stats.fouls}
- Cards: ${stats.cards}

Recent Events:
${events.slice(-10).map(event => 
  `- ${Math.floor(event.timestamp / 60)}:${(event.timestamp % 60).toString().padStart(2, '0')} - ${event.type}${event.team ? ` (${event.team} team)` : ''}${event.description ? `: ${event.description}` : ''}${event.player ? ` by ${event.player}` : ''}`
).join('\n')}${tacticalContext}
    `

    // Use coach-specific system prompt or default
    const defaultSystemPrompt = `You are an AI football analyst and coach assistant. You have access to detailed game data, events, and tactical analysis. Provide helpful analysis, tactical insights, and coaching advice based on the comprehensive game context provided. Be specific and reference actual events, tactical insights, and analysis when possible.

Current Game Context:
${gameContext}

Guidelines:
- Provide tactical analysis and coaching insights
- Reference specific events, tactical insights, and analysis data when relevant  
- Suggest improvements or highlight positive plays based on the tactical analysis
- Answer questions about training priorities, team strengths/weaknesses, and opponent analysis
- Be encouraging but constructive
- Keep responses concise but informative
- Focus on actionable advice for players and coaches
- When tactical analysis is available, use it to give deeper context to your advice`

    const finalSystemPrompt = systemPrompt ? `${systemPrompt}

Current Game Context:
${gameContext}` : defaultSystemPrompt

    // Build conversation history for Gemini
    let conversationText = finalSystemPrompt + '\n\n'
    
    // Add chat history
    chatHistory.forEach(msg => {
      if (msg.role === 'user') {
        conversationText += `Human: ${msg.content}\n\n`
      } else {
        conversationText += `Assistant: ${msg.content}\n\n`
      }
    })

    // Add current message
    conversationText += `Human: ${message}\n\nAssistant: `

    // Get Gemini model and generate response
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" })
    
    const result = await model.generateContent(conversationText)
    const aiResponse = result.response.text()

    res.json({
      response: aiResponse,
      gameStats: stats,
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('AI Chat error:', error)
    res.status(500).json({ 
      error: 'Failed to process chat request',
      details: error.message 
    })
  }
})

module.exports = router 