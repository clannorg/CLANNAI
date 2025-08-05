'use client'

import React from 'react'

interface TacticalData {
  tactical: Record<string, { content: string, filename: string, uploaded_at: string }>
  analysis: Record<string, any>
}

interface Props {
  tacticalData: TacticalData | null
  tacticalLoading: boolean
  gameId: string
  onSeekToTimestamp?: (timestampInSeconds: number) => void
}

export default function FifaStyleInsights({ tacticalData, tacticalLoading, gameId, onSeekToTimestamp }: Props) {
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

  // Parse the raw tactical data to extract structured insights
  let matchOverview = null
  let redTeamData = null
  let managerRecommendations = null
  let keyMoments = []

  // Extract data from tactical analysis
  if (tacticalData.tactical?.red_team) {
    try {
      const redTeamContent = parseContent(tacticalData.tactical.red_team.content)
      redTeamData = redTeamContent
    } catch (e) {
      console.log('Failed to parse red team data:', e)
    }
  }

  // Extract data from analysis section
  if (tacticalData.analysis) {
    matchOverview = tacticalData.analysis.match_overview
    managerRecommendations = tacticalData.analysis.manager_recommendations
    keyMoments = tacticalData.analysis.key_moments || []
  }

  return (
    <div className="space-y-6">
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

      {/* FIFA-Style Red Team Performance */}
      {redTeamData && (
        <div className="bg-gradient-to-br from-red-900/30 to-red-800/20 border border-red-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center mb-4">
            <div className="w-4 h-4 bg-red-500 rounded-full mr-3"></div>
            <h3 className="text-xl font-bold text-white">Red Team Performance</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths */}
            <div className="bg-black/20 rounded-lg p-4">
              <h4 className="text-green-400 font-semibold mb-3 flex items-center">
                💪 Strengths
              </h4>
              <div className="space-y-2">
                {redTeamData.strengths?.map((strength: string, i: number) => (
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
                {redTeamData.weaknesses?.map((weakness: string, i: number) => (
                  <div key={i} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-200 text-sm">{weakness}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Shot Accuracy */}
          {redTeamData.shot_accuracy && (
            <div className="mt-4 bg-black/20 rounded-lg p-4">
              <h4 className="text-blue-400 font-semibold mb-2 flex items-center">
                🎯 Shooting Analysis
              </h4>
              <p className="text-gray-200 text-sm">{redTeamData.shot_accuracy}</p>
            </div>
          )}
        </div>
      )}

      {/* FIFA-Style Manager Recommendations */}
      {managerRecommendations?.red_team && (
        <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 border border-purple-500/30 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center mr-3">
              <span className="text-white text-sm font-bold">🧠</span>
            </div>
            <h3 className="text-xl font-bold text-white">AI Coach Recommendations</h3>
          </div>

          <div className="space-y-3">
            {managerRecommendations.red_team.map((recommendation: string, i: number) => (
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
    </div>
  )
}