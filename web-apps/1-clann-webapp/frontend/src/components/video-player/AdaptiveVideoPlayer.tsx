'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';
import Hls from 'hls.js';
import { Play, Pause, Volume2, VolumeX, Maximize, Settings, Loader2 } from 'lucide-react';

interface AdaptiveVideoPlayerProps {
  src: string;
  title?: string;
  className?: string;
  onTimeUpdate?: (currentTime: number) => void;
  onDurationChange?: (duration: number) => void;
  onPlay?: () => void;
  onPause?: () => void;
  onLoadedMetadata?: () => void;
  autoPlay?: boolean;
  muted?: boolean;
  events?: Array<{
    timestamp: number;
    type: string;
    description?: string;
  }>;
  onEventClick?: (timestamp: number) => void;
}

interface VideoQuality {
  height: number;
  bitrate: number;
  level: number;
}

export function AdaptiveVideoPlayer({
  src,
  title,
  className = '',
  onTimeUpdate,
  onDurationChange,
  onPlay,
  onPause,
  onLoadedMetadata,
  autoPlay = false,
  muted = false,
  events = [],
  onEventClick,
}: AdaptiveVideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const hlsRef = useRef<Hls | null>(null);
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(muted);
  const [showControls, setShowControls] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [qualities, setQualities] = useState<VideoQuality[]>([]);
  const [currentQuality, setCurrentQuality] = useState<number>(-1);
  const [showQualityMenu, setShowQualityMenu] = useState(false);

  const controlsTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-hide controls
  const showControlsTemporarily = useCallback(() => {
    setShowControls(true);
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current);
    }
    controlsTimeoutRef.current = setTimeout(() => {
      if (isPlaying) {
        setShowControls(false);
      }
    }, 3000);
  }, [isPlaying]);

  // Initialize video player
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !src) return;

    const initializeVideo = async () => {
      setIsLoading(true);
      setError(null);

      // Check if src is an HLS URL
      const isHlsUrl = src.includes('.m3u8') || src.includes('playlist');
      
      // Try HLS first if supported and it looks like HLS
      if (isHlsUrl && Hls.isSupported()) {
        try {
          const hls = new Hls({
            enableWorker: true,
            lowLatencyMode: false,
            backBufferLength: 90,
            debug: false,
          });

          hls.loadSource(src);
          hls.attachMedia(video);

          hls.on(Hls.Events.MANIFEST_PARSED, () => {
            setIsLoading(false);
            
            // Extract quality levels
            const levels = hls.levels.map((level, index) => ({
              height: level.height || 0,
              bitrate: level.bitrate,
              level: index,
            }));
            setQualities(levels);
          });

          hls.on(Hls.Events.ERROR, (event, data) => {
            if (data.fatal) {
              setError('Failed to load video stream');
              setIsLoading(false);
            }
          });

          hlsRef.current = hls;
          return;
        } catch (err) {
          console.error('HLS initialization failed:', err);
        }
      }

      // Fallback to progressive download
      try {
        video.src = src;
        setIsLoading(false);
      } catch (err) {
        setError('Failed to load video');
        setIsLoading(false);
      }
    };

    initializeVideo();

    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy();
        hlsRef.current = null;
      }
    };
  }, [src]);

  // Video event handlers
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      const time = video.currentTime;
      setCurrentTime(time);
      onTimeUpdate?.(time);
    };

    const handleDurationChange = () => {
      const dur = video.duration;
      setDuration(dur);
      onDurationChange?.(dur);
    };

    const handlePlay = () => {
      setIsPlaying(true);
      onPlay?.();
    };

    const handlePause = () => {
      setIsPlaying(false);
      onPause?.();
    };

    const handleLoadedMetadata = () => {
      onLoadedMetadata?.();
      handleDurationChange();
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('durationchange', handleDurationChange);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('durationchange', handleDurationChange);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
    };
  }, [onTimeUpdate, onDurationChange, onPlay, onPause, onLoadedMetadata]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!videoRef.current) return;

      switch (e.code) {
        case 'Space':
          e.preventDefault();
          togglePlayPause();
          break;
        case 'KeyF':
          e.preventDefault();
          toggleFullscreen();
          break;
        case 'KeyM':
          e.preventDefault();
          toggleMute();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          seek(currentTime - 10);
          break;
        case 'ArrowRight':
          e.preventDefault();
          seek(currentTime + 10);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentTime]);

  // Mouse movement handler
  const handleMouseMove = useCallback(() => {
    showControlsTemporarily();
  }, [showControlsTemporarily]);

  const togglePlayPause = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    video.muted = !video.muted;
    setIsMuted(video.muted);
  };

  const toggleFullscreen = () => {
    const container = containerRef.current;
    if (!container) return;

    if (!document.fullscreenElement) {
      container.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const seek = (time: number) => {
    const video = videoRef.current;
    if (!video) return;

    video.currentTime = Math.max(0, Math.min(duration, time));
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    seek(percent * duration);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
      setIsMuted(newVolume === 0);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getEventTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'goal': return 'bg-green-500';
      case 'shot': return 'bg-blue-500';
      case 'foul': return 'bg-red-500';
      case 'yellow card': return 'bg-yellow-500';
      case 'red card': return 'bg-red-600';
      default: return 'bg-gray-500';
    }
  };

  if (error) {
    return (
      <div className={`relative aspect-video bg-gray-900 flex items-center justify-center ${className}`}>
        <div className="text-center text-white">
          <p className="text-lg font-medium">Failed to load video</p>
          <p className="text-sm text-gray-400 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className={`relative aspect-video bg-black group ${className}`}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => isPlaying && setShowControls(false)}
    >
      {/* Video Element */}
      <video
        ref={videoRef}
        className="w-full h-full"
        src={src}
        autoPlay={autoPlay}
        muted={isMuted}
        playsInline
        crossOrigin="anonymous"
      >
        <source src={src} type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      {/* Loading Spinner */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
          <Loader2 className="w-8 h-8 text-white animate-spin" />
        </div>
      )}

      {/* Event Timeline */}
      {duration > 0 && events.length > 0 && (
        <div className="absolute bottom-20 left-4 right-4">
          <div className="relative h-2 bg-white/20 rounded-full cursor-pointer" onClick={handleProgressClick}>
            {/* Progress bar */}
            <div 
              className="absolute top-0 left-0 h-full bg-[#016F32] rounded-full"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            />
            
            {/* Event markers */}
            {events.map((event, index) => (
              <button
                key={index}
                className={`absolute top-0 w-3 h-3 rounded-full transform -translate-y-0.5 ${getEventTypeColor(event.type)} hover:scale-125 transition-all`}
                style={{ left: `${(event.timestamp / duration) * 100}%` }}
                onClick={(e) => {
                  e.stopPropagation();
                  onEventClick?.(event.timestamp);
                }}
                title={`${event.type} - ${formatTime(event.timestamp)}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Controls */}
      {showControls && (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
          {/* Progress Bar */}
          <div className="mb-4">
            <div 
              className="relative h-1 bg-white/30 rounded-full cursor-pointer"
              onClick={handleProgressClick}
            >
              <div 
                className="absolute top-0 left-0 h-full bg-white rounded-full"
                style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
              />
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex items-center justify-between text-white">
            <div className="flex items-center space-x-4">
              {/* Play/Pause */}
              <button
                onClick={togglePlayPause}
                className="w-10 h-10 flex items-center justify-center rounded-full bg-white/20 hover:bg-white/30 transition-colors"
              >
                {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
              </button>

              {/* Volume */}
              <div className="flex items-center space-x-2">
                <button onClick={toggleMute} className="p-2 hover:bg-white/20 rounded">
                  {isMuted || volume === 0 ? (
                    <VolumeX className="w-5 h-5" />
                  ) : (
                    <Volume2 className="w-5 h-5" />
                  )}
                </button>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={isMuted ? 0 : volume}
                  onChange={handleVolumeChange}
                  className="w-20 accent-white"
                />
              </div>

              {/* Time Display */}
              <span className="text-sm">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>
            </div>

            <div className="flex items-center space-x-2">
              {/* Quality Menu */}
              {qualities.length > 0 && (
                <div className="relative">
                  <button
                    onClick={() => setShowQualityMenu(!showQualityMenu)}
                    className="p-2 hover:bg-white/20 rounded"
                  >
                    <Settings className="w-5 h-5" />
                  </button>
                  
                  {showQualityMenu && (
                    <div className="absolute bottom-full right-0 mb-2 bg-black/90 rounded-lg py-2 min-w-[120px]">
                      <button
                        onClick={() => {
                          if (hlsRef.current) {
                            hlsRef.current.currentLevel = -1;
                            setCurrentQuality(-1);
                          }
                          setShowQualityMenu(false);
                        }}
                        className={`block w-full text-left px-4 py-2 text-sm hover:bg-white/20 ${
                          currentQuality === -1 ? 'text-[#016F32]' : ''
                        }`}
                      >
                        Auto
                      </button>
                      {qualities.map((quality) => (
                        <button
                          key={quality.level}
                          onClick={() => {
                            if (hlsRef.current) {
                              hlsRef.current.currentLevel = quality.level;
                              setCurrentQuality(quality.level);
                            }
                            setShowQualityMenu(false);
                          }}
                          className={`block w-full text-left px-4 py-2 text-sm hover:bg-white/20 ${
                            currentQuality === quality.level ? 'text-[#016F32]' : ''
                          }`}
                        >
                          {quality.height}p
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Fullscreen */}
              <button
                onClick={toggleFullscreen}
                className="p-2 hover:bg-white/20 rounded"
              >
                <Maximize className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Keyboard Shortcuts Help */}
      <div className="absolute top-4 left-4 text-xs text-white/60">
        Space: Play/Pause • F: Fullscreen • M: Mute • ←→: Seek ±10s
      </div>
    </div>
  );
} 