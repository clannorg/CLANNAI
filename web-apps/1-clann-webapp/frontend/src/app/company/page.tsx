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
  s3_key?: string
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

  // Add to state at the top of CompanyDashboard
  const [showS3FilesModal, setShowS3FilesModal] = useState(false);
  const [s3Files, setS3Files] = useState({
    video: '',
    events: '',
    tactics: '',
    commentary: ''
  });
  const [s3LocationsUrl, setS3LocationsUrl] = useState('');
  const [autoFillError, setAutoFillError] = useState('');

  // VM File List state
  const [showVMUploadModal, setShowVMUploadModal] = useState(false);
  const [vmFileList, setVmFileList] = useState('');

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
      
      const parsedData = JSON.parse(jsonData.trim())
      
      // Handle both {"events": [...]} and [...] formats
      const events = Array.isArray(parsedData) ? parsedData : parsedData.events
      
      if (!events || !Array.isArray(events)) {
        throw new Error('Invalid JSON format. Expected an array or an object with "events" property.')
      }
      
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

  // Handler for opening the modal
  const handleAddS3Files = (game: Game) => {
    setSelectedGame(game);
    setS3Files({ video: '', events: '', tactics: '', commentary: '' });
    setS3LocationsUrl('');
    setAutoFillError('');
    setShowS3FilesModal(true);
  };

  // Handler for input changes
  const handleS3FileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setS3Files({ ...s3Files, [e.target.name]: e.target.value });
  };

  // Handler for auto-filling from s3_locations.json
  const handleS3LocationsUrlChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    setS3LocationsUrl(url);
    setAutoFillError('');
    if (url && url.startsWith('http')) {
      try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch JSON');
        const data = await response.json();
        if (data.s3_urls) {
          setS3Files((prev) => ({
            ...prev,
            video: data.s3_urls['video.mp4']?.url || prev.video,
            events: data.s3_urls['web_events.json']?.url || prev.events,
            tactics: data.s3_urls['tactical_coaching_insights.json']?.url || prev.tactics,
            commentary: data.s3_urls['match_commentary.md']?.url || prev.commentary
          }));
        } else {
          setAutoFillError('No s3_urls key found in JSON');
        }
      } catch (err) {
        setAutoFillError('Failed to fetch or parse s3_locations.json');
      }
    }
  };

  // Handler for submitting S3 files
  const handleSubmitS3Files = async (e: React.FormEvent) => {
    e.preventDefault();
    setUpdating(true);
    try {
      await fetch(`/api/games/${selectedGame?.id}/analysis-files`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ s3AnalysisFiles: s3Files })
      });
      setShowS3FilesModal(false);
      setS3Files({ video: '', events: '', tactics: '', commentary: '' });
      setS3LocationsUrl('');
      setAutoFillError('');
      setSelectedGame(null);
      setError('');
      loadDashboardData();
    } catch (err) {
      setError('Failed to update S3 file locations');
    } finally {
      setUpdating(false);
    }
  };

  // VM File List handlers
  const handleAddVMFiles = (game: Game) => {
    setSelectedGame(game);
    setVmFileList('');
    setShowVMUploadModal(true);
  };

  const parseVMFileList = (fileList: string) => {
    const files: Record<string, string> = {};
    const lines = fileList.split('\n').filter(line => line.includes('='));
    
    lines.forEach(line => {
      const [filename, url] = line.split('=');
      if (filename && url) {
        files[filename.trim()] = url.trim();
      }
    });
    
    return files;
  };

  const handleSubmitVMFiles = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGame || !vmFileList.trim()) return;

    try {
      setUpdating(true);
      setError('');
      
      // Parse the VM file list
      const fileMap = parseVMFileList(vmFileList.trim());
      
      // For now, just store as S3 analysis files
      await fetch(`/api/games/${selectedGame.id}/analysis-files`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'Authorization': `Bearer ${localStorage.getItem('token')}` 
        },
        body: JSON.stringify({ s3AnalysisFiles: fileMap })
      });
      
      setShowVMUploadModal(false);
      setVmFileList('');
      setSelectedGame(null);
      await loadDashboardData();
    } catch (err: any) {
      console.error('Failed to upload VM files:', err);
      setError(err.message || 'Failed to upload VM file list');
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
                        </div>
                      </div>
                      
                      <div className="flex flex-col lg:flex-row lg:flex-wrap gap-2 lg:ml-6">
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
                        {/* Add S3 Analysis Files Button */}
                        <button
                          className="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 ml-2"
                          onClick={() => handleAddS3Files(game)}
                        >
                          Add S3 Analysis Files
                        </button>
                        {/* Add VM File List Button */}
                        <button
                          className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg"
                          onClick={() => handleAddVMFiles(game)}
                        >
                          🧠 VM File List
                        </button>
                        {game.status === 'pending' && (
                          <button
                            onClick={() => handleMarkAnalyzed(game)}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 transition-colors"
                          >
                            Mark Analyzed
                          </button>
                        )}
                        {game.status === 'analyzed' && (
                          <button
                            onClick={() => handleMarkPending(game)}
                            className="bg-orange-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-orange-700 transition-colors"
                          >
                            Mark as Pending
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
            <p className="text-base font-semibold text-gray-900 mb-4">Game: {selectedGame.title}</p>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}
            
            <form onSubmit={handleSubmitVideo} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-1">S3 Video URL</label>
                <input
                  type="url"
                  value={videoUrl}
                  onChange={(e) => setVideoUrl(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#016F32]/20 focus:border-[#016F32]"
                  placeholder="games/game-id/full-game.mp4 or s3://clannai-video-storage/games/game-id/full-game.mp4"
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
                  className="px-6 py-2.5 text-gray-900 hover:text-gray-900 transition-colors"
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
            <p className="text-base font-semibold text-gray-900 mb-4">Game: {selectedGame.title}</p>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}
            
            <form onSubmit={handleSubmitJson} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-1">Events JSON</label>
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
              <div className="text-xs text-gray-900">
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
                  className="px-6 py-2.5 text-gray-900 hover:text-gray-900 transition-colors"
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

      {/* S3 Analysis Files Modal (AI-generated) */}
      {showS3FilesModal && selectedGame && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Add S3 Analysis File Locations</h3>
            <form onSubmit={handleSubmitS3Files} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-1">s3_locations.json URL (auto-fill)</label>
                <input
                  name="s3LocationsUrl"
                  type="url"
                  value={s3LocationsUrl}
                  onChange={handleS3LocationsUrlChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  placeholder="Paste S3 URL for s3_locations.json (optional)"
                  disabled={updating}
                />
                {autoFillError && <div className="text-red-600 text-xs mt-1">{autoFillError}</div>}
              </div>
              {['video', 'events', 'tactics', 'commentary'].map((type) => (
                <div key={type}>
                  <label className="block text-sm font-medium text-gray-900 mb-1">
                    {type.charAt(0).toUpperCase() + type.slice(1)} S3 URL
                  </label>
                  <input
                    name={type}
                    type="url"
                    value={s3Files[type]}
                    onChange={handleS3FileChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    placeholder={`S3 URL for ${type}`}
                    disabled={updating}
                  />
                </div>
              ))}
              <div className="flex justify-end space-x-3">
                <button type="button" onClick={() => setShowS3FilesModal(false)} className="px-6 py-2.5 text-gray-900">Cancel</button>
                <button type="submit" disabled={updating} className="bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700">
                  {updating ? 'Saving...' : 'Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* VM File List Upload Modal */}
      {showVMUploadModal && selectedGame && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-3xl shadow-xl">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Upload VM Analysis Files</h3>
            <p className="text-base text-gray-700 mb-4">
              Paste your VM analysis file list below. Each line should be in format: filename=S3_URL
            </p>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}
            
            <form onSubmit={handleSubmitVMFiles} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-1">
                  VM File List (copy from your VM output)
                </label>
                <textarea
                  value={vmFileList}
                  onChange={(e) => setVmFileList(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 font-mono text-xs"
                  placeholder={`1_veo_ground_truth.json=https://end-nov-webapp-clann.s3.amazonaws.com/analysis-data/f323-527e6a4e-1_veo_ground_truth-json.json
5_complete_timeline.txt=https://end-nov-webapp-clann.s3.amazonaws.com/analysis-data/f323-527e6a4e-5_complete_timeline-txt.txt
web_events.json=https://end-nov-webapp-clann.s3.amazonaws.com/analysis-data/f323-527e6a4e-web_events-json.json
video.mp4=https://end-nov-webapp-clann.s3.amazonaws.com/analysis-videos/f323-527e6a4e-video-mp4.mp4`}
                  rows={12}
                  required
                  disabled={updating}
                />
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">What happens:</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>✅ All file URLs are stored for this game</li>
                  <li>✅ Files are accessible for processing later</li>
                  <li>✅ Format: filename=url (one per line)</li>
                  <li>⏳ Next: We'll add automatic processing of these files</li>
                </ul>
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowVMUploadModal(false)
                    setVmFileList('')
                    setSelectedGame(null)
                    setError('')
                  }}
                  className="px-6 py-2.5 text-gray-900 hover:text-gray-900 transition-colors"
                  disabled={updating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updating || !vmFileList.trim()}
                  className="bg-purple-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {updating ? 'Uploading...' : 'Upload File List'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
} /* Cache bust: Mon Jul 28 23:42:50 BST 2025 */
