'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import apiClient from '@/lib/api-client'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL
if (!API_BASE_URL) {
  throw new Error('NEXT_PUBLIC_API_URL environment variable is not set')
}

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
  
  // New state for database overview
  const [activeTab, setActiveTab] = useState<'games' | 'database'>('games')
  const [dbData, setDbData] = useState<any>(null)
  const [dbLoading, setDbLoading] = useState(false)
  const [showAllUsers, setShowAllUsers] = useState(false)
  const [showAllTeams, setShowAllTeams] = useState(false)
  const [showAllGames, setShowAllGames] = useState(false)
  
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

  const handleResetEvents = async (game: Game) => {
    if (!confirm(`Reset "${game.title}" events back to AI analysis?\n\nThis will remove all user modifications and show the original ${game.ai_events_count} AI events.`)) {
      return
    }

    try {
      setUpdating(true)
      setError('')
      const response = await apiClient.resetEventsToAI(game.id)
      console.log('✅ Events reset:', response.message)
      await loadDashboardData()
    } catch (err: any) {
      console.error('Failed to reset events:', err)
      setError(err.message || 'Failed to reset events')
    } finally {
      setUpdating(false)
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

  // Metadata upload handler (single JSON to set video, events, tactical, team identity)
  const handleMetadataSave = async (game: Game, url: string) => {
    try {
      setUpdating(true);
      setError('');
      await apiClient.applyGameMetadata(game.id, url);
      console.log('✅ Metadata applied');
      await loadDashboardData();
    } catch (err: any) {
      console.error('Failed to apply metadata URL:', err);
      setError(err.message || 'Failed to apply metadata URL');
    } finally {
      setUpdating(false);
    }
  };

  // Load comprehensive database data
  const loadDatabaseData = async () => {
    try {
      setDbLoading(true);
      setError('');
      
      const response = await fetch(`${API_BASE_URL}/api/database/overview`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load database data');
      }
      
      const data = await response.json();
      setDbData(data);
    } catch (err: any) {
      console.error('Database load error:', err);
      setError(err.message || 'Failed to load database data');
    } finally {
      setDbLoading(false);
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

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('games')}
                className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'games'
                    ? 'border-[#016F32] text-[#016F32]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Games Management
              </button>
              <button
                onClick={() => {
                  setActiveTab('database');
                  if (!dbData) loadDatabaseData();
                }}
                className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'database'
                    ? 'border-[#016F32] text-[#016F32]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Database Overview
              </button>
            </nav>
          </div>
        </div>

        {/* Games Management Tab */}
        {activeTab === 'games' && (
          <>
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
                    <div className="space-y-4">
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
                          

                        </div>
                      
                      {/* Management Actions */}
                                                {/* Video URL Input */}
                        <div className="space-y-2">
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
                          {game.s3_key && (
                            <div className="ml-20 pl-2">
                              <p className="text-xs text-gray-500 mb-1">Current:</p>
                              <p className="text-sm text-green-700 font-mono bg-green-50 px-2 py-1 rounded break-all">
                                {game.s3_key}
                              </p>
                            </div>
                          )}
                        </div>

                        {/* Events URL Input */}
                        <div className="space-y-2">
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
                          {game.events_url && (
                            <div className="ml-20 pl-2">
                              <p className="text-xs text-gray-500 mb-1">Current:</p>
                              <p className="text-sm text-blue-700 font-mono bg-blue-50 px-2 py-1 rounded break-all">
                                {game.events_url}
                              </p>
                            </div>
                          )}
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

                        {/* Metadata URL Input */}
                        <div className="flex items-center space-x-2">
                          <label className="text-sm font-bold text-gray-900 whitespace-nowrap w-20">
                            Metadata:
                          </label>
                          <input
                            type="url"
                            placeholder="Paste metadata JSON URL..."
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white placeholder-gray-500 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                const input = e.target as HTMLInputElement;
                                if (input.value.trim()) {
                                  handleMetadataSave(game, input.value.trim());
                                  input.value = '';
                                }
                              }
                            }}
                          />
                          <button
                            className="bg-indigo-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-indigo-700 transition-colors"
                            onClick={(e) => {
                              const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                              if (input?.value.trim()) {
                                handleMetadataSave(game, input.value.trim());
                                input.value = '';
                              }
                            }}
                          >
                            Save
                          </button>
                        </div>

                        {/* Show Metadata Location if uploaded */}
                        {game.metadata_url && (
                          <div className="mt-2 text-sm">
                            <p className="text-base font-semibold text-gray-900"><strong>Current Metadata:</strong></p>
                            <p className="text-purple-600 font-mono text-xs break-all">
                              {game.metadata_url}
                            </p>
                          </div>
                        )}

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

                        {/* Events Management - Enhanced */}
                        <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-4 border border-gray-200">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <div className="flex items-center space-x-2">
                                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                                </svg>
                                <span className="text-sm font-semibold text-gray-700">Event Status</span>
                              </div>
                              
                              {game.has_modified_events ? (
                                <div className="flex items-center space-x-3">
                                  <div className="flex items-center space-x-2">
                                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 border border-blue-200">
                                      ✏️ User Modified ({game.modified_events_count} events)
                                    </span>
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    Original: {game.ai_events_count} AI events
                                  </div>
                                </div>
                              ) : (
                                <div className="flex items-center space-x-3">
                                  <div className="flex items-center space-x-2">
                                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 border border-green-200">
                                      🤖 Original AI Analysis ({game.ai_events_count || 0} events)
                                    </span>
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    No user modifications
                                  </div>
                                </div>
                              )}
                            </div>
                            
                            {game.has_modified_events && (
                              <button
                                onClick={() => handleResetEvents(game)}
                                disabled={updating}
                                className="inline-flex items-center px-4 py-2 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                                title="Reset to original AI events"
                              >
                                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                                Reset to AI Analysis
                              </button>
                            )}
                          </div>
                        </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
          </>
        )}

        {/* Database Overview Tab */}
        {activeTab === 'database' && (
          <div className="bg-white rounded-xl shadow-sm">
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-2xl font-bold text-gray-900">Database Overview</h2>
              <p className="text-gray-600 mt-1">Comprehensive view of all platform data</p>
            </div>
            
            <div className="p-6">
              {dbLoading ? (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#016F32]"></div>
                  <p className="mt-2 text-gray-900">Loading database data...</p>
                </div>
              ) : dbData ? (
                <div className="space-y-8">
                  {/* Users Section */}
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">👤 Users ({dbData.users?.length || 0})</h3>
                      {dbData.users?.length > 10 && (
                        <button
                          onClick={() => setShowAllUsers(!showAllUsers)}
                          className="bg-[#016F32] text-white px-4 py-2 rounded-lg text-sm hover:bg-[#014d24] transition-colors"
                        >
                          {showAllUsers ? 'Show Less' : 'Show All Users'}
                        </button>
                      )}
                    </div>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Team Memberships</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Games</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {(showAllUsers ? dbData.users : dbData.users?.slice(0, 10))?.map((user: any, index: number) => (
                            <tr key={index} className="hover:bg-gray-50">
                              <td className="px-6 py-4 text-sm text-gray-900">{user.email}</td>
                              <td className="px-6 py-4 text-sm text-gray-900">{user.name}</td>
                              <td className="px-6 py-4">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                  user.role === 'company' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                                }`}>
                                  {user.role}
                                </span>
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-900">
                                {user.team_names && user.team_names.length > 0 ? (
                                  <div className="flex flex-wrap gap-1">
                                    {user.team_names.map((teamName: string, idx: number) => (
                                      <span key={idx} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                                        {teamName}
                                      </span>
                                    ))}
                                  </div>
                                ) : (
                                  <span className="text-gray-400 text-xs">No teams</span>
                                )}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-900">{user.games_uploaded}</td>
                              <td className="px-6 py-4 text-sm text-gray-500">
                                {new Date(user.created_at).toLocaleDateString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {!showAllUsers && dbData.users?.length > 10 && (
                        <p className="text-sm text-gray-500 mt-2">Showing first 10 of {dbData.users.length} users</p>
                      )}
                      {showAllUsers && (
                        <p className="text-sm text-gray-500 mt-2">Showing all {dbData.users?.length} users</p>
                      )}
                    </div>
                  </div>

                  {/* Teams Section */}
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">⚽ Teams ({dbData.teams?.length || 0})</h3>
                      {dbData.teams?.length > 5 && (
                        <button
                          onClick={() => setShowAllTeams(!showAllTeams)}
                          className="bg-[#016F32] text-white px-4 py-2 rounded-lg text-sm hover:bg-[#014d24] transition-colors"
                        >
                          {showAllTeams ? 'Show Less' : 'Show All Teams'}
                        </button>
                      )}
                    </div>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Members</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Games</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {(showAllTeams ? dbData.teams : dbData.teams?.slice(0, 5))?.map((team: any, index: number) => (
                            <tr key={index} className="hover:bg-gray-50">
                              <td className="px-6 py-4 text-sm font-medium text-gray-900">{team.name}</td>
                              <td className="px-6 py-4 text-sm text-gray-900 font-mono">{team.team_code}</td>
                              <td className="px-6 py-4 text-sm text-gray-900">{team.members_count}</td>
                              <td className="px-6 py-4 text-sm text-gray-900">{team.games_count}</td>
                              <td className="px-6 py-4 text-sm text-gray-500">
                                {new Date(team.created_at).toLocaleDateString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {!showAllTeams && dbData.teams?.length > 5 && (
                        <p className="text-sm text-gray-500 mt-2">Showing first 5 of {dbData.teams.length} teams</p>
                      )}
                      {showAllTeams && (
                        <p className="text-sm text-gray-500 mt-2">Showing all {dbData.teams?.length} teams</p>
                      )}
                    </div>
                  </div>

                  {/* Games Section */}
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">🎮 Games ({dbData.games?.length || 0})</h3>
                      {dbData.games?.length > 5 && (
                        <button
                          onClick={() => setShowAllGames(!showAllGames)}
                          className="bg-[#016F32] text-white px-4 py-2 rounded-lg text-sm hover:bg-[#014d24] transition-colors"
                        >
                          {showAllGames ? 'Show Less' : 'Show All Games'}
                        </button>
                      )}
                    </div>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Team</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Analysis</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Events</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded By</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {(showAllGames ? dbData.games : dbData.games?.slice(0, 5))?.map((game: any, index: number) => (
                            <tr key={index} className="hover:bg-gray-50">
                              <td className="px-6 py-4 text-sm font-medium text-gray-900">{game.title}</td>
                              <td className="px-6 py-4 text-sm text-gray-900">{game.team_name}</td>
                              <td className="px-6 py-4">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                  game.status === 'analyzed' ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
                                }`}>
                                  {game.status}
                                </span>
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-900">
                                {game.has_analysis === 'Yes' ? '✅' : '❌'}
                                {game.has_tactical === 'Yes' ? ' 📊' : ''}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-900">
                                <div className="flex items-center space-x-2">
                                  <span>{game.events_count || 0}</span>
                                  {game.events_type === 'Modified' ? (
                                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                                      Modified
                                    </span>
                                  ) : (
                                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                                      AI
                                    </span>
                                  )}
                                </div>
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-500">{game.uploaded_by}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {!showAllGames && dbData.games?.length > 5 && (
                        <p className="text-sm text-gray-500 mt-2">Showing first 5 of {dbData.games.length} games</p>
                      )}
                      {showAllGames && (
                        <p className="text-sm text-gray-500 mt-2">Showing all {dbData.games?.length} games</p>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500">No database data available</p>
                  <button
                    onClick={loadDatabaseData}
                    className="mt-4 bg-[#016F32] text-white px-4 py-2 rounded-lg hover:bg-[#014d24] transition-colors"
                  >
                    Load Database Data
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
} /* Cache bust: Mon Jul 28 23:42:50 BST 2025 */
