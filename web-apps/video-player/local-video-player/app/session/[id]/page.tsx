'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';

interface Player {
  jersey: string;
  events: number;
}

interface Team {
  name: string;
  color: string;
  score: number;
  shots_made: number;
  shots_missed: number;
  rebounds: number;
  players: Record<string, Player>;
}

interface Event {
  id: number;
  timestamp: string;
  seconds: number;
  team: 'team_a' | 'team_b' | 'bystander';
  player: string;
  jersey: string;
  team_color: string;
  event_type: string;
  shot_type?: string;
  outcome?: string;
  basket?: string;
  rebound_type?: string;
  description: string;
  coordinates?: { x: number; y: number };
  bystander: boolean;
  source: 'ai' | 'veo';
}

interface MatchInfo {
  title: string;
  duration: string;
  time_range: string;
  total_events: number;
}

interface Analysis {
  possession_changes: number;
  fast_breaks: number;
  three_pointers: number;
  layups: number;
  free_throws: number;
  turnovers: number;
  steals: number;
}

interface FootballData {
  match_info: MatchInfo;
  teams: {
    team_a: Team;
    team_b: Team;
  };
  events: Event[];
  analysis: Analysis;
}

interface SessionData {
  id: string;
  name: string;
  videoFile: string;
  eventsFile: string;
  duration: string;
  eventCount: number;
}

