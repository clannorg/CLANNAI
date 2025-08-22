'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import Hls from 'hls.js'

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
    hlsUrl?: string
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
  onCurrentEventChange?: (eventIndex: number) => void
  // When false, hide timeline/controls overlays (used on mobile portrait)
  overlayVisible?: boolean
  // Notify parent about user interaction to reset auto-hide timers
  onUserInteract?: () => void
  // Downloads preview props
  selectedEvents?: Map<number, {
    beforePadding: number,  // 0-15 seconds before event
    afterPadding: number    // 0-15 seconds after event
  }>
  // Events tab padding data for autoplay
  eventPaddings?: Map<number, {
    beforePadding: number,  // 0-15 seconds before event
    afterPadding: number    // 0-15 seconds after event
  }>
  activeTab?: string
  autoplayEvents?: boolean
}

export default function VideoPlayer({
  game,
  events,
  allEvents,
  currentEventIndex,
  onTimeUpdate,
  onEventClick,
  onSeekToTimestamp,
  onCurrentEventChange,
  overlayVisible = true,
  onUserInteract,
  selectedEvents,
  eventPaddings,
  activeTab,
  autoplayEvents
}: VideoPlayerProps) {
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [playbackSpeed, setPlaybackSpeed] = useState(1)
  const [zoomLevel, setZoomLevel] = useState(1)
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const hlsRef = useRef<Hls | null>(null)
  const autoplayInitializedRef = useRef(false)
  const userSeekingRef = useRef(false)
  const lastSeekTimeRef = useRef(0)
  const userSeekTargetRef = useRef<number | null>(null)
  
  // Downloads preview state
  const [previewSegments, setPreviewSegments] = useState<Array<{
    id: number
    start: number
    end: number
    event: GameEvent
  }>>([])
  const [currentSegmentIndex, setCurrentSegmentIndex] = useState(0)
  const [flashRegion, setFlashRegion] = useState<string | null>(null)

  // Check if we're in preview mode (autoplay events mode only - downloads tab removed)
  const isPreviewMode = (activeTab === 'events' && autoplayEvents)

  // Calculate preview segments when selectedEvents or autoplay change
  useEffect(() => {
    if (isPreviewMode && allEvents) {
      let segments: Array<{
        id: number
        start: number
        end: number
        event: GameEvent
      }> = []

      if (activeTab === 'events' && autoplayEvents) {
        // Autoplay mode: use all events with individual timeline padding
        segments = allEvents
          .map((event, index) => {
            // Get individual padding from Events tab timeline settings
            const padding = eventPaddings?.get(index) || { beforePadding: 5, afterPadding: 3 }
            return {
              id: index,
              start: Math.max(0, event.timestamp - padding.beforePadding),
              end: event.timestamp + padding.afterPadding,
              event
            }
          })
      }
      // Downloads tab removed - functionality moved to Events tab
      
      // Sort segments by start time
      segments.sort((a, b) => a.start - b.start)
      
      setPreviewSegments(segments)
      setCurrentSegmentIndex(0)
    } else {
      setPreviewSegments([])
      setCurrentSegmentIndex(0)
    }
  }, [selectedEvents, allEvents, activeTab, isPreviewMode, autoplayEvents, eventPaddings])

  // Jump to first segment start when autoplay is enabled (only once)
  useEffect(() => {
    if (autoplayEvents && activeTab === 'events') {
      if (!autoplayInitializedRef.current && previewSegments.length > 0 && videoRef.current) {
        const firstSegment = previewSegments[0]
        
        videoRef.current.currentTime = firstSegment.start
        setCurrentSegmentIndex(0)
        autoplayInitializedRef.current = true
        // Notify parent about initial event
        if (onCurrentEventChange) {
          onCurrentEventChange(firstSegment.id)
        }
      }
    } else {
      // Reset when autoplay is turned off
      autoplayInitializedRef.current = false
    }
  }, [autoplayEvents, activeTab, previewSegments, onCurrentEventChange])

  // Initialize HLS player
  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    // Cleanup previous HLS instance
    if (hlsRef.current) {
      hlsRef.current.destroy()
      hlsRef.current = null
    }

    // Try HLS first if supported and URL is available
    if (game.hlsUrl && Hls.isSupported()) {
      console.log('🎬 Initializing HLS with URL:', game.hlsUrl)
      
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: false,
        backBufferLength: 90,
        debug: false,
      })

      hls.loadSource(game.hlsUrl)
      hls.attachMedia(video)

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        console.log('✅ HLS manifest loaded successfully')
      })

      hls.on(Hls.Events.ERROR, (event, data) => {
        console.error('❌ HLS Error:', data)
        if (data.fatal) {
          console.log('🔄 HLS fatal error, falling back to MP4')
          // Fallback to MP4
          video.src = game.s3Url
        }
      })

      hlsRef.current = hls
    } else if (game.hlsUrl && video.canPlayType('application/vnd.apple.mpegurl')) {
      // Native HLS support (Safari)
      console.log('🍎 Using native HLS support')
      video.src = game.hlsUrl
    } else {
      // Fallback to MP4
      console.log('📹 Using MP4 fallback')
      video.src = game.s3Url
    }

    // Cleanup on unmount
    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy()
        hlsRef.current = null
      }
    }
  }, [game.hlsUrl, game.s3Url])

  // Jump to next segment in preview mode
  const jumpToNextSegment = useCallback(() => {
    const nextIndex = currentSegmentIndex + 1
    if (nextIndex < previewSegments.length) {
      // Jump to next segment
      setCurrentSegmentIndex(nextIndex)
      if (videoRef.current) {
        videoRef.current.currentTime = previewSegments[nextIndex].start
      }
      // Notify parent about event change
      if (onCurrentEventChange && activeTab === 'events' && autoplayEvents) {
        onCurrentEventChange(previewSegments[nextIndex].id)
      }
    } else {
      // Loop back to first clip
      setCurrentSegmentIndex(0)
      if (videoRef.current) {
        videoRef.current.currentTime = previewSegments[0].start
      }
      // Notify parent about event change
      if (onCurrentEventChange && activeTab === 'events' && autoplayEvents) {
        onCurrentEventChange(previewSegments[0].id)
      }
    }
  }, [currentSegmentIndex, previewSegments])

  // Jump to previous segment in preview mode
  const jumpToPrevSegment = useCallback(() => {
    const prevIndex = currentSegmentIndex - 1
    if (prevIndex >= 0) {
      // Jump to previous segment
      setCurrentSegmentIndex(prevIndex)
      if (videoRef.current) {
        videoRef.current.currentTime = previewSegments[prevIndex].start
      }
      // Notify parent about event change
      if (onCurrentEventChange && activeTab === 'events' && autoplayEvents) {
        onCurrentEventChange(previewSegments[prevIndex].id)
      }
    } else {
      // Loop to last clip
      const lastIndex = previewSegments.length - 1
      setCurrentSegmentIndex(lastIndex)
      if (videoRef.current) {
        videoRef.current.currentTime = previewSegments[lastIndex].start
      }
      // Notify parent about event change
      if (onCurrentEventChange && activeTab === 'events' && autoplayEvents) {
        onCurrentEventChange(previewSegments[lastIndex].id)
      }
    }
  }, [currentSegmentIndex, previewSegments])

  // Keyboard shortcuts for clip navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isPreviewMode || previewSegments.length === 0) return
      
      // Only handle if not typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return
      
      switch (e.key) {
        case 'ArrowRight':
          e.preventDefault()
          jumpToNextSegment()
          break
        case 'ArrowLeft':
          e.preventDefault()
          jumpToPrevSegment()
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isPreviewMode, previewSegments.length, jumpToNextSegment, jumpToPrevSegment])

  // Generate smart timeline background for clips mode
  const generateSmartTimelineBackground = () => {
    if (!isPreviewMode || !previewSegments.length || !duration) {
      // Normal timeline - green progress, grey remainder
      const progressPercent = (currentTime / (duration || 1)) * 100
      return `linear-gradient(to right, #016F32 0%, #016F32 ${progressPercent}%, rgba(255,255,255,0.3) ${progressPercent}%, rgba(255,255,255,0.3) 100%)`
    }
    
    // Smart timeline - green clips, grey gaps
    let gradientStops = []
    let lastEnd = 0
    
    previewSegments.forEach((segment, index) => {
      const startPercent = (segment.start / duration) * 100
      const endPercent = (segment.end / duration) * 100
      
      // Grey gap before clip
      if (startPercent > lastEnd) {
        gradientStops.push(`rgba(255,255,255,0.2) ${lastEnd}%`)
        gradientStops.push(`rgba(255,255,255,0.2) ${startPercent}%`)
      }
      
      // Bright green clip segment
      gradientStops.push(`#22C55E ${startPercent}%`)
      gradientStops.push(`#22C55E ${endPercent}%`)
      
      lastEnd = endPercent
    })
    
    // Grey remainder after last clip
    if (lastEnd < 100) {
      gradientStops.push(`rgba(255,255,255,0.2) ${lastEnd}%`)
      gradientStops.push(`rgba(255,255,255,0.2) 100%`)
    }
    
    return `linear-gradient(to right, ${gradientStops.join(', ')})`
  }

  // Extract team colors from metadata and convert to CSS colors
  const redTeam = game.metadata?.teams?.red_team || { name: 'Red Team', jersey_color: '#DC2626' }
  const blueTeam = game.metadata?.teams?.blue_team || { name: 'Blue Team', jersey_color: '#2563EB' }
  
  // Convert jersey color descriptions to actual CSS colors
  const getTeamCSSColor = (jerseyColor: string) => {
    const color = jerseyColor.toLowerCase().trim()
    
    // Handle descriptive team names first
    if (color.includes('orange bibs') || color.includes('orange bib')) {
      return '#F97316' // Orange
    }
    if (color.includes('non bibs') || color.includes('colours') || color.includes('colors')) {
      return '#FFFFFF' // White
    }
    if (color.includes('blue bibs') || color.includes('blue bib')) {
      return '#3B82F6' // Blue
    }
    if (color.includes('red bibs') || color.includes('red bib')) {
      return '#DC2626' // Red
    }
    if (color.includes('yellow bibs') || color.includes('yellow bib')) {
      return '#EAB308' // Yellow
    }
    if (color.includes('green bibs') || color.includes('green bib')) {
      return '#22C55E' // Green
    }
    
    const primaryColor = color.split(' ')[0]
    
    switch (primaryColor) {
      case 'blue': return '#3B82F6'      // Blue
      case 'white': return '#FFFFFF'     // White  
      case 'red': return '#DC2626'       // Red
      case 'green': return '#22C55E'     // Green
      case 'black': return '#000000'     // Black
      case 'yellow': return '#EAB308'    // Yellow
      case 'orange': return '#F97316'    // Orange
      case 'purple': return '#A855F7'    // Purple
      case 'turquoise': return '#14B8A6' // Turquoise
      case 'teal': return '#14B8A6'      // Teal
      case 'navy': return '#1E40AF'      // Navy
      default: return '#6B7280'          // Gray fallback
    }
  }

  // Function to get event color - use metadata team colors
  const getTimelineEventColor = (event: GameEvent) => {
    const eventTeam = event.team?.toLowerCase() || ''
    
    // Check if event team matches red team (from metadata)
    if (eventTeam === redTeam.name.toLowerCase() || 
        eventTeam.includes(redTeam.name.toLowerCase()) ||
        redTeam.name.toLowerCase().includes(eventTeam)) {
      return getTeamCSSColor(redTeam.jersey_color)
    }
    
    // Check if event team matches blue team (from metadata)
    if (eventTeam === blueTeam.name.toLowerCase() || 
        eventTeam.includes(blueTeam.name.toLowerCase()) ||
        blueTeam.name.toLowerCase().includes(eventTeam)) {
      return getTeamCSSColor(blueTeam.jersey_color)
    }
    
    // Fallback to red team color for unmatched events
    return getTeamCSSColor(redTeam.jersey_color)
  }

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const time = videoRef.current.currentTime
      const dur = videoRef.current.duration || 0
      setCurrentTime(time)
      setDuration(dur)
      onTimeUpdate(time, dur)
      
      // Downloads preview auto-jump logic (skip if user is manually seeking)
      if (isPreviewMode && previewSegments.length > 0 && isPlaying) {
        if (userSeekingRef.current) {
          console.log('🛡️ Autoplay blocked - user is seeking')
          return
        }
        
        // Also block if we're near a user's recent seek target (give them 2 seconds to watch)
        if (userSeekTargetRef.current !== null && Math.abs(time - userSeekTargetRef.current) < 2) {
          console.log('🛡️ Autoplay blocked - near user seek target', userSeekTargetRef.current)
          return
        }
        const currentSegment = previewSegments[currentSegmentIndex]
        
        // Check if we're in a grey area (not in any clip segment)
        const inClipSegment = previewSegments.some(seg => 
          time >= seg.start && time <= seg.end
        )
        
        if (!inClipSegment) {
          // We're in grey area - jump to next clip segment
          const nextSegment = previewSegments.find(seg => seg.start > time)
          if (nextSegment) {
            console.log('🤖 Autoplay: Jumping to next segment at', nextSegment.start)
            // Jump to the start of the next segment
            videoRef.current.currentTime = nextSegment.start
            // Update current segment index
            const nextIndex = previewSegments.findIndex(seg => seg.id === nextSegment.id)
            setCurrentSegmentIndex(nextIndex)
            // Notify parent about event change for immediate sidebar update
            if (onCurrentEventChange && activeTab === 'events' && autoplayEvents) {
              onCurrentEventChange(nextSegment.id)
            }
          } else {
            // No more segments - stop playing
            videoRef.current.pause()
            setIsPlaying(false)
            setCurrentSegmentIndex(0)
          }
        } else if (currentSegment && time >= currentSegment.end) {
          // Hit end of current segment - advance to next segment
          const nextIndex = currentSegmentIndex + 1
          if (nextIndex < previewSegments.length) {
            // Jump to next segment
            setCurrentSegmentIndex(nextIndex)
            videoRef.current.currentTime = previewSegments[nextIndex].start
            // Notify parent about event change
            if (onCurrentEventChange && activeTab === 'events' && autoplayEvents) {
              onCurrentEventChange(previewSegments[nextIndex].id)
            }
          } else {
            // No more segments - stop or loop to beginning
            setCurrentSegmentIndex(0)
            videoRef.current.currentTime = previewSegments[0].start
            // Notify parent about event change
            if (onCurrentEventChange && activeTab === 'events' && autoplayEvents) {
              onCurrentEventChange(previewSegments[0].id)
            }
          }
        }
      }
    }
  }

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        // When starting to play in preview mode, ensure we're in a valid clip segment
        if (isPreviewMode && previewSegments.length > 0) {
          const currentTime = videoRef.current.currentTime
          
          // Check if current time is within any clip segment
          const currentSegment = previewSegments.find(seg => 
            currentTime >= seg.start && currentTime <= seg.end
          )
          
          if (!currentSegment) {
            // Not in any clip - jump to start of first clip
            const firstSegment = previewSegments[0]
            videoRef.current.currentTime = firstSegment.start
            setCurrentSegmentIndex(0)
          }
        }
        
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const triggerFlash = (region: string, action: () => void) => {
    setFlashRegion(region)
    setTimeout(() => setFlashRegion(null), 150)
    action()
    if (onUserInteract) onUserInteract()
  }

  const handleMuteToggle = () => {
    if (videoRef.current) {
      videoRef.current.muted = !videoRef.current.muted
      setIsMuted(videoRef.current.muted)
    }
  }

  const handleSpeedChange = (speed: number) => {
    if (videoRef.current) {
      videoRef.current.playbackRate = speed
      setPlaybackSpeed(speed)
    }
  }

  const handleZoomChange = (zoom: number) => {
    setZoomLevel(zoom)
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
        const now = Date.now()
        
        // Debounce rapid clicks (ignore if clicked within 100ms)
        if (now - lastSeekTimeRef.current < 100) {
          console.log('🚫 Ignoring rapid click - too soon after last seek')
          return
        }
        
        lastSeekTimeRef.current = now
        
        // Set user seeking flag to prevent autoplay interference
        userSeekingRef.current = true
        userSeekTargetRef.current = timestamp
        console.log('🎯 User seeking to:', timestamp, '- Autoplay disabled for 1000ms')
        
        // If in autoplay mode, update the current segment index to match the seek target
        if (isPreviewMode && previewSegments.length > 0) {
          const targetSegmentIndex = previewSegments.findIndex(seg => 
            timestamp >= seg.start && timestamp <= seg.end
          )
          if (targetSegmentIndex !== -1) {
            setCurrentSegmentIndex(targetSegmentIndex)
            console.log('🎯 Updated autoplay segment index to:', targetSegmentIndex)
          }
        }
        
        videoRef.current.currentTime = timestamp
        if (videoRef.current.paused) {
          videoRef.current.play()
        }
        videoRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
        
        // Clear the flag after a longer delay to ensure autoplay doesn't interfere
        setTimeout(() => {
          userSeekingRef.current = false
          console.log('🎯 User seeking complete - Autoplay re-enabled')
        }, 1000) // Increased to 1000ms for better protection
        
        // Clear the seek target after 5 seconds to allow normal autoplay to resume
        setTimeout(() => {
          userSeekTargetRef.current = null
          console.log('🎯 User seek target cleared - Normal autoplay resumed')
        }, 5000)
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
      className="relative h-full flex items-center justify-center overflow-hidden"
      onMouseMove={onUserInteract}
      onClick={onUserInteract}
      onKeyDown={onUserInteract as any}
      role="presentation"
    >
      {/* Video Element */}
      <video
        ref={videoRef}
        className="w-full h-full object-contain transition-transform duration-200"
        style={{ 
          transform: `scale(${zoomLevel})`,
          transformOrigin: 'center center'
        }}
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

      {/* Voronoi Diagram - Invisible Tap Regions */}
      <div className="absolute inset-0 z-20 pointer-events-auto">
        {/* Previous Event Region - Left 20% */}
        <div
          className="absolute top-0 left-0 w-1/5 h-full cursor-pointer"
          onClick={() => triggerFlash('prev', handlePreviousEvent)}
        >
          <div className={`absolute inset-0 bg-blue-500 pointer-events-none transition-opacity duration-150 ${
            flashRegion === 'prev' ? 'opacity-20' : 'opacity-0'
          }`} />
        </div>

        {/* -5s Region - Left-Center 20% */}
        <div
          className="absolute top-0 left-1/5 w-1/5 h-full cursor-pointer"
          onClick={() => triggerFlash('back', handleJumpBackward)}
        >
          <div className={`absolute inset-0 bg-yellow-500 pointer-events-none transition-opacity duration-150 ${
            flashRegion === 'back' ? 'opacity-20' : 'opacity-0'
          }`} />
        </div>

        {/* Play/Pause Region - Center 20% */}
        <div
          className="absolute top-0 left-2/5 w-1/5 h-full cursor-pointer"
          onClick={() => triggerFlash('play', handlePlayPause)}
        >
          <div className={`absolute inset-0 bg-green-500 pointer-events-none transition-opacity duration-150 ${
            flashRegion === 'play' ? 'opacity-30' : 'opacity-0'
          }`} />
        </div>

        {/* +5s Region - Right-Center 20% */}
        <div
          className="absolute top-0 left-3/5 w-1/5 h-full cursor-pointer"
          onClick={() => triggerFlash('forward', handleJumpForward)}
        >
          <div className={`absolute inset-0 bg-orange-500 pointer-events-none transition-opacity duration-150 ${
            flashRegion === 'forward' ? 'opacity-20' : 'opacity-0'
          }`} />
        </div>

        {/* Next Event Region - Right 20% */}
        <div
          className="absolute top-0 left-4/5 w-1/5 h-full cursor-pointer"
          onClick={() => triggerFlash('next', handleNextEvent)}
        >
          <div className={`absolute inset-0 bg-purple-500 pointer-events-none transition-opacity duration-150 ${
            flashRegion === 'next' ? 'opacity-20' : 'opacity-0'
          }`} />
        </div>
      </div>

      {/* Floating Play Controls - Above Timeline */}
      <div
        className={`absolute bottom-16 left-0 right-0 flex items-center justify-center z-30 transition-opacity duration-300 ${
          overlayVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
      >
        <div className="flex items-center space-x-8">
          {/* Previous Event */}
          <button
            onClick={() => triggerFlash('prev', handlePreviousEvent)}
            disabled={events.length === 0}
            className="flex items-center justify-center text-white hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Previous Event"
            style={{ filter: 'drop-shadow(2px 2px 4px rgba(0,0,0,0.8))' }}
          >
            <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          {/* Jump Backward 5s */}
          <button
            onClick={() => triggerFlash('back', handleJumpBackward)}
            className="flex items-center justify-center text-white hover:text-gray-300 transition-colors text-lg font-bold"
            title="Jump Backward 5s"
            style={{ filter: 'drop-shadow(2px 2px 4px rgba(0,0,0,0.8))' }}
          >
            -5s
          </button>

          {/* Play/Pause - LARGE CENTER BUTTON */}
          <button
            onClick={() => triggerFlash('play', handlePlayPause)}
            className="flex items-center justify-center text-white hover:text-gray-300 transition-colors"
            style={{ filter: 'drop-shadow(3px 3px 6px rgba(0,0,0,0.9))' }}
          >
            {isPlaying ? (
              <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
              </svg>
            ) : (
              <svg className="w-16 h-16 ml-1" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
            )}
          </button>

          {/* Jump Forward 5s */}
          <button
            onClick={() => triggerFlash('forward', handleJumpForward)}
            className="flex items-center justify-center text-white hover:text-gray-300 transition-colors text-lg font-bold"
            title="Jump Forward 5s"
            style={{ filter: 'drop-shadow(2px 2px 4px rgba(0,0,0,0.8))' }}
          >
            +5s
          </button>

          {/* Next Event */}
          <button
            onClick={() => triggerFlash('next', handleNextEvent)}
            disabled={events.length === 0}
            className="flex items-center justify-center text-white hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Next Event"
            style={{ filter: 'drop-shadow(2px 2px 4px rgba(0,0,0,0.8))' }}
          >
            <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

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

          {/* Bottom Timeline Bar Only */}
          <div className="mx-3 sm:mx-6 mb-[max(env(safe-area-inset-bottom),8px)]">
            <div className="flex items-center space-x-3">
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
                    background: generateSmartTimelineBackground()
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

              {/* Playback Speed */}
              <div className="relative group">
                <button
                  className="flex items-center justify-center w-8 h-6 text-white hover:text-gray-300 transition-colors text-xs font-mono"
                  title="Playback Speed"
                >
                  {playbackSpeed}x
                </button>
                {/* Invisible bridge to prevent menu disappearing */}
                <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 w-8 h-2 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto"></div>
                <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 bg-black/90 rounded-lg p-3 opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none group-hover:pointer-events-auto shadow-lg">
                  <div className="flex flex-col gap-1">
                    {[0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3, 5].map((speed) => (
                      <button
                        key={speed}
                        onClick={() => handleSpeedChange(speed)}
                        className={`px-3 py-2 text-xs rounded transition-colors whitespace-nowrap ${
                          playbackSpeed === speed 
                            ? 'bg-blue-600 text-white' 
                            : 'text-white hover:bg-white/20'
                        }`}
                      >
                        {speed}x
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Zoom */}
              <div className="relative group">
                <button
                  className="flex items-center justify-center w-6 h-6 text-white hover:text-gray-300 transition-colors"
                  title="Zoom"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                  </svg>
                </button>
                {/* Invisible bridge to prevent menu disappearing */}
                <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 w-6 h-2 opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto"></div>
                <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 bg-black/90 rounded-lg p-4 opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none group-hover:pointer-events-auto shadow-lg">
                  <div className="flex flex-col gap-3 items-center">
                    <span className="text-xs text-white font-mono">{Math.round(zoomLevel * 100)}%</span>
                    <input
                      type="range"
                      min="0.5"
                      max="3"
                      step="0.1"
                      value={zoomLevel}
                      onChange={(e) => handleZoomChange(parseFloat(e.target.value))}
                      className="w-24 h-1 bg-white/30 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-pointer"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleZoomChange(1)}
                        className="px-3 py-1 text-xs rounded bg-white/20 text-white hover:bg-white/30 transition-colors"
                      >
                        Reset
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}