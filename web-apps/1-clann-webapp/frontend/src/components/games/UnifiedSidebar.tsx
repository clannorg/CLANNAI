'use client'

import { useState, useEffect } from 'react'
import { useAIChat } from '../ai-chat'
import FifaStyleInsights from './FifaStyleInsights'

interface GameEvent {
  type: string
  timestamp: number
  player?: string
  description?: string
  team?: string
}

interface UnifiedSidebarProps {
  isOpen: boolean
  onClose: () => void
  activeTab?: 'events' | 'ai' | 'insights' | 'downloads'
  onTabChange?: (tab: 'events' | 'ai' | 'insights' | 'downloads') => void
  onWidthChange?: (width: number) => void
  isMobile?: boolean // New prop for mobile positioning
  mobileVideoComponent?: React.ReactNode // Video component for mobile header
  
  // Events tab props
  events: GameEvent[]
  allEvents: GameEvent[]
  currentEventIndex: number
  onEventClick: (event: GameEvent) => void
  eventTypeFilters: Record<string, boolean>
  setEventTypeFilters: (filters: Record<string, boolean> | ((prev: Record<string, boolean>) => Record<string, boolean>)) => void
  teamFilter: string
  setTeamFilter: (filter: string) => void
  showFilters: boolean
  setShowFilters: (show: boolean) => void
  
  // Insights tab props
  tacticalData: {
    tactical: Record<string, { content: string, filename: string, uploaded_at: string }>
    analysis: Record<string, { content: string, filename: string, uploaded_at: string }>
  } | null
  tacticalLoading: boolean
  gameId: string
  onSeekToTimestamp: (timestamp: number) => void
}

type TabType = 'events' | 'ai' | 'insights' | 'downloads'

