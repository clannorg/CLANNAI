'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import apiClient from '@/lib/api-client'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3002'

interface Game {
  id: string
  title: string
  description: string
  video_url: string
  s3_key?: string
  status: string
  team_name: string
  uploaded_by_name: string
  uploaded_by_email: string
  created_at: string
  has_analysis: boolean
  tactical_analysis_url?: string
  has_tactical?: boolean
  events_url?: string
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
  
  // Simplified state
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

  const handleMarkPending = async (game: Game) => {
    try {
      setError('')
      
      await apiClient.updateGameAnalysis(game.id, {
        status: 'pending'
      })
      
      await loadDashboardData()
    } catch (err: any) {
      console.error('Failed to mark as pending:', err)
      setError(err.message || 'Failed to mark as pending')
    }
  }



  // Video upload handler
  const handleVideoSave = async (game: Game, url: string) => {
    try {
      setUpdating(true);
      setError('');
      
      await fetch(`${API_BASE_URL}/api/games/${game.id}/upload-video`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'Authorization': `Bearer ${localStorage.getItem('token')}` 
        },
        body: JSON.stringify({ 
          s3Key: url,
          originalFilename: url.split('/').pop() || 'video.mp4',
          fileSize: 0,
          duration: 0
        })
      });
      console.log('✅ Video URL saved');
      await loadDashboardData();
      
    } catch (err: any) {
      console.error('Failed to save video URL:', err);
      setError(err.message || 'Failed to save video URL');
    } finally {
      setUpdating(false);
    }
  };

  // Events upload handler  
  const handleEventsSave = async (game: Game, url: string) => {
    try {
      setUpdating(true);
      setError('');
      
      await fetch(`${API_BASE_URL}/api/games/${game.id}/upload-events`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'Authorization': `Bearer ${localStorage.getItem('token')}` 
        },
        body: JSON.stringify({ 
          s3Key: url,
          originalFilename: url.split('/').pop() || 'events.json'
        })
      });
      console.log('✅ Events processed and saved');
      await loadDashboardData();
      
    } catch (err: any) {
      console.error('Failed to save events URL:', err);
      setError(err.message || 'Failed to save events URL');
    } finally {
      setUpdating(false);
    }
  };

  // Analysis upload handler (for tactical, timeline, etc.)
  const handleAnalysisSave = async (game: Game, url: string) => {
    try {
      setUpdating(true);
      setError('');
      
      const filename = url.split('/').pop() || 'analysis.txt';
      const urlLower = url.toLowerCase();
      
      // Determine if it's tactical or general analysis
      const isTactical = urlLower.includes('tactical') || urlLower.includes('coaching') || 
                        urlLower.includes('red_team') || urlLower.includes('yellow_team') ||
                        urlLower.includes('summary') || urlLower.includes('insights');
      
      const endpoint = isTactical ? 'upload-tactical' : 'upload-analysis-file';
      
      await fetch(`${API_BASE_URL}/api/games/${game.id}/${endpoint}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'Authorization': `Bearer ${localStorage.getItem('token')}` 
        },
        body: JSON.stringify({ 
          s3Key: url,
          originalFilename: filename
        })
      });
      console.log(`✅ ${isTactical ? 'Tactical' : 'Analysis'} file saved`);
      await loadDashboardData();
      
    } catch (err: any) {
      console.error('Failed to save analysis URL:', err);
      setError(err.message || 'Failed to save analysis URL');
    } finally {
      setUpdating(false);
    }
  };





  if (!user) {
    return <div className="min-h-screen bg-[#F7F6F1] flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#016F32]"></div>
        <p className="mt-2 text-gray-900">Loading...</p>
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
                width={160}
                height={42}
                className="h-10 w-auto"
                priority 
                alt="ClannAI" 
                width={48} 
                height={48}
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Company Dashboard</h1>
                <p className="text-base font-semibold text-gray-900">Welcome, {user.email}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <a
                href="/dashboard"
                className="border border-gray-300 text-gray-900 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
              >
                User Dashboard
              </a>
              <button
                onClick={handleLogout}
                className="border border-gray-300 text-gray-900 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
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
              <h3 className="text-sm font-medium text-gray-900">Total Games</h3>
              <p className="text-3xl font-bold text-gray-900">{stats.total_games}</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-sm font-medium text-gray-900">Pending</h3>
              <p className="text-3xl font-bold text-orange-600">{stats.pending_games}</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-sm font-medium text-gray-900">Analyzed</h3>
              <p className="text-3xl font-bold text-green-600">{stats.analyzed_games}</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-sm font-medium text-gray-900">Teams</h3>
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
                        : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
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
                <p className="mt-2 text-gray-900">Loading games...</p>
              </div>
            ) : games.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-900">No games found</p>
              </div>
            ) : (
              <div className="space-y-4">
                {games.map((game) => (
                  <div key={game.id} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between">
                      <div className="flex-1 mb-4 lg:mb-0">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-3 mb-3">
                          <h3 className="text-lg font-medium text-gray-900 mb-2 sm:mb-0">{game.title}</h3>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium w-fit ${
                            game.status === 'analyzed'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-orange-100 text-orange-800'
                          }`}>
                            {game.status.toUpperCase()}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-base font-semibold text-gray-900">
                          <div>
                            <p><strong>Team:</strong> {game.team_name}</p>
                            <p><strong>Uploaded by:</strong> {game.uploaded_by_name}</p>
                          </div>
                          <div>
                            <p><strong>Email:</strong> {game.uploaded_by_email}</p>
                            <p><strong>Date:</strong> {new Date(game.created_at).toLocaleDateString()}</p>
                          </div>
                        </div>
                        
                        <div className="mt-3 space-y-2">
                          <div>
                            <p className="text-base font-semibold text-gray-900"><strong>VEO URL:</strong></p>
                            <a 
                              href={game.video_url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-sm text-blue-600 hover:text-blue-800 break-all"
                            >
                              {game.video_url}
                            </a>
                          </div>
                          
                          {game.s3_key && (
                            <div>
                              <p className="text-base font-semibold text-gray-900"><strong>Current S3 Location:</strong></p>
                              <p className="text-sm text-green-700 font-mono bg-green-50 px-2 py-1 rounded break-all">
                                {game.s3_key}
                              </p>
                            </div>
                          )}
                          
                          {game.events_url && (
                            <div>
                              <p className="text-base font-semibold text-gray-900"><strong>Current Events Location:</strong></p>
                              <p className="text-sm text-blue-700 font-mono bg-blue-50 px-2 py-1 rounded break-all">
                                {game.events_url}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="space-y-3 lg:ml-6">
                                                {/* Video URL Input */}
                        <div className="flex items-center space-x-2">
                          <label className="text-sm font-bold text-gray-900 whitespace-nowrap w-20">
                            Video:
                          </label>
                          <input
                            type="url"
                            placeholder="Paste video S3 URL..."
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                const input = e.target as HTMLInputElement;
                                if (input.value.trim()) {
                                  handleVideoSave(game, input.value.trim());
                                  input.value = '';
                                }
                              }
                            }}
                          />
                          <button
                            className="bg-blue-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
                            onClick={(e) => {
                              const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                              if (input?.value.trim()) {
                                handleVideoSave(game, input.value.trim());
                                input.value = '';
                              }
                            }}
                          >
                            Save
                          </button>
                        </div>

                        {/* Events URL Input */}
                        <div className="flex items-center space-x-2">
                          <label className="text-sm font-bold text-gray-900 whitespace-nowrap w-20">
                            Events:
                          </label>
                          <input
                            type="url"
                            placeholder="Paste events JSON URL..."
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white placeholder-gray-500 focus:ring-2 focus:ring-green-500/20 focus:border-green-500"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                const input = e.target as HTMLInputElement;
                                if (input.value.trim()) {
                                  handleEventsSave(game, input.value.trim());
                                  input.value = '';
                                }
                              }
                            }}
                          />
                          <button
                            className="bg-green-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-green-700 transition-colors"
                            onClick={(e) => {
                              const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                              if (input?.value.trim()) {
                                handleEventsSave(game, input.value.trim());
                                input.value = '';
                              }
                            }}
                          >
                            Save
                          </button>
                        </div>

                        {/* Analysis URL Input */}
                        <div className="flex items-center space-x-2">
                          <label className="text-sm font-bold text-gray-900 whitespace-nowrap w-20">
                            Analysis:
                          </label>
                          <input
                            type="url"
                            placeholder="Paste analysis file URL..."
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white placeholder-gray-500 focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                const input = e.target as HTMLInputElement;
                                if (input.value.trim()) {
                                  handleAnalysisSave(game, input.value.trim());
                                  input.value = '';
                                }
                              }
                            }}
                          />
                          <button
                            className="bg-purple-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-purple-700 transition-colors"
                            onClick={(e) => {
                              const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                              if (input?.value.trim()) {
                                handleAnalysisSave(game, input.value.trim());
                                input.value = '';
                              }
                            }}
                          >
                            Save
                          </button>
                        </div>

                        {/* Show Tactical Analysis Location if uploaded */}
                        {game.tactical_analysis_url && (
                          <div className="mt-2 text-sm">
                            <p className="text-base font-semibold text-gray-900"><strong>Current Tactical Analysis:</strong></p>
                            <p className="text-green-600 font-mono text-xs break-all">
                              {game.tactical_analysis_url}
                            </p>
                          </div>
                        )}

                        {/* Status Toggle */}
                        <div className="flex items-center space-x-2">
                          <label className="text-sm font-bold text-gray-900 whitespace-nowrap w-20">
                            Status:
                          </label>
                          <button
                            onClick={() => game.status === 'pending' ? handleMarkAnalyzed(game) : handleMarkPending(game)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                              game.status === 'analyzed'
                                ? 'bg-orange-600 text-white hover:bg-orange-700'
                                : 'bg-green-600 text-white hover:bg-green-700'
                            }`}
                          >
                            Mark as {game.status === 'pending' ? 'Analyzed' : 'Pending'}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
} /* Cache bust: Mon Jul 28 23:42:50 BST 2025 */
