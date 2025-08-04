'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import apiClient from '@/lib/api-client'


interface Game {
  id: string
  title: string
  status: string
  team_name: string
  created_at: string
}

interface Team {
  id: string
  name: string
  team_code: string
  color: string
}

export default function Dashboard() {
  const router = useRouter()
  const veoUrlInputRef = useRef<HTMLInputElement>(null)
  const [user, setUser] = useState<any>(null)
  const [games, setGames] = useState<Game[]>([])
  const [demoGames, setDemoGames] = useState<Game[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [activeTab, setActiveTab] = useState('games')
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [showJoinModal, setShowJoinModal] = useState(false)
  const [showCreateTeamModal, setShowCreateTeamModal] = useState(false)
  const [showSettingsModal, setShowSettingsModal] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [joinTeamCode, setJoinTeamCode] = useState('')
  const [joinTeamLoading, setJoinTeamLoading] = useState(false)
  const [createTeamName, setCreateTeamName] = useState('')
  const [createTeamDescription, setCreateTeamDescription] = useState('')
  const [createTeamLoading, setCreateTeamLoading] = useState(false)
  const [uploadGameTitle, setUploadGameTitle] = useState('')
  const [uploadGameDescription, setUploadGameDescription] = useState('')
  const [uploadGameUrl, setUploadGameUrl] = useState('')
  const [uploadTeamName, setUploadTeamName] = useState('')
  const [uploadGameLoading, setUploadGameLoading] = useState(false)

  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (!userData) {
      router.push('/')
      return
    }

    const parsedUser = JSON.parse(userData)
    
    // Company users can access both dashboards
    // if (parsedUser.role === 'company') {
    //   router.push('/company')
    //   return
    // }
    
    setUser(parsedUser)
    loadUserData()
  }, [router])

  const loadUserData = async () => {
    try {
      setLoading(true)
      setError('')
      
      // Load games, demo games, and teams in parallel
      const [gamesResponse, demoGamesResponse, teamsResponse] = await Promise.all([
        apiClient.getUserGames(),
        apiClient.getDemoGames(),
        apiClient.getUserTeams()
      ])
      
      setGames(gamesResponse.games || [])
      setDemoGames(demoGamesResponse.games || [])
      setTeams(teamsResponse.teams || [])
    } catch (err: any) {
      console.error('Failed to load user data:', err)
      setError(err.message || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/'
  }

  const handleUploadVideoClick = () => {
    // Switch to games tab first
    setActiveTab('games')
    
    // Use setTimeout to ensure the tab content is rendered before scrolling
    setTimeout(() => {
      if (veoUrlInputRef.current) {
        // Scroll to the input and focus it
        veoUrlInputRef.current.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        })
        veoUrlInputRef.current.focus()
      }
    }, 100)
  }

  const handleJoinTeam = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!joinTeamCode.trim()) return

    try {
      setJoinTeamLoading(true)
      setError('')
      
      await apiClient.joinTeamByCode(joinTeamCode.trim().toUpperCase())
      
      // Reload teams after joining
      const teamsResponse = await apiClient.getUserTeams()
      setTeams(teamsResponse.teams || [])
      
      // Close modal and reset form
      setShowJoinModal(false)
      setJoinTeamCode('')
      
      // Switch to teams tab to show the joined team
      setActiveTab('teams')
    } catch (err: any) {
      console.error('Failed to join team:', err)
      setError(err.message || 'Failed to join team')
    } finally {
      setJoinTeamLoading(false)
    }
  }

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!createTeamName.trim()) return

    try {
      setCreateTeamLoading(true)
      setError('')
      
      const response = await apiClient.createTeam({
        name: createTeamName.trim(),
        description: createTeamDescription.trim() || undefined,
        color: '#016F32'
      })
      
      // Reload teams after creating
      const teamsResponse = await apiClient.getUserTeams()
      setTeams(teamsResponse.teams || [])
      
      // Close modal and reset form
      setShowCreateTeamModal(false)
      setCreateTeamName('')
      setCreateTeamDescription('')
      
      // Switch to teams tab to show the new team
      setActiveTab('teams')
    } catch (err: any) {
      console.error('Failed to create team:', err)
      setError(err.message || 'Failed to create team')
    } finally {
      setCreateTeamLoading(false)
    }
  }

  const handleUploadGame = async (e: React.FormEvent) => {
    e.preventDefault()
    console.log('🎯 Form submitted!', { uploadGameUrl, uploadTeamName, uploadGameTitle })
    if (!uploadGameTitle.trim() || !uploadGameUrl.trim()) return

    let selectedTeam

    // If user has no teams, create one with provided name
    if (teams.length === 0) {
      if (!uploadTeamName.trim()) {
        setError('Please enter a team name')
        return
      }
      
      try {
        setUploadGameLoading(true)
        setError('')
        
        // Create team first
        const newTeam = await apiClient.createTeam({
          name: uploadTeamName.trim(),
          description: `Team for ${uploadTeamName.trim()}`
        })
        
        selectedTeam = newTeam
        
        // Reload teams
        const teamsResponse = await apiClient.getUserTeams()
        setTeams(teamsResponse.teams || [])
      } catch (err: any) {
        console.error('Failed to create team:', err)
        setError(err.message || 'Failed to create team')
        setUploadGameLoading(false)
        return
      }
    } else {
      // Use existing team or create new one if team name provided
      if (uploadTeamName.trim()) {
        // Check if team with this name already exists
        const existingTeam = teams.find(t => t.name.toLowerCase() === uploadTeamName.trim().toLowerCase())
        if (existingTeam) {
          selectedTeam = existingTeam
        } else {
          // Create new team
          try {
            const newTeam = await apiClient.createTeam({
              name: uploadTeamName.trim(),
              description: `Team for ${uploadTeamName.trim()}`
            })
            selectedTeam = newTeam
            
            // Reload teams
            const teamsResponse = await apiClient.getUserTeams()
            setTeams(teamsResponse.teams || [])
          } catch (err: any) {
            console.error('Failed to create team:', err)
            setError(err.message || 'Failed to create team')
            setUploadGameLoading(false)
            return
          }
        }
      } else {
        // Use first existing team if user didn't specify team name
        selectedTeam = teams[0]
      }
    }

    try {
      setUploadGameLoading(true)
      setError('')
      
      await apiClient.createGame({
        title: uploadGameTitle.trim(),
        description: uploadGameDescription.trim() || undefined,
        videoUrl: uploadGameUrl.trim(),
        teamId: (selectedTeam as any).team?.id || (selectedTeam as any).id
      })
      
      // Reload games after uploading
      const gamesResponse = await apiClient.getUserGames()
      setGames(gamesResponse.games || [])
      
      // Reset form
      setUploadGameTitle('')
      setUploadGameDescription('')
      setUploadGameUrl('')
      setUploadTeamName('')
    } catch (err: any) {
      console.error('Failed to upload game:', err)
      setError(err.message || 'Failed to upload game')
    } finally {
      setUploadGameLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white pb-20">
      {/* Top Navigation - Match UserDashboard.js exactly */}
      <nav className="border-b border-gray-200/10 bg-white">
        <div className="max-w-7xl mx-auto px-4 py-4">
          {/* Mobile layout - stacked vertically */}
          <div className="flex flex-col items-center md:flex-row md:justify-between md:items-center">
            {/* Logo - centered on mobile, left-aligned on desktop */}
            <div className="mb-4 md:mb-0">
              <Image 
                src="/clann-logo-green.png" 
                alt="ClannAI" 
                width={160} 
                height={42}
                className="h-10 w-auto"
                priority
              />
            </div>
            
            {/* Action buttons - stacked on mobile, horizontal on desktop */}
            <div className="flex flex-col w-full md:flex-row md:w-auto md:items-center gap-3 md:gap-4">
              <button 
                onClick={handleUploadVideoClick}
                className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium w-full md:w-auto"
              >
                📹 Upload Video
              </button>
              
              <button 
                onClick={() => setShowJoinModal(true)}
                className="border border-gray-300 text-gray-700 px-6 py-2.5 rounded-lg font-medium w-full md:w-auto"
              >
                {teams.length > 0 ? `Join: ${teams[0].team_code}` : 'Join Team'}
              </button>
              
              <button 
                onClick={() => setShowSettingsModal(true)}
                className="flex items-center justify-center gap-2 text-gray-700 px-6 py-2.5 rounded-lg font-medium border border-gray-300 w-full md:w-auto"
              >
                <span>Settings</span>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
                </svg>
              </button>

              {/* Company Tools - Only show for company users */}
              {user?.role === 'company' && (
                <button 
                  onClick={() => router.push('/company')}
                  className="flex items-center justify-center gap-2 bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium w-full md:w-auto hover:bg-blue-700 transition-colors"
                >
                  <span>Company Tools</span>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 6a2 2 0 104 0 2 2 0 00-4 0zm6 0a2 2 0 104 0 2 2 0 00-4 0z" clipRule="evenodd" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* User Profile Section - Match UserDashboard.js exactly */}
      <div className="bg-white">
        <div className="max-w-7xl mx-auto px-8 py-12">
        <div className="flex items-center gap-6 mb-12">
          <div className="flex items-center gap-8">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                {teams.length > 0 ? teams[0].name : 
                  <div className="flex items-center gap-2 text-gray-500">
                    Upload footage to create a team
                    <button 
                      onClick={() => setShowUploadModal(true)}
                      className="text-sm px-3 py-1 bg-[#016F32]/10 text-[#016F32] rounded-lg hover:bg-[#016F32]/20"
                    >
                      Upload Now →
                    </button>
                  </div>
                }
                <span className="ml-2 px-2 py-1 text-sm rounded-full bg-gray-400/10 text-gray-400 hover:bg-green-400/10 hover:text-green-400 cursor-pointer">
                  FREE TIER - Upgrade
                </span>
              </h1>
              <div className="flex items-center gap-2 text-gray-600">
                <span>⚽</span>
                <div>
                  <p className="text-lg text-gray-500">Team Member:</p>
                  <p className="text-lg">{user?.email || 'demo@clann.ai'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>

      {/* Bottom section with cream background */}
      <div className="bg-[#F7F6F1] min-h-screen">


      {/* Content */}
      <div className="max-w-4xl mx-auto px-8 py-8">

        {/* Content Area */}
        <div className="space-y-4">

        {/* Games Tab */}
        {activeTab === 'games' && (
          <div className="space-y-6">
            {/* Matches List - CONTENT FIRST */}
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-100">
                <h2 className="text-xl font-bold text-gray-900">Your Matches</h2>
              </div>
              <div className="p-6">
                {loading ? (
                  <div className="text-center py-12">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#016F32]"></div>
                    <p className="mt-2 text-gray-500">Loading your games...</p>
                  </div>
                ) : error ? (
                  <div className="bg-red-50 rounded-lg p-6 text-center">
                    <p className="text-red-600 mb-4">{error}</p>
                    <button
                      onClick={loadUserData}
                      className="bg-[#016F32] text-white px-4 py-2 rounded-lg hover:bg-[#016F32]/90 transition-colors"
                    >
                      Try Again
                    </button>
                  </div>
                ) : games.length === 0 ? (
                  <div className="space-y-6">
                    <div className="text-center py-6 border-b border-gray-100">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Here's a demo game to get you started</h3>
                      <p className="text-gray-500">See what ClannAI analysis looks like, then upload your first VEO match above</p>
                    </div>
                    
                    {demoGames.length === 0 ? (
                      <div className="text-center py-8">
                        <div className="text-gray-500">Loading demo content...</div>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {demoGames.slice(0, 1).map((game: Game) => (
                          <div key={game.id} className="bg-gray-50 rounded-lg p-4 transition-colors">
                            <div className="space-y-4">
                              <div className="flex justify-between items-start">
                                <div>
                                  <h3 className="font-medium text-gray-900">{game.title}</h3>
                                  <p className="text-sm text-gray-600 mt-1">Team: {game.team_name}</p>
                                  <p className="text-xs text-gray-500 mt-1">
                                    {new Date(game.created_at).toLocaleDateString('en-US', {
                                      year: 'numeric',
                                      month: 'short',
                                      day: 'numeric'
                                    })}
                                  </p>
                                </div>
                                <div className="flex flex-col items-end space-y-2">
                                  <div className="flex items-center space-x-2">
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                      ✨ Demo
                                    </span>
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                      Analyzed
                                    </span>
                                  </div>
                                  <p className="text-xs text-gray-400 text-right">44 events • AI insights available</p>
                                </div>
                              </div>
                              
                              <div className="grid grid-cols-2 gap-2">
                                <button 
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    router.push(`/games/${game.id}?autoChat=true&message=${encodeURIComponent("What specific training drills should we focus on to improve our defensive shape and pressing after this match?")}`)
                                  }}
                                  className="flex items-center space-x-2 bg-purple-50 hover:bg-purple-100 border border-purple-200 hover:border-purple-300 text-purple-700 hover:text-purple-800 px-3 py-2 rounded-lg text-sm transition-all font-medium"
                                >
                                  <span>🏃</span>
                                  <span>Training Drills</span>
                                </button>
                                
                                <button 
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    router.push(`/games/${game.id}?autoChat=true&message=${encodeURIComponent("What attacking patterns worked best and what tactical adjustments should we make for our next match?")}`)
                                  }}
                                  className="flex items-center space-x-2 bg-purple-50 hover:bg-purple-100 border border-purple-200 hover:border-purple-300 text-purple-700 hover:text-purple-800 px-3 py-2 rounded-lg text-sm transition-all font-medium"
                                >
                                  <span>⚽</span>
                                  <span>Tactics</span>
                                </button>
                                
                                <button 
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    router.push(`/games/${game.id}?autoChat=true&message=${encodeURIComponent("Who were our best and worst performers in this match and what should each player work on?")}`)
                                  }}
                                  className="flex items-center space-x-2 bg-purple-50 hover:bg-purple-100 border border-purple-200 hover:border-purple-300 text-purple-700 hover:text-purple-800 px-3 py-2 rounded-lg text-sm transition-all font-medium"
                                >
                                  <span>⭐</span>
                                  <span>Player Analysis</span>
                                </button>
                                
                                <button 
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    router.push(`/games/${game.id}?autoChat=true&message=${encodeURIComponent("How should we prepare for our next opponent based on this match analysis and what formation should we use?")}`)
                                  }}
                                  className="flex items-center space-x-2 bg-purple-50 hover:bg-purple-100 border border-purple-200 hover:border-purple-300 text-purple-700 hover:text-purple-800 px-3 py-2 rounded-lg text-sm transition-all font-medium"
                                >
                                  <span>📈</span>
                                  <span>Next Match Prep</span>
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
              <div className="space-y-4">
                {games.map((game: any) => (
                  <div
                    key={game.id}
                    className="bg-gray-50 rounded-xl p-6 border border-gray-200 hover:border-[#016F32]/30 transition-all"
                  >
                    <div className="space-y-4">
                      <div 
                    onClick={() => router.push(`/games/${game.id}`)}
                        className="flex justify-between items-start cursor-pointer"
                  >
                      <div className="space-y-3 min-w-0 flex-1 mr-4">
                        <h3 className="text-xl font-bold truncate">{game.title}</h3>
                        
                        <div className="space-y-2 text-sm text-gray-600">
                          <div className="flex items-center gap-2">
                            <span className="flex-shrink-0">⚽</span>
                            <span className="truncate">Team: {game.team_name}</span>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <span className="flex-shrink-0">📅</span>
                            <span className="truncate">{new Date(game.created_at).toLocaleDateString()}</span>
                          </div>
                          
                          {game.video_url && (
                            <div className="flex items-center gap-2">
                              <span className="flex-shrink-0">🎥</span>
                              <a
                                href={game.video_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-[#016F32] hover:underline truncate"
                                onClick={(e) => e.stopPropagation()}
                              >
                                VEO Footage
                              </a>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex-shrink-0 flex flex-col items-end gap-2">
                        <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap ${
                          game.status === 'analyzed'
                            ? 'bg-green-500/20 text-green-600 border border-green-500/30'
                            : 'bg-yellow-500/20 text-yellow-600 border border-yellow-500/30'
                        }`}>
                          {game.status.toUpperCase()}
                          {game.status === 'analyzed' && <span className="text-lg">→</span>}
                        </div>
                        
                        {game.status === 'analyzed' && (
                          <span className="text-sm text-gray-500 whitespace-nowrap">
                            Click to view analysis
                          </span>
                        )}
                      </div>
                      </div>

                      {/* AI Conversation Starters for Analyzed Games */}
                      {game.status === 'analyzed' && (
                        <div className="border-t border-gray-200 pt-4">
                          <p className="text-sm font-medium text-gray-700 mb-3">💬 Start AI coaching conversation:</p>
                          <div className="grid grid-cols-2 gap-2">
                            <button 
                              onClick={(e) => {
                                e.stopPropagation()
                                router.push(`/games/${game.id}?autoChat=true&message=${encodeURIComponent("What specific training drills should we focus on to improve our defensive shape and pressing after this match?")}`)
                              }}
                              className="flex items-center space-x-2 bg-purple-50 hover:bg-purple-100 border border-purple-200 hover:border-purple-300 text-purple-700 hover:text-purple-800 px-3 py-2 rounded-lg text-sm transition-all font-medium"
                            >
                              <span>🏃</span>
                              <span>Training Drills</span>
                            </button>
                            
                            <button 
                              onClick={(e) => {
                                e.stopPropagation()
                                router.push(`/games/${game.id}?autoChat=true&message=${encodeURIComponent("What attacking patterns worked best and what tactical adjustments should we make for our next match?")}`)
                              }}
                              className="flex items-center space-x-2 bg-purple-50 hover:bg-purple-100 border border-purple-200 hover:border-purple-300 text-purple-700 hover:text-purple-800 px-3 py-2 rounded-lg text-sm transition-all font-medium"
                            >
                              <span>⚽</span>
                              <span>Tactics</span>
                            </button>
                            
                            <button 
                              onClick={(e) => {
                                e.stopPropagation()
                                router.push(`/games/${game.id}?autoChat=true&message=${encodeURIComponent("Who were our best and worst performers in this match and what should each player work on?")}`)
                              }}
                              className="flex items-center space-x-2 bg-purple-50 hover:bg-purple-100 border border-purple-200 hover:border-purple-300 text-purple-700 hover:text-purple-800 px-3 py-2 rounded-lg text-sm transition-all font-medium"
                            >
                              <span>⭐</span>
                              <span>Player Analysis</span>
                            </button>
                            
                            <button 
                              onClick={(e) => {
                                e.stopPropagation()
                                router.push(`/games/${game.id}?autoChat=true&message=${encodeURIComponent("How should we prepare for our next opponent based on this match analysis and what formation should we use?")}`)
                              }}
                              className="flex items-center space-x-2 bg-purple-50 hover:bg-purple-100 border border-purple-200 hover:border-purple-300 text-purple-700 hover:text-purple-800 px-3 py-2 rounded-lg text-sm transition-all font-medium"
                            >
                              <span>📈</span>
                              <span>Next Match Prep</span>
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
            </div>

            {/* Upload New Match - Moved to Bottom */}
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-100">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Upload New Match</h2>
                <div className="bg-gray-50 rounded-lg p-6">
                  <form onSubmit={handleUploadGame} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">VEO URL</label>
                      <input
                        ref={veoUrlInputRef}
                        type="url"
                        value={uploadGameUrl}
                        onChange={(e) => setUploadGameUrl(e.target.value)}
                        placeholder="Paste your VEO URL here..."
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32] focus:border-[#016F32] text-gray-900 placeholder-gray-500"
                        required
                      />
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Team Name</label>
                        <input
                          type="text"
                          value={uploadTeamName}
                          onChange={(e) => setUploadTeamName(e.target.value)}
                          placeholder="Enter team name"
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32] focus:border-[#016F32] text-gray-900 placeholder-gray-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Match Title</label>
                        <input
                          type="text"
                          value={uploadGameTitle}
                          onChange={(e) => setUploadGameTitle(e.target.value)}
                          placeholder="Enter match title"
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32] focus:border-[#016F32] text-gray-900 placeholder-gray-500"
                          required
                        />
                      </div>
                    </div>
                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={uploadGameLoading || !uploadGameTitle.trim() || !uploadGameUrl.trim()}
                        className="bg-[#016F32] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {uploadGameLoading ? 'Adding...' : 'Upload Match'}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
          </div>
        )}



        {/* Teams Tab - Simplified for Sharing */}
        {activeTab === 'teams' && (
          <div className="bg-white rounded-xl shadow-sm">
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Team Sharing</h2>
              <p className="text-gray-600">Share your team codes to invite others</p>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Your Teams for Sharing */}
              {teams.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Teams</h3>
                  <div className="space-y-4">
                    {teams.map((team: any) => (
                      <div key={team.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="text-lg font-medium text-gray-900">{team.name}</h4>
                          <span className="px-3 py-1 bg-[#016F32] text-white text-sm font-mono rounded-lg">
                            {team.team_code}
                          </span>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="flex-1">
                            <input
                              type="text"
                              value={`${window.location.origin}/join/${team.team_code}`}
                              readOnly
                              className="w-full px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg text-gray-600 font-mono"
                            />
                          </div>
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(`${window.location.origin}/join/${team.team_code}`)
                              const button = document.activeElement as HTMLButtonElement
                              const originalText = button.textContent
                              button.textContent = 'Copied!'
                              button.classList.add('bg-green-600')
                              setTimeout(() => {
                                button.textContent = originalText
                                button.classList.remove('bg-green-600')
                              }, 2000)
                            }}
                            className="px-4 py-2 bg-[#016F32] text-white text-sm rounded-lg hover:bg-[#016F32]/90 transition-colors font-medium"
                          >
                            Copy Link
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Quick Actions */}
              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={() => setShowJoinModal(true)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50"
                  >
                    Join Team
                  </button>
                  <button
                    onClick={() => setShowCreateTeamModal(true)}
                    className="px-4 py-2 bg-[#016F32] text-white rounded-lg font-medium hover:bg-[#016F32]/90"
                  >
                    Create Team
                  </button>
                </div>
                
                {/* Demo codes for easy discovery */}
                <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-700 font-medium mb-1">Try these demo teams:</p>
                  <div className="flex flex-wrap gap-2">
                    {['ARS269', 'CHE277', 'LIV297', 'TQJ105'].map(code => (
                      <button
                        key={code}
                        onClick={() => {
                          setJoinTeamCode(code)
                          setShowJoinModal(true)
                        }}
                        className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded font-mono hover:bg-blue-200"
                      >
                        {code}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>



      {/* Join Team Modal */}
      {showJoinModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Join Team</h3>
              
              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-600 text-sm">{error}</p>
                </div>
              )}
              
              <form onSubmit={handleJoinTeam} className="space-y-4">
              <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Team Code</label>
                <input
                  type="text"
                    value={joinTeamCode}
                    onChange={(e) => setJoinTeamCode(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                  placeholder="e.g., ARS269"
                    required
                    disabled={joinTeamLoading}
                  />
                </div>
                <div className="text-xs text-gray-500">
                  <p className="mb-1">Try these demo codes:</p>
                  <p>ARS269, CHE277, LIV297, MCI298, MUN304</p>
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowJoinModal(false)
                      setJoinTeamCode('')
                      setError('')
                    }}
                    className="px-6 py-2.5 text-gray-600 hover:text-gray-800 transition-colors"
                    disabled={joinTeamLoading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={joinTeamLoading || !joinTeamCode.trim()}
                    className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {joinTeamLoading ? 'Joining...' : 'Join Team'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

              {/* Create Team Modal */}
        {showCreateTeamModal && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
                    <h3 className="text-2xl font-bold text-gray-900 mb-4">Create New Team</h3>
                    
                    {error && (
                      <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-red-600 text-sm">{error}</p>
                      </div>
                    )}
                    
                    <form onSubmit={handleCreateTeam} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-600 mb-1">Team Name</label>
                            <input
                                type="text"
                                value={createTeamName}
                                onChange={(e) => setCreateTeamName(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                                placeholder="e.g., My Football Club"
                                required
                                disabled={createTeamLoading}
                                maxLength={255}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-600 mb-1">Description (Optional)</label>
                            <textarea
                                value={createTeamDescription}
                                onChange={(e) => setCreateTeamDescription(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                                placeholder="Brief description of your team"
                                rows={3}
                                disabled={createTeamLoading}
                                maxLength={500}
                />
              </div>
                        <div className="text-xs text-gray-500">
                          <p>A unique team code will be automatically generated for others to join your team.</p>
                        </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                                onClick={() => {
                                  setShowCreateTeamModal(false)
                                  setCreateTeamName('')
                                  setCreateTeamDescription('')
                                  setError('')
                                }}
                                className="px-6 py-2.5 text-gray-600 hover:text-gray-800 transition-colors"
                                disabled={createTeamLoading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                                disabled={createTeamLoading || !createTeamName.trim()}
                                className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                                {createTeamLoading ? 'Creating...' : 'Create Team'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create Team Modal */}
      {showCreateTeamModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Create Team</h3>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}
            
            <form onSubmit={handleCreateTeam} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Team Name</label>
                <input
                  type="text"
                  value={createTeamName}
                  onChange={(e) => setCreateTeamName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                  placeholder="e.g., My Football Club"
                  required
                  disabled={createTeamLoading}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Description (Optional)</label>
                <textarea
                  value={createTeamDescription}
                  onChange={(e) => setCreateTeamDescription(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                  placeholder="Brief description of your team"
                  rows={3}
                  disabled={createTeamLoading}
                />
              </div>
              <div className="text-xs text-gray-500">
                <p>A unique team code will be automatically generated for others to join your team.</p>
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateTeamModal(false)
                    setCreateTeamName('')
                    setCreateTeamDescription('')
                    setError('')
                  }}
                  className="px-6 py-2.5 text-gray-600 hover:text-gray-800 transition-colors"
                  disabled={createTeamLoading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createTeamLoading || !createTeamName.trim()}
                  className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {createTeamLoading ? 'Creating...' : 'Create Team'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Settings Modal - Match UserDashboard.js exactly */}
      {showSettingsModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
              <button
                onClick={() => setShowSettingsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            {/* Add email display */}
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Account Email</p>
              <p className="text-gray-900 font-medium">{user?.email || 'demo@clann.ai'}</p>
            </div>

            <div className="space-y-4">
              <button
                onClick={() => {
                  localStorage.removeItem('auth_token')
                  localStorage.removeItem('user')
                  router.push('/')
                }}
                className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}

        {/* Clean Feedback Toast like old app */}
        {error && (
          <div className="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg bg-red-50 text-red-600 max-w-md">
            {error}
          </div>
        )}
        </div>
      </div>

      {/* Bottom Tab Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200/20">
        <div className="flex justify-center">
          <div className="flex">
            {(['games', 'teams'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-8 py-3 font-medium text-sm whitespace-nowrap ${
                  activeTab === tab
                    ? 'text-[#016F32] border-t-2 border-[#016F32]'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab === 'games' ? 'My Games' : 'Teams'}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
} 