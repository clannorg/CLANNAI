'use client'

import { useState } from 'react'
import { AIChatSidebar, useAIChat } from '../ai-chat'
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

type TabType = 'events' | 'ai' | 'insights'

export default function UnifiedSidebar({
  isOpen,
  onClose,
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
  const [activeTab, setActiveTab] = useState<TabType>('events')
  const { isOpen: showChat } = useAIChat()

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  if (!isOpen) return null

  return (
    <div className="absolute top-0 right-0 h-full w-full md:w-80 bg-black/90 backdrop-blur-sm border-l border-gray-700 flex flex-col z-30">
      {/* Tab Header */}
      <div className="sticky top-0 bg-black/90 backdrop-blur-sm border-b border-gray-700 p-4 z-10">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-white">Game Analysis</h3>
          <button
            onClick={onClose}
            className="flex items-center justify-center w-8 h-8 bg-white/10 hover:bg-white/20 rounded-lg transition-all duration-200 border border-white/10 hover:border-white/20"
            title="Close Sidebar"
          >
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex bg-gray-800/50 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('events')}
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
            onClick={() => setActiveTab('ai')}
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
            onClick={() => setActiveTab('insights')}
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
              <div className="mt-4 text-center">
                <p className="text-yellow-400 text-sm">Click "AI Coach" in the header to start a conversation!</p>
              </div>
            </div>
            <div className="flex-1 p-4">
              <div className="bg-gray-800/50 rounded-lg p-6 text-center">
                <svg className="w-12 h-12 mx-auto mb-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <h5 className="text-white font-medium mb-2">AI Coaching Available</h5>
                <p className="text-gray-400 text-sm mb-4">Get personalized insights about:</p>
                <div className="space-y-2 text-sm text-gray-300">
                  <div>• Training drills recommendations</div>
                  <div>• Tactical analysis</div>
                  <div>• Player performance insights</div>
                  <div>• Match preparation tips</div>
                </div>
              </div>
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
                compact={true}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}