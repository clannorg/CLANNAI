'use client'

import Link from 'next/link'
import { getTeamInfo, getTeamColorClass } from '@/lib/team-utils'

interface GameHeaderProps {
  game: {
    team_name: string
    title: string
    metadata?: {
      teams?: {
        red_team: { name: string, jersey_color: string }
        blue_team: { name: string, jersey_color: string }
      }
    }
  }
  teamScores: {
    red: number
    blue: number
  }
  currentTime: number
  showEvents: boolean
  onToggleEvents: () => void
  isMobile?: boolean
}

export default function GameHeader({
  game,
  teamScores,
  currentTime,
  showEvents,
  onToggleEvents,
  isMobile = false
}: GameHeaderProps) {
  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  // Get team information from metadata
  const { redTeam, blueTeam } = getTeamInfo(game)
  
  // Get dynamic colors for team indicators
  const redTeamColorClass = getTeamColorClass(redTeam.jersey_color)
  const blueTeamColorClass = getTeamColorClass(blueTeam.jersey_color)
  
  // Extract just the background color part for the small indicator dots
  const getIndicatorColor = (colorClass: string) => {
    const bgMatch = colorClass.match(/bg-(\w+-\d+)/)
    return bgMatch ? bgMatch[1] : 'gray-500'
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
        
        <div className={`bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 shadow-lg ${
          isMobile ? 'px-3 py-2' : 'px-6 py-3'
        }`}>
          <div className={`flex items-center text-white ${
            isMobile ? 'space-x-2' : 'space-x-4'
          }`} style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>
            <div className={`flex items-center ${isMobile ? 'space-x-1.5' : 'space-x-3'}`}>
              <div className="flex items-center space-x-1" title={`${redTeam.name} (${redTeam.jersey_color})`}>
                <div className={`rounded-full bg-${getIndicatorColor(redTeamColorClass)} ${isMobile ? 'w-1.5 h-1.5' : 'w-2.5 h-2.5'}`}></div>
                <span className={`font-semibold ${isMobile ? 'text-sm' : 'text-base'}`} style={{ textShadow: '0 1px 4px rgba(0,0,0,0.8)' }}>
                  {isMobile ? redTeam.name.split(' ')[0] : redTeam.name}
                </span>
                <span className={`font-bold ${isMobile ? 'text-sm' : 'text-base'}`}>{teamScores.red}</span>
              </div>
              <span className={`text-white/60 font-medium ${isMobile ? 'text-sm' : 'text-base'}`}>-</span>
              <div className="flex items-center space-x-1" title={`${blueTeam.name} (${blueTeam.jersey_color})`}>
                <div className={`rounded-full bg-${getIndicatorColor(blueTeamColorClass)} ${isMobile ? 'w-1.5 h-1.5' : 'w-2.5 h-2.5'}`}></div>
                <span className={`font-semibold ${isMobile ? 'text-sm' : 'text-base'}`} style={{ textShadow: '0 1px 4px rgba(0,0,0,0.8)' }}>
                  {isMobile ? blueTeam.name.split(' ')[0] : blueTeam.name}
                </span>
                <span className={`font-bold ${isMobile ? 'text-sm' : 'text-base'}`}>{teamScores.blue}</span>
              </div>
            </div>
            <div className={`bg-white/30 ${isMobile ? 'w-px h-3' : 'w-px h-5'}`}></div>
            <span className={`font-mono text-white/80 ${isMobile ? 'text-sm' : 'text-base'}`}>{formatTime(currentTime)}</span>
          </div>
        </div>
      </div>

      {/* Right side - AI Coach toggle button (only show when sidebar is closed and not mobile) */}
      {!showEvents && !isMobile && (
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