export default function UnifiedSidebar({
  isOpen,
  onClose,
  activeTab: externalActiveTab,
  onTabChange,
  onWidthChange,
  isMobile = false,
  mobileVideoComponent,
  events,
  allEvents,
  currentEventIndex,
  onEventClick,
  eventTypeFilters,
  setEventTypeFilters,
  teamFilter,
  setTeamFilter,
  showFilters,
  setShowFilters,
  tacticalData,
  tacticalLoading,
  gameId,
  onSeekToTimestamp
}: UnifiedSidebarProps) {
  const [internalActiveTab, setInternalActiveTab] = useState<TabType>('events')
  const { messages, sendMessage, isLoading, inputValue, setInputValue, clearMessages } = useAIChat()
  const [chatInputValue, setChatInputValue] = useState('')
  const [sidebarWidth, setSidebarWidth] = useState(400) // Default 400px - wider for better usability
  const [isResizing, setIsResizing] = useState(false)
  
  // Downloads state
  const [selectedEvents, setSelectedEvents] = useState<Set<number>>(new Set())
  const [isCreatingClip, setIsCreatingClip] = useState(false)
  
  // Use external active tab if provided, otherwise use internal
  const activeTab = externalActiveTab || internalActiveTab
  
  const handleTabChange = (newTab: TabType) => {
    if (onTabChange) {
      onTabChange(newTab)
    } else {
      setInternalActiveTab(newTab)
    }
  }

  const handleSendMessage = async () => {
    if (!chatInputValue.trim() || isLoading) return
    await sendMessage(chatInputValue)
    setChatInputValue('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // Downloads functions
  const handleEventSelection = (eventIndex: number) => {
    const newSelected = new Set(selectedEvents)
    if (newSelected.has(eventIndex)) {
      newSelected.delete(eventIndex)
    } else if (newSelected.size < 5) {
      newSelected.add(eventIndex)
    }
    setSelectedEvents(newSelected)
  }

  const handleCreateClip = async () => {
    if (selectedEvents.size === 0) return
    
    setIsCreatingClip(true)
    
    try {
      // Get selected event timestamps
      const selectedEventData = Array.from(selectedEvents).map(index => ({
        timestamp: allEvents[index].timestamp,
        type: allEvents[index].type,
        description: allEvents[index].description
      }))
      
      console.log('🎬 Creating clip with events:', selectedEventData)
      
      // Call backend API to create clip
      const response = await fetch('http://localhost:3002/api/clips/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          gameId: gameId,
          events: selectedEventData
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to create clip')
      }

      const result = await response.json()
      console.log('✅ Clip created successfully:', result)
      
      // Create download link with authentication token
      const token = localStorage.getItem('token')
      const link = document.createElement('a')
      link.href = `http://localhost:3002${result.downloadUrl}`
      link.download = result.fileName
      link.style.display = 'none'
      
      // Add authorization header by creating a fetch request instead of direct link
      fetch(`http://localhost:3002${result.downloadUrl}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(response => response.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = result.fileName
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      })
      .catch((error: any) => {
        console.error('Download failed:', error)
        alert('Download failed. Please try again.')
      })
      
      // Clear selection after successful creation
      setSelectedEvents(new Set())
      
      alert(`🎉 Highlight reel created! (${result.eventCount} events, ${result.duration}s)\nDownload started automatically.`)
      
    } catch (error: any) {
      console.error('❌ Error creating clip:', error)
      alert(`Error creating clip: ${error.message}`)
    } finally {
      setIsCreatingClip(false)
    }
  }

  // Handle drag resize
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsResizing(true)
    
    const startX = e.clientX
    const startWidth = sidebarWidth

    const handleMouseMove = (e: MouseEvent) => {
      const deltaX = startX - e.clientX // Reverse direction for right sidebar
      const newWidth = Math.max(280, Math.min(600, startWidth + deltaX)) // Min 280px, Max 600px
      setSidebarWidth(newWidth)
      if (onWidthChange) {
        onWidthChange(newWidth)
      }
    }

    const handleMouseUp = () => {
      setIsResizing(false)
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = 'default'
      document.body.style.userSelect = 'auto'
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    document.body.style.cursor = 'ew-resize'
    document.body.style.userSelect = 'none'
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const getEventColor = (type: string) => {
    const colors: { [key: string]: string } = {
      goal: '#22c55e',
      shot: '#3b82f6', 
      save: '#f59e0b',
      foul: '#ef4444',
      'yellow card': '#eab308',
      'red card': '#dc2626',
      corner: '#06b6d4',
      substitution: '#8b5cf6',
      turnover: '#a855f7'
    }
    return colors[type.toLowerCase()] || '#6b7280'
  }

  if (!isOpen) return null

  return (
    <div 
      className={`${
        isMobile 
          ? 'relative w-full min-h-svh bg-black/90 backdrop-blur-sm border-t border-gray-700'
          : 'absolute top-0 right-0 h-full bg-black/90 backdrop-blur-sm border-l border-gray-700'
      } flex flex-col z-30`}
      style={isMobile ? {} : { 
        width: `${sidebarWidth}px`,
        minWidth: '280px',
        maxWidth: '600px'
      }}
    >
      {/* Mobile Video Header - sticky so it does not scroll */}
      {isMobile && mobileVideoComponent && (
        <div className="sticky top-0 z-30 bg-black">
          {mobileVideoComponent}
        </div>
      )}

      {/* Resize Handle */}
      <div
        className={`absolute left-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-blue-500/50 transition-colors ${
          isResizing ? 'bg-blue-500' : 'bg-transparent hover:bg-gray-500/30'
        }`}
        onMouseDown={handleMouseDown}
        title="Drag to resize"
      >
        <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-3 h-8 -ml-1 flex items-center justify-center">
          <div className={`w-0.5 h-4 bg-gray-500 rounded-full transition-all ${
            isResizing ? 'bg-blue-500 scale-110' : 'hover:bg-gray-400'
          }`} />
        </div>
      </div>
      {/* Tab Header - sticky; on mobile, offset by video height (16:9 => 56.25vw) */}
      <div className={`sticky bg-black/90 backdrop-blur-sm border-b border-gray-700 p-4 z-10 ${
        isMobile ? 'top-[56.25vw]' : 'top-0'
      }`}>
        <div className="flex items-center justify-between">
          {/* Close Button - Hidden on Mobile */}
          {!isMobile && (
            <button
              onClick={onClose}
              className="mr-3 flex items-center justify-center w-8 h-8 text-gray-400 hover:text-white hover:bg-gray-700/50 rounded-lg transition-all duration-200"
              title="Close Sidebar"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          )}
          
          {/* Tab Navigation */}
          <div className="flex bg-gray-800/50 rounded-lg p-1 flex-1">
          <button
            onClick={() => handleTabChange('events')}
            className={`flex-1 flex items-center justify-center space-x-2 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200 ${
              activeTab === 'events'
                ? 'bg-green-500/20 text-green-200 border border-green-500/30'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span>Events</span>
            {activeTab === 'events' && (
              <span className="inline-flex items-center justify-center w-5 h-5 text-xs bg-green-500 text-white rounded-full">
                {events.length}
              </span>
            )}
          </button>

          <button
            onClick={() => handleTabChange('ai')}
            className={`flex-1 flex items-center justify-center space-x-2 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200 ${
              activeTab === 'ai'
                ? 'bg-blue-500/20 text-blue-200 border border-blue-500/30'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <span>AI Coach</span>
          </button>

          <button
            onClick={() => handleTabChange('insights')}
            className={`flex-1 flex items-center justify-center space-x-2 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200 ${
              activeTab === 'insights'
                ? 'bg-purple-500/20 text-purple-200 border border-purple-500/30'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span>Insights</span>
          </button>

          <button
            onClick={() => handleTabChange('downloads')}
            className={`flex-1 flex items-center justify-center space-x-2 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200 ${
              activeTab === 'downloads'
                ? 'bg-orange-500/20 text-orange-200 border border-orange-500/30'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Downloads</span>
          </button>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {/* Events Tab */}
        {activeTab === 'events' && (
          <div className="h-full flex flex-col">
            {/* Filter Controls */}
            <div className="p-4 border-b border-gray-700">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border-2 w-full ${
                  showFilters 
                    ? 'bg-green-500/20 hover:bg-green-500/30 border-green-400/60 text-green-200 shadow-lg shadow-green-500/10' 
                    : 'bg-blue-500/20 hover:bg-blue-500/30 border-blue-400/60 text-blue-200 shadow-lg shadow-blue-500/10'
                }`}
                title="Toggle Filters"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.414A1 1 0 013 6.707V4z" />
                </svg>
                <span>{showFilters ? 'Hide Filters' : 'Show Filters'}</span>
                {!showFilters && (
                  <span className="inline-flex items-center justify-center w-5 h-5 text-xs bg-blue-500 text-white rounded-full ml-auto">
                    {Object.values(eventTypeFilters).filter(Boolean).length}
                  </span>
                )}
              </button>

              {/* Filter Controls */}
              {showFilters && (
                <div className="mt-4 space-y-4 text-sm">
                  {/* Event Type Filters - Pill Buttons */}
                  <div>
                    <label className="text-gray-300 block mb-3 font-medium">Event Types:</label>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(eventTypeFilters).map(([type, enabled]) => {
                        const getFilterColor = (eventType: string) => {
                          switch (eventType.toLowerCase()) {
                            case 'goal': return enabled ? 'bg-green-500 text-white border-green-500' : 'bg-green-500/20 text-green-400 border-green-500/30'
                            case 'shot': return enabled ? 'bg-blue-500 text-white border-blue-500' : 'bg-blue-500/20 text-blue-400 border-blue-500/30'
                            case 'foul': return enabled ? 'bg-red-500 text-white border-red-500' : 'bg-red-500/20 text-red-400 border-red-500/30'
                            case 'yellow_card': return enabled ? 'bg-yellow-500 text-black border-yellow-500' : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
                            case 'red_card': return enabled ? 'bg-red-600 text-white border-red-600' : 'bg-red-600/20 text-red-400 border-red-600/30'
                            case 'substitution': return enabled ? 'bg-purple-500 text-white border-purple-500' : 'bg-purple-500/20 text-purple-400 border-purple-500/30'
                            case 'corner': return enabled ? 'bg-cyan-500 text-white border-cyan-500' : 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30'
                            case 'turnover': return enabled ? 'bg-purple-500 text-white border-purple-500' : 'bg-purple-500/20 text-purple-400 border-purple-500/30'
                            case 'save': return enabled ? 'bg-orange-500 text-white border-orange-500' : 'bg-orange-500/20 text-orange-400 border-orange-500/30'
                            default: return enabled ? 'bg-gray-500 text-white border-gray-500' : 'bg-gray-500/20 text-gray-400 border-gray-500/30'
                          }
                        }
                        
                        return (
                          <button
                            key={type}
                            onClick={() => {
                              setEventTypeFilters(prev => {
                                const currentValues = Object.values(prev)
                                const allSelected = currentValues.every(val => val === true)
                                const selectedCount = currentValues.filter(val => val === true).length
                                
                                // If all are selected, clicking one should show only that one
                                if (allSelected) {
                                  const newFilters = Object.keys(prev).reduce((acc, key) => {
                                    acc[key] = key === type
                                    return acc
                                  }, {} as typeof prev)
                                  return newFilters
                                }
                                
                                // If only this one is selected, clicking it should show all
                                if (selectedCount === 1 && prev[type]) {
                                  const newFilters = Object.keys(prev).reduce((acc, key) => {
                                    acc[key] = true
                                    return acc
                                  }, {} as typeof prev)
                                  return newFilters
                                }
                                
                                // Otherwise, normal toggle
                                return {
                                  ...prev,
                                  [type]: !prev[type]
                                }
                              })
                            }}
                            className={`h-9 text-xs font-medium rounded-lg border-2 transition-colors hover:scale-105 ${getFilterColor(type)}`}
                          >
                            {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  {/* Team Filter - Big Buttons */}
                  <div>
                    <label className="text-gray-300 block mb-3 font-medium">Team:</label>
                    <div className="grid grid-cols-3 gap-2">
                      <button
                        onClick={() => setTeamFilter('both')}
                        className={`h-10 text-sm font-semibold rounded-lg border-2 transition-colors ${
                          teamFilter === 'both'
                            ? 'bg-white text-black hover:bg-gray-200 border-white'
                            : 'bg-white/10 text-white hover:bg-white/20 border-white/30'
                        }`}
                      >
                        Both
                      </button>
                      <button
                        onClick={() => setTeamFilter('red')}
                        className={`h-10 text-sm font-semibold rounded-lg border-2 transition-colors ${
                          teamFilter === 'red'
                            ? 'bg-red-500 text-white hover:bg-red-600 border-red-500'
                            : 'bg-red-500/20 text-red-400 hover:bg-red-500/30 border-red-500/30'
                        }`}
                      >
                        Red
                      </button>
                      <button
                        onClick={() => setTeamFilter('black')}
                        className={`h-10 text-sm font-semibold rounded-lg border-2 transition-colors ${
                          teamFilter === 'black'
                            ? 'bg-blue-500 text-white hover:bg-blue-600 border-blue-500'
                            : 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 border-blue-500/30'
                        }`}
                      >
                        Black
                      </button>
                    </div>
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
                        substitution: true,
                        turnover: true
                      })
                      setTeamFilter('both')
                    }}
                    className="w-full bg-gray-600/80 hover:bg-gray-500/80 text-white text-sm py-2.5 rounded-lg transition-colors font-medium"
                  >
                    Reset All Filters
                  </button>
                </div>
              )}
            </div>
            
            {/* Events List */}
            <div className="flex-1 overflow-y-auto p-4">
              <div className="space-y-2">
                {events.map((event, index) => {
                  const originalIndex = allEvents.indexOf(event)
                  return (
                  <button
                      key={`${event.timestamp}-${event.type}-${index}`}
                      id={`event-${originalIndex}`}
                    onClick={() => onEventClick(event)}
                    className={`w-full text-left p-3 rounded-lg transition-all duration-200 border ${
                        originalIndex === currentEventIndex 
                        ? 'bg-blue-600/20 text-white border-blue-500 ring-1 ring-blue-500' 
                        : 'bg-gray-800/60 text-gray-300 hover:bg-gray-700/60 border-gray-700 hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {/* Event Type Badge */}
                        <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${
                          event.type === 'goal' ? 'bg-green-500/20 text-green-300 border-green-500/30' :
                          event.type === 'shot' ? 'bg-blue-500/20 text-blue-300 border-blue-500/30' :
                          event.type === 'foul' ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' :
                          event.type === 'turnover' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' :
                          event.type === 'save' ? 'bg-orange-500/20 text-orange-300 border-orange-500/30' :
                          'bg-gray-500/20 text-gray-300 border-gray-500/30'
                        }`}>
                          {event.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                        
                        {/* Team Badge */}
                        {event.team && (
                          <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${
                            event.team === 'red' 
                              ? 'bg-red-500/20 text-red-300 border-red-500/30' 
                              : 'bg-blue-500/20 text-blue-300 border-blue-500/30'
                          }`}>
                            {event.team.charAt(0).toUpperCase() + event.team.slice(1)}
                          </span>
                        )}
                      </div>
                      
                      {/* Time Badge */}
                      <div className="flex items-center gap-1">
                        <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="text-xs text-gray-400 font-mono">{formatTime(event.timestamp)}</span>
                      </div>
                    </div>
                    
                    {/* Description */}
                    {event.description && (
                      <div className="text-xs text-gray-400 mt-2 leading-relaxed">{event.description}</div>
                    )}
                    
                    {/* Player */}
                    {event.player && (
                      <div className="text-xs text-gray-500 mt-1 italic">{event.player}</div>
                    )}
                  </button>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {/* AI Coach Tab */}
        {activeTab === 'ai' && (
          <div className="h-full flex flex-col">
            <div className="p-4 border-b border-gray-700">
              <h4 className="text-lg font-semibold text-white mb-2">AI Coach</h4>
              <p className="text-sm text-gray-400">Get personalized coaching insights and training recommendations.</p>
            </div>
            
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center py-8">
                  <svg className="w-12 h-12 mx-auto mb-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <h5 className="text-white font-medium mb-2">Ready to Coach!</h5>
                  <p className="text-gray-400 text-sm mb-4">Ask me about:</p>
                  <div className="space-y-2 text-sm text-gray-300">
                    <div>• Training drills recommendations</div>
                    <div>• Tactical analysis</div>
                    <div>• Player performance insights</div>
                    <div>• Match preparation tips</div>
                  </div>
                </div>
              ) : (
                messages.map((message, index) => (
                  <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] rounded-lg p-3 ${
                      message.role === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-700 text-gray-100'
                    }`}>
                      <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                    </div>
                  </div>
                ))
              )}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-700 text-gray-100 rounded-lg p-3 max-w-[80%]">
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
                      <span className="text-sm">AI Coach is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {/* Chat Input */}
            <div className="sticky bottom-0 z-20 bg-black/95 border-t border-gray-700 p-4 pb-[max(env(safe-area-inset-bottom),16px)]">
              <div className="flex items-end space-x-3">
                <input
                  type="text"
                  placeholder="Ask the AI coach..."
                  value={chatInputValue}
                  onChange={(e) => setChatInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isLoading}
                  className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white text-sm placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!chatInputValue.trim() || isLoading}
                  className="flex items-center justify-center w-12 h-12 bg-blue-500 hover:bg-blue-600 disabled:bg-white/10 text-white rounded-xl transition-all duration-200"
                >
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  )}
                </button>
              </div>
              {messages.length > 0 && (
                <button
                  onClick={clearMessages}
                  className="text-xs text-white/60 hover:text-white/80 mt-3 px-2 py-1 rounded-lg hover:bg-white/5"
                >
                  Clear chat
                </button>
              )}
            </div>
          </div>
        )}

        {/* Insights Tab */}
        {activeTab === 'insights' && (
          <div className="h-full overflow-y-auto">
            <div className="p-4">
              <h4 className="text-lg font-semibold text-white mb-4">Game Insights</h4>
              <FifaStyleInsights 
                tacticalData={tacticalData} 
                tacticalLoading={tacticalLoading} 
                gameId={gameId}
                onSeekToTimestamp={onSeekToTimestamp}
              />
            </div>
          </div>
        )}

        {/* Downloads Tab */}
        {activeTab === 'downloads' && (
          <div className="h-full flex flex-col">
            <div className="p-4 border-b border-gray-700">
              <h4 className="text-lg font-semibold text-white mb-2">📥 Create Highlights</h4>
              <p className="text-sm text-gray-400">Select events to create a highlight reel for social media</p>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4">
              <div className="space-y-4">
                {/* Event Selection */}
                <div>
                  <h5 className="text-white font-medium mb-3">Select Events (Max 5):</h5>
                  <div className="space-y-2">
                    {allEvents.slice(0, 20).map((event, index) => {
                      const isSelected = selectedEvents.has(index)
                      const isDisabled = !isSelected && selectedEvents.size >= 5
                      
                      return (
                        <label
                          key={`${event.timestamp}-${event.type}-${index}`}
                          className={`flex items-center space-x-3 p-3 rounded-lg transition-colors cursor-pointer ${
                            isSelected 
                              ? 'bg-orange-500/20 border border-orange-500/30' 
                              : isDisabled 
                                ? 'bg-gray-800/20 opacity-50 cursor-not-allowed'
                                : 'bg-gray-800/30 hover:bg-gray-800/50'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => !isDisabled && handleEventSelection(index)}
                            disabled={isDisabled}
                            className="w-4 h-4 text-orange-500 bg-gray-700 border-gray-600 rounded focus:ring-orange-500 focus:ring-2"
                          />
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <span 
                                className={`inline-block w-3 h-3 rounded-full`}
                                style={{ backgroundColor: getEventColor(event.type) }}
                              />
                              <span className="text-white font-medium capitalize">
                                {event.type}
                              </span>
                              <span className="text-gray-400 text-sm">
                                {formatTime(event.timestamp)}
                              </span>
                            </div>
                            <p className="text-gray-300 text-sm mt-1">
                              {event.description}
                            </p>
                          </div>
                        </label>
                      )
                    })}
                  </div>
                </div>

                {/* Summary */}
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-white font-medium">Selected Events:</span>
                    <span className="text-orange-400 font-bold">{selectedEvents.size} / 5</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-white font-medium">Estimated Duration:</span>
                    <span className="text-orange-400 font-bold">{selectedEvents.size * 10}s</span>
                  </div>
                </div>

                {/* Create Button */}
                <button
                  onClick={handleCreateClip}
                  disabled={selectedEvents.size === 0 || isCreatingClip}
                  className={`w-full font-semibold py-3 px-4 rounded-lg transition-colors border ${
                    selectedEvents.size === 0 || isCreatingClip
                      ? 'bg-gray-700/50 text-gray-500 border-gray-600 cursor-not-allowed'
                      : 'bg-orange-500/20 hover:bg-orange-500/30 text-orange-200 border-orange-500/30 hover:border-orange-500/40'
                  }`}
                >
                  {isCreatingClip ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-4 h-4 border-2 border-orange-400 border-t-transparent rounded-full animate-spin"></div>
                      <span>Creating Clip...</span>
                    </div>
                  ) : (
                    'Create Highlight Reel'
                  )}
                </button>

                {/* Info */}
                <div className="text-xs text-gray-500 text-center">
                  Each event includes 10 seconds (5s before + 5s after)
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}