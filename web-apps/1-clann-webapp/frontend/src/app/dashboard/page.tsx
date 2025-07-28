'use client'

import { useState, useEffect } from 'react'
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
                          <button className="px-3 py-1 bg-[#016F32] hover:bg-[#016F32]/90 text-white text-xs rounded transition-colors">
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
                      <div>
                        <h3 className="text-lg font-medium text-gray-900 mb-2">{team.name}</h3>
                        <p className="text-gray-600 text-sm">Join Code: {team.team_code}</p>
                      </div>
                      <div
                        className="w-12 h-12 rounded-full"
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
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Game Title</label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                  placeholder="e.g., Arsenal vs Brighton - July 28th"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">VEO URL</label>
                <input
                  type="url"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                  placeholder="https://veo.co/watch/..."
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-6 py-2.5 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors"
                >
                  Upload
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
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Team Name</label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                  placeholder="e.g., My Football Club"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Description (Optional)</label>
                <textarea
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                  placeholder="Brief description of your team"
                  rows={3}
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateTeamModal(false)}
                  className="px-6 py-2.5 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors"
                >
                  Create Team
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
} 