'use client'

import { useState, useEffect } from 'react'
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
  const [user, setUser] = useState<any>(null)
  const [games, setGames] = useState<Game[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [activeTab, setActiveTab] = useState('games')
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [showJoinModal, setShowJoinModal] = useState(false)
  const [showCreateTeamModal, setShowCreateTeamModal] = useState(false)
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
    if (userData) {
      setUser(JSON.parse(userData))
    }
    
    loadUserData()
  }, [])

  const loadUserData = async () => {
    try {
      setLoading(true)
      setError('')
      
      // Load games and teams in parallel
      const [gamesResponse, teamsResponse] = await Promise.all([
        apiClient.getUserGames(),
        apiClient.getUserTeams()
      ])
      
      setGames(gamesResponse.games || [])
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

  const handleJoinTeam = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!joinTeamCode.trim()) return

    try {
      setJoinTeamLoading(true)
      setError('')
      
      await apiClient.joinTeam(joinTeamCode.trim().toUpperCase())
      
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
        // Use first existing team
        selectedTeam = teams[0]
      }
    }

    try {
      if (!setUploadGameLoading) setUploadGameLoading(true)
      setError('')
      
      await apiClient.createGame({
        title: uploadGameTitle.trim(),
        description: uploadGameDescription.trim() || undefined,
        videoUrl: uploadGameUrl.trim(),
        teamId: selectedTeam.id
      })
      
      // Reload games after uploading
      const gamesResponse = await apiClient.getUserGames()
      setGames(gamesResponse.games || [])
      
      // Close modal and reset form
      setShowUploadModal(false)
      setUploadGameTitle('')
      setUploadGameDescription('')
      setUploadGameUrl('')
      setUploadTeamName('')
      
      // Switch to games tab to show the new game
      setActiveTab('games')
    } catch (err: any) {
      console.error('Failed to upload game:', err)
      setError(err.message || 'Failed to upload game')
    } finally {
      setUploadGameLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Professional Header */}
      <nav className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center py-4">
            {/* Logo */}
            <div className="flex items-center">
              <Image 
                src="/clann-logo-green.png" 
                alt="ClannAI" 
                width={120} 
                height={40}
                className="h-10 w-auto"
              />
            </div>
            
            {/* Right side - Auth like landing page */}
            <div className="flex items-center gap-4">
              {user?.role === 'company' && (
                <a
                  href="/company"
                  className="bg-[#016F32] text-white px-4 py-2 rounded-lg font-medium text-sm hover:bg-[#016F32]/90 transition-colors"
                >
                  Company Dashboard
                </a>
              )}
              
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-[#016F32] rounded-full flex items-center justify-center">
                    <span className="text-white font-medium text-sm">
                      {user?.email?.[0]?.toUpperCase() || 'U'}
                    </span>
                  </div>
                  <span className="text-sm text-gray-700 font-medium">{user?.email || 'Demo User'}</span>
                  {user?.role === 'company' && (
                    <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-700 font-medium">Company</span>
                  )}
                </div>
                
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-600 hover:text-gray-900 px-4 py-2 rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all font-medium"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Tab Navigation - centered like old app */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-center">
            <button
              onClick={() => setActiveTab('games')}
              className={`px-8 py-3 font-medium text-sm ${
                activeTab === 'games'
                  ? 'text-[#016F32] border-b-2 border-[#016F32]'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Games
            </button>
            <button
              onClick={() => setActiveTab('teams')}
              className={`px-8 py-3 font-medium text-sm ${
                activeTab === 'teams'
                  ? 'text-[#016F32] border-b-2 border-[#016F32]'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Teams
            </button>
          </div>
        </div>
      </div>

      {/* Simple Content */}
      <div className="max-w-4xl mx-auto px-8 py-8">

        {/* Content Area */}
        <div className="space-y-4">

        {/* Games Tab */}
        {activeTab === 'games' && (
          <div className="bg-white rounded-xl shadow-sm">
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
              <div className="bg-white rounded-lg border p-6 max-w-lg mx-auto">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Add VEO URL</h2>
                
                <form onSubmit={handleUploadGame} className="space-y-4">
                  <div>
                    <input
                      type="url"
                      value={uploadGameUrl}
                      onChange={(e) => setUploadGameUrl(e.target.value)}
                      placeholder="Paste your VEO URL here..."
                      className="w-full px-4 py-3 text-lg border-2 rounded-lg text-gray-900 placeholder-gray-500 bg-white focus:border-[#016F32]"
                      required
                    />
                  </div>
                  
                  <div className="flex gap-3">
                    <input
                      type="text"
                      value={uploadTeamName}
                      onChange={(e) => setUploadTeamName(e.target.value)}
                      placeholder="Team"
                      className="flex-1 px-3 py-2 border rounded-lg text-gray-900 placeholder-gray-500 bg-white"
                      required
                    />
                    
                    <input
                      type="text"
                      value={uploadGameTitle}
                      onChange={(e) => setUploadGameTitle(e.target.value)}
                      placeholder="Game title"
                      className="flex-1 px-3 py-2 border rounded-lg text-gray-900 placeholder-gray-500 bg-white"
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={uploadGameLoading || !uploadGameTitle.trim() || !uploadGameUrl.trim() || !uploadTeamName.trim()}
                    className="w-full bg-[#016F32] text-white py-3 rounded-lg font-medium text-lg hover:bg-[#016F32]/90 disabled:opacity-50"
                  >
                    {uploadGameLoading ? 'Adding...' : 'Add Team'}
                  </button>
                </form>
              </div>
            ) : (
              <div className="space-y-4">
                {games.map((game: any) => (
                  <div
                    key={game.id}
                    onClick={() => router.push(`/games/${game.id}`)}
                    className="bg-gray-50 rounded-xl p-6 border border-gray-200 hover:border-[#016F32]/30 transition-all cursor-pointer"
                  >
                    <div className="flex justify-between items-start">
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
                  </div>
                ))}
              </div>
            )}
            </div>
          </div>
        )}

        {/* Teams Tab */}
        {activeTab === 'teams' && (
          teams.length === 0 ? (
            <div className="bg-white rounded-lg border p-8 max-w-lg mx-auto text-center">
              <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">No teams yet</h2>
              <p className="text-gray-500 mb-8">Get started by joining or creating a team.</p>
              
              <div className="space-y-4">
                <div className="bg-gray-50 rounded-lg p-6 border">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Join Team</h3>
                  <p className="text-gray-600 mb-4">Enter a team code to join an existing team</p>
                  <div className="flex gap-2">
                                         <input
                       type="text"
                       placeholder="Enter team code (e.g., ARS269)"
                       className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32] text-gray-900 placeholder-gray-500"
                       value={joinTeamCode}
                       onChange={(e) => setJoinTeamCode(e.target.value)}
                     />
                    <button
                      onClick={() => setShowJoinModal(true)}
                      className="bg-[#016F32] text-white px-6 py-2 rounded-lg font-medium hover:bg-[#016F32]/90"
                    >
                      Join
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">Demo codes: ARS269 • CHE277 • LIV297</p>
                </div>

                <div className="bg-gray-50 rounded-lg p-6 border">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Create Team</h3>
                  <p className="text-gray-600 mb-4">Enter a team name to create a new team</p>
                  <div className="flex gap-2">
                                         <input
                       type="text"
                       placeholder="Enter team name"
                       className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32] text-gray-900 placeholder-gray-500"
                       value={createTeamName}
                       onChange={(e) => setCreateTeamName(e.target.value)}
                     />
                    <button
                      onClick={() => setShowCreateTeamModal(true)}
                      className="bg-[#016F32] text-white px-6 py-2 rounded-lg font-medium hover:bg-[#016F32]/90"
                    >
                      Create
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm">
              <div className="flex justify-between items-center p-6 border-b border-gray-100">
                <h2 className="text-2xl font-bold text-gray-900">Your Teams</h2>
                <div className="flex gap-2">
                  <button
                    onClick={() => setShowJoinModal(true)}
                    className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-50 text-sm"
                  >
                    Join Team
                  </button>
                  <button
                    onClick={() => setShowCreateTeamModal(true)}
                    className="bg-[#016F32] text-white px-4 py-2 rounded-lg font-medium hover:bg-[#016F32]/90 text-sm"
                  >
                    Create Team
                  </button>
                </div>
              </div>
              <div className="p-6 space-y-4">
                {teams.map((team: any) => (
                  <div key={team.id} className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">{team.name}</h3>
                    <p className="text-gray-600 text-sm">Join Code: <code className="bg-gray-200 px-2 py-1 rounded">{team.team_code}</code></p>
                  </div>
                ))}
              </div>
            </div>
          )
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

      {/* Clean Feedback Toast like old app */}
      {error && (
        <div className="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg bg-red-50 text-red-600 max-w-md">
          {error}
        </div>
      )}
      </div>
    </div>
  )
} 