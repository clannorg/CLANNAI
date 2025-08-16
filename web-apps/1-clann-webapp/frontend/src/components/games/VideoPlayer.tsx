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
        onError={() => {
          // Video loading failed - this is normal for pending uploads
        }}
        preload="metadata"
        playsInline
        controls={false}
        webkit-playsinline="true"
        x-webkit-airplay="deny"
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

                    {/* Clean Controls + Progress Bar */}
          <div className="mx-3 sm:mx-6 mb-[max(env(safe-area-inset-bottom),8px)]">
            <div className="flex items-center space-x-3">
              {/* Previous Event */}
              <button
                onClick={handlePreviousEvent}
                disabled={events.length === 0}
                className="flex items-center justify-center w-6 h-6 text-white hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Previous Event"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>

              {/* Play/Pause */}
              <button
                onClick={handlePlayPause}
                className="flex items-center justify-center w-8 h-8 text-white hover:text-gray-300 transition-colors"
              >
                {isPlaying ? (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                  </svg>
                ) : (
                  <svg className="w-4 h-4 ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                )}
              </button>

              {/* Next Event */}
              <button
                onClick={handleNextEvent}
                disabled={events.length === 0}
                className="flex items-center justify-center w-6 h-6 text-white hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Next Event"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>

              {/* Current Time */}
              <span className="text-white text-sm font-mono whitespace-nowrap">
                {formatTime(currentTime)}
              </span>

              {/* Progress Bar */}
              <div className="flex-1 relative min-w-0">
                <input
                  type="range"
                  min="0"
                  max={duration || 0}
                  step="0.1"
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full h-1 bg-white/30 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:shadow-lg [&::-webkit-slider-thumb]:cursor-pointer [&::-moz-range-thumb]:w-3 [&::-moz-range-thumb]:h-3 [&::-moz-range-thumb]:bg-white [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:border-none [&::-moz-range-thumb]:cursor-pointer"
                  style={{
                    background: `linear-gradient(to right, #016F32 0%, #016F32 ${(currentTime / (duration || 1)) * 100}%, rgba(255,255,255,0.3) ${(currentTime / (duration || 1)) * 100}%, rgba(255,255,255,0.3) 100%)`
                  }}
                />
              </div>

              {/* Duration */}
              <span className="text-white/80 text-sm font-mono whitespace-nowrap">
                {formatTime(duration)}
              </span>

              {/* Volume */}
              <button
                onClick={handleMuteToggle}
                className="flex items-center justify-center w-6 h-6 text-white hover:text-gray-300 transition-colors"
                title={isMuted ? "Unmute" : "Mute"}
              >
                {isMuted ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" clipRule="evenodd" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}