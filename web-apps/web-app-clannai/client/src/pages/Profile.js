import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import teamService from '../services/teamService';
import authService from '../services/authService';
import NavBar from '../components/ui/NavBar';
import TopNav from '../components/navigation/TopNav';
import api from '../services/api';
import TeamCard from '../components/TeamCard';
import TeamMembersModal from '../components/TeamMembersModal';

// Keep the stripePromise initialization:
const STRIPE_PUBLIC_KEY = process.env.REACT_APP_STRIPE_PUBLIC_KEY;
const stripePromise = loadStripe(STRIPE_PUBLIC_KEY);

// Add the generateShareMessage function
const generateShareMessage = (teamCode) => {
    const message = `🏃‍♂️ Join my team on Clann AI to see our game analysis!\n\n` +
        `1. Go to https://clannai.com\n` +
        `2. Create an account or sign in\n` +
        `3. Click "Join Team"\n` +
        `4. Enter team code: ${teamCode}\n\n` +
        `See you there! 🎮`;
    return message;
};

function Profile() {
    const navigate = useNavigate();
    const [teams, setTeams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [user, setUser] = useState(null);
    const [selectedTeam, setSelectedTeam] = useState(null);
    const [teamMembers, setTeamMembers] = useState({});
    const [membersLoading, setMembersLoading] = useState(false);
    const [feedback, setFeedback] = useState(null);
    const [removingMember, setRemovingMember] = useState(null);
    const [showMembersModal, setShowMembersModal] = useState(false);
    const [selectedTeamForMembers, setSelectedTeamForMembers] = useState(null);

    useEffect(() => {
        const userData = JSON.parse(localStorage.getItem('user'));
        if (!userData) {
            navigate('/');
            return;
        }
        setUser(userData);
        fetchTeams();
    }, [navigate]);

    useEffect(() => {
        if (feedback) {
            const timer = setTimeout(() => {
                setFeedback(null);
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [feedback]);

    useEffect(() => {
        if (teams.length > 0) {
            teams.forEach(team => {
                fetchTeamMembers(team.id);
            });
        }
    }, [teams]);

    const fetchTeams = async () => {
        try {
            const userTeams = await teamService.getUserTeams();
            setTeams(userTeams);
        } catch (err) {
            setError('Failed to load teams');
        } finally {
            setLoading(false);
        }
    };

    const fetchTeamMembers = async (teamId) => {
        setMembersLoading(true);
        try {
            // Update to check for ClannAI demo team ID
            const DEMO_TEAM_ID = '63bf8bce-72c4-4533-b090-e4c0be7c593e';

            if (teamId === DEMO_TEAM_ID) {
                setFeedback({
                    type: 'info',
                    message: 'Demo team members are private'
                });
                setShowMembersModal(false);
                setTeamMembers(prev => ({
                    ...prev,
                    [teamId]: []
                }));
                return;
            }

            const members = await teamService.getTeamMembers(teamId);
            setTeamMembers(prev => ({
                ...prev,
                [teamId]: members
            }));
        } catch (err) {
            setFeedback({
                type: 'error',
                message: err.message || 'Failed to fetch team members'
            });
            setShowMembersModal(false);
        } finally {
            setMembersLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        navigate('/');
    };

    const handleDeleteAccount = async () => {
        if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
            try {
                await authService.deleteAccount();
                localStorage.removeItem('user');
                localStorage.removeItem('token');
                navigate('/');
            } catch (err) {
                alert(err);
            }
        }
    };

    const handleUpgrade = async (teamId) => {
        try {
            // Get Stripe instance
            const stripe = await stripePromise;
            if (!stripe) {
                throw new Error('Failed to initialize Stripe');
            }

            // Create checkout session
            const response = await fetch(`${process.env.REACT_APP_API_URL}/create-checkout-session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ teamId }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Failed to create checkout session');
            }

            const { id: sessionId } = await response.json();

            // Redirect to checkout
            const { error } = await stripe.redirectToCheckout({ sessionId });

            if (error) {
                throw error;
            }
        } catch (error) {
            alert('Payment initialization failed: ' + error.message);
        }
    };

    const handleShare = async (teamCode) => {
        const message = generateShareMessage(teamCode);

        if (navigator.share) {
            try {
                await navigator.share({
                    title: 'Join my team on Clann AI',
                    text: message
                });
            } catch (err) {
                // Fallback to clipboard
                copyToClipboard(message);
            }
        } else {
            // Fallback to clipboard
            copyToClipboard(message);
        }
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text)
            .then(() => {
                setFeedback('Team code copied to clipboard!');
            })
            .catch(err => {
                setFeedback('Failed to copy team code');
            });
    };

    const handleRemoveMember = async (teamId, userId) => {
        if (window.confirm('Are you sure you want to remove this member?')) {
            try {
                await teamService.removeTeamMember(teamId, userId);
                fetchTeamMembers(teamId); // Refresh the list
                setFeedback('Team member removed successfully');
            } catch (err) {
                setFeedback(err.message || 'Failed to remove team member');
            }
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white pb-20">
            <TopNav 
                isLoggedIn={true} 
                onLogout={handleLogout} 
            />
            {feedback && (
                <div className={`mb-6 p-4 rounded-lg border ${
                    feedback.type === 'error'
                        ? 'bg-red-500/20 border-red-500/30 text-red-400'
                        : feedback.type === 'info'
                        ? 'bg-blue-500/20 border-blue-500/30 text-blue-400'
                        : 'bg-green-500/20 border-green-500/30 text-green-400'
                }`}>
                    {feedback.message}
                </div>
            )}
            <div className="max-w-7xl mx-auto px-4 py-4 md:p-8">
                {/* User Profile Card */}
                <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50 mb-8">
                    <div className="flex justify-between items-start">
                        <div>
                            <h2 className="text-2xl font-display text-transparent bg-clip-text 
                                         bg-gradient-to-r from-green-400 via-emerald-400 to-blue-500">
                                Your Profile
                            </h2>
                            <p className="text-lg text-gray-300 mt-2">{user?.email}</p>
                        </div>
                        <div className="space-x-4">
                            <button onClick={handleDeleteAccount}
                                className="px-4 py-2 bg-red-500/10 text-red-400 border border-red-500/30 
                                             rounded-lg hover:bg-red-500/20 transition-all">
                                Delete Account
                            </button>
                        </div>
                    </div>
                </div>

                {/* Teams Section */}
                <div className="space-y-6">
                    <h3 className="text-xl font-semibold">Your Teams</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {teams.map(team => (
                            <TeamCard
                                key={team.id}
                                team={team}
                                onUpgrade={handleUpgrade}
                                onShare={() => handleShare(team.team_code)}
                                onViewMembers={() => {
                                    if (team.team_code === 'STMARY') {
                                        setFeedback({
                                            type: 'info',
                                            message: 'Demo team members are private'
                                        });
                                        return;
                                    }
                                    setSelectedTeamForMembers(team);
                                    fetchTeamMembers(team.id);
                                    setShowMembersModal(true);
                                }}
                                members={teamMembers[team.id]}
                            />
                        ))}
                    </div>
                </div>
            </div>
            {showMembersModal && selectedTeamForMembers && (
                <TeamMembersModal
                    team={selectedTeamForMembers}
                    members={selectedTeamForMembers.team_code === 'STMARY'
                        ? []
                        : teamMembers[selectedTeamForMembers.id]
                    }
                    onClose={() => setShowMembersModal(false)}
                    onRemoveMember={handleRemoveMember}
                    userEmail={user?.email}
                />
            )}
            <NavBar />
        </div>
    );
}

export default Profile;