export default function SessionPage({ params }: { params: { id: string } }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [footballData, setFootballData] = useState<FootballData | null>(null);
  const [veoEvents, setVeoEvents] = useState<Event[]>([]);
  const [activeEventSource, setActiveEventSource] = useState<'ai' | 'veo'>('ai');
  const [currentEvent, setCurrentEvent] = useState<Event | null>(null);
  const [showEvents, setShowEvents] = useState(true);
  const [teamFilters, setTeamFilters] = useState<('team_a' | 'team_b' | 'bystander')[]>(['team_a', 'team_b', 'bystander']);
  const [outcomeFilters, setOutcomeFilters] = useState<('scored' | 'blocked' | 'saved')[]>(['scored', 'blocked', 'saved']);
  const [eventTypeFilters, setEventTypeFilters] = useState<string[]>(['goal', 'shot_on_target', 'pass', 'dribble', 'foul', 'turnover', 'free_kick']);
  const videoRef = useRef<HTMLVideoElement>(null);

  const timestampToSeconds = (ts: string): number => {
    if (!ts) return 0;
    const parts = ts.split(':').map(Number);
    if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
        return parts[0] * 60 + parts[1];
    }
    return 0;
  };

  // Load football data from JSON file
  useEffect(() => {
    const loadFootballData = async () => {
      try {
        const response = await fetch('/data/web_format.json'); // <-- 1. LOAD CORRECT FILE
        const data = await response.json();
        
        // 2. NORMALIZE DATA
        const rawEvents = (data.goals || []).concat(data.key_events || []);
        const normalizedEvents = rawEvents.map((e: any, index: number): Event => ({
            id: index,
            timestamp: e.timestamp,
            seconds: timestampToSeconds(e.timestamp),
            team: e.team?.toLowerCase().includes('black') ? 'team_a' : (e.team?.toLowerCase().includes('red') ? 'team_b' : 'bystander'),
            player: 'N/A',
            jersey: 'N/A',
            team_color: 'N/A',
            event_type: (e.type || 'unknown').toLowerCase().replace(/ /g, '_'),
            description: e.description,
            bystander: !e.team?.toLowerCase().includes('black') && !e.team?.toLowerCase().includes('red'),
            outcome: e.outcome,
            source: 'ai',
        }));

        const normalizedData: FootballData = {
            match_info: {
                title: data.match_id || "Football Game Analysis",
                duration: "N/A",
                time_range: "Full Match",
                total_events: normalizedEvents.length
            },
            teams: {
                team_a: { name: 'Black Team', color: 'cyan', score: 0, shots_made: 0, shots_missed: 0, rebounds: 0, players: {} },
                team_b: { name: 'Red Team', color: 'red', score: 0, shots_made: 0, shots_missed: 0, rebounds: 0, players: {} }
            },
            events: normalizedEvents.sort((a: Event, b: Event) => a.seconds - b.seconds),
            analysis: { 
                possession_changes: 0, fast_breaks: 0, three_pointers: 0, layups: 0, free_throws: 0, turnovers: 0, steals: 0
            }
        };

        setFootballData(normalizedData);
        console.log('Loaded and normalized football data:', normalizedData);

      } catch (error) {
        console.error('Failed to load football data:', error);
      }
    };

    const loadVeoData = async () => {
      try {
        const response = await fetch('/data/veo_ground_truth.json');
        if (!response.ok) {
          throw new Error(`File not found: ${response.statusText}`);
        }
        const data = await response.json();
        // The previous fix assumed `data.events`, let's be more robust
        const events = Array.isArray(data) ? data : data.events || [];
        const normalizedVeoEvents = events.map((e: any, index: number): Event => ({
            id: index + 1000, // Offset IDs to prevent key collisions
            timestamp: e.timestamp,
            seconds: e.timestamp_seconds,
            team: 'bystander',
            player: 'N/A',
            jersey: 'N/A',
            team_color: 'N/A',
            event_type: e.event_type?.toLowerCase() || 'unknown',
            description: e.event_type || 'Veo Event',
            bystander: true,
            source: 'veo',
            outcome: undefined,
            shot_type: undefined,
            basket: undefined,
            rebound_type: undefined,
            coordinates: undefined
        }));
        setVeoEvents(normalizedVeoEvents);
        console.log('Loaded and normalized Veo data:', normalizedVeoEvents);
      } catch (error) {
          console.warn('Could not load Veo ground truth data. It may be missing. This is not a critical error.', error);
          setVeoEvents([]); // Ensure veoEvents is an empty array on failure
      }
    };

    loadFootballData();
    loadVeoData();
  }, []);

  // Filter events based on current filters
  const getFilteredEvents = () => {
    const sourceEvents = activeEventSource === 'ai' ? footballData?.events : veoEvents;
    if (!sourceEvents) return [];

    return sourceEvents.filter(event => {
      // Team filter
      if (activeEventSource === 'ai') {
        const eventTeam = event.bystander ? 'bystander' : event.team;
        if (!teamFilters.includes(eventTeam)) return false;
      } else { // For 'veo', only show if 'bystander' is selected
        if (!teamFilters.includes('bystander')) return false;
      }

      // Event type filter
      if (eventTypeFilters.length > 0) {
        if (!eventTypeFilters.includes(event.event_type)) return false;
      }

      // Outcome filter (only for AI events)
      if (activeEventSource === 'ai' && outcomeFilters.length > 0 && event.outcome) {
        if (!outcomeFilters.includes(event.outcome as any)) return false;
      }

      return true;
    });
  };

  const filteredEvents = getFilteredEvents();

  // Update current event based on video time (using filtered events)
  useEffect(() => {
    if (!filteredEvents || filteredEvents.length === 0) {
      setCurrentEvent(null);
      return;
    }
    // Find the current event based on video time in filtered events
    const currentIndex = filteredEvents.findIndex(event => event.seconds > currentTime);
    const newEvent = currentIndex === -1 ? filteredEvents[filteredEvents.length - 1] : filteredEvents[Math.max(0, currentIndex - 1)];
    
    if (newEvent?.id !== currentEvent?.id) {
      setCurrentEvent(newEvent);
    }
  }, [currentTime, filteredEvents, currentEvent]);

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleMuteToggle = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const handleEventClick = (event: Event) => {
    if (videoRef.current) {
      videoRef.current.currentTime = event.seconds;
      setCurrentTime(event.seconds);
    }
  };

  const handlePreviousEvent = () => {
    if (filteredEvents.length === 0 || !currentEvent) return;
    
    // Find current event in filtered events
    const currentFilteredIndex = filteredEvents.findIndex(event => 
      event.id === currentEvent.id
    );
    
    if (currentFilteredIndex > 0) {
      const prevEvent = filteredEvents[currentFilteredIndex - 1];
      handleEventClick(prevEvent);
    }
  };

  const handleNextEvent = () => {
    if (filteredEvents.length === 0 || !currentEvent) return;
    
    // Find current event in filtered events
    const currentFilteredIndex = filteredEvents.findIndex(event => 
      event.id === currentEvent.id
    );
    
    if (currentFilteredIndex < filteredEvents.length - 1) {
      const nextEvent = filteredEvents[currentFilteredIndex + 1];
      handleEventClick(nextEvent);
    }
  };

  const handleJumpBackward = () => {
    if (videoRef.current && duration > 0) {
      const newTime = Math.max(0, currentTime - 5);
      console.log('Jumping backward:', { currentTime, newTime, duration });
      
      // Ensure video is ready for seeking
      if (videoRef.current.readyState >= 2) { // HAVE_CURRENT_DATA
        videoRef.current.currentTime = newTime;
        setCurrentTime(newTime);
      } else {
        console.log('Video not ready for seeking, readyState:', videoRef.current.readyState);
      }
    } else {
      console.log('Cannot jump backward:', { videoRef: !!videoRef.current, duration });
    }
  };

  const handleJumpForward = () => {
    if (videoRef.current && duration > 0) {
      const newTime = Math.min(duration, currentTime + 5);
      console.log('Jumping forward:', { currentTime, newTime, duration });
      
      // Ensure video is ready for seeking
      if (videoRef.current.readyState >= 2) { // HAVE_CURRENT_DATA
        videoRef.current.currentTime = newTime;
        setCurrentTime(newTime);
      } else {
        console.log('Video not ready for seeking, readyState:', videoRef.current.readyState);
      }
    } else {
      console.log('Cannot jump forward:', { videoRef: !!videoRef.current, duration });
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const getEventColor = (team: 'team_a' | 'team_b' | 'bystander', isBystander: boolean, source: 'ai' | 'veo') => {
    if (source === 'veo') return 'bg-green-500';
    if (!footballData) return 'bg-gray-500';
    
    if (isBystander) {
      return 'bg-yellow-500'; // Yellow for bystanders
    } else if (team === 'team_a') {
      return 'bg-red-500'; // Using Tailwind red for team A
    } else if (team === 'team_b') {
      return 'bg-cyan-500'; // Using Tailwind cyan for team B
    }
    return 'bg-gray-500';
  };

  const getTeamName = (team: string) => {
    if (!footballData) return team;
    
    if (team === 'team_a') {
      return footballData.teams.team_a.name;
    } else if (team === 'team_b') {
      return footballData.teams.team_b.name;
    }
    return team;
  };

  // Calculate current score based on video time
  const getCurrentScore = () => {
    if (!footballData) return { teamAScore: 0, teamBScore: 0 };
    
    let teamAScore = 0;
    let teamBScore = 0;
    
    footballData.events.forEach(event => {
      // Only count events that have happened (before current video time)
      if (event.seconds <= currentTime) {
        // Count goals for football
        if (event.event_type === 'goal' && !event.bystander) {
          if (event.team === 'team_a') {
            teamAScore += 1;
          } else if (event.team === 'team_b') {
            teamBScore += 1;
          }
        }
      }
    });
    
    return { teamAScore, teamBScore };
  };


  // Auto-scroll to current event in sidebar
  useEffect(() => {
    if (currentEvent && showEvents) {
      const eventElement = document.getElementById(`event-${currentEvent.id}`);
      if (eventElement) {
        eventElement.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
          inline: 'nearest'
        });
      }
    }
  }, [currentEvent, showEvents]);

  // Toggle filter functions
  const toggleTeamFilter = (team: 'team_a' | 'team_b' | 'bystander') => {
    setTeamFilters(prev => 
      prev.includes(team) 
        ? prev.filter(t => t !== team)
        : [...prev, team]
    );
  };

  const toggleOutcomeFilter = (outcome: 'scored' | 'blocked' | 'saved') => {
    setOutcomeFilters(prev => 
      prev.includes(outcome) 
        ? prev.filter(o => o !== outcome)
        : [...prev, outcome]
    );
  };

  const toggleEventTypeFilter = (eventType: string) => {
    setEventTypeFilters(prev => 
      prev.includes(eventType) 
        ? prev.filter(e => e !== eventType)
        : [...prev, eventType]
    );
  };

  return (
    <div className="h-screen bg-black relative overflow-hidden">
      {/* Top Header - Back Button and Score Banner */}
      <div className="absolute top-4 left-4 z-50 flex items-center space-x-4">
        <Link href="/" className="bg-black/80 backdrop-blur-sm rounded-lg px-4 py-2 text-white hover:text-gray-300 transition-colors">
          ← Back to Sessions
        </Link>
        
        {footballData?.teams ? (
          <div className="bg-black/80 backdrop-blur-sm rounded-lg px-6 py-2">
            <div className="flex items-center space-x-6 text-white">
              <span className="font-bold">{footballData.teams.team_a.name}</span>
              <span className="font-bold">{getCurrentScore().teamAScore}</span>
              <span>vs</span>
              <span className="font-bold">{getCurrentScore().teamBScore}</span>
              <span className="font-bold">{footballData.teams.team_b.name}</span>
              <span className="text-gray-300">|</span>
              <span>{formatTime(currentTime)}</span>
            </div>
          </div>
        ) : (
          <div className="bg-black/80 backdrop-blur-sm rounded-lg px-6 py-2">
            <div className="flex items-center space-x-6 text-white">
              <span className="font-bold">Loading...</span>
              <span className="text-gray-300">|</span>
              <span>{formatTime(currentTime)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Video Container */}
      <div className="relative h-full flex items-center justify-center">
        {/* Video Element */}
        <video
          ref={videoRef}
          className="w-full h-full object-contain"
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
        >
          <source src="/videos/ballyclare-20250111.mp4" type="video/mp4" />
          <div className="flex items-center justify-center w-full h-full bg-gray-900 text-white">
            <div className="text-center">
              <div className="text-6xl mb-4">⚽</div>
              <h3 className="text-xl font-semibold mb-2">Football Video Player</h3>
              <p className="text-gray-400">Video file not found. Add a football video to /public/videos/</p>
              <p className="text-sm text-gray-500 mt-2">Events data is loaded and functional</p>
            </div>
          </div>
        </video>



        {/* Progress Bar - Attached to Video Bottom */}
        <div className="absolute bottom-0 left-0 right-0 z-40">
          <div className="bg-transparent">
            {/* Timeline Dots Overlay */}
            {(footballData || veoEvents) && (
              <div className="relative h-12 px-4 pt-3 pointer-events-none z-5">
                {[...(footballData?.events || []), ...veoEvents].map((event, index) => {
                  // Use the last event's seconds as fallback duration if video duration isn't loaded
                  const effectiveDuration = duration > 0 ? duration : (footballData?.events[footballData.events.length - 1]?.seconds || 600);
                  const position = (event.seconds / effectiveDuration) * 100;
                  const isCurrent = event.id === currentEvent?.id;
                  
                  // Check if this event is in the filtered events
                  const isFiltered = filteredEvents.some(filteredEvent => 
                    filteredEvent.id === event.id
                  );
                  
                  return (
                    <button
                      key={event.id}
                      onClick={() => handleEventClick(event)}
                      className={`absolute top-1/2 transform -translate-y-1/2 w-2.5 h-2.5 transition-all duration-300 hover:scale-200 hover:shadow-xl pointer-events-auto ${
                        event.source === 'veo' ? 'rounded-sm' : 'rounded-full'
                      } ${
                        getEventColor(event.team, event.bystander, event.source)
                      } ${isCurrent ? 'ring-3 ring-yellow-400 ring-offset-2 ring-offset-black shadow-xl scale-125' : 'hover:ring-2 hover:ring-white/70'} ${
                        !isFiltered ? 'opacity-30' : ''
                      }`}
                      style={{ left: `${position}%` }}
                      title={`${getTeamName(event.team)} ${event.event_type} at ${event.timestamp}`}
                    />
                  );
                })}
              </div>
            )}

            {/* Main Control Bar - Veo Style */}
            <div className="px-6 py-3">
              <div className="flex items-center justify-between">
                {/* Left Side - Playback Controls */}
                <div className="flex items-center space-x-2">
                  {/* Play/Pause Button */}
                  <button
                    onClick={handlePlayPause}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title={isPlaying ? 'Pause' : 'Play'}
                  >
                    {isPlaying ? '⏸' : '▶'}
                  </button>

                  {/* Skip Backward */}
                  <button
                    onClick={handleJumpBackward}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title="Skip Backward 5s"
                  >
                    ↺
                  </button>

                  {/* Skip Forward */}
                  <button
                    onClick={handleJumpForward}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title="Skip Forward 5s"
                  >
                    ↻
                  </button>

                  {/* Volume Control */}
                  <button
                    onClick={handleMuteToggle}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title={isMuted ? 'Unmute' : 'Mute'}
                  >
                    {isMuted ? '🔇' : '🔊'}
                  </button>
                </div>

                {/* Center - Events Toggle, Time, and Progress Bar */}
                <div className="flex-1 flex flex-col items-center justify-center mx-8">
                  {/* Events Toggle Button - Above Time */}
                  <button
                    onClick={() => setShowEvents(!showEvents)}
                    className="text-white/90 hover:text-white transition-colors p-1 mb-2"
                    title="Toggle Events Panel"
                  >
                    ☰
                  </button>

                  {/* Time Display */}
                  <div className="text-white/90 text-sm font-medium mb-2">
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="w-full max-w-md">
                    <div className="relative">
                      <input
                        type="range"
                        min="0"
                        max={duration || 0}
                        value={currentTime}
                        onChange={handleSeek}
                        onInput={handleSeek}
                        className="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
                        style={{
                          background: `linear-gradient(to right, #ffffff 0%, #ffffff ${(currentTime / duration) * 100}%, #4b5563 ${(currentTime / duration) * 100}%, #4b5563 100%)`
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Right Side - Event Navigation */}
                <div className="flex items-center space-x-2">
                  {/* Previous Event */}
                  <button
                    onClick={handlePreviousEvent}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title="Previous Event"
                    disabled={filteredEvents.length === 0}
                  >
                    ◀
                  </button>

                  {/* Current Event Display - Centered */}
                  <div className="text-white/90 text-xs font-medium min-w-[140px] text-center flex items-center justify-center">
                    {currentEvent ? (
                      <div className="flex items-center justify-center space-x-1">
                        <span>{currentEvent.bystander ? '●' : (currentEvent.team === 'team_a' ? '●' : '●')}</span>
                        <span>{getTeamName(currentEvent.team)} {currentEvent.event_type}</span>
                      </div>
                    ) : (
                      <span>No event</span>
                    )}
                  </div>

                  {/* Next Event */}
                  <button
                    onClick={handleNextEvent}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title="Next Event"
                    disabled={filteredEvents.length === 0}
                  >
                    ▶
                  </button>

                  {/* Fullscreen Button */}
                  <button
                    onClick={() => {
                      if (document.fullscreenElement) {
                        document.exitFullscreen();
                      } else {
                        document.documentElement.requestFullscreen();
                      }
                    }}
                    className="text-white/90 hover:text-white transition-colors p-2"
                    title="Toggle Fullscreen"
                  >
                    ⛶
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Events Sidebar */}
      {showEvents && (footballData || veoEvents) && (
        <div className="absolute top-0 right-0 h-full w-80 bg-black/90 backdrop-blur-sm border-l border-gray-700 flex flex-col">
          {/* Sticky Header */}
          <div className="sticky top-0 bg-black/90 backdrop-blur-sm p-4 z-10">
            <div className="flex items-center justify-between mb-4">
              <button
                onClick={() => setShowEvents(false)}
                className="text-gray-300 hover:text-white text-xl font-bold"
                title="Hide Events"
              >
                ×
              </button>
              <h2 className="text-white font-semibold">Events ({filteredEvents.length})</h2>
            </div>
            {/* Source Toggles */}
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setActiveEventSource('ai')}
                className={`w-full py-2 text-sm font-medium rounded-md transition-colors ${activeEventSource === 'ai' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
              >
                AI Analysis
              </button>
              {veoEvents.length > 0 && (
                <button
                  onClick={() => setActiveEventSource('veo')}
                  className={`w-full py-2 text-sm font-medium rounded-md transition-colors ${activeEventSource === 'veo' ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                >
                  Veo Ground Truth
                </button>
              )}
            </div>
          </div>

          {/* Filter Section */}
          <div className="border-b border-t border-gray-700 p-4">
            <h3 className="text-white font-medium mb-3">Filters</h3>
            
            {/* Team Filters */}
            <div className="mb-4">
              <div className="text-xs text-gray-400 mb-2">Team</div>
              <div className="flex space-x-2">
                {[
                  { key: 'team_a', label: 'Team A', color: 'bg-red-600' },
                  { key: 'team_b', label: 'Team B', color: 'bg-cyan-600' },
                  { key: 'bystander', label: 'Bystander', color: 'bg-yellow-600' }
                ].map(filter => (
                  <button
                    key={filter.key}
                    onClick={() => toggleTeamFilter(filter.key as any)}
                    className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                      teamFilters.includes(filter.key as any) 
                        ? `${filter.color} text-white` 
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Outcome Filters */}
            <div className="mb-4">
              <div className="text-xs text-gray-400 mb-2">Event Outcome</div>
              <div className="flex space-x-2">
                {[
                  { key: 'scored', label: 'Scored' },
                  { key: 'blocked', label: 'Blocked' },
                  { key: 'saved', label: 'Saved' }
                ].map(filter => (
                  <button
                    key={filter.key}
                    onClick={() => toggleOutcomeFilter(filter.key as any)}
                    className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                      outcomeFilters.includes(filter.key as any) 
                        ? 'bg-green-600 text-white' 
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Event Type Filters */}
            <div className="mb-4">
              <div className="text-xs text-gray-400 mb-2">Event Type</div>
              <div className="flex space-x-2">
                {[
                  { key: 'goal', label: 'Goal' },
                  { key: 'shot_on_target', label: 'Shot' },
                  { key: 'pass', label: 'Pass' },
                  { key: 'dribble', label: 'Dribble' },
                  { key: 'foul', label: 'Foul' },
                  { key: 'turnover', label: 'Turnover' },
                  { key: 'free_kick', label: 'Free Kick' }
                ].map(filter => (
                  <button
                    key={filter.key}
                    onClick={() => toggleEventTypeFilter(filter.key as string)}
                    className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                      eventTypeFilters.includes(filter.key as string) 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          {/* Scrollable Events List */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              {filteredEvents.map((event) => (
                <button
                  key={event.id}
                  id={`event-${event.id}`}
                  onClick={() => handleEventClick(event)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    event.id === currentEvent?.id 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span>{event.source === 'veo' ? '🟩' : (event.bystander ? '🟡' : (event.team === 'team_a' ? '🔴' : '🔵'))}</span>
                      <span className="text-sm">
                        {event.bystander ? 'Bystander' : getTeamName(event.team)} {event.event_type}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">{event.timestamp}</span>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">{event.description}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Events Sidebar Toggle Button */}
      {!showEvents && (
        <div className="absolute top-4 right-4 z-50">
          <button
            onClick={() => setShowEvents(true)}
            className="bg-black/80 backdrop-blur-sm rounded-lg p-3 text-white hover:text-gray-300 transition-colors"
            title="Show Events"
          >
            📊
          </button>
        </div>
      )}
    </div>
  );
} 
