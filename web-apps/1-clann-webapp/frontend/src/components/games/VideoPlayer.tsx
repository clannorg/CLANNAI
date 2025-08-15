'use client'

import { useState, useEffect, useRef } from 'react'

interface GameEvent {
  type: string
  timestamp: number
  player?: string
  description?: string
  team?: string
}

interface VideoPlayerProps {
  game: {
    s3Url: string
    title: string
    metadata?: {
      teams?: {
        red_team?: { name: string; jersey_color: string }
        blue_team?: { name: string; jersey_color: string }
      }
    }
  }
  events: GameEvent[]
  allEvents: GameEvent[]
  currentEventIndex: number
  onTimeUpdate: (currentTime: number, duration: number) => void
  onEventClick: (event: GameEvent) => void
  onSeekToTimestamp: (timestamp: number) => void
  // When false, hide timeline/controls overlays (used on mobile portrait)
  overlayVisible?: boolean
  // Notify parent about user interaction to reset auto-hide timers
  onUserInteract?: () => void
}

export default function VideoPlayer({
  game,
  events,
  allEvents,
  currentEventIndex,
  onTimeUpdate,
  onEventClick,
  onSeekToTimestamp,
  overlayVisible = true,
  onUserInteract
}: VideoPlayerProps) {
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  
  const videoRef = useRef<HTMLVideoElement>(null)

  // Extract team colors from metadata
  const redTeam = game.metadata?.teams?.red_team || { name: 'Red Team', jersey_color: '#DC2626' }
  const blueTeam = game.metadata?.teams?.blue_team || { name: 'Blue Team', jersey_color: '#2563EB' }

  // Function to get event color - use team colors for team events, fallback to event type colors
  const getTimelineEventColor = (event: GameEvent) => {
    if (event.team === 'red') return redTeam.jersey_color
    if (event.team === 'blue') return blueTeam.jersey_color
    
    // Fallback to event type colors for neutral events
    switch (event.type) {
      case 'goal': return '#22C55E'
      case 'shot': return '#3B82F6'
      case 'foul': return '#F59E0B'
      case 'turnover': return '#A855F7'
      case 'save': return '#F97316'
      default: return '#6B7280'
    }
  }

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const time = videoRef.current.currentTime
      const dur = videoRef.current.duration || 0
      setCurrentTime(time)
      setDuration(dur)
      onTimeUpdate(time, dur)
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
    if (!events || events.length === 0) return
    const currentFilteredIndex = events.findIndex(event => 
      allEvents.indexOf(event) === currentEventIndex
    )
    if (currentFilteredIndex > 0) {
      const prevEvent = events[currentFilteredIndex - 1]
      onEventClick(prevEvent)
    }
  }

  const handleNextEvent = () => {
    if (!events || events.length === 0) return
    const currentFilteredIndex = events.findIndex(event => 
      allEvents.indexOf(event) === currentEventIndex
    )
    if (currentFilteredIndex < events.length - 1) {
      const nextEvent = events[currentFilteredIndex + 1]
      onEventClick(nextEvent)
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
      case 'turnover': return 'bg-purple-500'
      case 'save': return 'bg-orange-500'
      default: return 'bg-gray-500'
    }
  }

  // Expose seek function to parent through callback
  useEffect(() => {
    const seek = (timestamp: number) => {
      if (videoRef.current) {
        videoRef.current.currentTime = timestamp
        if (videoRef.current.paused) {
          videoRef.current.play()
        }
        videoRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
    
    // Call the seek function when onSeekToTimestamp changes
    if (typeof onSeekToTimestamp === 'function') {
      // Store the seek function reference
      (window as any).videoPlayerSeek = seek
    }
  }, [onSeekToTimestamp])

  return (
    <div
      className="relative h-full flex items-center justify-center"
      onMouseMove={onUserInteract}
      onClick={onUserInteract}
      onKeyDown={onUserInteract as any}
      role="presentation"
    >
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
        }}
        preload="metadata"
      />

      {/* Progress Bar + Controls Overlay (auto-hide capable) */}
      <div
        className={`absolute bottom-0 left-0 right-0 z-40 transition-opacity duration-300 ${
          overlayVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
      >
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
                    key={`${event.timestamp}-${event.type}-${index}`}
                    onClick={() => onEventClick(event)}
                    className={`absolute top-1/2 transform -translate-y-1/2 w-2 h-2 rounded-full transition-all duration-300 hover:scale-200 hover:shadow-xl pointer-events-auto ${
                      isCurrent ? 'ring-3 ring-yellow-400 ring-offset-2 ring-offset-black shadow-xl scale-125' : 'hover:ring-2 hover:ring-white/70'
                    }`}
                    style={{ backgroundColor: getTimelineEventColor(event), left: `${position}%` }}
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
          <div className="bg-black/60 backdrop-blur-md mx-3 sm:mx-6 mb-[max(env(safe-area-inset-bottom),12px)] rounded-lg border border-white/5 shadow-md">
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

              {/* Right Side - Event Navigation (Desktop Only) */}
              <div className="hidden lg:flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handlePreviousEvent}
                    disabled={events.length === 0}
                    className={`inline-flex items-center space-x-2 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200 border ${
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
  )
}