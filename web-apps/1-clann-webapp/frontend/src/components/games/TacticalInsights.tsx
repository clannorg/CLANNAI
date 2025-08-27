'use client'

import React from 'react'
import { useRouter } from 'next/navigation'
import TrainingRecommendations from './TrainingRecommendations'

interface TacticalData {
  tactical: Record<string, { content: string, filename: string, uploaded_at: string }>
  analysis: Record<string, any>
}

interface Props {
  tacticalData: TacticalData | null
  tacticalLoading: boolean
  gameId: string
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
  opposition_analysis: {
    their_threats: Array<{
      pattern: string
      evidence: string
      how_to_defend: string
    }>
    their_weaknesses: Array<{
      vulnerability: string
      evidence: string
      how_to_exploit: string
    }>
  }
  training_priorities: Array<{
    priority: number
    focus: string
    drill: string
    duration: string
    measure: string
  }>
  next_match_tactics: Array<{
    if_facing_similar_opponent: string
    set_piece_focus: string
    attacking_plan: string
  }>
  match_id: string
  generated_at: string
}

const TacticalInsights: React.FC<Props> = ({ tacticalData, tacticalLoading, gameId }) => {
  const router = useRouter()
  
  // Try to parse structured manager insights JSON
  const getManagerInsights = (): ManagerInsights | null => {
    if (!tacticalData?.analysis?.manager_insights) return null
    
    try {
      return JSON.parse(tacticalData.analysis.manager_insights.content)
    } catch {
      return null
    }
  }

  const managerInsights = getManagerInsights()

  // Navigate to video player with AI coach context
  const handleInsightClick = (context: string, details: string) => {
    // Store the context for AI coach
    sessionStorage.setItem('aiCoachContext', JSON.stringify({
      type: context,
      details,
      timestamp: Date.now()
    }))
    
    // Navigate to video player - we're already on the game page, so we need to scroll up or trigger AI chat
    window.scrollTo({ top: 0, behavior: 'smooth' })
    
    // Trigger AI chat after scroll
    setTimeout(() => {
      // The AI chat will be opened and we can send the context
      const event = new CustomEvent('openAICoachWithContext', { 
        detail: { context, details } 
      })
      window.dispatchEvent(event)
    }, 1000)
  }

  if (tacticalLoading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mb-4"></div>
          <div className="text-gray-400 text-sm">Loading tactical analysis...</div>
        </div>
      </div>
    )
  }

  if (!tacticalData) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 text-center">
        <div className="text-gray-400 mb-4">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-gray-300 mb-2">No Tactical Analysis Available</h3>
        <p className="text-gray-400">Tactical insights will appear here once analysis data is uploaded for this game.</p>
      </div>
    )
  }

  // If we have structured manager insights, show the enhanced view
  if (managerInsights) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Match Summary Card */}
            <div 
              className="bg-gradient-to-br from-blue-900/60 to-blue-800/40 border border-blue-500/50 rounded-xl p-6 hover:bg-gradient-to-br hover:from-blue-800/70 hover:to-blue-700/50 transition-all duration-300 cursor-pointer transform hover:scale-105 hover:shadow-xl"
              onClick={() => handleInsightClick('Match Summary', managerInsights.match_summary.key_tactical_story)}
            >
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-2xl">📊</span>
                </div>
                <h4 className="text-blue-200 font-bold text-lg">Match Summary</h4>
              </div>
              <div className="text-gray-300 text-sm space-y-3">
                <p className="font-medium line-clamp-3">{managerInsights.match_summary.key_tactical_story}</p>
                <div className="text-xs text-blue-300 font-medium">
                  {managerInsights.match_summary.result_factors.length} key factors
                </div>
              </div>
              <div className="mt-4 flex items-center text-xs text-blue-300">
                <span>Click to discuss with AI Coach</span>
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>

            {/* Team Strengths Card */}
            <div 
              className="bg-gradient-to-br from-green-900/60 to-green-800/40 border border-green-500/50 rounded-xl p-6 hover:bg-gradient-to-br hover:from-green-800/70 hover:to-green-700/50 transition-all duration-300 cursor-pointer transform hover:scale-105 hover:shadow-xl"
              onClick={() => handleInsightClick('Team Strengths', managerInsights.your_team_analysis.strengths_to_keep.map(s => s.area).join(', '))}
            >
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-2xl">💪</span>
                </div>
                <h4 className="text-green-200 font-bold text-lg">Strengths</h4>
              </div>
              <div className="text-gray-300 text-sm space-y-2">
                {managerInsights.your_team_analysis.strengths_to_keep.slice(0, 2).map((strength, i) => (
                  <div key={i} className="p-2 bg-green-800/20 rounded">
                    <p className="font-medium text-sm">{strength.area}</p>
                  </div>
                ))}
                <div className="text-xs text-green-300 font-medium">
                  {managerInsights.your_team_analysis.strengths_to_keep.length} strengths identified
                </div>
              </div>
              <div className="mt-4 flex items-center text-xs text-green-300">
                <span>Click to discuss with AI Coach</span>
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>

            {/* Team Weaknesses Card */}
            <div 
              className="bg-gradient-to-br from-red-900/60 to-red-800/40 border border-red-500/50 rounded-xl p-6 hover:bg-gradient-to-br hover:from-red-800/70 hover:to-red-700/50 transition-all duration-300 cursor-pointer transform hover:scale-105 hover:shadow-xl"
              onClick={() => handleInsightClick('Areas to Improve', managerInsights.your_team_analysis.weaknesses_to_fix.map(w => w.area).join(', '))}
            >
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-2xl">⚠️</span>
                </div>
                <h4 className="text-red-200 font-bold text-lg">Areas to Fix</h4>
              </div>
              <div className="text-gray-300 text-sm space-y-2">
                {managerInsights.your_team_analysis.weaknesses_to_fix.slice(0, 2).map((weakness, i) => (
                  <div key={i} className="p-2 bg-red-800/20 rounded">
                    <p className="font-medium text-sm">{weakness.area}</p>
                  </div>
                ))}
                <div className="text-xs text-red-300 font-medium">
                  {managerInsights.your_team_analysis.weaknesses_to_fix.length} areas to improve
                </div>
              </div>
              <div className="mt-4 flex items-center text-xs text-red-300">
                <span>Click to discuss with AI Coach</span>
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>

            {/* Training Drills Card */}
            <div 
              className="bg-gradient-to-br from-purple-900/60 to-purple-800/40 border border-purple-500/50 rounded-xl p-6 hover:bg-gradient-to-br hover:from-purple-800/70 hover:to-purple-700/50 transition-all duration-300 cursor-pointer transform hover:scale-105 hover:shadow-xl"
              onClick={() => handleInsightClick('Training Drills', managerInsights.training_priorities.map(p => p.focus).join(', '))}
            >
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-2xl">🏃</span>
                </div>
                <h4 className="text-purple-200 font-bold text-lg">Training Drills</h4>
              </div>
              <div className="text-gray-300 text-sm space-y-2">
                {managerInsights.training_priorities.slice(0, 2).map((priority, i) => (
                  <div key={i} className="p-2 bg-purple-800/20 rounded">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium text-sm">{priority.focus}</p>
                      <span className="text-purple-300 text-xs">#{priority.priority}</span>
                    </div>
                  </div>
                ))}
                <div className="text-xs text-purple-300 font-medium">
                  {managerInsights.training_priorities.length} training priorities
                </div>
              </div>
              <div className="mt-4 flex items-center text-xs text-purple-300">
                <span>Click to discuss with AI Coach</span>
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
        </div>

        {/* Additional insights in a second row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Opposition Analysis Card */}
            <div 
              className="bg-gradient-to-br from-orange-900/60 to-orange-800/40 border border-orange-500/50 rounded-xl p-6 hover:bg-gradient-to-br hover:from-orange-800/70 hover:to-orange-700/50 transition-all duration-300 cursor-pointer transform hover:scale-105 hover:shadow-xl"
              onClick={() => handleInsightClick('Opposition Analysis', 'Discuss opponent threats and weaknesses')}
            >
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-2xl">🔍</span>
                </div>
                <h4 className="text-orange-200 font-bold text-lg">Opposition Analysis</h4>
              </div>
              <div className="text-gray-300 text-sm space-y-2">
                <div className="p-2 bg-orange-800/20 rounded">
                  <p className="text-orange-300 font-medium text-xs">Threats Identified:</p>
                  <p className="text-sm">{managerInsights.opposition_analysis.their_threats.length}</p>
                </div>
                <div className="p-2 bg-orange-800/20 rounded">
                  <p className="text-orange-300 font-medium text-xs">Weaknesses Found:</p>
                  <p className="text-sm">{managerInsights.opposition_analysis.their_weaknesses.length}</p>
                </div>
              </div>
              <div className="mt-4 flex items-center text-xs text-orange-300">
                <span>Click to discuss with AI Coach</span>
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>

            {/* Next Match Tactics Card */}
            <div 
              className="bg-gradient-to-br from-yellow-900/60 to-yellow-800/40 border border-yellow-500/50 rounded-xl p-6 hover:bg-gradient-to-br hover:from-yellow-800/70 hover:to-yellow-700/50 transition-all duration-300 cursor-pointer transform hover:scale-105 hover:shadow-xl"
              onClick={() => handleInsightClick('Next Match Tactics', 'Discuss tactics for future matches')}
            >
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-2xl">⚡</span>
                </div>
                <h4 className="text-yellow-200 font-bold text-lg">Match Tactics</h4>
              </div>
              <div className="text-gray-300 text-sm space-y-2">
                {managerInsights.next_match_tactics.slice(0, 1).map((tactic, i) => (
                  <div key={i} className="space-y-2">
                    <div className="p-2 bg-yellow-800/20 rounded">
                      <p className="text-yellow-300 font-medium text-xs mb-1">Game Plan Preview:</p>
                      <p className="text-sm line-clamp-2">{tactic.if_facing_similar_opponent}</p>
                    </div>
                  </div>
                ))}
                <div className="text-xs text-yellow-300 font-medium">
                  Tactical recommendations available
                </div>
              </div>
              <div className="mt-4 flex items-center text-xs text-yellow-300">
                <span>Click to discuss with AI Coach</span>
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        </div>
    )
  }

  // Fallback to raw text display for unstructured data
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Red Team Analysis */}
          {tacticalData.tactical.red_team && (
            <div className="bg-red-900/30 border border-red-700/50 rounded-lg p-3">
              <h4 className="text-red-400 font-semibold mb-2 flex items-center text-sm">
                🔴 Red Team Analysis
              </h4>
              <div className="text-gray-300 text-xs max-h-24 overflow-y-auto">
                {tacticalData.tactical.red_team.content.split('\n').slice(0, 5).map((line, i) => (
                  <div key={i} className="mb-1">{line}</div>
                ))}
              </div>
            </div>
          )}

          {/* Yellow Team Analysis */}
          {tacticalData.tactical.yellow_team && (
            <div className="bg-yellow-900/30 border border-yellow-700/50 rounded-lg p-3">
              <h4 className="text-yellow-400 font-semibold mb-2 flex items-center text-sm">
                🟡 Yellow Team Analysis
              </h4>
              <div className="text-gray-300 text-xs max-h-24 overflow-y-auto">
                {tacticalData.tactical.yellow_team.content.split('\n').slice(0, 5).map((line, i) => (
                  <div key={i} className="mb-1">{line}</div>
                ))}
              </div>
            </div>
          )}

          {/* Match Summary */}
          {tacticalData.tactical.match_summary && (
            <div className="bg-blue-900/30 border border-blue-700/50 rounded-lg p-3">
              <h4 className="text-blue-400 font-semibold mb-2 flex items-center text-sm">
                📊 Match Summary
              </h4>
              <div className="text-gray-300 text-xs max-h-24 overflow-y-auto">
                {tacticalData.tactical.match_summary.content.split('\n').slice(0, 5).map((line, i) => (
                  <div key={i} className="mb-1">{line}</div>
                ))}
              </div>
            </div>
          )}

          {/* Timeline Analysis */}
          {tacticalData.analysis.complete_timeline && (
            <div className="bg-purple-900/30 border border-purple-700/50 rounded-lg p-3">
              <h4 className="text-purple-400 font-semibold mb-2 flex items-center text-sm">
                ⏱️ Timeline Analysis
              </h4>
              <div className="text-gray-300 text-xs max-h-24 overflow-y-auto">
                {tacticalData.analysis.complete_timeline.content.split('\n').slice(0, 5).map((line, i) => (
                  <div key={i} className="mb-1">{line}</div>
                ))}
              </div>
            </div>
          )}

          {/* Accuracy Comparison */}
          {tacticalData.analysis.accuracy_comparison && (
            <div className="bg-orange-900/30 border border-orange-700/50 rounded-lg p-3">
              <h4 className="text-orange-400 font-semibold mb-2 flex items-center text-sm">
                🎯 Accuracy Analysis
              </h4>
              <div className="text-gray-300 text-xs max-h-24 overflow-y-auto">
                {tacticalData.analysis.accuracy_comparison.content.split('\n').slice(0, 5).map((line, i) => (
                  <div key={i} className="mb-1">{line}</div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Training Recommendations Section */}
        <div className="mt-4">
          <TrainingRecommendations gameId={gameId} />
        </div>
    </div>
  )
}

export default TacticalInsights