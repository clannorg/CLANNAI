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
        
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl px-6 py-3 border border-white/20 shadow-lg">
          <div className="flex items-center space-x-4 text-white" style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>
            <span className="font-semibold text-base">{game.team_name}</span>
            <div className="w-px h-5 bg-white/30"></div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-1">
                <div className="w-2.5 h-2.5 rounded-full bg-red-400"></div>
                <span className="font-bold text-base">{teamScores.red}</span>
              </div>
              <span className="text-white/60 font-medium text-base">-</span>
              <div className="flex items-center space-x-1">
                <div className="w-2.5 h-2.5 rounded-full bg-blue-400"></div>
                <span className="font-bold text-base">{teamScores.black}</span>
              </div>
            </div>
            <div className="w-px h-5 bg-white/30"></div>
            <span className="font-medium text-base text-white/90">{game.title}</span>
            <div className="w-px h-5 bg-white/30"></div>
            <span className="font-mono text-base text-white/80">{formatTime(currentTime)}</span>
          </div>
        </div>
      </div>

      {/* Right side - AI Coach toggle button (only show when sidebar is closed) */}
      {!showEvents && (
        <div className="absolute top-4 right-4 z-50">
          <button
            onClick={onToggleEvents}
            className="group flex items-center space-x-3 px-6 py-3 rounded-2xl font-semibold text-base transition-all duration-300 border shadow-lg bg-gradient-to-r from-blue-500/20 to-purple-500/20 hover:from-blue-500/30 hover:to-purple-500/30 border-blue-400/40 hover:border-blue-300/60 text-white backdrop-blur-lg hover:scale-105"
            title="Open AI Coach"
          >
            <span className="text-lg group-hover:scale-110 transition-transform duration-300">🤖</span>
            <span style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }} className="font-semibold">
              AI Coach
            </span>
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          </button>
        </div>
      )}
    </>
  )
}