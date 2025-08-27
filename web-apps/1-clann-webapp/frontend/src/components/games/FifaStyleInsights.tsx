'use client'

import React, { useState } from 'react'
import TrainingRecommendations from './TrainingRecommendations'

interface TacticalData {
  tactical: Record<string, { content: string, filename: string, uploaded_at: string }>
  analysis: Record<string, any>
}

interface Props {
  tacticalData: TacticalData | null
  tacticalLoading: boolean
  gameId: string
  onSeekToTimestamp?: (timestampInSeconds: number) => void
  game?: {
    id: string
    title: string
    ai_analysis?: any[]
    metadata?: {
      teams?: {
        red_team: { name: string, jersey_color: string }
        blue_team: { name: string, jersey_color: string }
      }
    }
  }
}

interface EvidenceBasedStat {
  label: string
  value: string | number
  evidence: Array<{
    timestamp: number
    description: string
    type: string
  }>
  color: string
}

export default function FifaStyleInsights({ tacticalData, tacticalLoading, gameId, onSeekToTimestamp, game }: Props) {
  console.log('🎮 FifaStyleInsights rendered with gameId:', gameId);
  // Extract evidence-based stats from game events
  const extractEvidenceStats = (events: any[]): EvidenceBasedStat[] => {
    if (!events || !Array.isArray(events)) return []
    
    const stats: EvidenceBasedStat[] = []
    
    // Goals with evidence
    const goals = events.filter(e => e.type === 'goal')
    if (goals.length > 0) {
      stats.push({
        label: 'Goals Scored',
        value: goals.length,
        evidence: goals.map(g => ({
          timestamp: g.timestamp,
          description: g.description || `Goal scored by ${g.team} team`,
          type: g.type
        })),
        color: 'text-green-400'
      })
    }
    
    // Shots with evidence
    const shots = events.filter(e => e.type === 'shot')
    if (shots.length > 0) {
      const accuracy = goals.length > 0 ? Math.round((goals.length / shots.length) * 100) : 0
      stats.push({
        label: 'Shot Accuracy',
        value: `${accuracy}% (${goals.length}/${shots.length})`,
        evidence: shots.map(s => ({
          timestamp: s.timestamp,
          description: s.description || `Shot attempt by ${s.team} team`,
          type: s.type
        })),
        color: 'text-blue-400'
      })
    }
    
    // Fouls with evidence
    const fouls = events.filter(e => e.type === 'foul')
    if (fouls.length > 0) {
      stats.push({
        label: 'Fouls Committed',
        value: fouls.length,
        evidence: fouls.map(f => ({
          timestamp: f.timestamp,
          description: f.description || `Foul by ${f.team} team`,
          type: f.type
        })),
        color: 'text-red-400'
      })
    }
    
    // Cards with evidence
    const cards = events.filter(e => e.type === 'yellow_card' || e.type === 'red_card')
    if (cards.length > 0) {
      stats.push({
        label: 'Cards Received',
        value: cards.length,
        evidence: cards.map(c => ({
          timestamp: c.timestamp,
          description: c.description || `${c.type.replace('_', ' ')} for ${c.team} team`,
          type: c.type
        })),
        color: 'text-yellow-400'
      })
    }
    
    // Turnovers with evidence
    const turnovers = events.filter(e => e.type === 'turnover')
    if (turnovers.length > 0) {
      stats.push({
        label: 'Turnovers',
        value: turnovers.length,
        evidence: turnovers.map(t => ({
          timestamp: t.timestamp,
          description: t.description || `Turnover by ${t.team} team`,
          type: t.type
        })),
        color: 'text-purple-400'
      })
    }
    
    return stats
  }

  // Extract team-specific stats
  const extractTeamStats = (events: any[], teamName: string): EvidenceBasedStat[] => {
    if (!events || !Array.isArray(events)) return []
    
    // Filter events for this team (handle various team name formats)
    const teamEvents = events.filter(e => {
      const eventTeam = e.team?.toLowerCase() || ''
      const targetTeam = teamName.toLowerCase()
      return eventTeam.includes(targetTeam) || 
             eventTeam === 'red' && targetTeam.includes('red') ||
             eventTeam === 'blue' && targetTeam.includes('blue') ||
             eventTeam === 'white' && targetTeam.includes('white') ||
             eventTeam === 'black' && targetTeam.includes('black')
    })
    
    const stats: EvidenceBasedStat[] = []
    
    // Team goals
    const teamGoals = teamEvents.filter(e => e.type === 'goal')
    if (teamGoals.length > 0) {
      stats.push({
        label: 'Goals',
        value: teamGoals.length,
        evidence: teamGoals.map(g => ({
          timestamp: g.timestamp,
          description: g.description || `Goal scored`,
          type: g.type
        })),
        color: 'text-green-400'
      })
    }
    
    // Team fouls
    const teamFouls = teamEvents.filter(e => e.type === 'foul')
    if (teamFouls.length > 0) {
      stats.push({
        label: 'Fouls',
        value: teamFouls.length,
        evidence: teamFouls.map(f => ({
          timestamp: f.timestamp,
          description: f.description || `Foul committed`,
          type: f.type
        })),
        color: 'text-red-400'
      })
    }
    
    // Team shots
    const teamShots = teamEvents.filter(e => e.type === 'shot')
    if (teamShots.length > 0) {
      stats.push({
        label: 'Shots',
        value: teamShots.length,
        evidence: teamShots.map(s => ({
          timestamp: s.timestamp,
          description: s.description || `Shot attempt`,
          type: s.type
        })),
        color: 'text-blue-400'
      })
    }
    
    return stats
  }

  // Helper function to parse JSON content if it's a string
  const parseContent = (content: any) => {
    if (typeof content === 'string') {
      try {
        return JSON.parse(content)
      } catch {
        return content
      }
    }
    return content
  }

  if (tacticalLoading) {
    return (
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-6">
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-400"></div>
          <span className="text-gray-300 text-sm">Loading tactical analysis...</span>
        </div>
      </div>
    )
  }

  if (!tacticalData?.tactical && !tacticalData?.analysis) {
    return (
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-8 text-center">
        <div className="text-gray-500 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-300 mb-2">No Tactical Analysis Available</h3>
        <p className="text-gray-500 text-sm">
          Tactical insights will appear here once analysis data is uploaded for this game.
        </p>
      </div>
    )
  }

  // Extract evidence-based stats from game events
  const gameEvents = Array.isArray(game?.ai_analysis) 
    ? game.ai_analysis 
    : (game?.ai_analysis?.events || [])
  
  // Get the user's team (the team that owns this game)
  const userTeamName = game?.team_name || ''
  const userTeamColor = game?.team_color || '#016F32'
  
  // Get user's team color from metadata for reliable matching
  const getUserTeamColor = () => {
    // Check if metadata has team mapping
    if (game?.metadata?.teams) {
      const { red_team, blue_team } = game.metadata.teams
      
      // Match user's team name to red/blue team
      if (red_team?.name?.toLowerCase().includes(userTeamName.toLowerCase()) ||
          userTeamName.toLowerCase().includes(red_team?.name?.toLowerCase() || '')) {
        return 'red'
      }
      if (blue_team?.name?.toLowerCase().includes(userTeamName.toLowerCase()) ||
          userTeamName.toLowerCase().includes(blue_team?.name?.toLowerCase() || '')) {
        return 'blue'
      }
    }
    
    // Fallback: try to infer from team name
    const teamLower = userTeamName.toLowerCase()
    if (teamLower.includes('red') || teamLower.includes('home')) return 'red'
    if (teamLower.includes('blue') || teamLower.includes('away')) return 'blue'
    if (teamLower.includes('white')) return 'white'
    if (teamLower.includes('black')) return 'black'
    
    // Default to red (often the home team)
    return 'red'
  }
  
  const userTeamColorIdentifier = getUserTeamColor()
  
  // Filter events to show only the user's team performance (by color)
  const userTeamEvents = gameEvents.filter(event => {
    if (!event.team) return false
    const eventTeam = event.team.toLowerCase()
    
    // Match by color identifier (most reliable)
    return eventTeam === userTeamColorIdentifier ||
           // Fallback to name matching for legacy data
           eventTeam.includes(userTeamName.toLowerCase()) ||
           userTeamName.toLowerCase().includes(eventTeam)
  })
  
  const evidenceStats = extractEvidenceStats(userTeamEvents)

  // Parse the raw tactical data to extract structured insights
  let matchOverview = null
  let redTeamData = null
  let blueTeamData = null
  let managerRecommendations: any = null
  let keyMoments: any[] = []

  // Extract data from tactical analysis - focus on user's team
  let userTeamTacticalData = null
  
  if (tacticalData.tactical?.red_team) {
    try {
      const redTeamContent = parseContent(tacticalData.tactical.red_team.content)
      redTeamData = redTeamContent
      
      // Check if red team matches user's team
      const redTeamName = redTeamContent?.team_name || 'red team'
      if (redTeamName.toLowerCase().includes(userTeamName.toLowerCase()) || 
          userTeamName.toLowerCase().includes(redTeamName.toLowerCase())) {
        userTeamTacticalData = redTeamContent
      }
    } catch (e) {
      console.log('Failed to parse red team data:', e)
    }
  }

  if (tacticalData.tactical?.blue_team) {
    try {
      const blueTeamContent = parseContent(tacticalData.tactical.blue_team.content)
      blueTeamData = blueTeamContent
      
      // Check if blue team matches user's team
      const blueTeamName = blueTeamContent?.team_name || 'blue team'
      if (blueTeamName.toLowerCase().includes(userTeamName.toLowerCase()) || 
          userTeamName.toLowerCase().includes(blueTeamName.toLowerCase())) {
        userTeamTacticalData = blueTeamContent
      }
    } catch (e) {
      console.log('Failed to parse blue team data:', e)
    }
  }
  
  // If we can't match by name, default to red team (often the home/main team)
  if (!userTeamTacticalData && redTeamData) {
    userTeamTacticalData = redTeamData
  }

  // Extract data from analysis section
  if (tacticalData.analysis) {
    matchOverview = tacticalData.analysis.match_overview
    managerRecommendations = tacticalData.analysis.manager_recommendations
    keyMoments = tacticalData.analysis.key_moments || []
  }
  // Normalize manager recommendations shape
  const normalizeRecommendations = (value: any): string[] => {
    if (!value) return []
    if (Array.isArray(value)) return value
    if (typeof value === 'string') return [value]
    if (typeof value === 'object') {
      const flat: string[] = []
      Object.values(value).forEach((section: any) => {
        if (!section) return
        if (Array.isArray(section)) {
          section.forEach((item) => {
            if (typeof item === 'string') flat.push(item)
          })
        } else if (typeof section === 'string') {
          flat.push(section)
        }
      })
      return flat
    }
    return []
  }

  // Get recommendations for user's team
  const userTeamRecommendations: string[] = normalizeRecommendations(
    managerRecommendations?.red_team || managerRecommendations?.blue_team || managerRecommendations
  )

  // Normalize list items that could be strings or rich objects {title, description, ...}
  const normalizeDetailList = (list: any): string[] => {
    if (!Array.isArray(list)) return []
    return list.map((item: any) => {
      if (typeof item === 'string') return item
      if (item && typeof item === 'object') {
        const title = item.title || ''
        const desc = item.description || ''
        return [title, desc].filter(Boolean).join(' — ')
      }
      return String(item)
    })
  }

  return (
    <div className="space-y-6">
      {/* Evidence-Based Stats Cards */}
      {evidenceStats.length > 0 && (
        <div className="bg-gradient-to-br from-indigo-900/30 to-purple-900/30 border border-indigo-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center mb-4">
            <div 
              className="w-4 h-4 rounded-full mr-3" 
              style={{ backgroundColor: userTeamColor }}
            ></div>
            <h3 className="text-xl font-bold text-white">
              📊 {userTeamName} Performance with Evidence
            </h3>
          </div>
          
          <div className="space-y-3">
            {evidenceStats.map((stat, index) => {
              const [isExpanded, setIsExpanded] = useState(false)
              
              return (
                <div key={index} className="bg-black/20 rounded-lg overflow-hidden hover:bg-black/30 transition-colors">
                  {/* Stat Header - Always Visible */}
                  <div className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <h4 className={`font-semibold ${stat.color}`}>{stat.label}</h4>
                        <span className="text-white text-xl font-bold">{stat.value}</span>
                      </div>
                      
                      <button
                        onClick={() => setIsExpanded(!isExpanded)}
                        className="flex items-center space-x-2 px-3 py-1.5 bg-indigo-500/20 hover:bg-indigo-500/30 rounded-lg transition-colors text-sm"
                      >
                        <span className="text-indigo-300">
                          {stat.evidence.length} evidence
                        </span>
                        <svg 
                          className={`w-4 h-4 text-indigo-300 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                    </div>
                  </div>
                  
                  {/* Evidence Details - Expandable */}
                  {isExpanded && (
                    <div className="px-4 pb-4 border-t border-gray-700/50">
                      <div className="pt-3 space-y-2">
                        {stat.evidence.map((evidence, i) => (
                          <button
                            key={i}
                            onClick={() => onSeekToTimestamp?.(evidence.timestamp)}
                            className="w-full text-left p-3 bg-gray-800/50 hover:bg-gray-700/50 rounded-lg transition-colors group"
                            title="Click to jump to this moment"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-indigo-400 font-mono text-sm font-medium">
                                {Math.floor(evidence.timestamp / 60)}:{(evidence.timestamp % 60).toString().padStart(2, '0')}
                              </span>
                              <div className="flex items-center space-x-1 text-gray-400 group-hover:text-indigo-400 transition-colors">
                                <span className="text-xs">Jump to moment</span>
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m6-7a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                              </div>
                            </div>
                            <p className="text-gray-300 text-sm leading-relaxed">
                              {evidence.description}
                            </p>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* FIFA-Style Match Overview Header */}
      {matchOverview && (
        <div className="bg-gradient-to-r from-green-900/50 to-blue-900/50 border border-green-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-white flex items-center">
              ⚽ Match Analysis
            </h2>
            <div className="bg-black/30 px-4 py-2 rounded-lg">
              <span className="text-green-400 font-mono text-lg">{matchOverview.final_score}</span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-black/20 rounded-lg p-3 text-center">
              <div className="text-white text-lg font-semibold">{matchOverview.total_goals}</div>
              <div className="text-gray-300 text-sm">Goals</div>
            </div>
            <div className="bg-black/20 rounded-lg p-3 text-center">
              <div className="text-white text-lg font-semibold">{matchOverview.total_shots}</div>
              <div className="text-gray-300 text-sm">Total Shots</div>
            </div>
            <div className="bg-black/20 rounded-lg p-3 text-center">
              <div className="text-green-400 text-lg font-semibold">🏆</div>
              <div className="text-gray-300 text-sm">{matchOverview.winning_team} team</div>
            </div>
          </div>

          <div className="bg-black/20 rounded-lg p-4">
            <h3 className="text-green-400 font-semibold mb-2">📖 Match Story</h3>
            <p className="text-gray-200 text-sm leading-relaxed">{matchOverview.key_tactical_story}</p>
          </div>
        </div>
      )}

      {/* User's Team Tactical Analysis */}
      {userTeamTacticalData && (
        <div 
          className="bg-gradient-to-br from-gray-900/30 to-gray-800/20 border rounded-xl p-6 backdrop-blur-sm"
          style={{ 
            borderColor: `${userTeamColor}30`,
            backgroundImage: `linear-gradient(135deg, ${userTeamColor}10, ${userTeamColor}05)`
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div 
                className="w-4 h-4 rounded-full mr-3" 
                style={{ backgroundColor: userTeamColor }}
              ></div>
              <h3 className="text-xl font-bold text-white">
                {userTeamTacticalData?.team_name || userTeamName} Tactical Analysis
              </h3>
            </div>
            {/* Final Score Display */}
            {tacticalData?.analysis?.match_summary?.final_score && (
              <div className="bg-black/40 px-4 py-2 rounded-lg border border-green-500/30">
                <div className="text-green-400 font-mono text-lg font-bold">
                  {tacticalData.analysis.match_summary.final_score}
                </div>
                <div className="text-gray-400 text-xs text-center">Final Score</div>
              </div>
            )}
          </div>

          {/* Team-specific evidence stats */}
          {(() => {
            const teamStats = extractTeamStats(userTeamEvents, userTeamName)
            return teamStats.length > 0 && (
              <div className="mb-6">
                <h4 className="font-semibold mb-3 flex items-center" style={{ color: userTeamColor }}>
                  📊 Performance Evidence
                </h4>
                <div className="space-y-2">
                  {teamStats.map((stat, i) => (
                    <div key={i} className="bg-black/30 rounded-lg p-3 flex items-center justify-between hover:bg-black/40 transition-colors">
                      <div className="flex items-center space-x-3">
                        <span className={`text-lg font-bold ${stat.color}`}>{stat.value}</span>
                        <span className="text-gray-300 text-sm">{stat.label}</span>
                      </div>
                      <button
                        onClick={() => stat.evidence.length > 0 && onSeekToTimestamp?.(stat.evidence[0].timestamp)}
                        className="text-xs transition-colors px-2 py-1 rounded"
                        style={{ 
                          color: userTeamColor,
                          backgroundColor: `${userTeamColor}20`,
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = `${userTeamColor}30`}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = `${userTeamColor}20`}
                        title="Jump to first evidence"
                      >
                        {stat.evidence.length} evidence →
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )
          })()}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths */}
            <div className="bg-black/20 rounded-lg p-4">
              <h4 className="text-green-400 font-semibold mb-3 flex items-center">
                💪 Strengths
              </h4>
              <div className="space-y-2">
                {normalizeDetailList(userTeamTacticalData.strengths)?.map((strength: string, i: number) => (
                  <div key={i} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-200 text-sm">{strength}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Areas for Improvement */}
            <div className="bg-black/20 rounded-lg p-4">
              <h4 className="text-yellow-400 font-semibold mb-3 flex items-center">
                ⚠️ Areas to Improve
              </h4>
              <div className="space-y-2">
                {normalizeDetailList(userTeamTacticalData.weaknesses)?.map((weakness: string, i: number) => (
                  <div key={i} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-200 text-sm">{weakness}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Key Players Section */}
          {userTeamTacticalData.key_players && (
            <div className="mt-4 bg-black/20 rounded-lg p-4">
              <h4 className="text-blue-400 font-semibold mb-3 flex items-center">
                👥 Key Players
              </h4>
              <div className="space-y-2">
                {normalizeDetailList(userTeamTacticalData.key_players)?.map((player: string, i: number) => (
                  <div key={i} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-200 text-sm">{player}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tactical Setup */}
          {userTeamTacticalData.tactical_setup && (
            <div className="mt-4 bg-black/20 rounded-lg p-4">
              <h4 className="text-purple-400 font-semibold mb-3 flex items-center">
                ⚽ Tactical Setup
              </h4>
              <p className="text-gray-200 text-sm">{userTeamTacticalData.tactical_setup}</p>
            </div>
          )}

          {/* Performance Summary */}
          {userTeamTacticalData.performance_summary && (
            <div className="mt-4 bg-black/20 rounded-lg p-4">
              <h4 className="text-green-400 font-semibold mb-3 flex items-center">
                📈 Performance Summary
              </h4>
              <p className="text-gray-200 text-sm">{userTeamTacticalData.performance_summary}</p>
            </div>
          )}

          {/* Shot Accuracy */}
          {userTeamTacticalData.shot_accuracy && (
            <div className="mt-4 bg-black/20 rounded-lg p-4">
              <h4 className="text-blue-400 font-semibold mb-2 flex items-center">
                🎯 Shooting Analysis
              </h4>
              <p className="text-gray-200 text-sm">{userTeamTacticalData.shot_accuracy}</p>
            </div>
          )}
        </div>
      )}

      {/* AI Coach Recommendations for User's Team */}
      {userTeamRecommendations.length > 0 && (
        <div 
          className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 border border-purple-500/30 rounded-xl p-6 backdrop-blur-sm"
        >
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center mr-3">
              <span className="text-white text-sm font-bold">🧠</span>
            </div>
            <h3 className="text-xl font-bold text-white">
              AI Coach Recommendations for {userTeamName}
            </h3>
          </div>

          <div className="space-y-3">
            {userTeamRecommendations.map((recommendation: string, i: number) => (
              <div key={i} className="bg-black/20 rounded-lg p-4 flex items-start space-x-3">
                <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-xs font-bold">{i + 1}</span>
                </div>
                <span className="text-gray-200 text-sm">{recommendation}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Key Moments */}
      {keyMoments.length > 0 && (
        <div className="bg-gradient-to-br from-yellow-900/30 to-yellow-800/20 border border-yellow-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center mb-4">
            <div className="w-4 h-4 bg-yellow-500 rounded-full mr-3"></div>
            <h3 className="text-xl font-bold text-white">Key Moments</h3>
          </div>

          <div className="space-y-4">
            {keyMoments.map((moment: any, i: number) => (
              <div key={i} className="bg-black/20 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <button
                    onClick={() => onSeekToTimestamp?.(moment.timestamp)}
                    className="text-yellow-400 font-mono hover:text-yellow-300 hover:bg-yellow-500/10 px-2 py-1 rounded transition-all duration-200 cursor-pointer flex items-center space-x-1"
                    title="Click to jump to this moment in the video"
                  >
                    <span>
                      {Math.floor(moment.timestamp / 60)}:{(moment.timestamp % 60).toString().padStart(2, '0')}
                    </span>
                    <svg className="w-3 h-3 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m6-7a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>
                  <span className="text-gray-400 text-xs">Match Moment</span>
                </div>
                <p className="text-gray-200 text-sm mb-2">{moment.description}</p>
                {moment.tactical_significance && (
                  <p className="text-gray-300 text-xs italic">{moment.tactical_significance}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Training Recommendations Section */}
      <div className="mt-6">
        <TrainingRecommendations gameId={gameId} />
      </div>
    </div>
  )
}