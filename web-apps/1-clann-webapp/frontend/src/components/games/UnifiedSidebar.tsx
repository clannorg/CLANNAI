'use client'

import { useState, useEffect } from 'react'
import { useAIChat } from '../ai-chat'
import FifaStyleInsights from './FifaStyleInsights'

import { COACHES } from '../ai-chat/coaches'
import { getTeamInfo, getTeamColorClass } from '../../lib/team-utils'
import apiClient from '../../lib/api-client'

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
  
  // Game data for team metadata
  game: {
    id: string
    title: string
    metadata?: {
      teams?: {
        red_team: { name: string, jersey_color: string }
        blue_team: { name: string, jersey_color: string }
      }
    }
  }
  
  // Events tab props
  events: GameEvent[]
  allEvents: GameEvent[]
  currentEventIndex: number
  onEventClick: (event: GameEvent) => void
  eventTypeFilters: {
    goal: boolean
    shot: boolean
    save: boolean
    foul: boolean
    yellow_card: boolean
    red_card: boolean
    corner: boolean
    substitution: boolean
    turnover: boolean
  }
  setEventTypeFilters: React.Dispatch<React.SetStateAction<{
    goal: boolean
    shot: boolean
    save: boolean
    foul: boolean
    yellow_card: boolean
    red_card: boolean
    corner: boolean
    substitution: boolean
    turnover: boolean
  }>>
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
  
  // Video time for new event creation
  currentTime?: number
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
  game,
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
  onSeekToTimestamp,
  currentTime = 0
}: UnifiedSidebarProps) {
  // Auto-open AI Coach by default (mobile and desktop)
  const [internalActiveTab, setInternalActiveTab] = useState<TabType>('ai')
  const { messages, sendMessage, isLoading, inputValue, setInputValue, clearMessages, selectedCoach, setSelectedCoach } = useAIChat()
  const [chatInputValue, setChatInputValue] = useState('')
  const [sidebarWidth, setSidebarWidth] = useState(400) // Default 400px - wider for better usability

  // Get team information from metadata
  const { redTeam, blueTeam } = getTeamInfo(game)
  
  // Get dynamic colors for team filter buttons
  const redTeamColorClass = getTeamColorClass(redTeam.jersey_color)
  const blueTeamColorClass = getTeamColorClass(blueTeam.jersey_color)

  // Function to replace "red" and "blue" with actual team names in descriptions
  const transformDescription = (description: string) => {
    if (!description) return description
    
    return description
      .replace(/\bred\b/gi, redTeam.name)
      .replace(/\bblue\b/gi, blueTeam.name)
      .replace(/\bblack\b/gi, blueTeam.name) // Legacy support for "black" team
  }

  // Function to get team name from team type
  const getTeamName = (teamType: string) => {
    const teamLower = teamType.toLowerCase()
    
    // Handle descriptive team names
    if (teamLower.includes('orange bibs') || teamLower.includes('orange bib')) {
      return blueTeam.name
    }
    if (teamLower.includes('non bibs') || teamLower.includes('colours') || teamLower.includes('colors')) {
      return redTeam.name
    }
    
    // Handle standard color identifiers
    switch (teamLower) {
      case 'red': return redTeam.name
      case 'blue':
      case 'black': return blueTeam.name
      case 'orange': return blueTeam.name
      case 'white': return redTeam.name
      default: return teamType.charAt(0).toUpperCase() + teamType.slice(1)
    }
  }

  // Function to get team badge colors - white for clann, orange for lostthehead
  const getTeamBadgeColors = (teamType: string) => {
    const teamLower = teamType.toLowerCase()
    
    // Lostthehead gets nice orange
    if (teamLower.includes('lostthehead') || teamLower.includes('lost')) {
      return 'bg-orange-500/15 text-orange-200 border-orange-500/25'
    }
    
    // Everything else gets simple white
    return 'bg-white/10 text-white border-white/20'
  }

  // Get emoji for event type
  const getEventEmoji = (eventType: string) => {
    switch (eventType.toLowerCase()) {
      case 'goal': return '⚽'
      case 'shot': return '🎯'
      case 'foul': return '🚨'
      case 'turnover': return '🔄'
      case 'save': return '🥅'
      case 'kick_off': return '⚽'
      case 'corner': return '📐'
      case 'throw_in': return '👐'
      case 'free_kick': return '🦶'
      case 'penalty': return '🥅'
      case 'offside': return '🚫'
      case 'substitution': return '🔄'
      case 'yellow_card': return '🟨'
      case 'red_card': return '🟥'
      default: return '⚡'
    }
  }
  const [isResizing, setIsResizing] = useState(false)

  
  // Downloads state
  const [selectedEvents, setSelectedEvents] = useState<Set<number>>(new Set())
  const [isCreatingClip, setIsCreatingClip] = useState(false)
  
  // Manual annotation state
  const [binnedEvents, setBinnedEvents] = useState<Set<number>>(new Set())
  const [isSavingEvents, setIsSavingEvents] = useState(false)
  
  // New event creation state
  const [isCreatingEvent, setIsCreatingEvent] = useState(false)
  const [newEvent, setNewEvent] = useState({
    type: 'goal',
    timestamp: currentTime,
    team: redTeam.name.toLowerCase(),
    description: '',
    player: ''
  })
  
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

  // Manual annotation functions
  const handleBinEvent = async (eventIndex: number) => {
    const newBinned = new Set(binnedEvents)
    newBinned.add(eventIndex)
    setBinnedEvents(newBinned)
    
    // Also remove from selected events if it was selected
    const newSelected = new Set(selectedEvents)
    newSelected.delete(eventIndex)
    setSelectedEvents(newSelected)
    
    // Save to database
    await saveModifiedEvents()
  }
  
  const handleUnbinEvent = async (eventIndex: number) => {
    const newBinned = new Set(binnedEvents)
    newBinned.delete(eventIndex)
    setBinnedEvents(newBinned)
    
    // Save to database
    await saveModifiedEvents()
  }
  
  const saveModifiedEvents = async () => {
    if (!gameId || isSavingEvents) return
    
    setIsSavingEvents(true)
    try {
      // Create modified events array (filter out binned events)
      const modifiedEvents = allEvents
        .map((event, index) => ({ ...event, originalIndex: index }))
        .filter((_, index) => !binnedEvents.has(index))
      
      await apiClient.saveModifiedEvents(gameId, modifiedEvents)
      console.log('✅ Modified events saved successfully')
    } catch (error) {
      console.error('❌ Error saving modified events:', error)
      alert('Failed to save changes. Please try again.')
    } finally {
      setIsSavingEvents(false)
    }
  }

  // New event creation functions
  const handleStartCreatingEvent = () => {
    setNewEvent({
      type: 'goal',
      timestamp: Math.round(currentTime),
      team: redTeam.name.toLowerCase(),
      description: '',
      player: ''
    })
    setIsCreatingEvent(true)
  }

  const handleCancelNewEvent = () => {
    setIsCreatingEvent(false)
    setNewEvent({
      type: 'goal',
      timestamp: currentTime,
      team: redTeam.name.toLowerCase(),
      description: '',
      player: ''
    })
  }

  const handleSaveNewEvent = async () => {
    console.log('🔍 handleSaveNewEvent called', { gameId, isSavingEvents, newEvent })
    if (!gameId || isSavingEvents) return

    try {
      setIsSavingEvents(true)
      
      // Create the new event object
      const eventToAdd = {
        type: newEvent.type,
        timestamp: newEvent.timestamp,
        team: newEvent.team,
        description: newEvent.description.trim() || undefined,
        player: newEvent.player.trim() || undefined
      }
      console.log('🔍 Event to add:', eventToAdd)

      // Get current events and add the new one
      const currentEvents = allEvents
        .map((event, index) => ({ ...event, originalIndex: index }))
        .filter((_, index) => !binnedEvents.has(index))
      
      console.log('🔍 Current events count:', currentEvents.length)
      
      // Insert new event in chronological order
      const newEvents = [...currentEvents, eventToAdd]
        .sort((a, b) => a.timestamp - b.timestamp)

      console.log('🔍 New events count:', newEvents.length)
      console.log('🔍 Calling apiClient.saveModifiedEvents...')
      
      await apiClient.saveModifiedEvents(gameId, newEvents)
      console.log('✅ New event added successfully')
      
      // Reset form
      setIsCreatingEvent(false)
      setNewEvent({
        type: 'goal',
        timestamp: currentTime,
        team: redTeam.name.toLowerCase(),
        description: '',
        player: ''
      })
      
      // Show success message
      alert('✅ Event added successfully! Refreshing to show new event...')
      
      // Refresh after a short delay to let user see the success
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    } catch (error) {
      console.error('❌ Error adding new event:', error)
      alert('Failed to add event. Please try again.')
    } finally {
      setIsSavingEvents(false)
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
      
      // Call backend API using ApiClient (same pattern as everything else)
      const result = await apiClient.createClip(gameId, selectedEventData)
      console.log('✅ Clip created successfully:', result)
      
      // Download the clip using ApiClient
      try {
        const blob = await apiClient.downloadClip(result.downloadUrl)
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = result.fileName
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (downloadError: any) {
        console.error('Download failed:', downloadError)
        alert('Clip created but download failed. Please try again.')
        return
      }
      
      // Clear selection after successful creation
      setSelectedEvents(new Set())
      
      // Show success message with better formatting
      const message = `🎉 Highlight reel created!\n\n📊 ${result.eventCount} events\n⏱️ ${result.duration} seconds\n💾 Download completed!`
      alert(message)
      
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
                ? 'bg-green-500/10 text-green-300 border border-green-500/20'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span>Events</span>
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
            <span>Coach</span>
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
            <span>Stats</span>
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
            <span>Clips</span>
          </button>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {/* Events Tab */}
        {activeTab === 'events' && (
          <div className="h-full flex flex-col">
            {/* Team Filters - Always Visible */}
            <div className="p-4 border-b border-gray-700">
              <div className="space-y-4">
                <div>
                  <label className="text-gray-300 block mb-3 font-medium">Team:</label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => {
                        if (teamFilter === 'both') {
                          setTeamFilter('red') // Both selected -> Red only
                        } else if (teamFilter === 'red') {
                          setTeamFilter('blue') // Red only -> Blue only
                        } else {
                          setTeamFilter('both') // Blue only -> Both
                        }
                      }}
                      className={`h-12 text-xs font-semibold rounded-lg border-2 transition-colors ${
                        teamFilter === 'red' || teamFilter === 'both'
                          ? `${redTeamColorClass} hover:opacity-90`
                          : `bg-gray-500/20 text-gray-400 border-gray-500/30 hover:bg-gray-500/30`
                      }`}
                      title={`${redTeam.name} (${redTeam.jersey_color})`}
                    >
                      {redTeam.name.length > 8 ? redTeam.name.split(' ')[0] : redTeam.name}
                    </button>
                    <button
                      onClick={() => {
                        if (teamFilter === 'both') {
                          setTeamFilter('blue') // Both selected -> Blue only
                        } else if (teamFilter === 'blue' || teamFilter === 'black') {
                          setTeamFilter('red') // Blue only -> Red only
                        } else {
                          setTeamFilter('both') // Red only -> Both
                        }
                      }}
                      className={`h-12 text-xs font-semibold rounded-lg border-2 transition-colors ${
                        teamFilter === 'blue' || teamFilter === 'black' || teamFilter === 'both'
                          ? `${blueTeamColorClass} hover:opacity-90`
                          : `bg-gray-500/20 text-gray-400 border-gray-500/30 hover:bg-gray-500/30`
                      }`}
                      title={`${blueTeam.name} (${blueTeam.jersey_color})`}
                    >
                      {blueTeam.name.length > 8 ? blueTeam.name.split(' ')[0] : blueTeam.name}
                    </button>
                  </div>
                </div>

                {/* More Filters - Collapsible */}
                <div>
                  <button
                    onClick={() => setShowFilters(!showFilters)}
                    className="flex items-center justify-center px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border-2 w-full bg-gray-500/10 hover:bg-gray-500/20 border-gray-400/30 text-gray-300"
                    title="Toggle More Filters"
                  >
                    <div className="flex items-center space-x-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.414A1 1 0 013 6.707V4z" />
                      </svg>
                      <span>More Filters</span>
                      <svg className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>

                  </button>

                  {/* Event Type Filters - Collapsible */}
                  {showFilters && (
                    <div className="mt-4 space-y-4 text-sm">
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
                                        (acc as any)[key] = key === type
                                        return acc
                                      }, {} as typeof prev)
                                      return newFilters
                                    }
                                    
                                    // If only this one is selected, clicking it should show all
                                    if (selectedCount === 1 && (prev as any)[type]) {
                                      const newFilters = Object.keys(prev).reduce((acc, key) => {
                                        (acc as any)[key] = true
                                        return acc
                                      }, {} as typeof prev)
                                      return newFilters
                                    }
                                    
                                    // Otherwise, normal toggle
                                    return {
                                      ...prev,
                                      [type]: !(prev as any)[type]
                                    }
                                  })
                                }}
                                className={`h-9 text-xs font-medium rounded-lg border-2 transition-colors hover:scale-105 ${getFilterColor(type)}`}
                              >
                                {type.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                              </button>
                            )
                          })}
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

                {/* Add Event Button OR Inline Form */}
                <div>
                  {!isCreatingEvent ? (
                    // Add Event Button
                    <button
                      onClick={handleStartCreatingEvent}
                      disabled={isSavingEvents}
                      className="flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border-2 w-full bg-gray-500/10 hover:bg-gray-500/20 border-gray-400/30 text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Add new event at current time"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                      <span>Add Event</span>
                      <span className="text-xs text-gray-400">({Math.floor(currentTime / 60)}:{(currentTime % 60).toFixed(0).padStart(2, '0')})</span>
                    </button>
                  ) : (
                    // Inline Event Creation Form (replaces button)
                    <div className="p-3 rounded-lg bg-purple-900/20 border border-purple-500/30 space-y-3">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          {/* Time Input */}
                          <div className="flex items-center gap-1">
                            <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <input
                              type="text"
                              value={`${Math.floor(newEvent.timestamp / 60)}:${(newEvent.timestamp % 60).toString().padStart(2, '0')}`}
                              onChange={(e) => {
                                const timeStr = e.target.value
                                const parts = timeStr.split(':')
                                if (parts.length === 2) {
                                  const minutes = parseInt(parts[0]) || 0
                                  const seconds = parseInt(parts[1]) || 0
                                  if (seconds < 60) {
                                    setNewEvent({...newEvent, timestamp: minutes * 60 + seconds})
                                  }
                                }
                              }}
                              className="w-16 bg-gray-800 text-gray-300 text-xs font-mono px-2 py-1 rounded border border-gray-600 focus:border-purple-400 focus:outline-none"
                              placeholder="0:00"
                            />
                          </div>
                          
                          {/* Event Type Dropdown */}
                          <select
                            value={newEvent.type}
                            onChange={(e) => setNewEvent({...newEvent, type: e.target.value})}
                            className="bg-gray-800 text-gray-300 text-xs px-2 py-1 rounded border border-gray-600 focus:border-purple-400 focus:outline-none"
                          >
                            <option value="goal">Goal</option>
                            <option value="shot">Shot</option>
                            <option value="save">Save</option>
                            <option value="foul">Foul</option>
                            <option value="yellow_card">Yellow Card</option>
                            <option value="red_card">Red Card</option>
                            <option value="corner">Corner</option>
                            <option value="substitution">Substitution</option>
                            <option value="turnover">Turnover</option>
                            <option value="offside">Offside</option>
                          </select>
                          
                          {/* Team Dropdown */}
                          <select
                            value={newEvent.team}
                            onChange={(e) => setNewEvent({...newEvent, team: e.target.value})}
                            className="bg-gray-800 text-gray-300 text-xs px-2 py-1 rounded border border-gray-600 focus:border-purple-400 focus:outline-none"
                          >
                            <option value={redTeam.name.toLowerCase()}>{redTeam.name}</option>
                            <option value={blueTeam.name.toLowerCase()}>{blueTeam.name}</option>
                          </select>
                        </div>
                        
                        {/* Action Buttons */}
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => {
                              console.log('🔍 Save button clicked!')
                              handleSaveNewEvent()
                            }}
                            disabled={isSavingEvents}
                            className="p-1 text-green-400 hover:text-green-300 hover:bg-green-500/10 rounded transition-colors disabled:opacity-50"
                            title="Save event"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          </button>
                          
                          <button
                            onClick={handleCancelNewEvent}
                            disabled={isSavingEvents}
                            className="p-1 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition-colors disabled:opacity-50"
                            title="Cancel"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      </div>
                      
                      {/* Description Input */}
                      <div>
                        <input
                          type="text"
                          value={newEvent.description}
                          onChange={(e) => setNewEvent({...newEvent, description: e.target.value})}
                          placeholder="Event description..."
                          className="w-full bg-gray-800 text-gray-300 text-xs px-3 py-2 rounded border border-gray-600 focus:border-purple-400 focus:outline-none"
                        />
                      </div>
                      
                      {/* Player Input */}
                      <div>
                        <input
                          type="text"
                          value={newEvent.player}
                          onChange={(e) => setNewEvent({...newEvent, player: e.target.value})}
                          placeholder="Player name/number (optional)..."
                          className="w-full bg-gray-800 text-gray-300 text-xs px-3 py-2 rounded border border-gray-600 focus:border-purple-400 focus:outline-none"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* Events List - Only events scroll */}
            <div className="flex-1 overflow-y-auto p-4">
              <div className="space-y-2">
                {events.map((event, index) => {
                  const originalIndex = allEvents.indexOf(event)
                  const isBinned = binnedEvents.has(originalIndex)
                  
                  // Skip binned events
                  if (isBinned) return null
                  
                  return (
                    <div
                      key={`${event.timestamp}-${event.type}-${index}`}
                      id={`event-${originalIndex}`}
                      onClick={() => onEventClick(event)}
                      className={`w-full text-left p-3 rounded-lg transition-all duration-200 border cursor-pointer ${
                        originalIndex === currentEventIndex 
                          ? 'bg-blue-600/20 text-white border-blue-500 ring-1 ring-blue-500' 
                          : 'bg-gray-800/60 text-gray-300 hover:bg-gray-700/60 border-gray-700 hover:border-gray-600'
                      }`}
                    >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {/* Time Badge - moved to front */}
                        <div className="flex items-center gap-1">
                          <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span className="text-xs text-gray-400 font-mono">{formatTime(event.timestamp)}</span>
                        </div>
                        
                        {/* Event Type Badge */}
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium border ${
                          event.type === 'goal' ? 'bg-green-500/20 text-green-300 border-green-500/30' :
                          event.type === 'shot' ? 'bg-blue-500/20 text-blue-300 border-blue-500/30' :
                          event.type === 'foul' ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' :
                          event.type === 'turnover' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' :
                          event.type === 'save' ? 'bg-orange-500/20 text-orange-300 border-orange-500/30' :
                          'bg-gray-500/20 text-gray-300 border-gray-500/30'
                        }`}>
                          <span>{getEventEmoji(event.type)}</span>
                          <span>{event.type.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</span>
                        </span>
                        
                        {/* Team Badge */}
                        {event.team && (
                          <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${getTeamBadgeColors(event.team)}`}>
                            {getTeamName(event.team)}
                          </span>
                        )}
                      </div>
                      
                      {/* Action Buttons - bin and edit */}
                      <div className="flex items-center gap-1">
                        {/* Bin Button */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleBinEvent(originalIndex)
                          }}
                          disabled={isSavingEvents}
                          className="p-1 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                          title="Delete this event"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                        
                        {/* Edit Button */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            // TODO: Open edit modal
                            console.log('Edit event:', event)
                          }}
                          className="p-1 text-gray-400 hover:text-blue-400 hover:bg-blue-500/10 rounded transition-colors"
                          title="Edit this event"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    
                    {/* Description */}
                    {event.description && (
                      <div className="text-xs text-gray-400 mt-2 leading-relaxed">{transformDescription(event.description)}</div>
                    )}
                    
                    {/* Player */}
                    {event.player && (
                      <div className="text-xs text-gray-500 mt-1 italic">{event.player}</div>
                    )}
                  </div>
                )
                })}
                
                {/* Binned Events Section */}
                {binnedEvents.size > 0 && (
                  <div className="mt-6 pt-4 border-t border-gray-700">
                    <h5 className="text-white font-medium mb-3">🗑️ Deleted Events ({binnedEvents.size}):</h5>
                    <div className="space-y-2">
                      {allEvents.map((event, index) => {
                        if (!binnedEvents.has(index)) return null
                        
                        return (
                          <div
                            key={`binned-${event.timestamp}-${event.type}-${index}`}
                            className="flex items-center justify-between gap-2 p-3 rounded-lg bg-red-900/20 border border-red-500/30 opacity-75"
                          >
                            <div className="flex items-center gap-2">
                              {/* Time Badge */}
                              <div className="flex items-center gap-1">
                                <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span className="text-xs text-gray-400 font-mono">{formatTime(event.timestamp)}</span>
                              </div>
                              
                              {/* Event Type Badge */}
                              <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium border ${
                                event.type === 'goal' ? 'bg-green-500/20 text-green-300 border-green-500/30' :
                                event.type === 'shot' ? 'bg-blue-500/20 text-blue-300 border-blue-500/30' :
                                event.type === 'foul' ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' :
                                event.type === 'turnover' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' :
                                event.type === 'save' ? 'bg-orange-500/20 text-orange-300 border-orange-500/30' :
                                'bg-gray-500/20 text-gray-300 border-gray-500/30'
                              }`}>
                                <span>{getEventEmoji(event.type)}</span>
                                <span>{event.type.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</span>
                              </span>
                              
                              {/* Team Badge */}
                              {event.team && (
                                <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${getTeamBadgeColors(event.team)}`}>
                                  {getTeamName(event.team)}
                                </span>
                              )}
                            </div>
                            
                            {/* Restore Button */}
                            <button
                              onClick={() => handleUnbinEvent(index)}
                              disabled={isSavingEvents}
                              className="p-1 text-gray-400 hover:text-green-400 hover:bg-green-500/10 rounded transition-colors"
                              title="Restore this event"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                              </svg>
                            </button>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* AI Coach Tab */}
        {activeTab === 'ai' && (
          <div className="h-full flex flex-col">
            <div className="p-4 border-b border-gray-700">
              <h4 className="text-lg font-semibold text-white mb-3">AI Coach</h4>
              
              {/* Coach Selection Cards */}
              <div className="grid grid-cols-3 gap-2 mb-3">
                {COACHES.map((coach) => (
                  <button
                    key={coach.id}
                    onClick={() => setSelectedCoach(coach)}
                    className={`p-3 rounded-lg border-2 transition-all duration-200 ${
                      selectedCoach?.id === coach.id
                        ? 'border-green-500 bg-green-500/10'
                        : 'border-gray-600 bg-gray-800/30 hover:border-gray-500 hover:bg-gray-800/50'
                    }`}
                  >
                    <div className="flex flex-col items-center space-y-2">
                      <div className="w-20 h-20 rounded-lg overflow-hidden border border-gray-600">
                        <img 
                          src={coach.image} 
                          alt={coach.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="text-center">
                        <div className="text-xs font-medium text-white leading-tight">
                          {coach.name.split(' ')[0]} {/* First name only for space */}
                        </div>
                        <div className={`text-xs px-1.5 py-0.5 rounded-full mt-1 ${
                          selectedCoach?.id === coach.id
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-700 text-gray-300'
                        }`}>
                          {coach.title}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
            
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center py-8">
                  <svg className="w-12 h-12 mx-auto mb-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <h5 className="text-white font-medium mb-3">Ready to Coach!</h5>
                  <div className="space-y-2">
                    <button
                      onClick={() => sendMessage("What specific training drills should we focus on based on this match?")}
                      className="w-full text-left p-3 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-colors border border-gray-600 hover:border-green-500"
                    >
                      <span className="text-green-400 mr-2">🏃</span>
                      <span className="text-gray-300 text-sm">Training drills recommendations</span>
                    </button>
                    
                    <button
                      onClick={() => sendMessage("What tactical adjustments should we make based on this match analysis?")}
                      className="w-full text-left p-3 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-colors border border-gray-600 hover:border-green-500"
                    >
                      <span className="text-blue-400 mr-2">⚽</span>
                      <span className="text-gray-300 text-sm">Tactical analysis</span>
                    </button>
                    
                    <button
                      onClick={() => sendMessage("What key moments from this match should we review and learn from?")}
                      className="w-full text-left p-3 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-colors border border-gray-600 hover:border-green-500"
                    >
                      <span className="text-yellow-400 mr-2">🎯</span>
                      <span className="text-gray-300 text-sm">Key moments analysis</span>
                    </button>
                    
                    <button
                      onClick={() => sendMessage("How should we prepare for our next match based on this analysis?")}
                      className="w-full text-left p-3 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg transition-colors border border-gray-600 hover:border-green-500"
                    >
                      <span className="text-purple-400 mr-2">📈</span>
                      <span className="text-gray-300 text-sm">Match preparation tips</span>
                    </button>
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
                game={{
                  ...game,
                  ai_analysis: allEvents
                }}
              />
            </div>
          </div>
        )}

        {/* Downloads Tab */}
        {activeTab === 'downloads' && (
          <div className="h-full flex flex-col">
            {/* Header - Fixed at top */}
            <div className="p-4 border-b border-gray-700">
              <h4 className="text-lg font-semibold text-white mb-2">📥 Create Highlights</h4>
              <p className="text-sm text-gray-400">Select events to create a highlight reel for social media</p>
            </div>
            
            {/* Event Selection - Scrollable middle */}
            <div className="flex-1 overflow-y-auto p-4">
              <div>
                <h5 className="text-white font-medium mb-3">Select Events (Max 5):</h5>
                <div className="space-y-2">
                  {allEvents.slice(0, 20).map((event, index) => {
                    const isBinned = binnedEvents.has(index)
                    const isSelected = selectedEvents.has(index)
                    const isDisabled = !isSelected && selectedEvents.size >= 5
                    
                    // Skip binned events
                    if (isBinned) return null
                    
                    return (
                      <div
                        key={`${event.timestamp}-${event.type}-${index}`}
                        className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                          isSelected 
                            ? 'bg-orange-500/20 border border-orange-500/30' 
                            : isDisabled 
                              ? 'bg-gray-800/20 opacity-50'
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
                            {transformDescription(event.description || '')}
                          </p>
                        </div>
                        
                        {/* Bin Button */}
                        <button
                          onClick={() => handleBinEvent(index)}
                          disabled={isSavingEvents}
                          className="p-1 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                          title="Delete this event"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    )
                  })}
                </div>
                
                {/* Binned Events Section */}
                {binnedEvents.size > 0 && (
                  <div className="mt-6 pt-4 border-t border-gray-700">
                    <h5 className="text-white font-medium mb-3">🗑️ Deleted Events ({binnedEvents.size}):</h5>
                    <div className="space-y-2">
                      {allEvents.map((event, index) => {
                        if (!binnedEvents.has(index)) return null
                        
                        return (
                          <div
                            key={`binned-${event.timestamp}-${event.type}-${index}`}
                            className="flex items-center space-x-3 p-3 rounded-lg bg-red-900/20 border border-red-500/30 opacity-75"
                          >
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
                                {transformDescription(event.description || '')}
                              </p>
                            </div>
                            
                            {/* Restore Button */}
                            <button
                              onClick={() => handleUnbinEvent(index)}
                              disabled={isSavingEvents}
                              className="p-1 text-gray-400 hover:text-green-400 hover:bg-green-500/10 rounded transition-colors"
                              title="Restore this event"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                              </svg>
                            </button>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Summary + Button - Pinned at bottom */}
            <div className="border-t border-gray-700 p-4 space-y-4">
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
        )}
      </div>
    </div>
  )
}