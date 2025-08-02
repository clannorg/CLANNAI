'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api-client'

interface Game {
  id: string
  title: string
  status: string
  team_name: string
  created_at: string
  tactical_analysis?: {
    tactical: Record<string, { content: string, filename: string, uploaded_at: string }>
    analysis: Record<string, { content: string, filename: string, uploaded_at: string }>
  }
}

interface ManagerInsights {
  match_summary: {
    key_tactical_story: string
    result_factors: string[]
  }
  your_team_analysis: {
    strengths_to_keep: Array<{
      area: string
      evidence: string
      keep_doing: string
    }>
    weaknesses_to_fix: Array<{
      area: string
      evidence: string
      training_focus: string
    }>
  }
  training_priorities: Array<{
    priority: number
    focus: string
    drill: string
    duration: string
    measure: string
  }>
  match_id: string
  generated_at: string
}

interface InsightCard {
  gameId: string
  gameTitle: string
  type: 'summary' | 'strengths' | 'weaknesses' | 'training'
  title: string
  content: string
  count?: number
  color: string
  emoji: string
  trainingVideos?: TrainingVideo[]
}

interface TrainingVideo {
  title: string
  url: string
  duration: string
  description: string
}

// Training video recommendations based on common weaknesses
const getTrainingVideos = (weaknessArea: string): TrainingVideo[] => {
  const area = weaknessArea.toLowerCase()
  
  if (area.includes('set piece') || area.includes('corner') || area.includes('free kick')) {
    return [
      {
        title: "Defending Set Pieces - Zonal vs Man Marking",
        url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        duration: "12:34",
        description: "Master the fundamentals of set piece defending with professional coaching methods"
      },
      {
        title: "Set Piece Organization Drills",
        url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ", 
        duration: "8:45",
        description: "Practical drills to improve your team's set piece defensive shape"
      }
    ]
  }
  
  if (area.includes('passing') || area.includes('possession')) {
    return [
      {
        title: "Possession-Based Passing Drills",
        url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        duration: "15:20",
        description: "Improve your team's passing accuracy and possession retention"
      }
    ]
  }
  
  if (area.includes('defensive') || area.includes('pressing')) {
    return [
      {
        title: "High Intensity Pressing Drills",
        url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        duration: "10:15",
        description: "Coordinate team pressing to win the ball back quickly"
      }
    ]
  }
  
  if (area.includes('attacking') || area.includes('finishing')) {
    return [
      {
        title: "Clinical Finishing Under Pressure",
        url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        duration: "9:30",
        description: "Improve your team's conversion rate with these finishing drills"
      }
    ]
  }
  
  // Default training videos for general improvement
  return [
    {
      title: "Complete Football Training Session",
      url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      duration: "20:45",
      description: "A comprehensive training session covering all aspects of the game"
    }
  ]
}

