'use client'

import Link from 'next/link'
import { ChatToggleButton } from '../ai-chat'

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
  showChat: boolean
  showEvents: boolean
  onToggleEvents: () => void
}

export default function GameHeader({
  game,
  teamScores,
  currentTime,
  showChat,
  showEvents,
  onToggleEvents
}: GameHeaderProps) {
  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <div className={`absolute top-4 z-50 flex items-center space-x-2 md:space-x-4 transition-all duration-300 ${
      showChat ? 'md:left-[336px] left-4' : 'left-4'
    }`}>
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

      <div className="flex items-center space-x-3">
        <ChatToggleButton 
          className="mobile-chat-toggle"
        />
        
        <button
          onClick={onToggleEvents}
          className={`group flex items-center space-x-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 border shadow-lg ${
            showEvents 
              ? 'bg-green-500/20 hover:bg-green-500/30 border-green-400/40 text-green-200' 
              : 'bg-white/10 hover:bg-white/20 border-white/20 hover:border-white/30 text-white'
          }`}
          title="Toggle Events"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>Events</span>
        </button>
      </div>
    </div>
  )
}