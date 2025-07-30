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
  ai_analysis: GameEvent[] | { events: GameEvent[] } | null
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
  
  // Chat state
  const [showChat, setShowChat] = useState(false)
  const [chatMessages, setChatMessages] = useState<Array<{
    role: 'user' | 'assistant'
    content: string
    timestamp: string
  }>>([])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (!userData) {
      router.push('/')
      return
    }
    
    loadGame()
  }, [gameId, router])

  // Initialize time range when game is loaded
  useEffect(() => {
    if (game && duration > 0) {
      setTimeRange([0, duration])
    }
  }, [game, duration])

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

  // Chat functionality
  const handleSendMessage = async () => {
    if (!chatInput.trim() || chatLoading || !game) return

    const userMessage = {
      role: 'user' as const,
      content: chatInput.trim(),
      timestamp: new Date().toISOString()
    }

    // Add user message immediately
    setChatMessages(prev => [...prev, userMessage])
    setChatInput('')
    setChatLoading(true)

    try {
      // Send to AI with chat history
      const response = await apiClient.chatWithAI(
        game.id,
        userMessage.content,
        chatMessages.map(msg => ({ role: msg.role, content: msg.content }))
      )

      const aiMessage = {
        role: 'assistant' as const,
        content: response.response,
        timestamp: response.timestamp
      }

      setChatMessages(prev => [...prev, aiMessage])

      // Scroll to bottom of chat
      setTimeout(() => {
        if (chatContainerRef.current) {
          chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
        }
      }, 100)

    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage = {
        role: 'assistant' as const,
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }
      setChatMessages(prev => [...prev, errorMessage])
    } finally {
      setChatLoading(false)
    }
  }

  const handleChatKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
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

  // Handle both direct array format and {events: [...]} format
  const events = filteredEvents

  return (
    <div className="h-screen bg-black relative overflow-hidden">
      {/* AI Chat Sidebar - LEFT SIDE */}
      {showChat && (
        <div className="absolute top-0 left-0 h-full w-80 bg-black/90 backdrop-blur-sm border-r border-gray-700 flex flex-col z-30">
          <div className="sticky top-0 bg-black/90 backdrop-blur-sm border-b border-gray-700 p-4 z-10">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-white font-semibold flex items-center space-x-2">
                <span>🤖</span>
                <span>AI Coach</span>
              </h2>
              <button
                onClick={() => setShowChat(false)}
                className="text-gray-300 hover:text-white text-xl font-bold"
                title="Hide Chat"
              >
                ×
              </button>
            </div>
            <p className="text-xs text-gray-400">
              Ask questions about tactics, player performance, or get coaching advice based on this game.
            </p>
          </div>
          
          {/* Chat Messages */}
          <div 
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-3"
          >
            {chatMessages.length === 0 && (
              <div className="text-center text-gray-400 text-sm mt-8">
                <div className="mb-4 text-4xl">🤖</div>
                <p className="mb-2">Welcome to AI Coach!</p>
                <p className="text-xs">Try asking:</p>
                <div className="text-xs mt-2 space-y-1">
                  <div>• "How did we perform in the first half?"</div>
                  <div>• "What should we improve?"</div>
                  <div>• "Analyze our goal scoring"</div>
                </div>
              </div>
            )}
            
            {chatMessages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] p-3 rounded-lg text-sm ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-300'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex items-center space-x-2 mb-2">
                      <span>🤖</span>
                      <span className="text-xs text-gray-400">AI Coach</span>
                    </div>
                  )}
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div className="text-xs opacity-60 mt-1">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800 text-gray-300 p-3 rounded-lg text-sm">
                  <div className="flex items-center space-x-2">
                    <span>🤖</span>
                    <span className="text-xs text-gray-400">AI Coach</span>
                  </div>
                  <div className="flex items-center space-x-1 mt-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Chat Input */}
          <div className="sticky bottom-0 bg-black/90 backdrop-blur-sm border-t border-gray-700 p-4">
            <div className="flex space-x-2">
              <input
                type="text"
                placeholder="Ask the AI coach..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={handleChatKeyPress}
                disabled={chatLoading}
                className="flex-1 bg-gray-800 text-white text-sm p-3 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none disabled:opacity-50"
              />
              <button
                onClick={handleSendMessage}
                disabled={!chatInput.trim() || chatLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg transition-colors"
                title="Send Message"
              >
                {chatLoading ? '⏳' : '📤'}
              </button>
            </div>
            {chatMessages.length > 0 && (
              <button
                onClick={() => setChatMessages([])}
                className="text-xs text-gray-400 hover:text-gray-300 mt-2 transition-colors"
              >
                Clear conversation
              </button>
            )}
          </div>
        </div>
      )}

      {/* Top Header - Back Button and Game Info */}
      <div className={`absolute top-4 z-50 flex items-center space-x-4 transition-all duration-300 ${
        showChat ? 'left-[336px]' : 'left-4'
      }`}>
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
            <span className="font-bold text-red-400">Red: {teamScores.red}</span>
            <span className="text-gray-300">-</span>
            <span className="font-bold text-blue-400">Black: {teamScores.black}</span>
            <span className="text-gray-300">|</span>
            <span className="font-medium">{game.title}</span>
            <span className="text-gray-300">|</span>
            <span>{formatTime(currentTime)}</span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowChat(!showChat)}
            className="bg-black/80 backdrop-blur-sm rounded-lg px-3 py-2 text-white hover:text-gray-300 transition-colors"
            title="Toggle AI Chat"
          >
            🤖 AI Coach
          </button>
          
          <button
            onClick={() => setShowEvents(!showEvents)}
            className="bg-black/80 backdrop-blur-sm rounded-lg px-3 py-2 text-white hover:text-gray-300 transition-colors"
            title="Toggle Events"
          >
            📊 Events
          </button>
        </div>

        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          game.status === 'analyzed'
            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
            : 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
        }`}>
          {game.status.toUpperCase()}
        </div>
      </div>

      {/* Video Container - with dynamic margins for sidebars */}
      <div className={`relative h-full flex items-center justify-center transition-all duration-300 ${
        showChat ? 'ml-80' : ''
      } ${
        showEvents ? 'mr-80' : ''
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
            <div className="relative px-4 pb-4">
              <input
                type="range"
                min="0"
                max={duration || 0}
                step="0.1"
                value={currentTime}
                onChange={handleSeek}
                className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer range-slider"
                style={{
                  background: `linear-gradient(to right, #016F32 0%, #016F32 ${(currentTime / (duration || 1)) * 100}%, #374151 ${(currentTime / (duration || 1)) * 100}%, #374151 100%)`
                }}
              />
            </div>

            {/* Video Controls */}
            <div className="bg-black/80 backdrop-blur-sm mx-4 mb-4 rounded-lg">
              <div className="flex items-center justify-between p-4">
                {/* Left Side - Main Controls */}
                <div className="flex items-center space-x-4">
                  <button
                    onClick={handlePlayPause}
                    className="text-white hover:text-gray-300 transition-colors text-2xl"
                  >
                    {isPlaying ? '⏸' : '▶'}
                  </button>

                  <button
                    onClick={handleJumpBackward}
                    className="text-white/90 hover:text-white transition-colors"
                    title="Jump back 5s"
                  >
                    ⏪
                  </button>

                  <button
                    onClick={handleJumpForward}
                    className="text-white/90 hover:text-white transition-colors"
                    title="Jump forward 5s"
                  >
                    ⏩
                  </button>

                  <button
                    onClick={handleMuteToggle}
                    className="text-white/90 hover:text-white transition-colors"
                    title={isMuted ? 'Unmute' : 'Mute'}
                  >
                    {isMuted ? '🔇' : '🔊'}
                  </button>
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
                    {currentEventIndex >= 0 && allEvents[currentEventIndex] ? (
                      <span>{allEvents[currentEventIndex].type}</span>
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

      {/* Events Sidebar - RIGHT SIDE */}
      {showEvents && allEvents.length > 0 && (
        <div className="absolute top-0 right-0 h-full w-80 bg-black/90 backdrop-blur-sm border-l border-gray-700 flex flex-col z-30">
          <div className="sticky top-0 bg-black/90 backdrop-blur-sm border-b border-gray-700 p-4 z-10">
            <div className="flex items-center justify-between mb-3">
              <button
                onClick={() => setShowEvents(false)}
                className="text-gray-300 hover:text-white text-xl font-bold"
                title="Hide Events"
              >
                ×
              </button>
              <h2 className="text-white font-semibold">Events ({events.length}/{allEvents.length})</h2>
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="text-gray-300 hover:text-white text-sm px-2 py-1 rounded border border-gray-600"
                title="Toggle Filters"
              >
                🔍 Filters
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
          <button
            onClick={() => setShowChat(true)}
            className="block bg-black/80 backdrop-blur-sm rounded-lg p-3 text-white hover:text-gray-300 transition-colors"
            title="Show AI Chat"
          >
            🤖 AI Coach
          </button>
        </div>
      )}
    </div>
  )
} 