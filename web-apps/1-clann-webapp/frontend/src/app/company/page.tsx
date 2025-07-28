'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import apiClient from '@/lib/api-client'

interface Game {
  id: string
  title: string
  description: string
  video_url: string
  status: string
  team_name: string
  uploaded_by_name: string
  uploaded_by_email: string
  created_at: string
  has_analysis: boolean
}

interface Stats {
  total_games: number
  pending_games: number
  analyzed_games: number
  veo_uploads: number
  teams_count: number
  users_count: number
}

export default function CompanyDashboard() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [games, setGames] = useState<Game[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  
  // Modal states
  const [showVideoModal, setShowVideoModal] = useState(false)
  const [showJsonModal, setShowJsonModal] = useState(false)
  const [selectedGame, setSelectedGame] = useState<Game | null>(null)
  const [videoUrl, setVideoUrl] = useState('')
  const [jsonData, setJsonData] = useState('')
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (!userData) {
      router.push('/')
      return
    }

    const parsedUser = JSON.parse(userData)
    if (parsedUser.role !== 'company') {
      router.push('/dashboard')
      return
    }

    setUser(parsedUser)
    loadDashboardData()
  }, [router])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError('')
      
      const [gamesResponse, statsResponse] = await Promise.all([
        apiClient.getCompanyGames(statusFilter === 'all' ? undefined : statusFilter),
        apiClient.getCompanyStats()
      ])
      
      setGames(gamesResponse.games || [])
      setStats(statsResponse.stats || null)
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err)
      setError(err.message || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      loadDashboardData()
    }
  }, [statusFilter, user])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/')
  }

  const handleAddVideo = (game: Game) => {
    setSelectedGame(game)
    setVideoUrl('')
    setShowVideoModal(true)
  }

  const handleAddJson = (game: Game) => {
    setSelectedGame(game)
    setJsonData('')
    setShowJsonModal(true)
  }

  const handleSubmitVideo = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedGame || !videoUrl.trim()) return

    try {
      setUpdating(true)
      setError('')
      
      await apiClient.updateGameAnalysis(selectedGame.id, {
        videoUrl: videoUrl.trim()
      })
      
      setShowVideoModal(false)
      setVideoUrl('')
      setSelectedGame(null)
      await loadDashboardData()
    } catch (err: any) {
      console.error('Failed to update video:', err)
      setError(err.message || 'Failed to update video')
    } finally {
      setUpdating(false)
    }
  }

  const handleSubmitJson = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedGame || !jsonData.trim()) return

    try {
      setUpdating(true)
      setError('')
      
      const events = JSON.parse(jsonData.trim())
      
      await apiClient.updateGameAnalysis(selectedGame.id, {
        events,
        status: 'analyzed'
      })
      
      setShowJsonModal(false)
      setJsonData('')
      setSelectedGame(null)
      await loadDashboardData()
    } catch (err: any) {
      console.error('Failed to update analysis:', err)
      setError(err.message || 'Failed to update analysis')
    } finally {
      setUpdating(false)
    }
  }

  const handleMarkAnalyzed = async (game: Game) => {
    try {
      setError('')
      
      await apiClient.updateGameAnalysis(game.id, {
        status: 'analyzed'
      })
      
      await loadDashboardData()
    } catch (err: any) {
      console.error('Failed to mark as analyzed:', err)
      setError(err.message || 'Failed to mark as analyzed')
    }
  }

  if (!user) {
    return <div className="min-h-screen bg-[#F7F6F1] flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#016F32]"></div>
        <p className="mt-2 text-gray-500">Loading...</p>
      </div>
    </div>
  }

  return (
    <div className="min-h-screen bg-[#F7F6F1]">
      {/* Header */}
      <nav className="border-b border-gray-200/10 bg-white">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Image 
                src="/clann-logo-green.png" 
                alt="ClannAI" 
                width={48} 
                height={48}
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Company Dashboard</h1>
                <p className="text-sm text-gray-600">Welcome, {user.email}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <a
                href="/dashboard"
                className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
              >
                User Dashboard
              </a>
              <button
                onClick={handleLogout}
                className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-8 py-12">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-sm font-medium text-gray-500">Total Games</h3>
              <p className="text-3xl font-bold text-gray-900">{stats.total_games}</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-sm font-medium text-gray-500">Pending</h3>
              <p className="text-3xl font-bold text-orange-600">{stats.pending_games}</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-sm font-medium text-gray-500">Analyzed</h3>
              <p className="text-3xl font-bold text-green-600">{stats.analyzed_games}</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-sm font-medium text-gray-500">Teams</h3>
              <p className="text-3xl font-bold text-blue-600">{stats.teams_count}</p>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm mb-6">
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">All Games</h2>
              <div className="flex space-x-2">
                {['all', 'pending', 'analyzed'].map((filter) => (
                  <button
                    key={filter}
                    onClick={() => setStatusFilter(filter)}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      statusFilter === filter
                        ? 'bg-[#016F32] text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {filter.charAt(0).toUpperCase() + filter.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="p-6">
            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#016F32]"></div>
                <p className="mt-2 text-gray-500">Loading games...</p>
              </div>
            ) : games.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">No games found</p>
              </div>
            ) : (
              <div className="space-y-4">
                {games.map((game) => (
                  <div key={game.id} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-3">
                          <h3 className="text-lg font-medium text-gray-900">{game.title}</h3>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            game.status === 'analyzed'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-orange-100 text-orange-800'
                          }`}>
                            {game.status.toUpperCase()}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                          <div>
                            <p><strong>Team:</strong> {game.team_name}</p>
                            <p><strong>Uploaded by:</strong> {game.uploaded_by_name}</p>
                          </div>
                          <div>
                            <p><strong>Email:</strong> {game.uploaded_by_email}</p>
                            <p><strong>Date:</strong> {new Date(game.created_at).toLocaleDateString()}</p>
                          </div>
                        </div>
                        
                        <div className="mt-3">
                          <p className="text-sm text-gray-600"><strong>VEO URL:</strong></p>
                          <a 
                            href={game.video_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:text-blue-800 break-all"
                          >
                            {game.video_url}
                          </a>
                        </div>
                      </div>
                      
                      <div className="flex flex-col space-y-2 ml-6">
                        <button
                          onClick={() => handleAddVideo(game)}
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
                        >
                          Add S3 Video
                        </button>
                        <button
                          onClick={() => handleAddJson(game)}
                          className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-purple-700 transition-colors"
                        >
                          Add Analysis
                        </button>
                        {game.status === 'pending' && (
                          <button
                            onClick={() => handleMarkAnalyzed(game)}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 transition-colors"
                          >
                            Mark Analyzed
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
      </div>

      {/* Add Video Modal */}
      {showVideoModal && selectedGame && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Add S3 Video URL</h3>
            <p className="text-sm text-gray-600 mb-4">Game: {selectedGame.title}</p>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}
            
            <form onSubmit={handleSubmitVideo} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">S3 Video URL</label>
                <input
                  type="url"
                  value={videoUrl}
                  onChange={(e) => setVideoUrl(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                  placeholder="s3://bucket/game-id/full-game.mp4"
                  required
                  disabled={updating}
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowVideoModal(false)
                    setVideoUrl('')
                    setSelectedGame(null)
                    setError('')
                  }}
                  className="px-6 py-2.5 text-gray-600 hover:text-gray-800 transition-colors"
                  disabled={updating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updating || !videoUrl.trim()}
                  className="bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {updating ? 'Adding...' : 'Add Video'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add JSON Modal */}
      {showJsonModal && selectedGame && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl shadow-xl">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Add Analysis JSON</h3>
            <p className="text-sm text-gray-600 mb-4">Game: {selectedGame.title}</p>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}
            
            <form onSubmit={handleSubmitJson} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Events JSON</label>
                <textarea
                  value={jsonData}
                  onChange={(e) => setJsonData(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32] font-mono text-sm"
                  placeholder='{"events": [{"type": "goal", "timestamp": 245.5, "player": "Smith #9"}]}'
                  rows={10}
                  required
                  disabled={updating}
                />
              </div>
              <div className="text-xs text-gray-500">
                <p>This will mark the game as "analyzed" and update the status.</p>
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowJsonModal(false)
                    setJsonData('')
                    setSelectedGame(null)
                    setError('')
                  }}
                  className="px-6 py-2.5 text-gray-600 hover:text-gray-800 transition-colors"
                  disabled={updating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updating || !jsonData.trim()}
                  className="bg-purple-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {updating ? 'Adding...' : 'Add Analysis'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
} 