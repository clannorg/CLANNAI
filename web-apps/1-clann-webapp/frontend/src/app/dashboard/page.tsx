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

    // Check if user has teams
    if (teams.length === 0) {
      setError('Please join or create a team first before uploading games')
      return
    }

    // Use the first team by default (could be enhanced with team selection)
    const selectedTeam = teams[0]

    try {
      setUploadGameLoading(true)
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
    <div className="min-h-screen bg-[#F7F6F1]">
      {/* Header */}
      <nav className="border-b border-gray-200/10 bg-white">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex flex-col items-center md:flex-row md:justify-between md:items-center">
            {/* Logo */}
            <div className="mb-4 md:mb-0">
          <div className="flex items-center space-x-4">
                <Image 
                  src="/clann-logo-green.png" 
                  alt="ClannAI" 
                  width={64} 
                  height={64}
                />
            {user && (
                  <div className="text-gray-600">
                    {user.name || user.email}
                {user.role === 'company' && (
                      <span className="ml-2 px-2 py-1 text-sm rounded bg-[#016F32] text-white">Company</span>
                    )}
                  </div>
                )}
              </div>
          </div>
            {/* Action buttons */}
            <div className="flex flex-col w-full md:flex-row md:w-auto md:items-center gap-3 md:gap-4">
            {user?.role === 'company' && (
              <a
                href="/company"
                  className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium w-full md:w-auto text-center hover:bg-[#016F32]/90 transition-colors"
              >
                Company Dashboard
              </a>
            )}
            <button
              onClick={handleLogout}
                className="border border-gray-300 text-gray-700 px-6 py-2.5 rounded-lg font-medium w-full md:w-auto hover:bg-gray-50 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
      </nav>

            {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200/10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-center overflow-x-auto scrollbar-hide">
            <button
              onClick={() => setActiveTab('games')}
                                className={`px-8 py-3 font-medium text-base whitespace-nowrap ${
                activeTab === 'games'
                      ? 'text-[#016F32] border-b-2 border-[#016F32]'
                      : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Games
            </button>
            <button
              onClick={() => setActiveTab('teams')}
                                className={`px-8 py-3 font-medium text-base whitespace-nowrap ${
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

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-8 py-12">

        {/* Games Tab */}
        {activeTab === 'games' && (
          <div className="bg-white rounded-xl shadow-sm">
            <div className="flex justify-between items-center p-6 border-b border-gray-100">
              <h2 className="text-2xl font-bold text-gray-900">Your Games</h2>
              <button
                onClick={() => {
                  if (teams.length === 0) {
                    alert('Please join or create a team first before uploading games')
                    setActiveTab('teams')
                  } else {
                    setShowUploadModal(true)
                  }
                }}
                className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors"
              >
                Upload VEO URL
              </button>
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
              <div className="bg-gray-50 rounded-lg p-12 text-center">
                <div className="text-gray-400 mb-4">
                  <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <h3 className="text-xl font-medium text-gray-900 mb-2">No games yet</h3>
                  <p className="text-gray-500">Upload your first VEO URL to get started with AI analysis</p>
                </div>
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="bg-[#016F32] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors"
                >
                  Upload Your First Game
                </button>
              </div>
            ) : (
              <div className="space-y-4">
              {games.map((game: any) => (
                  <div key={game.id} className="bg-gray-50 rounded-lg p-6">
                  <div className="flex justify-between items-start">
                    <div>
                        <h3 className="text-lg font-medium text-gray-900 mb-2">{game.title}</h3>
                        <p className="text-gray-600 text-sm mb-2">Team: {game.team_name}</p>
                      <p className="text-gray-500 text-xs">
                        Uploaded: {new Date(game.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        game.status === 'analyzed'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {game.status.toUpperCase()}
                      </span>
                      {game.status === 'analyzed' && (
                          <button 
                            onClick={() => router.push(`/games/${game.id}`)}
                            className="px-3 py-1 bg-[#016F32] hover:bg-[#016F32]/90 text-white text-xs rounded transition-colors"
                          >
                          View Analysis
                        </button>
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
          <div className="bg-white rounded-xl shadow-sm">
            <div className="flex justify-between items-center p-6 border-b border-gray-100">
              <h2 className="text-2xl font-bold text-gray-900">Your Teams</h2>
              <button
                onClick={() => setShowJoinModal(true)}
                className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors"
              >
                Join Team
              </button>
            </div>
                          <div className="p-6">

                {loading ? (
                  <div className="text-center py-12">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#016F32]"></div>
                    <p className="mt-2 text-gray-500">Loading your teams...</p>
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
                ) : teams.length === 0 ? (
              <div className="bg-gray-50 rounded-lg p-12 text-center">
                <div className="text-gray-400 mb-4">
                  <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  <h3 className="text-xl font-medium text-gray-900 mb-2">No teams joined yet</h3>
                  <p className="text-gray-500 mb-6">Join a team or create your own to start uploading games</p>
                  <div className="text-sm text-gray-500 mb-6">
                    <p className="mb-2">Demo team codes to try:</p>
                    <div className="space-y-1">
                      <p>• Arsenal FC Academy (ARS269)</p>
                      <p>• Chelsea Youth (CHE277)</p>
                      <p>• Liverpool Reserves (LIV297)</p>
                    </div>
                  </div>
                </div>
                <div className="space-x-4">
                  <button
                    onClick={() => setShowJoinModal(true)}
                    className="bg-[#016F32] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors"
                  >
                    Join Team
                  </button>
                  <button
                    onClick={() => setShowCreateTeamModal(true)}
                    className="border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                  >
                    Create Team
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
              {teams.map((team: any) => (
                  <div key={team.id} className="bg-gray-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                        <h3 className="text-lg font-medium text-gray-900 mb-2">{team.name}</h3>
                        <p className="text-gray-600 text-sm mb-3">Join Code: {team.team_code}</p>
                        
                        {/* Team Invite URL Section */}
                        <div className="bg-gradient-to-r from-[#016F32]/5 to-[#016F32]/10 rounded-lg p-4 border border-[#016F32]/20">
                          <div className="flex items-center space-x-2 mb-3">
                            <svg className="w-4 h-4 text-[#016F32]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                            </svg>
                            <p className="text-sm font-semibold text-[#016F32]">Share Team Invite</p>
                          </div>
                          <div className="space-y-3">
                            <div className="bg-white rounded-lg border border-gray-200 p-3">
                              <p className="text-xs text-gray-600 mb-2">Shareable URL:</p>
                              <div className="flex items-center space-x-2">
                                <input
                                  type="text"
                                  value={`${typeof window !== 'undefined' ? window.location.origin : 'localhost:3000'}/join/${team.team_code}`}
                                  readOnly
                                  className="text-xs bg-gray-50 border border-gray-100 rounded-md px-3 py-2 flex-1 font-mono text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#016F32]/20"
                                />
                                <button
                                  onClick={(e) => {
                                    const inviteUrl = `${typeof window !== 'undefined' ? window.location.origin : 'localhost:3000'}/join/${team.team_code}`;
                                    navigator.clipboard.writeText(inviteUrl);
                                    // Enhanced feedback
                                    const button = e.target as HTMLButtonElement;
                                    const originalText = button.textContent;
                                    button.textContent = '✓ Copied!';
                                    button.className = button.className.replace('bg-[#016F32]', 'bg-green-600');
                                    setTimeout(() => {
                                      button.textContent = originalText || 'Copy';
                                      button.className = button.className.replace('bg-green-600', 'bg-[#016F32]');
                                    }, 2000);
                                  }}
                                  className="text-xs bg-[#016F32] text-white px-4 py-2 rounded-md hover:bg-[#014d24] transition-all duration-200 transform hover:scale-105 font-medium shadow-sm"
                                >
                                  Copy
                                </button>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2 text-xs text-gray-600">
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <span>Share this link with players to join instantly</span>
                            </div>
                          </div>
                        </div>
                    </div>
                    <div
                      className="w-12 h-12 rounded-full ml-4"
                      style={{ backgroundColor: team.color }}
                    ></div>
                  </div>
                </div>
              ))}
              </div>
            )}
            </div>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Upload VEO URL</h3>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}
            
            <form onSubmit={handleUploadGame} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Game Title</label>
                <input
                  type="text"
                  value={uploadGameTitle}
                  onChange={(e) => setUploadGameTitle(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                  placeholder="e.g., Arsenal vs Brighton - July 28th"
                  required
                  disabled={uploadGameLoading}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">VEO URL</label>
                <input
                  type="url"
                  value={uploadGameUrl}
                  onChange={(e) => setUploadGameUrl(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                  placeholder="https://veo.co/watch/..."
                  required
                  disabled={uploadGameLoading}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Description (Optional)</label>
                <textarea
                  value={uploadGameDescription}
                  onChange={(e) => setUploadGameDescription(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                  placeholder="Brief description of the game"
                  rows={3}
                  disabled={uploadGameLoading}
                />
              </div>
              {teams.length > 0 && (
                <div className="text-xs text-gray-500">
                  <p>Will be uploaded to team: <strong>{teams[0].name}</strong></p>
                </div>
              )}
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowUploadModal(false)
                    setUploadGameTitle('')
                    setUploadGameDescription('')
                    setUploadGameUrl('')
                    setError('')
                  }}
                  className="px-6 py-2.5 text-gray-600 hover:text-gray-800 transition-colors"
                  disabled={uploadGameLoading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploadGameLoading || !uploadGameTitle.trim() || !uploadGameUrl.trim()}
                  className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploadGameLoading ? 'Uploading...' : 'Upload Game'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

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
    </div>
  )
} 