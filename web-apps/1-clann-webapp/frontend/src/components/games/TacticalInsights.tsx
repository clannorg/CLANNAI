'use client'

import React from 'react'

interface TacticalData {
  tactical: Record<string, { content: string, filename: string, uploaded_at: string }>
  analysis: Record<string, { content: string, filename: string, uploaded_at: string }>
}

interface Props {
  tacticalData: TacticalData | null
  tacticalLoading: boolean
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

const TacticalInsights: React.FC<Props> = ({ tacticalData, tacticalLoading }) => {
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

  if (tacticalLoading) {
    return (
      <div className="absolute bottom-0 left-0 right-0 max-h-40 bg-black/95 backdrop-blur-sm border-t border-gray-700 overflow-y-auto">
        <div className="p-4">
          <h3 className="text-white text-lg font-bold mb-4 flex items-center">
            🧠 Game Insights
          </h3>
          <div className="text-gray-400 text-sm">Loading tactical analysis...</div>
        </div>
      </div>
    )
  }

  if (!tacticalData) {
    return (
      <div className="absolute bottom-0 left-0 right-0 max-h-40 bg-black/95 backdrop-blur-sm border-t border-gray-700 overflow-y-auto">
        <div className="p-4">
          <h3 className="text-white text-lg font-bold mb-4 flex items-center">
            🧠 Game Insights
          </h3>
          <div className="text-gray-500 text-sm">No tactical analysis available for this game.</div>
        </div>
      </div>
    )
  }

  // If we have structured manager insights, show the enhanced view
  if (managerInsights) {
    return (
      <div className="absolute bottom-0 left-0 right-0 max-h-96 bg-black/95 backdrop-blur-sm border-t border-gray-700 overflow-y-auto">
        <div className="p-4">
          <h3 className="text-white text-lg font-bold mb-4 flex items-center">
            🧠 Game Insights
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Match Summary Card */}
            <div className="bg-blue-900/30 border border-blue-700/50 rounded-lg p-4">
              <h4 className="text-blue-400 font-semibold mb-3 flex items-center text-sm">
                📊 Match Summary
              </h4>
              <div className="text-gray-300 text-xs space-y-2">
                <p className="font-medium">{managerInsights.match_summary.key_tactical_story}</p>
                <div>
                  <p className="text-blue-300 font-medium mb-1">Key Factors:</p>
                  <ul className="list-disc list-inside space-y-1">
                    {managerInsights.match_summary.result_factors.map((factor, i) => (
                      <li key={i}>{factor}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Your Team Card */}
            <div className="bg-green-900/30 border border-green-700/50 rounded-lg p-4">
              <h4 className="text-green-400 font-semibold mb-3 flex items-center text-sm">
                🎯 Your Team Analysis
              </h4>
              <div className="text-gray-300 text-xs space-y-3">
                {/* Strengths */}
                <div>
                  <p className="text-green-300 font-medium mb-2">✅ Strengths to Keep:</p>
                  {managerInsights.your_team_analysis.strengths_to_keep.map((strength, i) => (
                    <div key={i} className="mb-2 p-2 bg-green-800/20 rounded">
                      <p className="font-medium">{strength.area}</p>
                      <p className="text-xs text-gray-400 mt-1">{strength.evidence}</p>
                    </div>
                  ))}
                </div>
                
                {/* Weaknesses */}
                <div>
                  <p className="text-red-300 font-medium mb-2">⚠️ Areas to Fix:</p>
                  {managerInsights.your_team_analysis.weaknesses_to_fix.map((weakness, i) => (
                    <div key={i} className="mb-2 p-2 bg-red-800/20 rounded">
                      <p className="font-medium">{weakness.area}</p>
                      <p className="text-xs text-gray-400 mt-1">{weakness.evidence}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Opposition Analysis Card */}
            <div className="bg-red-900/30 border border-red-700/50 rounded-lg p-4">
              <h4 className="text-red-400 font-semibold mb-3 flex items-center text-sm">
                🔍 Opposition Analysis
              </h4>
              <div className="text-gray-300 text-xs space-y-3">
                {/* Their Threats */}
                <div>
                  <p className="text-red-300 font-medium mb-2">⚡ Their Threats:</p>
                  {managerInsights.opposition_analysis.their_threats.map((threat, i) => (
                    <div key={i} className="mb-2 p-2 bg-red-800/20 rounded">
                      <p className="font-medium">{threat.pattern}</p>
                      <p className="text-xs text-gray-400 mt-1">{threat.how_to_defend}</p>
                    </div>
                  ))}
                </div>
                
                {/* Their Weaknesses */}
                <div>
                  <p className="text-orange-300 font-medium mb-2">🎯 Their Weaknesses:</p>
                  {managerInsights.opposition_analysis.their_weaknesses.map((weakness, i) => (
                    <div key={i} className="mb-2 p-2 bg-orange-800/20 rounded">
                      <p className="font-medium">{weakness.vulnerability}</p>
                      <p className="text-xs text-gray-400 mt-1">{weakness.how_to_exploit}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Training Focus Card */}
            <div className="bg-purple-900/30 border border-purple-700/50 rounded-lg p-4">
              <h4 className="text-purple-400 font-semibold mb-3 flex items-center text-sm">
                🏃 Training Priorities
              </h4>
              <div className="text-gray-300 text-xs space-y-2">
                {managerInsights.training_priorities.map((priority, i) => (
                  <div key={i} className="p-2 bg-purple-800/20 rounded">
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium">{priority.focus}</p>
                      <span className="text-purple-300 text-xs">#{priority.priority}</span>
                    </div>
                    <p className="text-xs text-gray-400 mb-1">{priority.drill}</p>
                    <p className="text-xs text-purple-300">{priority.duration}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Next Match Tactics Card */}
            <div className="bg-yellow-900/30 border border-yellow-700/50 rounded-lg p-4">
              <h4 className="text-yellow-400 font-semibold mb-3 flex items-center text-sm">
                ⚡ Next Match Tactics
              </h4>
              <div className="text-gray-300 text-xs space-y-2">
                {managerInsights.next_match_tactics.map((tactic, i) => (
                  <div key={i} className="space-y-2">
                    <div className="p-2 bg-yellow-800/20 rounded">
                      <p className="text-yellow-300 font-medium mb-1">Game Plan:</p>
                      <p>{tactic.if_facing_similar_opponent}</p>
                    </div>
                    <div className="p-2 bg-yellow-800/20 rounded">
                      <p className="text-yellow-300 font-medium mb-1">Set Pieces:</p>
                      <p>{tactic.set_piece_focus}</p>
                    </div>
                    <div className="p-2 bg-yellow-800/20 rounded">
                      <p className="text-yellow-300 font-medium mb-1">Attack Plan:</p>
                      <p>{tactic.attacking_plan}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Fallback to raw text display for unstructured data
  return (
    <div className="absolute bottom-0 left-0 right-0 max-h-40 bg-black/95 backdrop-blur-sm border-t border-gray-700 overflow-y-auto">
      <div className="p-4">
        <h3 className="text-white text-lg font-bold mb-4 flex items-center">
          🧠 Game Insights
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
      </div>
    </div>
  )
}

export default TacticalInsights