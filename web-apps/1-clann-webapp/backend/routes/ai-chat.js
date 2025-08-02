const express = require('express')
const router = express.Router()
const { GoogleGenerativeAI } = require('@google/generative-ai')
const { Pool } = require('pg')
const { authenticateToken } = require('../middleware/auth')

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
})

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
    const gameQuery = `
      SELECT g.*, t.name as team_name
      FROM games g
      LEFT JOIN teams t ON g.team_id = t.id
      WHERE g.id = $1
    `
    const gameResult = await pool.query(gameQuery, [gameId])
    
    if (gameResult.rows.length === 0) {
      return res.status(404).json({ error: 'Game not found' })
    }

    const game = gameResult.rows[0]
    
    // Parse events from ai_analysis
    let events = []
    if (game.ai_analysis) {
      events = Array.isArray(game.ai_analysis) 
        ? game.ai_analysis 
        : (game.ai_analysis.events || [])
    }

    // Parse tactical analysis
    let tacticalAnalysis = null
    if (game.tactical_analysis) {
      tacticalAnalysis = game.tactical_analysis
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

    // Build tactical context from analysis
    let tacticalContext = ''
    if (tacticalAnalysis) {
      tacticalContext = '\n\nTactical Analysis Available:'
      
      // Add manager insights if available
      if (tacticalAnalysis.analysis && tacticalAnalysis.analysis.manager_insights) {
        try {
          const insights = JSON.parse(tacticalAnalysis.analysis.manager_insights.content)
          tacticalContext += `
          
Match Summary:
- Key Story: ${insights.match_summary.key_tactical_story}
- Result Factors: ${insights.match_summary.result_factors.join(', ')}

Your Team Analysis:
${insights.your_team_analysis.strengths_to_keep.map(s => `- Strength: ${s.area} (${s.evidence})`).join('\n')}
${insights.your_team_analysis.weaknesses_to_fix.map(w => `- Weakness: ${w.area} (${w.evidence}) - Training Focus: ${w.training_focus}`).join('\n')}

Opposition Analysis:
${insights.opposition_analysis.their_threats.map(t => `- Threat: ${t.pattern} - Counter: ${t.how_to_defend}`).join('\n')}
${insights.opposition_analysis.their_weaknesses.map(w => `- Vulnerability: ${w.vulnerability} - Exploit: ${w.how_to_exploit}`).join('\n')}

Training Priorities:
${insights.training_priorities.map(p => `${p.priority}. ${p.focus} - ${p.drill} (${p.duration})`).join('\n')}

Next Match Tactics:
${insights.next_match_tactics.map(t => `- Game Plan: ${t.if_facing_similar_opponent}\n- Set Pieces: ${t.set_piece_focus}\n- Attack Plan: ${t.attacking_plan}`).join('\n')}
          `
        } catch (e) {
          tacticalContext += '\n- Manager insights available but not in structured format'
        }
      }
      
      // Add basic tactical files
      if (tacticalAnalysis.tactical) {
        if (tacticalAnalysis.tactical.match_summary) {
          tacticalContext += `\n\nMatch Summary: ${tacticalAnalysis.tactical.match_summary.content.slice(0, 200)}...`
        }
        if (tacticalAnalysis.tactical.red_team) {
          tacticalContext += `\n\nRed Team Analysis: ${tacticalAnalysis.tactical.red_team.content.slice(0, 200)}...`
        }
        if (tacticalAnalysis.tactical.yellow_team) {
          tacticalContext += `\n\nYellow Team Analysis: ${tacticalAnalysis.tactical.yellow_team.content.slice(0, 200)}...`
        }
      }
    }

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