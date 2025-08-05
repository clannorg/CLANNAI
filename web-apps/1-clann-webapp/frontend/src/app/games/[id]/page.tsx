'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter, useParams, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import apiClient from '@/lib/api-client'
import FifaStyleInsights from '../../../components/games/FifaStyleInsights'
import { AIChatProvider, AIChatSidebar, ChatToggleButton, useAIChat } from '../../../components/ai-chat'

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
  is_demo?: boolean
  ai_analysis: GameEvent[] | { events: GameEvent[] } | null
  tactical_analysis: {
    tactical: Record<string, { content: string, filename: string, uploaded_at: string }>
    analysis: Record<string, { content: string, filename: string, uploaded_at: string }>
  } | null
  team_name: string
  team_color: string
  created_at: string
}

const GameViewContent: React.FC<{ game: Game }> = ({ game }) => {
  const { isOpen: showChat, toggleChat, sendMessage } = useAIChat()
  const router = useRouter()
  const params = useParams()
  const searchParams = useSearchParams()
  const gameId = params.id as string
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [currentEventIndex, setCurrentEventIndex] = useState(-1)
  const [showEvents, setShowEvents] = useState(true)
  const [teamScores, setTeamScores] = useState({ red: 0, black: 0 })
  
  // Filter state
  const [eventTypeFilters, setEventTypeFilters] = useState({
    goal: true,
    shot: true,
    save: true,
    foul: true,
    yellow_card: true,
    red_card: true,
    corner: true,
    substitution: true
  })
  const [teamFilter, setTeamFilter] = useState('both') // 'red', 'black', 'both'
  const [timeRange, setTimeRange] = useState([0, 0]) // [start, end] in seconds
  const [searchText, setSearchText] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  
  // Chat state is now handled by AIChatProvider
  
  // Tactical analysis state
  const [tacticalData, setTacticalData] = useState<{
    tactical: Record<string, { content: string, filename: string, uploaded_at: string }>
    analysis: Record<string, { content: string, filename: string, uploaded_at: string }>
  } | null>(null)
  const [tacticalLoading, setTacticalLoading] = useState(false)
  
  const videoRef = useRef<HTMLVideoElement>(null)

  // Function to seek to specific timestamp
  const seekToTimestamp = (timestampInSeconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = timestampInSeconds
      // Also play the video if it's not already playing
      if (videoRef.current.paused) {
        videoRef.current.play()
      }
      // Scroll to video for better UX
      videoRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  // Initialize time range when game is loaded
  useEffect(() => {
    if (game && duration > 0) {
      setTimeRange([0, duration])
    }
  }, [game, duration])

  // Load tactical data from game
  useEffect(() => {
      setTacticalLoading(true)
    if (game.tactical_analysis) {
      setTacticalData(game.tactical_analysis)
      console.log('📊 Tactical data loaded from game:', 
        Object.keys(game.tactical_analysis.tactical || {}), 
        Object.keys(game.tactical_analysis.analysis || {})
      )
      } else {
        console.log('No tactical analysis data available')
      setTacticalData(null)
      }
      setTacticalLoading(false)
  }, [game])

  // Auto-open AI chat and start conversation for demo games
  useEffect(() => {
    const autoChat = searchParams.get('autoChat')
    const customMessage = searchParams.get('message')
    
    if (game && game.is_demo && !showChat && autoChat === 'true') {
      console.log('🤖 Auto-opening AI chat and starting conversation for demo game')
      // Delay slightly to let the page load
      setTimeout(() => {
        toggleChat()
        // Send custom message or default welcome message
        setTimeout(() => {
          const messageToSend = customMessage || "Hi! I'm new to ClannAI. Can you tell me about this match and what insights you can provide?"
          sendMessage(messageToSend)
        }, 800)
      }, 1500)
    }
  }, [game, showChat, toggleChat, sendMessage, searchParams])



  // Filter events based on current filter settings
  const filterEvents = (events: GameEvent[]) => {
    return events.filter(event => {
      // Filter by event type
      if (!eventTypeFilters[event.type as keyof typeof eventTypeFilters]) {
        return false
      }
      
      // Filter by team
      if (teamFilter !== 'both' && event.team && event.team !== teamFilter) {
        return false
      }
      
      // Filter by time range
      if (event.timestamp < timeRange[0] || event.timestamp > timeRange[1]) {
        return false
      }
      
      // Filter by search text
      if (searchText && event.description) {
        const searchLower = searchText.toLowerCase()
        if (!event.description.toLowerCase().includes(searchLower) && 
            !event.player?.toLowerCase().includes(searchLower)) {
          return false
        }
      }
      
      return true
    })
  }

  // Get all events and filtered events
  const allEvents = Array.isArray(game?.ai_analysis) 
    ? game.ai_analysis 
    : (game?.ai_analysis?.events || [])
  
  const filteredEvents = filterEvents(allEvents)

  // Update current event and score based on video time
  useEffect(() => {
    if (!allEvents || allEvents.length === 0) return

    const currentEvent = allEvents.findIndex(event => event.timestamp > currentTime)
    const newIndex = currentEvent === -1 ? allEvents.length - 1 : Math.max(0, currentEvent - 1)
    
    if (newIndex !== currentEventIndex) {
      setCurrentEventIndex(newIndex)
    }

    // Calculate current scores by team based on goals up to current time
    const redGoals = allEvents.filter(event => 
      event.type === 'goal' && event.timestamp <= currentTime && event.team === 'red'
    ).length
    
    const blackGoals = allEvents.filter(event => 
      event.type === 'goal' && event.timestamp <= currentTime && event.team === 'black'
    ).length
    
    if (redGoals !== teamScores.red || blackGoals !== teamScores.black) {
      setTeamScores({ red: redGoals, black: blackGoals })
    }
  }, [currentTime, game?.ai_analysis, currentEventIndex, teamScores.red, teamScores.black, allEvents])

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
    if (!filteredEvents || filteredEvents.length === 0) return
    const currentFilteredIndex = filteredEvents.findIndex(event => 
      allEvents.indexOf(event) === currentEventIndex
    )
    if (currentFilteredIndex > 0) {
      const prevEvent = filteredEvents[currentFilteredIndex - 1]
      handleEventClick(prevEvent)
    }
  }

  const handleNextEvent = () => {
    if (!filteredEvents || filteredEvents.length === 0) return
    const currentFilteredIndex = filteredEvents.findIndex(event => 
      allEvents.indexOf(event) === currentEventIndex
    )
    if (currentFilteredIndex < filteredEvents.length - 1) {
      const nextEvent = filteredEvents[currentFilteredIndex + 1]
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

  // Chat functionality now handled by AIChatProvider



  // Handle both direct array format and {events: [...]} format
  const events = filteredEvents

  return (
    <div className="min-h-screen bg-black">
      {/* Video Section */}
    <div className="h-screen bg-black relative overflow-hidden">
      {/* AI Chat Sidebar - Now componentized */}
      <AIChatSidebar />

      {/* Top Header - Back Button and Game Info */}
      <div className={`absolute top-4 z-50 flex items-center space-x-2 md:space-x-4 transition-all duration-300 ${
        showChat ? 'md:left-[336px] left-4' : 'left-4'
      }`}>
        <Link 
          href="/dashboard" 
          className="group flex items-center space-x-2 bg-white/10 hover:bg-white/20 backdrop-blur-lg rounded-xl px-4 py-2.5 text-white transition-all duration-200 border border-white/20 hover:border-white/30 shadow-lg"
        >
          <svg className="w-4 h-4 transition-transform group-hover:-translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="font-medium" style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>Dashboard</span>
        </Link>
        
        <div className="bg-white/10 backdrop-blur-lg rounded-xl px-6 py-2.5 border border-white/20 shadow-lg">
          <div className="flex items-center space-x-4 text-white" style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>
            <span className="font-semibold text-sm">{game.team_name}</span>
            <div className="w-px h-4 bg-white/30"></div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 rounded-full bg-red-400"></div>
                <span className="font-bold text-sm">{teamScores.red}</span>
              </div>
              <span className="text-white/60 font-medium">-</span>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                <span className="font-bold text-sm">{teamScores.black}</span>
              </div>
            </div>
            <div className="w-px h-4 bg-white/30"></div>
            <span className="font-medium text-sm text-white/90">{game.title}</span>
            <div className="w-px h-4 bg-white/30"></div>
            <span className="font-mono text-sm text-white/80">{formatTime(currentTime)}</span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <ChatToggleButton 
            className="mobile-chat-toggle"
          />
          
          <button
            onClick={() => setShowEvents(!showEvents)}
            className={`group flex items-center space-x-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 border shadow-lg ${
              showEvents 
                ? 'bg-green-500/20 hover:bg-green-500/30 border-green-400/40 text-green-200' 
                : 'bg-white/10 hover:bg-white/20 border-white/20 hover:border-white/30 text-white'
            }`}
            title="Toggle Events"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>Events</span>
          </button>
        </div>

      </div>

      {/* Video Container - with dynamic margins for sidebars */}
      <div className={`relative h-full flex items-center justify-center transition-all duration-300 ${
        showChat ? 'md:ml-80' : ''
      } ${
        showEvents ? 'md:mr-80' : ''
      }`}>
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
          onError={(e) => {
            console.error('Video loading error:', e)
            // Could add error state here
          }}
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
                  const originalIndex = allEvents.indexOf(event)
                  const isCurrent = originalIndex === currentEventIndex
                  
                  return (
                    <button
                      key={`${event.timestamp}-${event.type}`}
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

            {/* Progress/Scrub Bar */}
            <div className="relative px-4 pb-3">
              <div className="relative">
                <input
                  type="range"
                  min="0"
                  max={duration || 0}
                  step="0.1"
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full h-2 bg-white/20 rounded-full appearance-none cursor-pointer range-slider hover:h-3 transition-all duration-150 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-0 [&::-webkit-slider-thumb]:h-0 [&::-moz-range-thumb]:appearance-none [&::-moz-range-thumb]:border-none [&::-moz-range-thumb]:w-0 [&::-moz-range-thumb]:h-0"
                  style={{
                    background: `linear-gradient(to right, #016F32 0%, #016F32 ${(currentTime / (duration || 1)) * 100}%, rgba(255,255,255,0.2) ${(currentTime / (duration || 1)) * 100}%, rgba(255,255,255,0.2) 100%)`
                  }}
                />
                {/* Progress indicator thumb */}
                <div 
                  className="absolute top-1/2 w-4 h-4 bg-white rounded-full shadow-lg transform -translate-y-1/2 pointer-events-none border-2 border-[#016F32] transition-all duration-150"
                  style={{ left: `calc(${(currentTime / (duration || 1)) * 100}% - 8px)` }}
                />
              </div>
            </div>

            {/* Video Controls */}
            <div className="bg-black/60 backdrop-blur-md mx-6 mb-3 rounded-lg border border-white/5 shadow-md">
              <div className="flex items-center justify-between px-4 py-3">
                {/* Left Side - Main Controls */}
                <div className="flex items-center space-x-4">
                  <button
                    onClick={handlePlayPause}
                    className="group flex items-center justify-center w-12 h-12 bg-white/15 hover:bg-white/25 rounded-full transition-all duration-200 border border-white/20 hover:border-white/30 shadow-lg"
                  >
                    {isPlaying ? (
                      <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"/>
                      </svg>
                    )}
                  </button>

                  <div className="flex items-center space-x-2">
                  <button
                    onClick={handleJumpBackward}
                      className="group flex items-center justify-center w-10 h-10 bg-white/10 hover:bg-white/20 rounded-xl transition-all duration-200 border border-white/10 hover:border-white/20"
                      title="Jump back 5s"
                  >
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.334 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z" />
                      </svg>
                  </button>

                  <button
                    onClick={handleJumpForward}
                      className="group flex items-center justify-center w-10 h-10 bg-white/10 hover:bg-white/20 rounded-xl transition-all duration-200 border border-white/10 hover:border-white/20"
                      title="Jump forward 5s"
                  >
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z" />
                      </svg>
                  </button>

                  <button
                    onClick={handleMuteToggle}
                      className="group flex items-center justify-center w-10 h-10 bg-white/10 hover:bg-white/20 rounded-xl transition-all duration-200 border border-white/10 hover:border-white/20"
                    title={isMuted ? 'Unmute' : 'Mute'}
                  >
                      {isMuted ? (
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                        </svg>
                      )}
                  </button>
                  </div>
                  
                  <div className="flex items-center space-x-3 text-white/90">
                    <div className="font-mono text-sm">
                      {formatTime(currentTime)}
                    </div>
                    <div className="w-px h-4 bg-white/20"></div>
                    <div className="font-mono text-sm text-white/60">
                      {formatTime(duration)}
                    </div>
                  </div>
                </div>

                {/* Right Side - Event Navigation */}
                                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                  <button
                    onClick={handlePreviousEvent}
                      disabled={events.length === 0}
                      className={`group flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200 border ${
                        events.length > 0
                          ? 'bg-white/10 hover:bg-white/20 border-white/20 hover:border-white/30 text-white'
                          : 'bg-white/5 border-white/10 text-white/40 cursor-not-allowed'
                      }`}
                    title="Previous Event"
                  >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                      </svg>
                      <span>Prev</span>
                  </button>

                    <div className="px-4 py-2 bg-white/5 rounded-xl border border-white/10 min-w-[120px] text-center">
                      <div className="text-white/90 text-xs font-medium">
                        {currentEventIndex >= 0 && allEvents[currentEventIndex] ? (
                          <span className="capitalize">{allEvents[currentEventIndex].type}</span>
                        ) : (
                          <span className="text-white/60">No event</span>
                        )}
                      </div>
                  </div>

                  <button
                    onClick={handleNextEvent}
                      disabled={events.length === 0}
                      className={`group flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200 border ${
                        events.length > 0
                          ? 'bg-white/10 hover:bg-white/20 border-white/20 hover:border-white/30 text-white'
                          : 'bg-white/5 border-white/10 text-white/40 cursor-not-allowed'
                      }`}
                    title="Next Event"
                  >
                      <span>Next</span>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                  </button>
                  </div>

                  <button
                    onClick={() => {
                      if (document.fullscreenElement) {
                        document.exitFullscreen()
                      } else {
                        document.documentElement.requestFullscreen()
                      }
                    }}
                    className="group flex items-center justify-center w-10 h-10 bg-white/10 hover:bg-white/20 rounded-xl transition-all duration-200 border border-white/10 hover:border-white/20"
                    title="Toggle Fullscreen"
                  >
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Events Sidebar - RIGHT SIDE */}
      {showEvents && allEvents.length > 0 && (
        <div className="absolute top-0 right-0 h-full w-full md:w-80 bg-black/90 backdrop-blur-sm border-l border-gray-700 flex flex-col z-30">
          <div className="sticky top-0 bg-black/90 backdrop-blur-sm border-b border-gray-700 p-4 z-10">
            <div className="flex items-center justify-between mb-3">
              <button
                onClick={() => setShowEvents(false)}
                className="flex items-center justify-center w-8 h-8 bg-white/10 hover:bg-white/20 rounded-lg transition-all duration-200 border border-white/10 hover:border-white/20"
                title="Hide Events"
              >
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200 border ${
                  showFilters 
                    ? 'bg-green-500/20 hover:bg-green-500/30 border-green-400/40 text-green-200' 
                    : 'bg-white/10 hover:bg-white/20 border-white/20 hover:border-white/30 text-white'
                }`}
                title="Toggle Filters"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.414A1 1 0 013 6.707V4z" />
                </svg>
                <span>Filters</span>
              </button>
            </div>

            {/* Filter Controls */}
            {showFilters && (
              <div className="space-y-3 text-sm">
                {/* Event Type Filters */}
                <div>
                  <label className="text-gray-300 block mb-2">Event Types:</label>
                  <div className="grid grid-cols-2 gap-1">
                    {Object.entries(eventTypeFilters).map(([type, enabled]) => (
                      <label key={type} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={enabled}
                          onChange={(e) => setEventTypeFilters(prev => ({
                            ...prev,
                            [type]: e.target.checked
                          }))}
                          className="w-3 h-3"
                        />
                        <span className="text-xs text-gray-300 capitalize">{type.replace('_', ' ')}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Team Filter */}
                <div>
                  <label className="text-gray-300 block mb-2">Team:</label>
                  <select
                    value={teamFilter}
                    onChange={(e) => setTeamFilter(e.target.value)}
                    className="w-full bg-gray-800 text-white text-xs p-2 rounded border border-gray-600"
                  >
                    <option value="both">Both Teams</option>
                    <option value="red">Red Team</option>
                    <option value="black">Black Team</option>
                  </select>
                </div>

                {/* Time Range */}
                <div>
                  <label className="text-gray-300 block mb-2">Time Range:</label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="range"
                      min="0"
                      max={duration || 0}
                      value={timeRange[0]}
                      onChange={(e) => setTimeRange([parseFloat(e.target.value), timeRange[1]])}
                      className="flex-1 h-1"
                    />
                    <input
                      type="range"
                      min="0"
                      max={duration || 0}
                      value={timeRange[1]}
                      onChange={(e) => setTimeRange([timeRange[0], parseFloat(e.target.value)])}
                      className="flex-1 h-1"
                    />
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {formatTime(timeRange[0])} - {formatTime(timeRange[1])}
                  </div>
                </div>

                {/* Search */}
                <div>
                  <label className="text-gray-300 block mb-2">Search:</label>
                  <input
                    type="text"
                    placeholder="Search descriptions..."
                    value={searchText}
                    onChange={(e) => setSearchText(e.target.value)}
                    className="w-full bg-gray-800 text-white text-xs p-2 rounded border border-gray-600"
                  />
                </div>

                {/* Reset Filters */}
                <button
                  onClick={() => {
                    setEventTypeFilters({
                      goal: true,
                      shot: true,
                      save: true,
                      foul: true,
                      yellow_card: true,
                      red_card: true,
                      corner: true,
                      substitution: true
                    })
                    setTeamFilter('both')
                    setTimeRange([0, duration || 0])
                    setSearchText('')
                  }}
                  className="w-full bg-gray-700 hover:bg-gray-600 text-white text-xs py-2 rounded transition-colors"
                >
                  Reset Filters
                </button>
              </div>
            )}
          </div>
          
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              {events.map((event, index) => {
                const originalIndex = allEvents.indexOf(event)
                return (
                <button
                    key={`${event.timestamp}-${event.type}-${index}`}
                    id={`event-${originalIndex}`}
                  onClick={() => handleEventClick(event)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                      originalIndex === currentEventIndex 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${getEventColor(event.type)}`} />
                      <span className="text-sm font-medium">{event.type}</span>
                        {event.team && (
                          <span className={`text-xs px-1 py-0.5 rounded ${
                            event.team === 'red' ? 'bg-red-600' : 'bg-blue-600'
                          }`}>
                            {event.team}
                          </span>
                        )}
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
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* Toggle Buttons for when sidebars are closed */}
      {!showChat && !showEvents && (
        <div className="absolute top-4 right-4 z-50 space-y-2">
          <button
            onClick={() => setShowEvents(true)}
            className="block bg-black/80 backdrop-blur-sm rounded-lg p-3 text-white hover:text-gray-300 transition-colors"
            title="Show Events"
          >
            📊 Events ({allEvents.length})
          </button>
          <ChatToggleButton variant="floating" />
        </div>
      )}

      </div>

      {/* Game Insights Section - Separate scrollable section below video */}
      <div className="bg-gray-900 min-h-screen">
        <div className="container mx-auto px-6 py-8">
          <h2 className="text-3xl font-bold text-white mb-6">Game Insights</h2>
      <FifaStyleInsights 
        tacticalData={tacticalData} 
        tacticalLoading={tacticalLoading} 
        gameId={gameId}
        onSeekToTimestamp={seekToTimestamp}
      />
        </div>
      </div>
    </div>
  )
} 

export default function GameView() {
  const router = useRouter()
  const params = useParams()
  const gameId = params.id as string
  
  const [game, setGame] = useState<Game | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

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

  if (error || !game) {
    return (
      <div className="h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">
            {error ? 'Error' : 'Game Not Found'}
          </h1>
          <p className="text-red-400 mb-4">{error || 'The requested game could not be found'}</p>
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

  return (
    <AIChatProvider game={game}>
      <GameViewContent game={game} />
    </AIChatProvider>
  )
} 