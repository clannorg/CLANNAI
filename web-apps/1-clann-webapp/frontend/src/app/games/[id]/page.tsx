'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import apiClient from '@/lib/api-client'

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
  const [isMuted, setIsMuted] = useState(false)
  const [currentEventIndex, setCurrentEventIndex] = useState(-1)
  const [showEvents, setShowEvents] = useState(true)
  
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

  // Update current event based on video time
  useEffect(() => {
    if (!game?.ai_analysis || game.ai_analysis.length === 0) return

    const currentEvent = game.ai_analysis.findIndex(event => event.timestamp > currentTime)
    const newIndex = currentEvent === -1 ? game.ai_analysis.length - 1 : Math.max(0, currentEvent - 1)
    
    if (newIndex !== currentEventIndex) {
      setCurrentEventIndex(newIndex)
    }
  }, [currentTime, game?.ai_analysis, currentEventIndex])

  // Auto-scroll to current event in sidebar
  useEffect(() => {
    if (currentEventIndex >= 0 && showEvents) {
      const eventElement = document.getElementById(`event-${currentEventIndex}`)
      if (eventElement) {
        eventElement.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
          inline: 'nearest'
        })
      }
    }
  }, [currentEventIndex, showEvents])

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

  const handleMuteToggle = () => {
    if (videoRef.current) {
      videoRef.current.muted = !videoRef.current.muted
      setIsMuted(videoRef.current.muted)
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value)
    if (videoRef.current) {
      videoRef.current.currentTime = time
      setCurrentTime(time)
    }
  }

  const handleEventClick = (event: GameEvent) => {
    if (videoRef.current) {
      videoRef.current.currentTime = event.timestamp
      setCurrentTime(event.timestamp)
    }
  }

  const handleJumpBackward = () => {
    if (videoRef.current && duration > 0) {
      const newTime = Math.max(0, currentTime - 5)
      if (videoRef.current.readyState >= 2) {
        videoRef.current.currentTime = newTime
        setCurrentTime(newTime)
      }
    }
  }

  const handleJumpForward = () => {
    if (videoRef.current && duration > 0) {
      const newTime = Math.min(duration, currentTime + 5)
      if (videoRef.current.readyState >= 2) {
        videoRef.current.currentTime = newTime
        setCurrentTime(newTime)
      }
    }
  }

  const handlePreviousEvent = () => {
    if (!game?.ai_analysis || game.ai_analysis.length === 0) return
    if (currentEventIndex > 0) {
      const prevEvent = game.ai_analysis[currentEventIndex - 1]
      handleEventClick(prevEvent)
    }
  }

  const handleNextEvent = () => {
    if (!game?.ai_analysis || game.ai_analysis.length === 0) return
    if (currentEventIndex < game.ai_analysis.length - 1) {
      const nextEvent = game.ai_analysis[currentEventIndex + 1]
      handleEventClick(nextEvent)
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const getEventColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'goal': return 'bg-green-500'
      case 'shot': return 'bg-blue-500'
      case 'foul': return 'bg-red-500'
      case 'yellow_card': return 'bg-yellow-500'
      case 'red_card': return 'bg-red-600'
      case 'substitution': return 'bg-purple-500'
      case 'corner': return 'bg-cyan-500'
      default: return 'bg-gray-500'
    }
  }

  if (loading) {
    return (
      <div className="h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          <p className="mt-2 text-white">Loading game...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Error</h1>
          <p className="text-red-400 mb-4">{error}</p>
          <Link
            href="/dashboard"
            className="bg-[#016F32] text-white px-6 py-2 rounded-lg hover:bg-[#014d24] transition-colors"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  if (!game) {
    return (
      <div className="h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Game Not Found</h1>
          <Link
            href="/dashboard"
            className="bg-[#016F32] text-white px-6 py-2 rounded-lg hover:bg-[#014d24] transition-colors"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  if (game.status === 'pending') {
    return (
      <div className="h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Analysis In Progress</h2>
          <p className="text-gray-400">This game is being processed by our AI analysis system.</p>
          <Link
            href="/dashboard"
            className="mt-4 inline-block bg-[#016F32] text-white px-6 py-2 rounded-lg hover:bg-[#014d24] transition-colors"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  const events = game.ai_analysis || []

  return (
    <div className="h-screen bg-black relative overflow-hidden">
      {/* Top Header - Back Button and Game Info */}
      <div className="absolute top-4 left-4 z-50 flex items-center space-x-4">
        <Link 
          href="/dashboard" 
          className="bg-black/80 backdrop-blur-sm rounded-lg px-4 py-2 text-white hover:text-gray-300 transition-colors"
        >
          ← Back to Dashboard
        </Link>
        
        <div className="bg-black/80 backdrop-blur-sm rounded-lg px-6 py-2">
          <div className="flex items-center space-x-6 text-white">
            <span className="font-bold">{game.team_name}</span>
            <span className="text-gray-300">|</span>
            <span className="font-medium">{game.title}</span>
            <span className="text-gray-300">|</span>
            <span>{formatTime(currentTime)}</span>
          </div>
        </div>

        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          game.status === 'analyzed'
            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
            : 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
        }`}>
          {game.status.toUpperCase()}
        </div>
      </div>

      {/* Video Container */}
      <div className="relative h-full flex items-center justify-center">
        {/* Video Element */}
        <video
          ref={videoRef}
          className="w-full h-full object-contain"
          src={game.s3Url}
          crossOrigin="anonymous"
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleTimeUpdate}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          preload="metadata"
        />

        {/* Progress Bar - Attached to Video Bottom */}
        <div className="absolute bottom-0 left-0 right-0 z-40">
          <div className="bg-transparent">
            {/* Timeline Dots Overlay */}
            {events.length > 0 && duration > 0 && (
              <div className="relative h-12 px-4 pt-3 pointer-events-none z-5">
                {events.map((event, index) => {
                  const position = (event.timestamp / duration) * 100
                  const isCurrent = index === currentEventIndex
                  
                  return (
                    <button
                      key={index}
                      onClick={() => handleEventClick(event)}
                      className={`absolute top-1/2 transform -translate-y-1/2 w-2 h-2 rounded-full transition-all duration-300 hover:scale-200 hover:shadow-xl pointer-events-auto ${
                        getEventColor(event.type)
                      } ${isCurrent ? 'ring-3 ring-yellow-400 ring-offset-2 ring-offset-black shadow-xl scale-125' : 'hover:ring-2 hover:ring-white/70'}`}
                      style={{ left: `${position}%` }}
                      title={`${event.type} - ${formatTime(event.timestamp)}`}
                    />
                  )
                })}
              </div>
            )}

            {/* Main Control Bar */}
            <div className="px-6 py-3 bg-gradient-to-t from-black/80 to-transparent">
              <div className="flex items-center justify-between">
                {/* Left Side - Playback Controls */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handlePlayPause}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title={isPlaying ? 'Pause' : 'Play'}
                  >
                    {isPlaying ? '⏸' : '▶'}
                  </button>

                  <button
                    onClick={handleJumpBackward}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title="Skip Backward 5s"
                  >
                    ↺
                  </button>

                  <button
                    onClick={handleJumpForward}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title="Skip Forward 5s"
                  >
                    ↻
                  </button>

                  <button
                    onClick={handleMuteToggle}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title={isMuted ? 'Unmute' : 'Mute'}
                  >
                    {isMuted ? '🔇' : '🔊'}
                  </button>
                </div>

                {/* Center - Events Toggle, Time, and Progress Bar */}
                <div className="flex-1 flex flex-col items-center justify-center mx-8">
                  <button
                    onClick={() => setShowEvents(!showEvents)}
                    className="text-white/90 hover:text-white transition-colors p-1 mb-2"
                    title="Toggle Events Panel"
                  >
                    ☰
                  </button>

                  <div className="text-white/90 text-sm font-medium mb-2">
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </div>
                  
                  <div className="w-full max-w-md">
                    <div className="relative">
                      <input
                        type="range"
                        min="0"
                        max={duration || 0}
                        value={currentTime}
                        onChange={handleSeek}
                        className="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
                        style={{
                          background: `linear-gradient(to right, #ffffff 0%, #ffffff ${(currentTime / duration) * 100}%, #4b5563 ${(currentTime / duration) * 100}%, #4b5563 100%)`
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Right Side - Event Navigation */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handlePreviousEvent}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title="Previous Event"
                    disabled={events.length === 0}
                  >
                    ◀
                  </button>

                  <div className="text-white/90 text-xs font-medium min-w-[140px] text-center flex items-center justify-center">
                    {currentEventIndex >= 0 && events[currentEventIndex] ? (
                      <span>{events[currentEventIndex].type}</span>
                    ) : (
                      <span>No event</span>
                    )}
                  </div>

                  <button
                    onClick={handleNextEvent}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title="Next Event"
                    disabled={events.length === 0}
                  >
                    ▶
                  </button>

                  <button
                    onClick={() => {
                      if (document.fullscreenElement) {
                        document.exitFullscreen()
                      } else {
                        document.documentElement.requestFullscreen()
                      }
                    }}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title="Toggle Fullscreen"
                  >
                    ⛶
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Events Sidebar */}
      {showEvents && events.length > 0 && (
        <div className="absolute top-0 right-0 h-full w-80 bg-black/90 backdrop-blur-sm border-l border-gray-700 flex flex-col">
          <div className="sticky top-0 bg-black/90 backdrop-blur-sm border-b border-gray-700 p-4 z-10">
            <div className="flex items-center justify-between">
              <button
                onClick={() => setShowEvents(false)}
                className="text-gray-300 hover:text-white text-xl font-bold"
                title="Hide Events"
              >
                ×
              </button>
              <h2 className="text-white font-semibold">Events ({events.length})</h2>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              {events.map((event, index) => (
                <button
                  key={index}
                  id={`event-${index}`}
                  onClick={() => handleEventClick(event)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    index === currentEventIndex 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${getEventColor(event.type)}`} />
                      <span className="text-sm font-medium">{event.type}</span>
                    </div>
                    <span className="text-xs text-gray-400">{formatTime(event.timestamp)}</span>
                  </div>
                  {event.description && (
                    <div className="text-xs text-gray-400 mt-1">{event.description}</div>
                  )}
                  {event.player && (
                    <div className="text-xs text-gray-400 mt-1">{event.player}</div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Events Sidebar Toggle Button */}
      {!showEvents && events.length > 0 && (
        <div className="absolute top-4 right-4 z-50">
          <button
            onClick={() => setShowEvents(true)}
            className="bg-black/80 backdrop-blur-sm rounded-lg p-3 text-white hover:text-gray-300 transition-colors"
            title="Show Events"
          >
            📊 Events ({events.length})
          </button>
        </div>
      )}
    </div>
  )
} 