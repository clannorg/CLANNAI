import React, { useState, useEffect } from 'react';
import sessionService from '../services/sessionService';
import teamService from '../services/teamService';
import NavBar from '../components/ui/NavBar';
import TopNav from '../components/navigation/TopNav';
import { Link, useNavigate } from 'react-router-dom';
import SessionCard from '../components/SessionCard';
import Header from '../components/ui/Header';

const getSourceType = (url) => {
  try {
    const hostname = new URL(url).hostname;
    if (hostname.includes('veo')) return 'Veo';
    if (hostname.includes('youtube')) return 'YouTube';
    return hostname;
  } catch (e) {
    return 'Unknown';
  }
};

const getRelativeTime = (date) => {
  const now = new Date();
  const then = new Date(date);
  const diffInHours = Math.floor((now - then) / (1000 * 60 * 60));

  if (diffInHours < 24) {
    return diffInHours === 1 ? '1 hour ago' : `${diffInHours} hours ago`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays === 1) return 'Yesterday';
  if (diffInDays < 7) return `${diffInDays} days ago`;

  return then.toLocaleDateString();
};

function Sessions() {
  const [url, setUrl] = useState('');
  const [teamName, setTeamName] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [teamCode, setTeamCode] = useState('');
  const [selectedAnalyses, setSelectedAnalyses] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchUserTeams = async () => {
    try {
      const teams = await teamService.getUserTeams();
      // If user has teams, pre-fill with most recent team name
      if (teams.length > 0) {
        setTeamName(teams[0].name);
      }
    } catch (err) {
      console.error('Failed to fetch teams:', err);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setFeedback(null);

    if (!url.trim()) {
      setFeedback({
        type: 'error',
        message: 'Please enter a game footage URL'
      });
      setIsLoading(false);
      return;
    }

    // Check if URL already exists in current sessions
    const urlExists = sessions.some(session => session.footage_url === url.trim());
    if (urlExists) {
      setFeedback({
        type: 'error',
        message: 'This footage URL has already been uploaded'
      });
      setIsLoading(false);
      return;
    }

    if (!teamName.trim()) {
      setFeedback({
        type: 'error',
        message: 'Please enter a team name'
      });
      setIsLoading(false);
      return;
    }

    try {
      const response = await sessionService.createSession(url.trim(), teamName.trim());
      setFeedback({
        type: 'success',
        message: (
          <div className="flex flex-col gap-4">
            <p>Success! Your team code is: <span className="font-bold">{response.team_code}</span></p>
            <button
              onClick={() => copyToClipboard(response.team_code)}
              className="text-sm px-4 py-2 bg-green-500/20 text-green-400 
                         rounded-lg border border-green-500 
                         hover:bg-green-500/30 transition-colors"
            >
              📋 Copy Invite Message
            </button>
          </div>
        )
      });
      setUrl('');
      setTeamName('');
      fetchSessions();
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.message || 'Upload failed',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinTeam = async (e) => {
    e.preventDefault();
    if (!teamCode.trim()) {
      setFeedback({
        type: 'error',
        message: 'Please enter a team code'
      });
      return;
    }

    try {
      setIsLoading(true);
      const response = await teamService.joinTeam(teamCode);
      setFeedback({
        type: 'success',
        message: `Successfully joined team ${response.team_name}`
      });
      setTeamCode(''); // Clear the input
      fetchSessions(); // Refresh sessions to show new team's sessions
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.message || 'Failed to join team'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSessions = async () => {
    try {
      const response = await sessionService.getSessions();
      setSessions(response || []);
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
      setFeedback({
        type: 'error',
        message: err.message || 'Failed to fetch sessions'
      });
      setSessions([]);
    }
  };

  const handleDelete = async (sessionId) => {
    try {
      await sessionService.deleteSession(sessionId);
      setFeedback({
        type: 'success',
        message: 'Session deleted successfully'
      });
      // Refresh sessions list
      fetchSessions();
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.message || 'Failed to delete session'
      });
    }
  };

  const handleAnalysisSelect = (sessionId, type) => {
    setSelectedAnalyses(prev => ({
      ...prev,
      [sessionId]: type
    }));
  };

  const generateShareMessage = (teamCode) => {
    const message = `🏃‍♂️ Join my team on Clann AI to see our game analysis!\n\n` +
      `1. Go to https://clannai.com\n` +
      `2. Create an account or sign in\n` +
      `3. Click "Join Team"\n` +
      `4. Enter team code: ${teamCode}\n\n` +
      `See you there! 🎮`;
    return message;
  };

  const copyToClipboard = (teamCode) => {
    const message = generateShareMessage(teamCode);
    navigator.clipboard.writeText(message);
    setFeedback({
      type: 'success',
      message: 'Invite message copied to clipboard! Share it with your team.'
    });
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white pb-20">
      <TopNav 
        isLoggedIn={true} 
        onLogout={handleLogout} 
      />
      <div className="max-w-7xl mx-auto px-4 py-4 md:p-8 pt-24">
        {/* Feedback Messages */}
        {feedback && (
          <div className={`mb-6 p-4 rounded-lg border ${
            feedback.type === 'error'
              ? 'bg-red-500/20 border-red-500/30 text-red-400'
              : 'bg-green-500/20 border-green-500/30 text-green-400'
          }`}>
            {feedback.message}
          </div>
        )}

        {/* Upload and Join Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
          {/* Upload New Game */}
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50 hover:border-green-500/30 transition-all">
            <div className="flex items-center gap-3 mb-6">
              <span className="text-2xl">🎥</span>
              <h2 className="text-xl font-bold">Upload New Game</h2>
            </div>
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Game Footage URL</label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter URL"
                  className="w-full bg-gray-900/50 text-white px-4 py-2 rounded-lg border border-gray-700/50 
                           focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 focus:outline-none
                           transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Team Name</label>
                <input
                  type="text"
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  placeholder="Enter Team Name"
                  className="w-full bg-gray-900/50 text-white px-4 py-2 rounded-lg border border-gray-700/50 
                           focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 focus:outline-none
                           transition-colors"
                />
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                  isLoading
                    ? 'bg-blue-600/20 text-blue-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-500 text-white'
                }`}
              >
                {isLoading ? 'Uploading...' : 'Upload Game'}
              </button>
            </form>
          </div>

          {/* Join Team Section */}
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50 hover:border-green-500/30 transition-all">
            <div className="flex items-center gap-3 mb-6">
              <span className="text-2xl">👥</span>
              <h2 className="text-xl font-bold">Join Existing Team</h2>
            </div>
            <form onSubmit={handleJoinTeam} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Team Code</label>
                <input
                  type="text"
                  value={teamCode}
                  onChange={(e) => setTeamCode(e.target.value)}
                  placeholder="Enter Team Code"
                  maxLength={6}
                  className="w-full bg-gray-900/50 text-white px-4 py-2 rounded-lg border border-gray-700/50 
                           focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 focus:outline-none
                           transition-colors"
                />
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${isLoading
                  ? 'bg-blue-600/20 text-blue-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-500 text-white'
                }`}
              >
                {isLoading ? 'Joining...' : 'Join Team'}
              </button>
            </form>
          </div>
        </div>

        {/* Sessions List */}
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📊</span>
            <h2 className="text-2xl font-bold">Your Sessions</h2>
          </div>

          {isLoading ? (
            <p className="text-gray-400">Loading sessions...</p>
          ) : sessions?.length === 0 ? (
            <p className="text-gray-400">No sessions uploaded yet.</p>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {sessions.map(session => (
                <div
                  key={session.id}
                  onClick={() => navigate(`/session/${session.id}`)}
                  className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50 hover:border-green-500/30 transition-all cursor-pointer overflow-hidden"
                >
                  <div className="flex justify-between items-start max-w-full">
                    <div className="space-y-3 min-w-0 flex-1 mr-4">
                      <h3 className="text-xl font-bold truncate">{session.team_name}</h3>

                      <div className="space-y-2 text-sm text-gray-400">
                        <div className="flex items-center gap-2">
                          <span className="flex-shrink-0">📅</span>
                          <span className="truncate">{new Date(session.game_date).toLocaleDateString()}</span>
                        </div>

                        <div className="flex items-center gap-2">
                          <span className="flex-shrink-0">🎥</span>
                          <a
                            href={session.footage_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:underline truncate"
                            onClick={(e) => e.stopPropagation()}
                          >
                            {getSourceType(session.footage_url)}
                          </a>
                        </div>

                        <div className="flex items-center gap-2">
                          <span className="flex-shrink-0">🔗</span>
                          <a
                            href={session.footage_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-500 hover:text-gray-400 truncate"
                            onClick={(e) => e.stopPropagation()}
                          >
                            {session.footage_url}
                          </a>
                        </div>
                      </div>
                    </div>

                    <div className="flex-shrink-0 flex flex-col items-end gap-2">
                      <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap
                        ${session.status === 'PENDING'
                          ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                          : 'bg-green-500/20 text-green-400 border border-green-500/30'
                        }`}
                      >
                        {session.status}
                        {session.status === 'REVIEWED' && <span className="text-lg">→</span>}
                      </div>

                      {session.status === 'REVIEWED' && (
                        <span className="text-sm text-gray-500 whitespace-nowrap">
                          Analyzed: {getRelativeTime(session.updated_at)}
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
      <NavBar />
    </div>
  );
}

export default Sessions;
