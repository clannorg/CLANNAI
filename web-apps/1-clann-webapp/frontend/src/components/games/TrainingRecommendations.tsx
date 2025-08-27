'use client'

import React, { useState, useEffect } from 'react'
import apiClient from '@/lib/api-client'

interface TrainingDrill {
  drill_name: string
  youtube_url: string
  youtube_embed: string
  description: string
  focus_areas: string
  match_evidence: string
  why_needed: string
  priority: number
}

interface TrainingData {
  match_id: string
  generated_at: string
  training_recommendations: TrainingDrill[]
}

interface Props {
  gameId: string
}

const TrainingRecommendations: React.FC<Props> = ({ gameId }) => {
  console.log('🏋️ TrainingRecommendations component rendered with gameId:', gameId);
  
  const [trainingData, setTrainingData] = useState<TrainingData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedDrill, setExpandedDrill] = useState<number | null>(null)

  useEffect(() => {
    console.log('🏋️ TrainingRecommendations component mounted with gameId:', gameId)
    
    const fetchTrainingRecommendations = async () => {
      try {
        console.log('🏋️ Starting to fetch training recommendations for game:', gameId)
        setLoading(true)
        setError(null)
        
        console.log('🏋️ Making API call to getTrainingRecommendations...')
        const response = await apiClient.getTrainingRecommendations(gameId)
        console.log('🏋️ API response received:', response)
        
        if (response.training_recommendations) {
          console.log('🏋️ Training data found:', response.training_recommendations.training_recommendations?.length, 'drills')
          setTrainingData(response.training_recommendations)
        } else {
          console.log('🏋️ No training recommendations in response')
          setTrainingData(null)
        }
      } catch (err: any) {
        console.error('🏋️ Failed to fetch training recommendations:', err)
        setError(err.message || 'Failed to load training recommendations')
      } finally {
        console.log('🏋️ Training recommendations fetch completed')
        setLoading(false)
      }
    }

    if (gameId) {
      console.log('🏋️ GameId exists, fetching training recommendations...')
      fetchTrainingRecommendations()
    } else {
      console.log('🏋️ No gameId provided to TrainingRecommendations component')
    }
  }, [gameId])

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-700/50 rounded-lg p-4">
        <div className="flex items-center space-x-2 mb-3">
          <div className="w-5 h-5 animate-spin rounded-full border-2 border-orange-500 border-t-transparent"></div>
          <h3 className="text-orange-400 font-semibold">Loading Training Recommendations...</h3>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-900/30 border border-red-700/50 rounded-lg p-4">
        <h3 className="text-red-400 font-semibold mb-2 flex items-center">
          ⚠️ Training Recommendations
        </h3>
        <p className="text-gray-300 text-sm">Failed to load training recommendations: {error}</p>
      </div>
    )
  }

  if (!trainingData || !trainingData.training_recommendations?.length) {
    return (
      <div className="bg-gray-900/30 border border-gray-700/50 rounded-lg p-4">
        <h3 className="text-gray-400 font-semibold mb-2 flex items-center">
          🏋️ Training Recommendations
        </h3>
        <p className="text-gray-500 text-sm">No training recommendations available for this match.</p>
      </div>
    )
  }

  return (
    <div className="bg-orange-900/30 border border-orange-700/50 rounded-lg p-4">
      <h3 className="text-orange-400 font-semibold mb-3 flex items-center">
        🏋️ Training Recommendations
        <span className="ml-2 text-xs bg-orange-700/50 px-2 py-1 rounded">
          {trainingData.training_recommendations.length} drills
        </span>
      </h3>
      
      <div className="space-y-3">
        {trainingData.training_recommendations.map((drill, index) => (
          <div key={index} className="bg-black/30 border border-orange-700/30 rounded-lg overflow-hidden">
            {/* Drill Header */}
            <div 
              className="p-3 cursor-pointer hover:bg-orange-900/20 transition-colors"
              onClick={() => setExpandedDrill(expandedDrill === index ? null : index)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-orange-300 font-medium text-sm">
                      {drill.priority}. {drill.drill_name}
                    </span>
                    <a 
                      href={drill.youtube_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-red-400 hover:text-red-300 transition-colors"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                      </svg>
                    </a>
                  </div>
                  <p className="text-gray-400 text-xs mb-1">{drill.description}</p>
                  <p className="text-orange-200 text-xs">
                    <strong>Evidence:</strong> {drill.match_evidence}
                  </p>
                </div>
                <button className="text-orange-400 hover:text-orange-300 ml-2">
                  <svg 
                    className={`w-4 h-4 transition-transform ${expandedDrill === index ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Expanded Content */}
            {expandedDrill === index && (
              <div className="border-t border-orange-700/30 p-3 bg-black/20">
                <div className="space-y-3">
                  {/* Why Needed */}
                  <div>
                    <h5 className="text-orange-300 font-medium text-xs mb-1">Why This Drill:</h5>
                    <p className="text-gray-300 text-xs">{drill.why_needed}</p>
                  </div>

                  {/* Focus Areas */}
                  <div>
                    <h5 className="text-orange-300 font-medium text-xs mb-1">Focus Areas:</h5>
                    <p className="text-gray-300 text-xs">{drill.focus_areas}</p>
                  </div>

                  {/* YouTube Embed */}
                  <div>
                    <h5 className="text-orange-300 font-medium text-xs mb-2">Training Video:</h5>
                    <div className="relative aspect-video bg-black rounded overflow-hidden">
                      <iframe
                        src={drill.youtube_embed}
                        title={drill.drill_name}
                        className="absolute inset-0 w-full h-full"
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-3 pt-2 border-t border-orange-700/30">
        <p className="text-gray-500 text-xs">
          Generated on {new Date(trainingData.generated_at).toLocaleDateString()} • 
          Based on tactical analysis and match evidence
        </p>
      </div>
    </div>
  )
}

export default TrainingRecommendations
