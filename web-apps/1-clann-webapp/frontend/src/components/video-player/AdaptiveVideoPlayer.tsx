'use client';

import React, { useRef, useEffect, useState } from 'react';
import { Play, Pause, Volume2, VolumeX } from 'lucide-react';

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
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(muted);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
      setIsLoading(false);
      onPlay?.();
    };

    const handlePause = () => {
      setIsPlaying(false);
      onPause?.();
    };

    const handleLoadedMetadata = () => {
      setIsLoading(false);
      setError(null);
      onLoadedMetadata?.();
      handleDurationChange();
    };

    const handleCanPlay = () => {
      setIsLoading(false);
      setError(null);
    };

    const handleError = () => {
      setError('Failed to load video');
      setIsLoading(false);
    };

    const handleLoadStart = () => {
      setIsLoading(true);
      setError(null);
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('durationchange', handleDurationChange);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('canplay', handleCanPlay);
    video.addEventListener('error', handleError);
    video.addEventListener('loadstart', handleLoadStart);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('durationchange', handleDurationChange);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('canplay', handleCanPlay);
      video.removeEventListener('error', handleError);
      video.removeEventListener('loadstart', handleLoadStart);
    };
  }, [onTimeUpdate, onDurationChange, onPlay, onPause, onLoadedMetadata]);

  const togglePlayPause = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play().catch((e) => {
        console.error('Play failed:', e);
        setError('Playback failed');
      });
    }
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    video.muted = !video.muted;
    setIsMuted(video.muted);
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const video = videoRef.current;
    if (!video || duration === 0) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    video.currentTime = percent * duration;
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
          <p className="text-xs text-gray-500 mt-2">URL: {src}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative aspect-video bg-black group ${className}`}>
      {/* Video Element - SIMPLE & WORKING */}
      <video
        ref={videoRef}
        className="w-full h-full object-contain"
        src={src}
        autoPlay={autoPlay}
        muted={isMuted}
        playsInline
        crossOrigin="anonymous"
        controls={false}
        preload="metadata"
      />

      {/* Loading Spinner */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
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

      {/* Simple Controls */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 opacity-0 group-hover:opacity-100 transition-opacity">
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
        </div>
      </div>
    </div>
  );
} 