'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { apiClient } from '../../lib/api-client'

interface Game {
  id: number
  title: string
  status: 'pending' | 'reviewed'
  created_at: string
  team_name?: string
}

interface Team {
  id: number
  name: string
  code: string
  member_count: number
}

export default function DashboardPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<'games' | 'teams'>('games')
  const [games, setGames] = useState<Game[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  // Form states
  const [veoUrl, setVeoUrl] = useState('')
  const [teamName, setTeamName] = useState('')
  const [gameTitle, setGameTitle] = useState('')
  const [joinTeamCode, setJoinTeamCode] = useState('')
  const [createTeamName, setCreateTeamName] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [gamesResponse, teamsResponse] = await Promise.all([
        apiClient.getUserGames(),
        apiClient.getUserTeams()
      ])
      setGames(gamesResponse.games || [])
      setTeams(teamsResponse.teams || [])
    } catch (err) {
      setError('Failed to load data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    router.push('/auth')
  }

  const handleCreateGame = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!veoUrl || !teamName || !gameTitle) return

    try {
      await apiClient.createGame({
        veo_url: veoUrl,
        team_name: teamName,
        title: gameTitle
      })
      setVeoUrl('')
      setTeamName('')
      setGameTitle('')
      loadData()
    } catch (err) {
      setError('Failed to create game')
    }
  }

  const handleJoinTeam = async () => {
    if (!joinTeamCode) return
    try {
      await apiClient.joinTeam(joinTeamCode)
      setJoinTeamCode('')
      loadData()
    } catch (err) {
      setError('Failed to join team')
    }
  }

  const handleCreateTeam = async () => {
    if (!createTeamName) return
    try {
      await apiClient.createTeam(createTeamName)
      setCreateTeamName('')
      loadData()
    } catch (err) {
      setError('Failed to create team')
    }
  }

  if (loading) {
    return <div className="min-h-screen bg-[#F7F6F1] flex items-center justify-center">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm px-6 py-4">
        <div className="flex items-center justify-between">
            {/* Logo */}
          <div className="flex items-center">
              <Image 
                src="/clann-logo-green.png" 
              alt="Clann AI"
              width={120}
              height={40}
              className="h-10 w-auto"
            />
            </div>
            
          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            <button className="bg-[#016F32] text-white px-4 py-2 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors">
              Upload Match
            </button>
            <button 
              onClick={() => setActiveTab('teams')}
              className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Join Team
            </button>
                <button
                  onClick={handleLogout}
              className="flex items-center gap-2 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Settings
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
                </button>
              </div>
            </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Account Information Section */}
        <div className="mb-8">
          <div className="flex items-baseline gap-4 mb-4">
            <h1 className="text-3xl font-bold text-gray-900">test</h1>
            <span className="text-sm text-gray-500 uppercase font-medium">FREE TIER - </span>
            <a href="#" className="text-sm text-[#016F32] hover:underline font-medium">Upgrade</a>
          </div>
          <div className="flex items-center gap-2 text-gray-600">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>Team Member:</span>
            <span className="font-medium">thomas@clannai.com</span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('games')}
              className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                activeTab === 'games'
                  ? 'border-[#016F32] text-[#016F32]'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Matches
            </button>
            <button
              onClick={() => setActiveTab('teams')}
              className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                activeTab === 'teams'
                  ? 'border-[#016F32] text-[#016F32]'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Team
            </button>
          </div>
        </div>

        {/* Games Tab */}
        {activeTab === 'games' && (
          <div>
            {/* Section Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Your Matches</h2>
              <div className="flex items-center gap-2">
                <button className="bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium">
                  All
                </button>
                <button className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-300">
                  Reviewed
                </button>
                <button className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-300">
                  Pending
                </button>
              </div>
            </div>

            {/* Match Cards */}
            <div className="space-y-4">
              {/* Sample Match Card - Pending */}
              <div className="bg-gray-700 rounded-lg p-6 text-white">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                    <span className="text-sm font-medium uppercase tracking-wide">PENDING</span>
                  </div>
                  <span className="text-gray-300 text-sm">15/05/2025, 18:09:42</span>
                </div>
                
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-4">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="font-medium">test</span>
                  </div>
                  <div className="text-gray-300">-</div>
                  <div className="text-center">
                    <span className="font-medium">VS</span>
                  </div>
                  <div className="text-gray-300">-</div>
                  <div className="font-medium">Opponent</div>
                </div>

                {/* Stats Row */}
                <div className="grid grid-cols-5 gap-4 mb-4">
                  <div className="bg-gray-600 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-300 mb-1">Distance</div>
                    <div className="flex items-center justify-center gap-1">
                      <span className="text-lg font-bold">0.0</span>
                      <span className="text-gray-300">|</span>
                      <span className="text-lg font-bold">0.0</span>
                      <span className="text-xs text-gray-300 ml-1">km</span>
                    </div>
                  </div>
                  
                  <div className="bg-gray-600 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-300 mb-1">Energy</div>
                    <div className="flex items-center justify-center gap-1">
                      <span className="text-lg font-bold">0</span>
                      <span className="text-gray-300">|</span>
                      <span className="text-lg font-bold">0</span>
                      <span className="text-xs text-gray-300 ml-1">kJ</span>
                    </div>
                  </div>
                  
                  <div className="bg-gray-600 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-300 mb-1">Sprints</div>
                    <div className="flex items-center justify-center gap-1">
                      <span className="text-lg font-bold">-</span>
                      <span className="text-gray-300">|</span>
                      <span className="text-lg font-bold">-</span>
                    </div>
                  </div>
                  
                  <div className="bg-gray-600 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-300 mb-1">Sprint Dist</div>
                    <div className="flex items-center justify-center gap-1">
                      <span className="text-lg font-bold">0</span>
                      <span className="text-gray-300">|</span>
                      <span className="text-lg font-bold">0</span>
                      <span className="text-xs text-gray-300 ml-1">m</span>
                    </div>
                  </div>

                  <div className="bg-gray-600 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-300 mb-1">Sprint Speed</div>
                    <div className="flex items-center justify-center gap-1">
                      <span className="text-lg font-bold">0.0</span>
                      <span className="text-gray-300">|</span>
                      <span className="text-lg font-bold">0.0</span>
                      <span className="text-xs text-gray-300 ml-1">m/s</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-yellow-400 text-sm">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                    </svg>
                    <span>Analysis in progress - check back soon</span>
                  </div>
                  <button className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                    View Uploaded Footage
                  </button>
                </div>
              </div>

              {/* Sample Match Card 2 - Also Pending */}
              <div className="bg-gray-700 rounded-lg p-6 text-white">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                    <span className="text-sm font-medium uppercase tracking-wide">PENDING</span>
                  </div>
                  <span className="text-gray-300 text-sm">15/05/2025, 18:09:15</span>
                          </div>
                          
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-4">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="font-medium">test</span>
                  </div>
                  <div className="text-gray-300">-</div>
                  <div className="text-center">
                    <span className="font-medium">VS</span>
                  </div>
                  <div className="text-gray-300">-</div>
                  <div className="font-medium">Opponent</div>
                          </div>
                          
                {/* Stats Row - All zeros */}
                <div className="grid grid-cols-5 gap-4 mb-4">
                  <div className="bg-gray-600 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-300 mb-1">Distance</div>
                    <div className="flex items-center justify-center gap-1">
                      <span className="text-lg font-bold">0.0</span>
                      <span className="text-gray-300">|</span>
                      <span className="text-lg font-bold">0.0</span>
                      <span className="text-xs text-gray-300 ml-1">km</span>
                        </div>
                      </div>
                      
                  <div className="bg-gray-600 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-300 mb-1">Energy</div>
                    <div className="flex items-center justify-center gap-1">
                      <span className="text-lg font-bold">0</span>
                      <span className="text-gray-300">|</span>
                      <span className="text-lg font-bold">0</span>
                      <span className="text-xs text-gray-300 ml-1">kJ</span>
                    </div>
                  </div>
                  
                  <div className="bg-gray-600 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-300 mb-1">Sprints</div>
                    <div className="flex items-center justify-center gap-1">
                      <span className="text-lg font-bold">-</span>
                      <span className="text-gray-300">|</span>
                      <span className="text-lg font-bold">-</span>
            </div>
                  </div>
                  
                  <div className="bg-gray-600 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-300 mb-1">Sprint Dist</div>
                    <div className="flex items-center justify-center gap-1">
                      <span className="text-lg font-bold">0</span>
                      <span className="text-gray-300">|</span>
                      <span className="text-lg font-bold">0</span>
                      <span className="text-xs text-gray-300 ml-1">m</span>
                    </div>
                  </div>
                  
                  <div className="bg-gray-600 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-300 mb-1">Sprint Speed</div>
                    <div className="flex items-center justify-center gap-1">
                      <span className="text-lg font-bold">0.0</span>
                      <span className="text-gray-300">|</span>
                      <span className="text-lg font-bold">0.0</span>
                      <span className="text-xs text-gray-300 ml-1">m/s</span>
                            </div>
                          </div>
                        </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-yellow-400 text-sm">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                    </svg>
                    <span>Analysis in progress - check back soon</span>
                  </div>
                  <button className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                    View Uploaded Footage
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Teams Tab */}
        {activeTab === 'teams' && (
          <div>
            {teams.length === 0 ? (
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
                        onClick={handleJoinTeam}
                        className="bg-[#016F32] text-white px-6 py-2 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={!joinTeamCode}
                      >
                        Join
                  </button>
            </div>
          </div>

                  <div className="bg-gray-50 rounded-lg p-6 border">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Create Team</h3>
                    <p className="text-gray-600 mb-4">Start a new team and invite others</p>
                    <div className="flex gap-2">
                            <input
                                type="text"
                        placeholder="Enter team name"
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32] text-gray-900 placeholder-gray-500"
                                value={createTeamName}
                                onChange={(e) => setCreateTeamName(e.target.value)}
                      />
                <button
                        onClick={handleCreateTeam}
                        className="bg-[#016F32] text-white px-6 py-2 rounded-lg font-medium hover:bg-[#016F32]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={!createTeamName}
                      >
                        Create
                </button>
              </div>
          </div>
        </div>
              </div>
            ) : (
              <div className="space-y-4">
                {teams.map((team) => (
                  <div key={team.id} className="bg-white rounded-lg border p-6">
                    <div className="flex items-center justify-between">
              <div>
                        <h3 className="font-semibold text-gray-900">{team.name}</h3>
                        <p className="text-gray-600 text-sm">Code: {team.code}</p>
                      </div>
                      <div className="text-gray-600 text-sm">
                        {team.member_count} members
              </div>
              </div>
              </div>
                ))}
              </div>
            )}
        </div>
      )}

        {/* Error Toast */}
      {error && (
        <div className="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg bg-red-50 text-red-600 max-w-md">
          {error}
            <button 
              onClick={() => setError('')}
              className="ml-4 text-red-500 hover:text-red-700"
            >
              ×
            </button>
        </div>
      )}
      </div>
    </div>
  )
} 