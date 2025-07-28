'use client'

import { useState, useEffect } from 'react'

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

  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
    }
    
    // Mock data for demo
    setGames([
      {
        id: '1',
        title: 'Arsenal vs Brighton - July 28th',
        status: 'pending',
        team_name: 'Arsenal FC Academy',
        created_at: '2024-07-28T14:00:00Z'
      },
      {
        id: '2', 
        title: 'Arsenal vs Tottenham - July 20th',
        status: 'analyzed',
        team_name: 'Arsenal FC Academy',
        created_at: '2024-07-20T16:00:00Z'
      }
    ])
    
    setTeams([
      {
        id: '1',
        name: 'Arsenal FC Academy',
        team_code: 'ARS269',
        color: '#FF0000'
      }
    ])
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/'
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-white">ClannAI</h1>
            {user && (
              <div className="text-gray-300">
                Welcome, {user.name}
                {user.role === 'company' && (
                  <span className="ml-2 px-2 py-1 bg-blue-600 text-xs rounded">Company</span>
                )}
              </div>
            )}
          </div>
          <div className="flex items-center space-x-4">
            {user?.role === 'company' && (
              <a
                href="/company"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Company Dashboard
              </a>
            )}
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Tabs */}
        <div className="border-b border-gray-700 mb-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('games')}
              className={`py-2 px-4 border-b-2 font-medium text-sm ${
                activeTab === 'games'
                  ? 'border-green-500 text-green-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Games
            </button>
            <button
              onClick={() => setActiveTab('teams')}
              className={`py-2 px-4 border-b-2 font-medium text-sm ${
                activeTab === 'teams'
                  ? 'border-green-500 text-green-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Teams
            </button>
          </nav>
        </div>

        {/* Games Tab */}
        {activeTab === 'games' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-white">Your Games</h2>
              <button
                onClick={() => setShowUploadModal(true)}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                Upload VEO URL
              </button>
            </div>

            <div className="grid gap-4">
              {games.map((game: any) => (
                <div key={game.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-medium text-white mb-2">{game.title}</h3>
                      <p className="text-gray-400 text-sm mb-2">Team: {game.team_name}</p>
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
                        <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors">
                          View Analysis
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Teams Tab */}
        {activeTab === 'teams' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-white">Your Teams</h2>
              <button
                onClick={() => setShowJoinModal(true)}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                Join Team
              </button>
            </div>

            <div className="grid gap-4">
              {teams.map((team: any) => (
                <div key={team.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-medium text-white mb-2">{team.name}</h3>
                      <p className="text-gray-400 text-sm">Join Code: {team.team_code}</p>
                    </div>
                    <div
                      className="w-12 h-12 rounded-full"
                      style={{ backgroundColor: team.color }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-white mb-4">Upload VEO URL</h3>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Game Title</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                  placeholder="e.g., Arsenal vs Brighton - July 28th"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">VEO URL</label>
                <input
                  type="url"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                  placeholder="https://veo.co/watch/..."
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-white mb-4">Join Team</h3>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Team Code</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                  placeholder="e.g., ARS269"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowJoinModal(false)}
                  className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                >
                  Join
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
} 