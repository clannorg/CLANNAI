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
      {/* Left side - Dashboard icon */}
      <div className="absolute top-4 left-4 z-50">
        <Link 
          href="/dashboard" 
          className={`group flex items-center justify-center bg-white/10 hover:bg-white/20 backdrop-blur-lg rounded-2xl text-white transition-all duration-200 border border-white/20 hover:border-white/30 shadow-xl ${
            isMobile ? 'px-3 py-2.5' : 'px-4 py-4'
          }`}
          title="Back to Dashboard"
        >
          <svg className={`transition-transform group-hover:-translate-x-0.5 ${isMobile ? 'w-4 h-4' : 'w-5 h-5'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Link>
      </div>

      {/* Left side - Score Display */}
      <div className="absolute top-4 left-20 z-50">
        <div className={`bg-black/50 backdrop-blur-lg rounded-2xl border border-white/30 shadow-xl ${
          isMobile ? 'px-4 py-2.5' : 'px-8 py-4'
        }`}>
          <div className={`flex items-center ${isMobile ? 'space-x-2' : 'space-x-4'}`}>
            <div className="flex items-center space-x-2" title={`${redTeam.name} (${redTeam.jersey_color})`}>
              <span className={`font-medium text-white/90 ${isMobile ? 'text-sm' : 'text-base'}`} style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>
                {isMobile ? redTeam.name.split(' ')[0].toUpperCase() : redTeam.name.toUpperCase()}
              </span>
              <span className={`font-bold text-white ${isMobile ? 'text-xl' : 'text-2xl'}`} style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>
                {teamScores.red}
              </span>
              <div className={`rounded-full bg-${getIndicatorColor(redTeamColorClass)} ${isMobile ? 'w-2 h-2' : 'w-3 h-3'}`}></div>
            </div>
            
            <span className={`text-white/80 font-bold ${isMobile ? 'text-lg' : 'text-xl'}`} style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>-</span>
            
            <div className="flex items-center space-x-2" title={`${blueTeam.name} (${blueTeam.jersey_color})`}>
              <div className={`rounded-full bg-${getIndicatorColor(blueTeamColorClass)} ${isMobile ? 'w-2 h-2' : 'w-3 h-3'}`}></div>
              <span className={`font-bold text-white ${isMobile ? 'text-xl' : 'text-2xl'}`} style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>
                {teamScores.blue}
              </span>
              <span className={`font-medium text-white/90 ${isMobile ? 'text-sm' : 'text-base'}`} style={{ textShadow: '0 2px 8px rgba(0,0,0,0.8)' }}>
                {isMobile ? blueTeam.name.split(' ')[0].toUpperCase() : blueTeam.name.toUpperCase()}
              </span>
            </div>

            <div className={`bg-white/30 ${isMobile ? 'w-px h-3' : 'w-px h-4'}`}></div>
            
            <span className={`font-mono text-white/90 font-medium ${isMobile ? 'text-sm' : 'text-base'}`} style={{ textShadow: '0 1px 4px rgba(0,0,0,0.8)' }}>
              {formatTime(currentTime)}
            </span>
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