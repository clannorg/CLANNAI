'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Image from 'next/image'
import apiClient from '@/lib/api-client'
import { AdaptiveVideoPlayer } from '@/components/video-player/AdaptiveVideoPlayer'

interface GameEvent {
  type: string
  timestamp: number
  player?: string
  description?: string
  team?: string
}

interface Game {
  id: string
  title: string
  description: string
  s3Url: string
  status: string
  ai_analysis: GameEvent[]
  team_name: string
  team_color: string
  created_at: string
}

export default function GameView() {
  const router = useRouter()
  const params = useParams()
  const gameId = params.id as string
  
  const [game, setGame] = useState<Game | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState<GameEvent | null>(null)
  
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (!userData) {
      router.push('/')
      return
    }
    
    loadGame()
  }, [gameId, router])

  const loadGame = async () => {
    try {
      setLoading(true)
      setError('')
      
      const response = await apiClient.getGame(gameId) as { game: Game }
      setGame(response.game)
    } catch (err: any) {
      console.error('Failed to load game:', err)
      setError(err.message || 'Failed to load game')
    } finally {
      setLoading(false)
    }
  }

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
      setDuration(videoRef.current.duration || 0)
    }
  }

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const jumpToEvent = (timestamp: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = timestamp
      setCurrentTime(timestamp)
      if (!isPlaying) {
        videoRef.current.play()
        setIsPlaying(true)
      }
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getEventTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'goal': return 'bg-green-500'
      case 'shot': return 'bg-blue-500'
      case 'foul': return 'bg-red-500'
      case 'yellow card': return 'bg-yellow-500'
      case 'red card': return 'bg-red-600'
      case 'substitution': return 'bg-purple-500'
      default: return 'bg-gray-500'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F7F6F1] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#016F32]"></div>
          <p className="mt-2 text-gray-500">Loading game...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#F7F6F1] flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Error</h1>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="bg-[#016F32] text-white px-6 py-2 rounded-lg hover:bg-[#014d24] transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  if (!game) {
    return (
      <div className="min-h-screen bg-[#F7F6F1] flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Game Not Found</h1>
          <button
            onClick={() => router.push('/dashboard')}
            className="bg-[#016F32] text-white px-6 py-2 rounded-lg hover:bg-[#014d24] transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#F7F6F1]">
      {/* Header */}
      <nav className="border-b border-gray-200/10 bg-white">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Image 
                src="/clann-logo-green.png" 
                alt="ClannAI" 
                width={48} 
                height={48}
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{game.title}</h1>
                <p className="text-sm text-gray-600">{game.team_name}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                game.status === 'analyzed'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-orange-100 text-orange-800'
              }`}>
                {game.status.toUpperCase()}
              </span>
              <button
                onClick={() => router.push('/dashboard')}
                className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-8 py-8">
        {game.status === 'pending' ? (
          // Pending game state
          <div className="bg-white rounded-xl shadow-sm p-8 text-center">
            <div className="mb-6">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis In Progress</h2>
              <p className="text-gray-600">This game is being processed by our AI analysis system.</p>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-600"><strong>VEO URL:</strong></p>
              <a 
                href={game.s3Url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:text-blue-800 break-all"
              >
                {game.s3Url}
              </a>
            </div>
            
            <p className="text-sm text-gray-500">You'll be notified when the analysis is complete.</p>
          </div>
        ) : (
          // Analyzed game with video player
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Video Player */}
            <div className="lg:col-span-3">
              <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                <AdaptiveVideoPlayer
                  src={game.s3Url}
                  title={game.title}
                  events={game.ai_analysis || []}
                  onTimeUpdate={handleTimeUpdate}
                  onDurationChange={(dur) => setDuration(dur)}
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                  onLoadedMetadata={handleTimeUpdate}
                  onEventClick={jumpToEvent}
                  className="w-full"
                />
                
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{game.title}</h3>
                  {game.description && (
                    <p className="text-gray-600 mb-4">{game.description}</p>
                  )}
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>Duration: {formatTime(duration)}</span>
                    <span>Current: {formatTime(currentTime)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Events Sidebar */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-xl shadow-sm">
                <div className="p-6 border-b border-gray-100">
                  <h3 className="text-lg font-semibold text-gray-900">Match Events</h3>
                  <p className="text-sm text-gray-600">
                    {game.ai_analysis?.length || 0} events detected
                  </p>
                </div>
                
                <div className="p-4 max-h-96 overflow-y-auto">
                  {game.ai_analysis && game.ai_analysis.length > 0 ? (
                    <div className="space-y-3">
                      {game.ai_analysis
                        .sort((a, b) => a.timestamp - b.timestamp)
                        .map((event, index) => (
                        <button
                          key={index}
                          onClick={() => jumpToEvent(event.timestamp)}
                          className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors border border-gray-100"
                        >
                          <div className="flex items-center space-x-2 mb-1">
                            <div className={`w-2 h-2 rounded-full ${getEventTypeColor(event.type)}`} />
                            <span className="font-medium text-sm text-gray-900">{event.type}</span>
                            <span className="text-xs text-gray-500 ml-auto">{formatTime(event.timestamp)}</span>
                          </div>
                          {event.player && (
                            <p className="text-xs text-gray-600">{event.player}</p>
                          )}
                          {event.description && (
                            <p className="text-xs text-gray-600 mt-1">{event.description}</p>
                          )}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-500 text-sm">No events detected</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 