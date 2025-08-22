'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useAIChat } from '../ai-chat'
import FifaStyleInsights from './FifaStyleInsights'
import AppleStyleTrimmer from './AppleStyleTrimmer'

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
  activeTab?: 'events' | 'ai' | 'insights' | 'players'
  onTabChange?: (tab: 'events' | 'ai' | 'insights' | 'players') => void
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
  
  // Downloads preview callback
  onSelectedEventsChange?: (selectedEvents: Map<number, {
    beforePadding: number,  // 0-15 seconds before event
    afterPadding: number    // 0-15 seconds after event
  }>) => void
  
  // Autoplay events callback
  onAutoplayChange?: (autoplay: boolean) => void
  
  // Event padding data from Events tab timelines
  eventPaddings?: Map<number, { beforePadding: number, afterPadding: number }>
  onEventPaddingsChange?: (paddings: Map<number, { beforePadding: number, afterPadding: number }>) => void
  
  // Events update callback for edit mode
  onEventsUpdate?: (events: GameEvent[]) => void
}

type TabType = 'events' | 'ai' | 'insights' | 'players'

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
  currentTime = 0,
  onSelectedEventsChange,
  onAutoplayChange,
  eventPaddings,
  onEventPaddingsChange,
  onEventsUpdate
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

  
  // Downloads state - individual padding per event
  const [selectedEvents, setSelectedEvents] = useState<Map<number, {
    beforePadding: number,  // 0-15 seconds before event
    afterPadding: number    // 0-15 seconds after event
  }>>(new Map())
  
  // Edit mode state
  const [isEditMode, setIsEditMode] = useState(false)
  const [editModeEvents, setEditModeEvents] = useState<Map<number, GameEvent>>(new Map())
  const [isCreatingClip, setIsCreatingClip] = useState(false)
  
  // Download mode state
  const [isDownloadMode, setIsDownloadMode] = useState(false)
  const [selectedDownloadEvents, setSelectedDownloadEvents] = useState<Set<number>>(new Set())
  const [includeScoreline, setIncludeScoreline] = useState(true)
  
  // Individual event padding state (for timeline trimmers)
  // Helper to get padding for an event (with defaults)
  const getEventPadding = (eventIndex: number) => {
    return eventPaddings?.get(eventIndex) || { beforePadding: 5, afterPadding: 3 }
  }
  
  // Helper to update padding for an event timeline
  const updateEventTimelinePadding = (eventIndex: number, beforePadding: number, afterPadding: number) => {
    if (onEventPaddingsChange && eventPaddings) {
      const newPaddings = new Map(eventPaddings)
      newPaddings.set(eventIndex, { beforePadding, afterPadding })
      onEventPaddingsChange(newPaddings)
      
      // Auto-save padding changes to database (will be defined later)
      if (savePaddingChanges) {
        savePaddingChanges()
      }
    }
  }
  
  // Wrapper to update selectedEvents and notify parent
  const updateSelectedEvents = (newSelectedEvents: Map<number, {
    beforePadding: number,
    afterPadding: number
  }>) => {
    setSelectedEvents(newSelectedEvents)
    onSelectedEventsChange?.(newSelectedEvents)
  }
  
  // Download mode functions
  const handleToggleDownloadMode = () => {
    setIsDownloadMode(!isDownloadMode)
    setSelectedDownloadEvents(new Set()) // Clear selection when toggling
  }
  
  const handleToggleEventDownload = (eventIndex: number) => {
    const newSelected = new Set(selectedDownloadEvents)
    if (newSelected.has(eventIndex)) {
      newSelected.delete(eventIndex)
    } else {
      newSelected.add(eventIndex)
    }
    setSelectedDownloadEvents(newSelected)
  }
  
  const handleDownloadSelected = async () => {
    if (selectedDownloadEvents.size === 0) return
    
    setIsCreatingClip(true)
    
    try {
      // Convert selected events to the format expected by the API
      const selectedEventData = Array.from(selectedDownloadEvents).map(index => {
        const padding = getEventPadding(index)
        return {
          timestamp: allEvents[index].timestamp,
          type: allEvents[index].type,
          description: allEvents[index].description,
          beforePadding: padding.beforePadding,
          afterPadding: padding.afterPadding
        }
      })
      
      console.log('🎬 Downloading selected events:', selectedEventData)
      
      // Use the same API as clips with scoreline option
      const result = await apiClient.createClipFFmpeg(gameId, selectedEventData, includeScoreline)
      console.log('✅ Download started:', result)
      
      if (result.method === 'ffmpeg' && result.blob) {
        // Create download link from blob
        const url = window.URL.createObjectURL(result.blob)
        const link = document.createElement('a')
        link.href = url
        link.download = result.fileName || `events_${gameId}_${Date.now()}.mp4`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        // Clear selection and exit download mode
        setSelectedDownloadEvents(new Set())
        setIsDownloadMode(false)
        alert(`🚀 ${selectedEventData.length === 1 ? 'Event' : 'Events'} downloaded successfully!`)
      }
      
    } catch (error: any) {
      console.error('❌ Error downloading events:', error)
      alert(`Error downloading events: ${error.message}`)
    } finally {
      setIsCreatingClip(false)
    }
  }
  
  // Manual annotation state
  const [binnedEvents, setBinnedEvents] = useState<Set<number>>(new Set())
  const [isSavingEvents, setIsSavingEvents] = useState(false)
  
  // Event editing state
  const [editingEventIndex, setEditingEventIndex] = useState<number | null>(null)
  const [editingEvent, setEditingEvent] = useState<GameEvent | null>(null)
  
  // Debounced save for padding changes
  const savePaddingChangesTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  
  const savePaddingChanges = useCallback(() => {
    // Clear existing timeout
    if (savePaddingChangesTimeoutRef.current) {
      clearTimeout(savePaddingChangesTimeoutRef.current)
    }
    
    // Set new timeout to save after 1 second of inactivity
    savePaddingChangesTimeoutRef.current = setTimeout(async () => {
      if (!gameId || isSavingEvents) return
      
      try {
        // Create events with current padding data
        const eventsWithPadding = allEvents.map((event, index) => {
          const padding = eventPaddings?.get(index) || { beforePadding: 5, afterPadding: 3 }
          return {
            ...event,
            beforePadding: padding.beforePadding,
            afterPadding: padding.afterPadding
          }
        })
        
        await apiClient.saveModifiedEvents(gameId, eventsWithPadding)
        console.log('✅ Padding changes auto-saved')
      } catch (error) {
        console.error('❌ Error auto-saving padding changes:', error)
      }
    }, 1000)
  }, [gameId, allEvents, eventPaddings, isSavingEvents])
  
  // New event creation state
  const [isCreatingEvent, setIsCreatingEvent] = useState(false)
  const [newEvent, setNewEvent] = useState({
    type: 'goal',
    timestamp: currentTime,
    team: redTeam.name.toLowerCase(),
    description: '',
    player: ''
  })
  
  // Autoplay events state
  const [autoplayEvents, setAutoplayEvents] = useState(false)
  
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
    const newSelected = new Map(selectedEvents)
    newSelected.delete(eventIndex)
    updateSelectedEvents(newSelected)
    
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

  // Event editing functions
  const handleStartEditingEvent = (eventIndex: number) => {
    const event = allEvents[eventIndex]
    setEditingEventIndex(eventIndex)
    setEditingEvent({
      ...event,
      // Keep timestamp as is for editing
      timestamp: event.timestamp
    })
  }

  const handleCancelEditingEvent = () => {
    setEditingEventIndex(null)
    setEditingEvent(null)
  }

  const handleSaveEditedEvent = async () => {
    if (!editingEvent || editingEventIndex === null) return

    try {
      setIsSavingEvents(true)
      
      // Update the event in allEvents array
      const updatedEvents = [...allEvents]
      updatedEvents[editingEventIndex] = editingEvent
      
      // Include padding data for all events when saving
      const eventsWithPadding = updatedEvents.map((event, index) => {
        const padding = eventPaddings.get(index) || { beforePadding: 5, afterPadding: 3 }
        return {
          ...event,
          beforePadding: padding.beforePadding,
          afterPadding: padding.afterPadding
        }
      })
      
      // Save to backend
      await apiClient.saveModifiedEvents(gameId, eventsWithPadding)
      
      // Reset editing state
      setEditingEventIndex(null)
      setEditingEvent(null)
      
    } catch (error) {
      console.error('Error saving edited event:', error)
    } finally {
      setIsSavingEvents(false)
    }
  }
  
  const saveModifiedEvents = async () => {
    if (!gameId || isSavingEvents) return
    
    setIsSavingEvents(true)
    try {
      // Create modified events array (filter out binned events)
      const modifiedEvents = allEvents
        .map((event, index) => {
          // Get padding for this event (use defaults if not set)
          const padding = eventPaddings.get(index) || { beforePadding: 5, afterPadding: 3 }
          
          return { 
            ...event, 
            originalIndex: index,
            beforePadding: padding.beforePadding,
            afterPadding: padding.afterPadding
          }
        })
        .filter((_, index) => !binnedEvents.has(index))
      
      await apiClient.saveModifiedEvents(gameId, modifiedEvents)
      console.log('✅ Modified events saved successfully (including padding)')
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

  // Edit mode functions
  const handleToggleEditMode = () => {
    if (!isEditMode) {
      // Entering edit mode - initialize edit data with current events
      const editData = new Map()
      allEvents.forEach((event, index) => {
        editData.set(index, { ...event })
      })
      setEditModeEvents(editData)
    } else {
      // Exiting edit mode - save changes
      handleSaveEditModeChanges()
    }
    setIsEditMode(!isEditMode)
  }

  const handleUpdateEditModeEvent = (eventIndex: number, updatedEvent: GameEvent) => {
    const newEditData = new Map(editModeEvents)
    newEditData.set(eventIndex, updatedEvent)
    setEditModeEvents(newEditData)
  }

  const handleSaveEditModeChanges = async () => {
    try {
      // Convert Map to array of events
      const updatedEvents = Array.from(editModeEvents.values())

      // Save to backend
      await apiClient.saveModifiedEvents(gameId, updatedEvents)
      
      // Update local state
      onEventsUpdate?.(updatedEvents)
      
      console.log('✅ Edit mode changes saved successfully')
    } catch (error) {
      console.error('❌ Failed to save edit mode changes:', error)
      alert('Failed to save changes. Please try again.')
    }
  }

  // Downloads functions
  const handleEventSelection = (eventIndex: number) => {
    const newSelected = new Map(selectedEvents)
    if (newSelected.has(eventIndex)) {
      newSelected.delete(eventIndex)
    } else if (newSelected.size < 5) {
      // Add event with default 5s before, 3s after
      newSelected.set(eventIndex, {
        beforePadding: 5,
        afterPadding: 3
      })
    }
    updateSelectedEvents(newSelected)
  }

  // Update individual event padding
  const updateEventPadding = (eventIndex: number, type: 'before' | 'after', value: number) => {
    const newSelected = new Map(selectedEvents)
    const current = newSelected.get(eventIndex)
    if (current) {
      newSelected.set(eventIndex, {
        ...current,
        [type === 'before' ? 'beforePadding' : 'afterPadding']: value
      })
      updateSelectedEvents(newSelected)
    }
  }

  const handleCreateClip = async () => {
    if (selectedEvents.size === 0) return
    
    setIsCreatingClip(true)
    
    try {
      // Get selected event timestamps with individual padding
      const selectedEventData = Array.from(selectedEvents.entries()).map(([index, padding]) => ({
        timestamp: allEvents[index].timestamp,
        type: allEvents[index].type,
        description: allEvents[index].description,
        beforePadding: padding.beforePadding,
        afterPadding: padding.afterPadding
      }))
      
      console.log('🎬 Starting clip creation with events:', selectedEventData)
      
      // Use FFmpeg for all clip creation
      console.log('🔗 Using FFmpeg for clip creation')
      const result = await apiClient.createClipFFmpeg(gameId, selectedEventData)
      console.log('✅ Clip creation started:', result)
      
      // FFmpeg returns blob directly
      if (result.method === 'ffmpeg' && result.blob) {
        // FFmpeg - direct blob download
        alert(`🚀 ${result.message}\n\n💾 Starting download now!`)
        
        // Create download link from blob
        const url = window.URL.createObjectURL(result.blob)
        const link = document.createElement('a')
        link.href = url
        link.download = result.fileName || `highlight_${gameId}_${Date.now()}.mp4`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        // Clear selection after successful download
        updateSelectedEvents(new Map())
        setIsCreatingClip(false)
        
      } else {
        // Unknown response format
        console.error('Unexpected response format:', result)
        alert('Clip creation completed but response format was unexpected.')
        setIsCreatingClip(false)
      }
      
    } catch (error: any) {
      console.error('❌ Error starting clip creation:', error)
      alert(`Error starting clip creation: ${error.message}`)
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
            onClick={() => handleTabChange('players')}
            className={`flex-1 flex items-center justify-center space-x-2 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200 ${
              activeTab === 'players'
                ? 'bg-orange-500/20 text-orange-200 border border-orange-500/30'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>Players</span>
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
                  <label className="text-gray-300 block mb-3 font-medium">Filters:</label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => {
                        if (teamFilter === 'both') {
                          setTeamFilter(redTeam.name.toLowerCase()) // Both selected -> Red team only
                        } else if (teamFilter === redTeam.name.toLowerCase()) {
                          setTeamFilter(blueTeam.name.toLowerCase()) // Red team only -> Blue team only
                        } else {
                          setTeamFilter('both') // Blue team only -> Both
                        }
                      }}
                      className={`h-12 text-xs font-semibold rounded-lg border-2 transition-colors ${
                        teamFilter === redTeam.name.toLowerCase() || teamFilter === 'both'
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
                          setTeamFilter(blueTeam.name.toLowerCase()) // Both selected -> Blue team only
                        } else if (teamFilter === blueTeam.name.toLowerCase()) {
                          setTeamFilter(redTeam.name.toLowerCase()) // Blue team only -> Red team only
                        } else {
                          setTeamFilter('both') // Red team only -> Both
                        }
                      }}
                      className={`h-12 text-xs font-semibold rounded-lg border-2 transition-colors ${
                        teamFilter === blueTeam.name.toLowerCase() || teamFilter === 'both'
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

                {/* Autoplay and Edit Events Buttons - Side by Side */}
                <div>
                  {!isCreatingEvent && !isEditMode && (
                    <div className="grid grid-cols-2 gap-2 mb-3">
                      {/* Autoplay Toggle */}
                      <button
                        onClick={() => {
                          const newAutoplay = !autoplayEvents
                          setAutoplayEvents(newAutoplay)
                          onAutoplayChange?.(newAutoplay)
                        }}
                        className="flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border-2 bg-gray-500/10 hover:bg-gray-500/20 border-gray-400/30 text-gray-300"
                      >
                        <span>Autoplay</span>
                        <div className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                          autoplayEvents ? 'bg-green-500' : 'bg-gray-600'
                        }`}>
                          <span
                            className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                              autoplayEvents ? 'translate-x-5' : 'translate-x-1'
                            }`}
                          />
                        </div>
                      </button>
                      
                      {/* Edit Events Button */}
                      <button
                        onClick={handleToggleEditMode}
                        className="flex items-center justify-center space-x-2 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border-2 bg-gray-500/10 hover:bg-gray-500/20 border-gray-400/30 text-gray-300 hover:text-white"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                        <span>Edit</span>
                      </button>
                    </div>
                  )}

                  {/* Edit Mode: Autoplay and Add Event side by side */}
                  {!isCreatingEvent && isEditMode && (
                    <div className="space-y-2 mb-3">
                      <div className="grid grid-cols-2 gap-2">
                        {/* Autoplay Toggle */}
                        <button
                          onClick={() => {
                            const newAutoplay = !autoplayEvents
                            setAutoplayEvents(newAutoplay)
                            onAutoplayChange?.(newAutoplay)
                          }}
                          className="flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border-2 bg-gray-500/10 hover:bg-gray-500/20 border-gray-400/30 text-gray-300"
                        >
                          <span>Autoplay</span>
                          <div className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                            autoplayEvents ? 'bg-green-500' : 'bg-gray-600'
                          }`}>
                            <span
                              className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                                autoplayEvents ? 'translate-x-5' : 'translate-x-1'
                              }`}
                            />
                          </div>
                        </button>
                        
                        {/* Add Event Button - Only in Edit Mode */}
                        <button
                          onClick={handleStartCreatingEvent}
                          disabled={isSavingEvents}
                          className="flex items-center justify-center space-x-2 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border-2 bg-purple-500/10 hover:bg-purple-500/20 border-purple-400/30 text-purple-300 disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Add new event at current time"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                          </svg>
                          <span>Add Event</span>
                        </button>
                      </div>
                      
                      {/* Save & Exit Button - Full width in Edit Mode */}
                      <button
                        onClick={handleToggleEditMode}
                        className="w-full flex items-center justify-center space-x-2 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 border-2 bg-blue-500/20 text-blue-300 border-blue-500/40 hover:bg-blue-500/30"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>Save & Exit</span>
                      </button>
                    </div>
                  )}

                  {isCreatingEvent && (
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
                  
                                    // Show edit form if this event is being edited (individual editing only, not bulk edit mode)
                  if (editingEventIndex === originalIndex && editingEvent && !isEditMode) {
                  return (
                      <div
                        key={`${event.timestamp}-${event.type}-${index}-editing`}
                        className="p-3 rounded-lg bg-gray-800 border border-blue-500/30 space-y-3"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            {/* Time Input */}
                            <div className="flex items-center gap-1">
                              <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <input
                                type="text"
                                value={`${Math.floor(editingEvent.timestamp / 60)}:${(editingEvent.timestamp % 60).toFixed(0).padStart(2, '0')}`}
                                onChange={(e) => {
                                  const [minutes, seconds] = e.target.value.split(':').map(Number)
                                  if (!isNaN(minutes) && !isNaN(seconds)) {
                                    setEditingEvent({...editingEvent, timestamp: minutes * 60 + seconds})
                                  }
                                }}
                                className="w-16 px-2 py-1 text-xs bg-gray-700 border border-gray-600 rounded text-white font-mono"
                                placeholder="MM:SS"
                              />
                            </div>
                            
                            {/* Event Type Dropdown */}
                            <select
                              value={editingEvent.type}
                              onChange={(e) => setEditingEvent({...editingEvent, type: e.target.value})}
                              className="px-2 py-1 text-xs bg-gray-700 border border-gray-600 rounded text-white"
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
                            </select>
                            
                            {/* Team Dropdown */}
                            <select
                              value={editingEvent.team || ''}
                              onChange={(e) => setEditingEvent({...editingEvent, team: e.target.value})}
                              className="px-2 py-1 text-xs bg-gray-700 border border-gray-600 rounded text-white"
                            >
                              <option value="">No Team</option>
                              <option value={redTeam.name.toLowerCase()}>{redTeam.name}</option>
                              <option value={blueTeam.name.toLowerCase()}>{blueTeam.name}</option>
                            </select>
                          </div>
                          
                          {/* Save/Cancel Buttons */}
                          <div className="flex items-center gap-1">
                            {/* Save Button */}
                    <button
                              onClick={handleSaveEditedEvent}
                              disabled={isSavingEvents}
                              className="p-1 text-gray-400 hover:text-green-400 hover:bg-green-500/10 rounded transition-colors"
                              title="Save changes"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            </button>
                            
                            {/* Cancel Button */}
                            <button
                              onClick={handleCancelEditingEvent}
                              className="p-1 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                              title="Cancel editing"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          </div>
                        </div>
                        
                        {/* Description Input */}
                        <textarea
                          value={editingEvent.description || ''}
                          onChange={(e) => setEditingEvent({...editingEvent, description: e.target.value})}
                          className="w-full px-3 py-2 text-sm bg-gray-700 border border-gray-600 rounded text-white resize-none"
                          placeholder="Event description..."
                          rows={2}
                        />
                        
                        {/* Player Input */}
                        <input
                          type="text"
                          value={editingEvent.player || ''}
                          onChange={(e) => setEditingEvent({...editingEvent, player: e.target.value})}
                          className="w-full px-3 py-2 text-sm bg-gray-700 border border-gray-600 rounded text-white"
                          placeholder="Player name (optional)..."
                        />
                      </div>
                    )
                  }

                  return (
                    <div
                      key={`${event.timestamp}-${event.type}-${index}`}
                      id={`event-${originalIndex}`}
                      onClick={() => isDownloadMode ? handleToggleEventDownload(originalIndex) : onEventClick(event)}
                      className={`w-full text-left p-3 rounded-lg transition-all duration-200 border cursor-pointer ${
                        isDownloadMode && selectedDownloadEvents.has(originalIndex)
                          ? 'bg-gray-800 text-white border-green-500 ring-1 ring-green-500'
                          : originalIndex === currentEventIndex 
                          ? 'bg-gray-800 text-white border-green-500 ring-0.5 ring-green-500' 
                          : 'bg-gray-800 text-gray-300 hover:bg-gray-800 border-gray-700 hover:border-gray-600'
                      }`}
                    >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {/* Time Badge - editable in edit mode */}
                        <div className="flex items-center gap-1">
                          <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {isEditMode ? (
                            <input
                              type="text"
                              value={`${Math.floor((editModeEvents.get(originalIndex) || event).timestamp / 60)}:${((editModeEvents.get(originalIndex) || event).timestamp % 60).toFixed(0).padStart(2, '0')}`}
                              onChange={(e) => {
                                e.stopPropagation()
                                const [minutes, seconds] = e.target.value.split(':').map(Number)
                                if (!isNaN(minutes) && !isNaN(seconds)) {
                                  const updatedEvent = {...(editModeEvents.get(originalIndex) || event), timestamp: minutes * 60 + seconds}
                                  handleUpdateEditModeEvent(originalIndex, updatedEvent)
                                }
                              }}
                              className="w-12 px-1 py-0.5 text-xs bg-gray-700 border border-gray-600 rounded text-white font-mono"
                              onClick={(e) => e.stopPropagation()}
                            />
                          ) : (
                            <span className="text-xs text-gray-400 font-mono">{formatTime(event.timestamp)}</span>
                          )}
                        </div>
                        
                        {/* Event Type Badge - editable in edit mode */}
                        {isEditMode ? (
                          <select
                            value={(editModeEvents.get(originalIndex) || event).type}
                            onChange={(e) => {
                              e.stopPropagation()
                              const updatedEvent = {...(editModeEvents.get(originalIndex) || event), type: e.target.value}
                              handleUpdateEditModeEvent(originalIndex, updatedEvent)
                            }}
                            className="px-2 py-1 text-xs bg-gray-700 border border-gray-600 rounded text-white"
                            onClick={(e) => e.stopPropagation()}
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
                          </select>
                        ) : (
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
                        )}
                        
                        {/* Team Badge - editable in edit mode */}
                        {isEditMode ? (
                          <select
                            value={(editModeEvents.get(originalIndex) || event).team || ''}
                            onChange={(e) => {
                              e.stopPropagation()
                              const updatedEvent = {...(editModeEvents.get(originalIndex) || event), team: e.target.value}
                              handleUpdateEditModeEvent(originalIndex, updatedEvent)
                            }}
                            className="px-2 py-1 text-xs bg-gray-700 border border-gray-600 rounded text-white"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <option value="">No Team</option>
                            <option value={redTeam.name.toLowerCase()}>{redTeam.name}</option>
                            <option value={blueTeam.name.toLowerCase()}>{blueTeam.name}</option>
                          </select>
                        ) : (
                          event.team && (
                          <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${getTeamBadgeColors(event.team)}`}>
                            {getTeamName(event.team)}
                          </span>
                          )
                        )}
                      </div>
                      
                      {/* Action Buttons - bin and edit (hidden in download mode) */}
                      {!isDownloadMode && (
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
                            handleStartEditingEvent(originalIndex)
                          }}
                          className="p-1 text-gray-400 hover:text-blue-400 hover:bg-blue-500/10 rounded transition-colors"
                          title="Edit this event"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                      </div>
                      )}
                    </div>
                    
                    {/* Description - editable in edit mode */}
                    {isEditMode ? (
                      <textarea
                        value={(editModeEvents.get(originalIndex) || event).description || ''}
                        onChange={(e) => {
                          e.stopPropagation()
                          const updatedEvent = {...(editModeEvents.get(originalIndex) || event), description: e.target.value}
                          handleUpdateEditModeEvent(originalIndex, updatedEvent)
                        }}
                        className="w-full px-2 py-1 text-xs bg-gray-700 border border-gray-600 rounded text-white resize-none mt-2"
                        placeholder="Event description..."
                        rows={2}
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      event.description && (
                      <div className="text-xs text-gray-400 mt-2 leading-relaxed">{transformDescription(event.description)}</div>
                      )
                    )}
                    
                    {/* Apple-style Timeline Trimmer */}
                    <div className="mt-3" onClick={(e) => e.stopPropagation()}>
                      <AppleStyleTrimmer
                        eventTimestamp={event.timestamp}
                        beforePadding={getEventPadding(originalIndex).beforePadding}
                        afterPadding={getEventPadding(originalIndex).afterPadding}
                        maxPadding={15}
                        currentTime={currentTime}
                        onPaddingChange={(before, after) => {
                          updateEventTimelinePadding(originalIndex, before, after)
                        }}
                        className=""
                      />
                    </div>
                    
                    {/* Player - editable in edit mode */}
                    {isEditMode ? (
                      <input
                        type="text"
                        value={(editModeEvents.get(originalIndex) || event).player || ''}
                        onChange={(e) => {
                          e.stopPropagation()
                          const updatedEvent = {...(editModeEvents.get(originalIndex) || event), player: e.target.value}
                          handleUpdateEditModeEvent(originalIndex, updatedEvent)
                        }}
                        className="w-full px-2 py-1 text-xs bg-gray-700 border border-gray-600 rounded text-white mt-1"
                        placeholder="Player name (optional)..."
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      event.player && (
                      <div className="text-xs text-gray-500 mt-1 italic">{event.player}</div>
                      )
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
            
            {/* Download Mode Toggle Button - Fixed at bottom */}
            <div className="p-4 border-t border-gray-700 bg-gray-900/50">
              {!isDownloadMode ? (
                <button
                  onClick={handleToggleDownloadMode}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 border-2 bg-gray-500/10 hover:bg-gray-500/20 border-gray-400/30 text-gray-300"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>Download Mode</span>
                </button>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm text-gray-300">
                    <span>Selected: <span className="font-medium text-blue-300">{selectedDownloadEvents.size}</span> event{selectedDownloadEvents.size !== 1 ? 's' : ''}</span>
                    <button
                      onClick={() => {
                        if (selectedDownloadEvents.size === events.length) {
                          // Deselect all
                          setSelectedDownloadEvents(new Set())
                        } else {
                          // Select all visible events
                          const allEventIndices = new Set<number>()
                          events.forEach((_, index) => {
                            const originalIndex = allEvents.indexOf(events[index])
                            if (originalIndex !== -1) {
                              allEventIndices.add(originalIndex)
                            }
                          })
                          setSelectedDownloadEvents(allEventIndices)
                        }
                      }}
                      className="text-xs px-2 py-1 rounded bg-blue-500/20 text-blue-300 hover:bg-blue-500/30 transition-colors"
                    >
                      {selectedDownloadEvents.size === events.length ? 'Deselect All' : 'Select All'}
                    </button>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleDownloadSelected}
                      disabled={selectedDownloadEvents.size === 0 || isCreatingClip}
                      className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 border-2 bg-green-500/10 hover:bg-green-500/20 border-green-400/30 text-green-300 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span>{isCreatingClip ? 'Downloading...' : 'Download Selected'}</span>
                    </button>
                    <button
                      onClick={handleToggleDownloadMode}
                      className="px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 border-2 bg-gray-500/10 hover:bg-gray-500/20 border-gray-400/30 text-gray-300"
                    >
                      Exit
                    </button>
                  </div>
                </div>
              )}
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

        {/* Players Tab */}
        {activeTab === 'players' && (
          <div className="h-full overflow-y-auto">
            <div className="p-4">
              <h4 className="text-lg font-semibold text-white mb-4">Player Insights</h4>
              
              {/* Coming Soon Section */}
              <div className="bg-gradient-to-br from-orange-900/20 to-orange-800/10 border border-orange-500/30 rounded-xl p-8 text-center">
                <div className="text-orange-400 mb-4">
                  <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-orange-300 mb-3">Coming Soon</h3>
                <p className="text-orange-200/80 text-sm">
                  Player focus, reels and insights for each player.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Removed Downloads Tab - functionality moved to Events tab */}
        {false && (
          <div className="h-full flex flex-col">
            {/* Header - Fixed at top */}
            <div className="p-4 border-b border-gray-700">
              <h4 className="text-lg font-semibold text-white mb-2">📥 Create Highlights</h4>
              <p className="text-sm text-gray-400">Select events to create a highlight reel for social media</p>
            </div>
            
            {/* Event Selection - Scrollable middle */}
            <div className="flex-1 overflow-y-auto p-4">
              <div>
                <h5 className="text-white font-medium mb-3">Select Events:</h5>
                <div className="space-y-2">
                  {allEvents.slice(0, 20).map((event, index) => {
                    const isBinned = binnedEvents.has(index)
                    const isSelected = selectedEvents.has(index)
                    const isDisabled = !isSelected && selectedEvents.size >= 10
                    const eventPadding = selectedEvents.get(index)
                    
                    // Skip binned events
                    if (isBinned) return null
                    
                    return (
                      <div
                        key={`${event.timestamp}-${event.type}-${index}`}
                        onClick={() => !isDisabled && handleEventSelection(index)}
                        className={`w-full text-left p-3 rounded-lg transition-all duration-200 border cursor-pointer ${
                          isSelected 
                            ? 'bg-orange-500/20 text-white border-orange-500 ring-1 ring-orange-500' 
                            : isDisabled 
                              ? 'bg-gray-800/20 opacity-50 cursor-not-allowed border-gray-700'
                              : 'bg-gray-800/60 text-gray-300 hover:bg-gray-700/60 border-gray-700 hover:border-gray-600'
                        }`}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            {/* Time Badge - matching Events tab */}
                            <div className="flex items-center gap-1">
                              <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <span className="text-xs text-gray-400 font-mono">{formatTime(event.timestamp)}</span>
                            </div>
                            
                            {/* Event Type Badge - matching Events tab */}
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
                            
                            {/* Team Badge - matching Events tab */}
                            {event.team && (
                              <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${getTeamBadgeColors(event.team)}`}>
                                {getTeamName(event.team)}
                              </span>
                            )}
                          </div>
                          
                          {/* Bin Button - matching Events tab */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation() // Prevent card selection
                              handleBinEvent(index)
                            }}
                            disabled={isSavingEvents}
                            className="p-1 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                            title="Delete this event"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                        
                        {/* Description - matching Events tab */}
                        {event.description && (
                          <div className="text-xs text-gray-400 mt-2 leading-relaxed">{transformDescription(event.description)}</div>
                        )}
                        
                        {/* Player - matching Events tab */}
                        {event.player && (
                          <div className="text-xs text-gray-500 mt-1 italic">{event.player}</div>
                        )}
                        
                        {/* Apple-style Timeline Trimmer - Only show if selected */}
                        {isSelected && eventPadding && (
                          <div className="mt-3" onClick={(e) => e.stopPropagation()}>
                            <AppleStyleTrimmer
                              eventTimestamp={event.timestamp}
                              beforePadding={eventPadding.beforePadding}
                              afterPadding={eventPadding.afterPadding}
                              maxPadding={15}
                              currentTime={currentTime}
                              onPaddingChange={(before, after) => {
                                const newSelected = new Map(selectedEvents);
                                const current = newSelected.get(index);
                                if (current) {
                                  newSelected.set(index, {
                                    beforePadding: before,
                                    afterPadding: after
                                  });
                                  updateSelectedEvents(newSelected);
                                }
                              }}
                            />
                          </div>
                        )}
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
                  <span className="text-orange-400 font-bold">{selectedEvents.size} / 10</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white font-medium">Total Duration:</span>
                  <span className="text-orange-400 font-bold">
                    {Array.from(selectedEvents.values()).reduce((total, padding) => 
                      total + padding.beforePadding + padding.afterPadding, 0
                    )}s
                  </span>
                </div>
                {selectedEvents.size > 0 && (
                  <p className="text-xs text-gray-400 mt-2">
                    Individual padding: {Array.from(selectedEvents.values()).map(p => 
                      `${p.beforePadding}+${p.afterPadding}s`
                    ).join(', ')}
                  </p>
                )}
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