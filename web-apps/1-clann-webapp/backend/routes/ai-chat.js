const express = require('express')
const router = express.Router()
const { GoogleGenerativeAI } = require('@google/generative-ai')
const { authenticateToken } = require('../middleware/auth')
const { getGameById } = require('../utils/database')

// Initialize Gemini client
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY)

// Chat with AI about a specific game
router.post('/game/:gameId', authenticateToken, async (req, res) => {
  try {
    const { gameId } = req.params
    const { message, chatHistory = [] } = req.body

    if (!message) {
      return res.status(400).json({ error: 'Message is required' })
    }

    // Get game details with events
    const game = await getGameById(gameId)
    
    if (!game) {
      return res.status(404).json({ error: 'Game not found' })
    }
    
    // Parse events from ai_analysis
    let events = []
    if (game.ai_analysis) {
      events = Array.isArray(game.ai_analysis) 
        ? game.ai_analysis 
        : (game.ai_analysis.events || [])
    }

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

    const systemPrompt = `You are an AI football analyst and coach assistant. You have access to detailed game data, events, and tactical analysis. Provide helpful analysis, tactical insights, and coaching advice based on the comprehensive game context provided. Be specific and reference actual events, tactical insights, and analysis when possible.

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

    // Build conversation history for Gemini
    let conversationText = systemPrompt + '\n\n'
    
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
    const model = genAI.getGenerativeModel({ model: "gemini-2.5-pro" })
    
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