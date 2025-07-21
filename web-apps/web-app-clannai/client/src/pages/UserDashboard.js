import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import sessionService from '../services/sessionService';
import teamService from '../services/teamService';
import authService from '../services/authService';
import Header from '../components/ui/Header';
import clannLogo from '../assets/images/clann.ai-green.png';
import playerIcon from '../assets/images/icon-player.png';
import MatchesSection from '../components/MatchesSection';
import TeamPage from '../components/TeamPage';
import { loadStripe } from '@stripe/stripe-js';
import SubscriptionManager from '../components/SubscriptionManager';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY);

function UserDashboard() {
  const [activeTab, setActiveTab] = useState('matches');
  const [user, setUser] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [teamMembers, setTeamMembers] = useState({});
  const [feedback, setFeedback] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [url, setUrl] = useState('');
  const [teamName, setTeamName] = useState('');
  const [teamCode, setTeamCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [teamColor, setTeamColor] = useState('#D1FB7A'); // Clann light green default
  const [teamStatus, setTeamStatus] = useState({ isPremium: false, status: 'FREE' });
  const [teamDetails, setTeamDetails] = useState(null);
  const [statusChecked, setStatusChecked] = useState(false);
  const [selectedTeamId, setSelectedTeamId] = useState(null);
  const navigate = useNavigate();

  const fetchTeamStatus = async () => {
    if (statusChecked) return;
    
    try {
        const currentTeam = sessions.find(s => s.team_name !== 'ClannAI demo');
        console.log('1. Current non-demo team:', currentTeam);
        if (!currentTeam?.team_id) return;

        const response = await fetch(`${process.env.REACT_APP_API_URL}/create-checkout-session`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                teamId: currentTeam.team_id,
                teamName: currentTeam.team_name
            })
        });
        
        const data = await response.json();
        console.log('2. Response status:', response.status);
        console.log('3. Response data:', data);
        
        if (response.status === 400 && data.error === 'Team already has an active subscription') {
            console.log('4a. Setting team status to PREMIUM');
            setTeamStatus({
                isPremium: true,
                status: 'PREMIUM'
            });
        } else {
            console.log('4b. Setting team status to FREE');
            setTeamStatus({
                isPremium: false,
                status: 'FREE'
            });
        }
        setStatusChecked(true);
    } catch (err) {
        console.error('Error fetching team status:', err);
        setTeamStatus({ isPremium: false, status: 'FREE' });
    }
  };

  useEffect(() => {
    console.log('Sessions changed:', sessions);
    if (sessions.length > 0 && !statusChecked) {
        fetchTeamStatus();
    }
  }, [sessions, statusChecked]);

  useEffect(() => {
    console.log('Team status changed to:', teamStatus);
  }, [teamStatus]);

  const fetchTeamDetails = async () => {
    try {
      if (!user?.teamId) {
        setTeamDetails(null);
        return;
      }

      const response = await fetch(`${process.env.REACT_APP_API_URL}/teams/${user.teamId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch team details');
      }
      
      const data = await response.json();
      setTeamDetails(data);
      setTeamName(data.name);
    } catch (err) {
      setTeamDetails(null);
    }
  };

  useEffect(() => {
    const userData = JSON.parse(localStorage.getItem('user'));
    if (!userData) {
      navigate('/');
      return;
    }
    setUser(userData);
    
    const initializeData = async () => {
      await fetchTeamDetails();
      await fetchSessions();
      if (activeTab === 'team') {
        await fetchTeamMembers();
      }
    };

    initializeData();
  }, [navigate, activeTab]);

  const fetchSessions = async () => {
    try {
      const data = await sessionService.getSessions();
      const sessionsWithData = await Promise.all(
        data.map(async (session) => {
          const details = await sessionService.getSessionDetails(session.id);
          return {
            ...session,
            session_data: details.session_data
          };
        })
      );
      setSessions(sessionsWithData);
    } catch (err) {
      setSessions([]);
    }
  };

  const fetchTeamMembers = async (teamId) => {
    try {
        // Skip for demo team or if no teamId provided
        if (!teamId || teamId === 'ClannAI demo') {
            return;
        }

        const members = await teamService.getTeamMembers(teamId);
        setTeamMembers(prev => ({
            ...prev,
            [teamId]: members
        }));
    } catch (err) {
        console.error('Failed to fetch team members:', err);
    }
  };

  // Add effect to fetch team members when selected team changes
  useEffect(() => {
    if (selectedTeamId) {
        fetchTeamMembers(selectedTeamId);
    }
  }, [selectedTeamId]);

  // Add effect to update team color when selected team changes
  useEffect(() => {
    if (selectedTeamId) {
      const selectedTeam = sessions.find(s => s.team_id === selectedTeamId);
      if (selectedTeam?.team_color) {
        setTeamColor(selectedTeam.team_color);
      }
    }
  }, [selectedTeamId, sessions]);

  useEffect(() => {
    const currentTeam = sessions.find(s => s.team_name !== 'ClannAI demo');
    if (currentTeam?.team_id) {
        fetchTeamMembers(currentTeam.team_id);
    }
  }, [sessions]);

  // Add new effect to fetch team members for all teams
  useEffect(() => {
    const fetchAllTeamMembers = async () => {
      const nonDemoTeams = sessions.filter(s => s.team_name !== 'ClannAI demo');
      for (const team of nonDemoTeams) {
        await fetchTeamMembers(team.team_id);
      }
    };
    
    if (sessions.length > 0) {
      fetchAllTeamMembers();
    }
  }, [sessions]);

  const getAdminTeams = () => {
    // Get all teams the user is a member of (not just admin teams)
    const userTeams = sessions
      .filter(s => s.team_name !== 'ClannAI demo' && 
        teamMembers[s.team_id]?.some(member => 
          member.email === user?.email
        )
      );
    
    // Then filter for unique team names
    return [...new Map(
      userTeams.map(team => [team.team_name, team])
    ).values()];
  };

  // Check if current user is admin of the selected team
  const isCurrentUserAdmin = () => {
    if (!selectedTeamId || !user?.email) return false;
    const members = teamMembers[selectedTeamId] || [];
    return members.some(member => member.email === user.email && member.is_admin);
  };

  // Handle removing a team member
  const handleRemoveMember = async (memberId, memberEmail) => {
    if (!selectedTeamId || !isCurrentUserAdmin()) return;
    
    // Ask for confirmation before removing
    if (!window.confirm(`Are you sure you want to remove ${memberEmail} from the team?`)) {
      return; // User cancelled the operation
    }
    
    try {
      setIsLoading(true);
      
      // Optimistically update UI by removing the member from the list
      const currentMembers = teamMembers[selectedTeamId] || [];
      const updatedMembers = currentMembers.filter(member => member.user_id !== memberId);
      
      // Update state immediately for responsive UI
      setTeamMembers(prev => ({
        ...prev,
        [selectedTeamId]: updatedMembers
      }));
      
      // Then make the API call with both teamId and memberId
      await teamService.removeTeamMember(selectedTeamId, memberId);
      
      // Refresh the team members list to ensure UI is in sync with server
      const refreshedMembers = await teamService.getTeamMembers(selectedTeamId);
      setTeamMembers(prev => ({
        ...prev,
        [selectedTeamId]: refreshedMembers
      }));
      
      // Show success message
      setFeedback({
        type: 'success',
        message: `${memberEmail} was removed from the team`
      });
      
    } catch (err) {
      console.error('Error removing team member:', err);
      
      // If there's an error, revert the UI change by fetching the current members
      try {
        const currentMembers = await teamService.getTeamMembers(selectedTeamId);
        setTeamMembers(prev => ({
          ...prev,
          [selectedTeamId]: currentMembers
        }));
      } catch (fetchErr) {
        console.error('Error fetching team members after failed removal:', fetchErr);
      }
      
      setFeedback({
        type: 'error',
        message: err.message || 'Failed to remove team member'
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const adminTeams = getAdminTeams();
    if (adminTeams.length > 0 && !selectedTeamId) {
      setSelectedTeamId(adminTeams[0].team_id);
    }
  }, [sessions, teamMembers, user]);

  const getSelectedTeam = () => {
    return sessions.find(s => s.team_id === selectedTeamId);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setFeedback(null);

    if (!url.trim() || !teamName.trim()) {
        setFeedback({
            type: 'error',
            message: 'Please fill in all fields'
        });
        setIsLoading(false);
        return;
    }

    try {
        // Normal upload flow
        const response = await sessionService.createSession(url.trim(), teamName.trim(), teamColor);
        await fetchSessions();
        
        // Set the selected team to the newly created team
        setSelectedTeamId(response.team_id);
        
        // Show success message
        setFeedback({
            type: 'success',
            message: (
                <div className="flex flex-col gap-4">
                    <p>Success! Your team code is: <span className="font-bold">{response.team_code}</span></p>
                    <button
                        onClick={() => copyInviteMessage(response.team_code, teamName)}
                        className="text-sm px-4 py-2 bg-green-500/20 text-green-400 rounded-lg border border-green-500 hover:bg-green-500/30 transition-colors"
                    >
                        📋 Copy Invite Message
                    </button>
                </div>
            )
        });

        // Reset form
        setUrl('');
        setTeamName('');
        setShowUploadModal(false);

        // Automatically trigger upgrade right after successful upload
        handleTrialUpgrade();

    } catch (err) {
        console.error('Upload error:', err);
        setFeedback({
            type: 'error',
            message: err.message || 'Failed to upload match'
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
      setFeedback(null);

      console.log('Attempting to join team with code:', teamCode.trim());
      
      // Join team and wait for response
      const response = await teamService.joinTeam(teamCode.trim());
      console.log('Join team response:', response);
      
      // If we get here, the join was successful
      // Set the selected team to the newly joined team
      if (response?.team_id) {
        console.log('Setting selected team to:', response.team_id);
        setSelectedTeamId(response.team_id);
        
        // Try to refresh the data
        try {
          console.log('Refreshing sessions and user data...');
          await Promise.all([
            fetchSessions(),
            authService.getCurrentUser().then(setUser)
          ]);
        } catch (refreshError) {
          console.warn('Data refresh error:', refreshError);
          // Continue even if refresh fails
        }
        
        // Show success message
        setFeedback({
          type: 'success',
          message: `Successfully joined ${response.team_name || 'the team'}`
        });
        
        setTeamCode('');
        setShowJoinModal(false);
      } else {
        console.error('Invalid team response:', response);
        throw new Error('Invalid team response');
      }
      
    } catch (err) {
      console.error('Join team error:', err);
      console.error('Error details:', {
        message: err.message,
        response: err.response,
        data: err.response?.data
      });

      // If we have the team info despite the error, still show success
      if (err.response?.data?.team_id) {
        console.log('Found team ID in error response:', err.response.data.team_id);
        setSelectedTeamId(err.response.data.team_id);
        setFeedback({
          type: 'success',
          message: `Successfully joined the team`
        });
        setTeamCode('');
        setShowJoinModal(false);
      } else {
        setFeedback({
          type: 'error',
          message: err.message || 'Failed to join team. Please check your team code.'
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/');
  };

  const handleDeleteAccount = async () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      try {
        await authService.deleteAccount();
        localStorage.removeItem('user');
        navigate('/');
      } catch (err) {
        setFeedback({
          type: 'error',
          message: 'Failed to delete account'
        });
      }
    }
  };

  const generateInviteMessage = (teamCode, teamName) => {
    return `🎮 Join "${teamName}" on Clann AI!\n\n` +
      `To join:\n` +
      `1. Go to https://clannai.com\n` +
      `2. Create an account\n` +
      `3. Click "Join Team"\n` +
      `4. Enter team code: ${teamCode}`;
  };

  const copyInviteMessage = (teamCode, teamName) => {
    const message = generateInviteMessage(teamCode, teamName);
    navigator.clipboard.writeText(message);
    setFeedback({
      type: 'success',
      message: 'Invite message copied to clipboard!'
    });
  };

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedFile(reader.result);
        // Here you would typically upload to your server
        // For now, we'll just store in localStorage
        localStorage.setItem('userProfileImage', reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadModalOpen = () => {
    if (sessions.length > 0) {
        const nonDemoSession = sessions.find(session => session.team_name !== 'ClannAI demo');
        if (nonDemoSession) {
            setTeamName(nonDemoSession.team_name);
        } else {
            setTeamName('');
        }
    }
    setShowUploadModal(true);
  };

  // Add color options
  const colorOptions = [
    { name: 'Clann Green', value: '#D1FB7A' },
    { name: 'Clann Blue', value: '#B9E8EB' },
    { name: 'Red', value: '#FF6B6B' },
    { name: 'Orange', value: '#FFB067' },
    { name: 'Purple', value: '#B197FC' },
    { name: 'Yellow', value: '#FFE066' },
  ];

  const handleColorChange = (color) => {
    setTeamColor(color);
  };

  const handleTrialUpgrade = async () => {
    try {
        const currentTeam = sessions.find(s => s.team_name !== 'ClannAI demo');
        if (!currentTeam?.team_id) {
            throw new Error('No team selected');
        }

        const stripe = await stripePromise;
        if (!stripe) throw new Error('Failed to initialize Stripe');

        const response = await fetch(`${process.env.REACT_APP_API_URL}/create-checkout-session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                teamId: currentTeam.team_id,
                teamName: currentTeam.team_name,
                metadata: {
                    teamId: currentTeam.team_id,
                    teamName: currentTeam.team_name
                },
                fromTrial: true,  // Add this flag to indicate it's a trial conversion
                price: 7500
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to create checkout session');
        }

        const data = await response.json();
        const { error } = await stripe.redirectToCheckout({ 
            sessionId: data.id
        });
        
        if (error) throw error;

    } catch (err) {
        console.error('Upgrade error:', err);
        setFeedback({
            type: 'error',
            message: err.message || 'Failed to process upgrade'
        });
    }
  };

  const handleUpgradeClick = async () => {
    const currentTeam = sessions.find(s => s.team_name !== 'ClannAI demo');
    if (!currentTeam?.team_id) {
      setFeedback({
        type: 'error',
        message: 'Please create a team first to upgrade to Premium'
      });
      return;
    }
    handleTrialUpgrade();
  };

  return (
    <div className="min-h-screen bg-[#F7F6F1]">
      {/* Top Navigation - Responsive redesign */}
      <nav className="border-b border-gray-200/10 bg-white">
        <div className="max-w-7xl mx-auto px-4 py-4">
          {/* Mobile layout - stacked vertically */}
          <div className="flex flex-col items-center md:flex-row md:justify-between md:items-center">
            {/* Logo - centered on mobile, left-aligned on desktop */}
            <div className="mb-4 md:mb-0">
              <img src={clannLogo} alt="Clann" className="h-8" />
            </div>
            
            {/* Action buttons - stacked on mobile, horizontal on desktop */}
            <div className="flex flex-col w-full md:flex-row md:w-auto md:items-center gap-3 md:gap-4">
              <button 
                onClick={handleUploadModalOpen}
                className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium w-full md:w-auto"
              >
                Upload Match
              </button>
              
              <button 
                onClick={() => setShowJoinModal(true)}
                className="border border-gray-300 text-gray-700 px-6 py-2.5 rounded-lg font-medium w-full md:w-auto"
              >
                Join Team
              </button>
              
              <button 
                onClick={() => setShowSettingsModal(true)}
                className="flex items-center justify-center gap-2 text-gray-700 px-6 py-2.5 rounded-lg font-medium border border-gray-300 w-full md:w-auto"
              >
                <span>Settings</span>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Tab Navigation - centered tabs */}
      <div className="bg-white border-b border-gray-200/10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-center overflow-x-auto scrollbar-hide">
            <button
              onClick={() => setActiveTab('matches')}
              className={`px-8 py-3 font-medium text-sm whitespace-nowrap ${
                activeTab === 'matches'
                  ? 'text-[#016F32] border-b-2 border-[#016F32]'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Matches
            </button>
            <button
              onClick={() => setActiveTab('team')}
              className={`px-8 py-3 font-medium text-sm whitespace-nowrap ${
                activeTab === 'team'
                  ? 'text-[#016F32] border-b-2 border-[#016F32]'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Team
            </button>
          </div>
        </div>
      </div>

      {/* User Profile Section */}
      <div className="max-w-7xl mx-auto px-8 py-12">
        <div className="flex items-center gap-6 mb-12">
          <div className="flex items-center gap-8">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                {sessions.find(s => s.team_name !== 'ClannAI demo')?.team_name || 
                  <div className="flex items-center gap-2 text-gray-500">
                    Upload footage to create a team
                    <button 
                      onClick={handleUploadModalOpen}
                      className="text-sm px-3 py-1 bg-[#016F32]/10 text-[#016F32] rounded-lg hover:bg-[#016F32]/20"
                    >
                      Upload Now →
                    </button>
                  </div>
                }
                <span 
                  onClick={handleUpgradeClick}
                  className={`ml-2 px-2 py-1 text-sm rounded-full ${
                    teamStatus.isPremium 
                      ? 'bg-green-400/10 text-green-400' 
                      : 'bg-gray-400/10 text-gray-400 hover:bg-green-400/10 hover:text-green-400 cursor-pointer'
                  }`}
                >
                  {teamStatus.isPremium ? '⭐️ PREMIUM' : 'FREE TIER - Upgrade'}
                </span>
              </h1>
              <div className="flex items-center gap-2 text-gray-600">
                <span>⚽</span>
                <div>
                  <p className="text-lg text-gray-500">Team Member:</p>
                  <p className="text-lg">{user?.email}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="space-y-4">
          {activeTab === 'matches' ? (
            <MatchesSection sessions={sessions} />
          ) : (
            <div className="bg-white rounded-xl shadow-sm">
              {/* Team Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-100">
                <h2 className="text-2xl font-bold">
                  {sessions.find(s => s.team_name !== 'ClannAI demo')?.team_name || 'Create Your Team'}
                </h2>
                {sessions.find(s => s.team_name !== 'ClannAI demo') && (
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <span>Team Color:</span>
                      <input 
                        type="color" 
                        value={teamColor}
                        onChange={(e) => setTeamColor(e.target.value)}
                        className="w-8 h-8 rounded cursor-pointer"
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Team Info Grid */}
              <div className="grid md:grid-cols-2 gap-6 p-6">
                {/* Invite Section */}
                {sessions.find(s => s.team_name !== 'ClannAI demo') ? (
                  <div className="bg-gray-50 rounded-lg p-6 h-fit">
                    <div className="flex flex-col sm:flex-row gap-3 mb-4">
                      <h3 className="text-lg font-semibold whitespace-nowrap">📨 Share With Your Team</h3>
                      {getAdminTeams().length > 0 && (
                        <select
                          value={selectedTeamId || ''}
                          onChange={(e) => setSelectedTeamId(e.target.value)}
                          className="w-full sm:w-auto px-3 py-1.5 bg-white border border-gray-300 rounded-md text-sm"
                        >
                          {getAdminTeams().map(team => (
                            <option key={team.team_id} value={team.team_id}>
                              {team.team_name}
                            </option>
                          ))}
                        </select>
                      )}
                    </div>
                    
                    {/* Team Code Display */}
                    <div className="bg-white p-4 rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-gray-600">Your Team Code:</span>
                        <code className="bg-gray-100 px-3 py-1 rounded text-lg font-mono font-bold">
                          {getSelectedTeam()?.team_code}
                        </code>
                      </div>
                      
                      {/* Preview Message */}
                      <div className="bg-gray-50 p-3 rounded-lg mb-3 text-sm text-gray-600">
                        <p className="font-medium mb-2">Invite Message Preview:</p>
                        <p className="whitespace-pre-line">
                          {generateInviteMessage(
                            getSelectedTeam()?.team_code,
                            getSelectedTeam()?.team_name
                          )}
                        </p>
                      </div>

                      <button
                        onClick={() => copyInviteMessage(
                          getSelectedTeam()?.team_code,
                          getSelectedTeam()?.team_name
                        )}
                        className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                      >
                        <span>📋</span>
                        Copy Invite Message
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4">🎮 Create Your Team</h3>
                    <div className="bg-white p-4 rounded-lg">
                      <div className="flex items-center gap-3 text-gray-600 mb-4">
                        <span className="text-xl">1</span>
                        <p>Click the "Upload Match" button at the top of the page</p>
                      </div>
                      <div className="flex items-center gap-3 text-gray-600 mb-4">
                        <span className="text-xl">2</span>
                        <p>Enter your team name and match URL</p>
                      </div>
                      <div className="flex items-center gap-3 text-gray-600 mb-4">
                        <span className="text-xl">3</span>
                        <p>Choose your team color</p>
                      </div>
                      <button
                        onClick={handleUploadModalOpen}
                        className="w-full bg-[#016F32] text-white py-2 rounded-lg hover:bg-[#016F32]/90 transition-colors flex items-center justify-center gap-2 mt-4"
                      >
                        Upload Your First Match
                      </button>
                    </div>
                  </div>
                )}

                {/* Members Section */}
                <div className="bg-gray-50 rounded-lg p-6 h-fit">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">Team Members</h3>
                  </div>
                  <div className="space-y-2">
                    {getSelectedTeam() ? (
                      <>
                        <div className="bg-white p-3 rounded-lg mb-3">
                          <p className="text-sm text-gray-600">Members in team:</p>
                          <p className="font-medium truncate max-w-full">{getSelectedTeam()?.team_name}</p>
                        </div>
                        <div className="max-h-[400px] overflow-y-auto">
                          {teamMembers[selectedTeamId]?.map(member => (
                            <div 
                              key={member.email} 
                              className="flex items-center p-3 bg-white rounded-lg mb-2"
                            >
                              <div className="w-8 h-8 flex-shrink-0 bg-gray-200 rounded-full flex items-center justify-center">
                                {member.email[0].toUpperCase()}
                              </div>
                              <div className="flex-1 min-w-0 mx-3">
                                <span className="truncate text-sm block">{member.email}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                {member.is_admin && (
                                  <span className="flex-shrink-0 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                    Admin
                                  </span>
                                )}
                                {/* Only show remove button if current user is admin and not for themselves */}
                                {isCurrentUserAdmin() && member.email !== user?.email && (
                                  <button
                                    onClick={() => handleRemoveMember(member.user_id, member.email)}
                                    className="flex-shrink-0 text-xs text-red-600 hover:text-red-800 p-1 rounded-full hover:bg-red-50"
                                    title="Remove member"
                                  >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                  </button>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </>
                    ) : (
                      <div className="p-4 bg-white rounded-lg">
                        <p className="text-gray-600 mb-2">No team members yet</p>
                        <p className="text-sm text-gray-500">Upload your first match to create a team and start inviting members.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      {/* Feedback Toast */}
      {feedback && (
        <div className={`fixed bottom-4 right-4 p-4 rounded-lg shadow-lg ${
          feedback.type === 'error' 
            ? 'bg-red-50 text-red-600'
            : 'bg-green-50 text-green-600'
        }`}>
          {feedback.message}
        </div>
      )}
      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Upload Match</h2>
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-600 mb-2">Match URL</label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter match URL"
                  className="w-full px-4 py-2 rounded-lg border"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-2">Team Name</label>
                <input
                  type="text"
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  placeholder="Enter team name"
                  className="w-full px-4 py-2 rounded-lg border"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-2">Team Color</label>
                <div className="flex flex-col gap-3">
                  <div className="flex gap-2 flex-wrap">
                    {colorOptions.map((color) => (
                      <button
                        key={color.value}
                        type="button"
                        onClick={() => handleColorChange(color.value)}
                        className={`w-8 h-8 rounded-full border-2 transition-all ${
                          teamColor === color.value 
                            ? 'border-gray-900 scale-110' 
                            : 'border-transparent hover:scale-105'
                        }`}
                        style={{ backgroundColor: color.value }}
                        title={color.name}
                      />
                    ))}
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <label className="text-sm text-gray-600">Custom color:</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="color"
                        value={teamColor}
                        onChange={(e) => handleColorChange(e.target.value)}
                        className="w-8 h-8 rounded cursor-pointer"
                      />
                      <span className="text-sm text-gray-600">{teamColor}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex justify-end gap-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowUploadModal(false);
                    setTeamColor('#D1FB7A'); // Reset to default when closing
                  }}
                  className="px-4 py-2 text-gray-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="bg-[#016F32] text-white px-6 py-2 rounded-lg font-medium disabled:opacity-50"
                >
                  {isLoading ? 'Uploading...' : 'Upload Match'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {/* Join Team Modal */}
      {showJoinModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Join Team</h2>
            <form onSubmit={handleJoinTeam} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-600 mb-2">Team Code</label>
                <input
                  type="text"
                  value={teamCode}
                  onChange={(e) => setTeamCode(e.target.value)}
                  placeholder="Enter team code"
                  className="w-full px-4 py-2 rounded-lg border"
                  required
                />
              </div>
              <div className="flex justify-end gap-4">
                <button
                  type="button"
                  onClick={() => setShowJoinModal(false)}
                  className="px-4 py-2 text-gray-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="bg-[#016F32] text-white px-6 py-2 rounded-lg font-medium disabled:opacity-50"
                >
                  {isLoading ? 'Joining...' : 'Join Team'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {/* Settings Modal */}
      {showSettingsModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
              <button
                onClick={() => setShowSettingsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            {/* Add email display */}
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Account Email</p>
              <p className="text-gray-900 font-medium">{user?.email}</p>
            </div>

            <SubscriptionManager 
              teamStatus={teamStatus}
              user={user}
              setFeedback={setFeedback}
              handleTrialUpgrade={handleTrialUpgrade}
            />

            <div className="space-y-4">
              <button
                onClick={handleLogout}
                className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg"
              >
                Sign Out
              </button>
              <button
                onClick={handleDeleteAccount}
                className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg"
              >
                Delete Account
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserDashboard; 