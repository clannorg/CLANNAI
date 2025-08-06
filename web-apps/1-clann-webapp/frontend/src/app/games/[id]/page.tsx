'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import apiClient from '@/lib/api-client'
import VideoPlayer from '../../../components/games/VideoPlayer'
import GameHeader from '../../../components/games/GameHeader'
import UnifiedSidebar from '../../../components/games/UnifiedSidebar'
import { AIChatProvider, useAIChat } from '../../../components/ai-chat'

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
  const params = useParams()
  const gameId = params.id as string
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [currentEventIndex, setCurrentEventIndex] = useState(-1)
  const [showSidebar, setShowSidebar] = useState(true)
  const [sidebarTab, setSidebarTab] = useState<'events' | 'ai' | 'insights'>('events')
  const [sidebarWidth, setSidebarWidth] = useState(400)
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
    substitution: true,
    turnover: true
  })
  const [teamFilter, setTeamFilter] = useState('both') // 'red', 'black', 'both'
  const [showFilters, setShowFilters] = useState(false)
  
  // Tactical analysis state
  const [tacticalData, setTacticalData] = useState<{
    tactical: Record<string, { content: string, filename: string, uploaded_at: string }>
    analysis: Record<string, { content: string, filename: string, uploaded_at: string }>
  } | null>(null)
  const [tacticalLoading, setTacticalLoading] = useState(false)
  
  // Function to seek to specific timestamp
  const seekToTimestamp = (timestampInSeconds: number) => {
    // Use the global reference stored by VideoPlayer
    if ((window as any).videoPlayerSeek) {
      (window as any).videoPlayerSeek(timestampInSeconds)
    }
  }

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

  // Auto-open AI chat and start conversation when requested via sessionStorage
  useEffect(() => {
    if (!game) return
    
    try {
      const autoChatData = sessionStorage.getItem('autoChat')
      if (autoChatData) {
        const { message, timestamp } = JSON.parse(autoChatData)
        
        // Only use recent auto-chat requests (within last 30 seconds)
        if (Date.now() - timestamp < 30000) {
          console.log('🤖 Auto-opening AI chat and starting conversation')
          
          // Clear the sessionStorage so it doesn't repeat
          sessionStorage.removeItem('autoChat')
          
      // Delay slightly to let the page load
      setTimeout(() => {
            setShowSidebar(true)
            setSidebarTab('ai')
        setTimeout(() => {
              sendMessage(message)
        }, 800)
      }, 1500)
        } else {
          // Clean up old auto-chat data
          sessionStorage.removeItem('autoChat')
        }
      }
    } catch (error) {
      console.error('Error parsing autoChat data:', error)
      sessionStorage.removeItem('autoChat')
    }
  }, [game]) // Only depend on game, not chat functions

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
    if (currentEventIndex >= 0 && showSidebar) {
      const eventElement = document.getElementById(`event-${currentEventIndex}`)
      if (eventElement) {
        eventElement.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
          inline: 'nearest'
        })
      }
    }
  }, [currentEventIndex, showSidebar])

  const handleTimeUpdate = (time: number, dur: number) => {
      setCurrentTime(time)
    setDuration(dur)
  }

  const handleEventClick = (event: GameEvent) => {
    seekToTimestamp(event.timestamp)
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Video Section */}
    <div className="h-screen bg-black relative overflow-hidden">
        
        {/* Game Header */}
        <GameHeader
          game={game}
          teamScores={teamScores}
          currentTime={currentTime}
          showEvents={showSidebar}
          onToggleEvents={() => setShowSidebar(!showSidebar)}
        />

      {/* Video Container - with dynamic margins for sidebars */}
      <div 
        className="relative h-full flex items-center justify-center transition-all duration-300"
        style={{
          marginRight: showSidebar ? `${sidebarWidth}px` : '0'
        }}
      >
          
          <VideoPlayer
            game={game}
            events={filteredEvents}
            allEvents={allEvents}
            currentEventIndex={currentEventIndex}
          onTimeUpdate={handleTimeUpdate}
            onEventClick={handleEventClick}
            onSeekToTimestamp={seekToTimestamp}
          />

          </div>
          
        {/* Unified Sidebar */}
                <UnifiedSidebar
          isOpen={showSidebar}
          onClose={() => setShowSidebar(false)}
          activeTab={sidebarTab}
          onTabChange={setSidebarTab}
          onWidthChange={setSidebarWidth}
          events={filteredEvents}
          allEvents={allEvents}
          currentEventIndex={currentEventIndex}
          onEventClick={handleEventClick}
          eventTypeFilters={eventTypeFilters}
          setEventTypeFilters={setEventTypeFilters}
          teamFilter={teamFilter}
          setTeamFilter={setTeamFilter}
          showFilters={showFilters}
          setShowFilters={setShowFilters}
        tacticalData={tacticalData} 
        tacticalLoading={tacticalLoading} 
            gameId={gameId}
          onSeekToTimestamp={seekToTimestamp}
      />

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