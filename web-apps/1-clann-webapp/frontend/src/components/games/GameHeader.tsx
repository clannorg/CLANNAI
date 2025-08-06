'use client'

import Link from 'next/link'

interface GameHeaderProps {
  game: {
    team_name: string
    title: string
  }
  teamScores: {
    red: number
    black: number
  }
  currentTime: number
  showEvents: boolean
  onToggleEvents: () => void
}

export default function GameHeader({
  game,
  teamScores,
  currentTime,
  showEvents,
  onToggleEvents
}: GameHeaderProps) {
  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <>
      {/* Left side - Dashboard link and game info */}
      <div className="absolute top-4 left-4 z-50 flex items-center space-x-2 md:space-x-4 transition-all duration-300">
        <Link 
          href="/dashboard" 
          className="group flex items-center space-x-2 bg-white/10 hover:bg-white/20 backdrop-blur-lg rounded-xl px-4 py-2.5 text-white transition-all duration-200 border border-white/20 hover:border-white/30 shadow-lg"
        >
          <svg className="w-4 h-4 transition-transform group-hover:-translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="font-medium" style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>Dashboard</span>
        </Link>
        
        <div className="bg-white/10 backdrop-blur-lg rounded-xl px-6 py-2.5 border border-white/20 shadow-lg">
          <div className="flex items-center space-x-4 text-white" style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>
            <span className="font-semibold text-sm">{game.team_name}</span>
            <div className="w-px h-4 bg-white/30"></div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 rounded-full bg-red-400"></div>
                <span className="font-bold text-sm">{teamScores.red}</span>
              </div>
              <span className="text-white/60 font-medium">-</span>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                <span className="font-bold text-sm">{teamScores.black}</span>
              </div>
            </div>
            <div className="w-px h-4 bg-white/30"></div>
            <span className="font-medium text-sm text-white/90">{game.title}</span>
            <div className="w-px h-4 bg-white/30"></div>
            <span className="font-mono text-sm text-white/80">{formatTime(currentTime)}</span>
          </div>
        </div>
      </div>

      {/* Right side - AI Coach toggle button (only show when sidebar is closed) */}
      {!showEvents && (
        <div className="absolute top-4 right-4 z-50">
          <button
            onClick={onToggleEvents}
            className="group flex items-center space-x-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 border shadow-lg bg-white/10 hover:bg-white/20 border-white/20 hover:border-white/30 text-white"
            title="Open AI Coach"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <span style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>AI Coach</span>
          </button>
        </div>
      )}
    </>
  )
}