const DashboardInsights: React.FC = () => {
  const router = useRouter()
  const [insights, setInsights] = useState<InsightCard[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadInsights()
  }, [])

  const loadInsights = async () => {
    try {
      setLoading(true)
      console.log('🔍 Loading dashboard insights...')
      
      // Get all games with tactical analysis
      const gamesResponse = await apiClient.getUserGames() as { games: Game[] }
      const games = gamesResponse.games || []
      console.log('📋 Found games:', games.length, games.map(g => ({ id: g.id, title: g.title, status: g.status })))
      
      const insightCards: InsightCard[] = []
      
      // Process each game for insights
      for (const game of games.slice(0, 10)) { // Limit to recent 10 games
        try {
          console.log(`🎮 Loading game details for: ${game.title} (${game.id})`)
          const gameResponse = await apiClient.getGame(game.id) as { game: Game }
          const fullGame = gameResponse.game
          
          console.log('📊 Game tactical_analysis:', {
            hasAnalysis: !!fullGame.tactical_analysis,
            hasAnalysisObject: !!fullGame.tactical_analysis?.analysis,
            hasManagerInsights: !!fullGame.tactical_analysis?.analysis?.manager_insights,
            keys: fullGame.tactical_analysis ? Object.keys(fullGame.tactical_analysis) : 'none'
          })
          
          if (fullGame.tactical_analysis?.analysis?.manager_insights) {
            console.log('✅ Found manager insights for:', game.title)
            const managerInsights: ManagerInsights = JSON.parse(
              fullGame.tactical_analysis.analysis.manager_insights.content
            )
            
            // Create insight cards from this game
            insightCards.push(
              {
                gameId: game.id,
                gameTitle: game.title,
                type: 'summary',
                title: 'Match Summary',
                content: managerInsights.match_summary.key_tactical_story,
                count: managerInsights.match_summary.result_factors.length,
                color: 'from-blue-900/60 to-blue-800/40 border-blue-500/50',
                emoji: '📊'
              },
              {
                gameId: game.id,
                gameTitle: game.title,
                type: 'strengths',
                title: 'Team Strengths',
                content: managerInsights.your_team_analysis.strengths_to_keep[0]?.area || 'Strengths identified',
                count: managerInsights.your_team_analysis.strengths_to_keep.length,
                color: 'from-green-900/60 to-green-800/40 border-green-500/50',
                emoji: '💪'
              },
              {
                gameId: game.id,
                gameTitle: game.title,
                type: 'weaknesses',
                title: 'Areas to Improve',
                content: managerInsights.your_team_analysis.weaknesses_to_fix[0]?.area || 'Areas to work on',
                count: managerInsights.your_team_analysis.weaknesses_to_fix.length,
                color: 'from-red-900/60 to-red-800/40 border-red-500/50',
                emoji: '⚠️'
              },
              {
                gameId: game.id,
                gameTitle: game.title,
                type: 'training',
                title: 'Training Focus',
                content: managerInsights.training_priorities[0]?.focus || 'Training priorities set',
                count: managerInsights.training_priorities.length,
                color: 'from-purple-900/60 to-purple-800/40 border-purple-500/50',
                emoji: '🏃'
              }
            )
          }
        } catch (error) {
          console.log(`❌ No insights for game ${game.title} (${game.id}):`, error instanceof Error ? error.message : error)
        }
      }
      
      console.log(`📈 Dashboard insights loaded: ${insightCards.length} total insights from ${games.length} games`)
      setInsights(insightCards)
    } catch (error) {
      console.error('❌ Failed to load insights:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInsightClick = (insight: InsightCard) => {
    // Navigate to game with AI coach context
    sessionStorage.setItem('aiCoachContext', JSON.stringify({
      type: insight.title,
      details: insight.content,
      gameTitle: insight.gameTitle,
      timestamp: Date.now()
    }))
    
    router.push(`/games/${insight.gameId}`)
  }

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mb-4"></div>
          <div className="text-gray-400 text-sm">Loading AI insights...</div>
        </div>
      </div>
    )
  }

  if (insights.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 text-center">
        <div className="text-gray-400 mb-4">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-gray-300 mb-2">No AI Insights Yet</h3>
        <p className="text-gray-400">Upload games with analysis to see AI coaching insights here.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">AI Coaching Insights</h2>
        <div className="text-sm text-gray-400">
          {insights.length} insights from recent games
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {insights.map((insight, index) => (
          <div
            key={index}
            className={`bg-gradient-to-br ${insight.color} rounded-xl p-4 hover:scale-105 transition-all duration-300 cursor-pointer shadow-lg hover:shadow-xl`}
            onClick={() => handleInsightClick(insight)}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center mr-2">
                  <span className="text-lg">{insight.emoji}</span>
                </div>
                <div>
                  <h4 className="text-white font-semibold text-sm">{insight.title}</h4>
                  <p className="text-white/70 text-xs">{insight.gameTitle}</p>
                </div>
              </div>
              {insight.count && (
                <div className="bg-white/20 rounded-full px-2 py-1 text-xs text-white">
                  {insight.count}
                </div>
              )}
            </div>
            
            <p className="text-white/90 text-sm line-clamp-2 mb-3">
              {insight.content}
            </p>
            
            <div className="flex items-center text-xs text-white/70">
              <span>Click to analyze with AI Coach</span>
              <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default DashboardInsights