import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SessionCard from './SessionCard';
import NavBar from '../../components/ui/NavBar';
import sessionService from '../../services/sessionService';
import Header from '../../components/ui/Header';
import StatsOverview from '../../components/dashboard/StatsOverview';
import TeamsList from '../../components/dashboard/TeamList';    
import TeamMembersModal from '../../components/TeamMembersModal';
import SessionList from '../../components/dashboard/SessionList';
import teamService from '../../services/teamService';
import Feedback from '../../components/ui/Feedback';
import DatabaseOverview from '../../components/dashboard/DatabaseOverview';

function CompanyDashboard() {
    const navigate = useNavigate();
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [view, setView] = useState('PENDING');
    const [sortOrder, setSortOrder] = useState('oldest');
    const [showTeamMembers, setShowTeamMembers] = useState(false);
    const [selectedTeam, setSelectedTeam] = useState(null);
    const [teamMembers, setTeamMembers] = useState([]);
    const [teamsWithValidSessions, setTeamsWithValidSessions] = useState([]);
    const [feedback, setFeedback] = useState(null);
    const [activeView, setActiveView] = useState('sessions');
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [teamToDelete, setTeamToDelete] = useState(null);
    const [selectedTeamObj, setSelectedTeamObj] = useState(null);
    const user = JSON.parse(localStorage.getItem('user'));

    const organizedSessions = {
        pending: sessions.filter(s => s.status === 'PENDING')
            .sort((a, b) => {
                const dateA = new Date(a.created_at);
                const dateB = new Date(b.created_at);
                return sortOrder === 'oldest' ? dateA - dateB : dateB - dateA;
            }),
        completed: sessions.filter(s => s.status === 'REVIEWED')
            .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    };

    useEffect(() => {
        const user = JSON.parse(localStorage.getItem('user'));
        if (!user || user.role !== 'COMPANY_MEMBER') {
            navigate('/');
            return;
        }
        fetchSessions();
        fetchTeamsWithValidSessions();  
    }, [navigate]);

    useEffect(() => {
        if (feedback) {
            const timer = setTimeout(() => {
                setFeedback(null);
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [feedback]);

    const fetchSessions = async () => {
        try {
            const data = await sessionService.getAllSessions();
            setSessions(data);
        } catch (err) {
            setError('Failed to fetch sessions');
        } finally {
            setLoading(false);
        }
    };

    const fetchTeamsWithValidSessions = async () => {
        try {
            const data = await sessionService.getTeamsWithValidSessions();
            setTeamsWithValidSessions(data);
        } catch (err) {
            setError('Failed to fetch teams with valid sessions');
        }   
    };

    const fetchTeamMembers = async (teamId, teamName) => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL}/teams/${teamId}/members`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch team members');
            }
            
            const data = await response.json();
            setTeamMembers(data);
            setSelectedTeam(teamName);
            setSelectedTeamObj({ id: teamId, name: teamName, is_admin: true });
            setShowTeamMembers(true);
        } catch (err) {
            console.error('Error fetching team members:', err);
            setFeedback({
                type: 'error',
                message: 'Failed to fetch team members'
            });
        }
    };

    const handleDeleteTeam = async (teamId) => {
        try {
            await teamService.deleteTeam(teamId);
            setTeamsWithValidSessions(prev => prev.filter(team => team.id !== teamId));
            setShowDeleteConfirm(false);
            setTeamToDelete(null);
            setFeedback({
                type: 'success',
                message: 'Team deleted successfully'
            });
        } catch (err) {
            console.error('Failed to delete team:', err);
            setFeedback({
                type: 'error',
                message: 'Failed to delete team'
            });
        }
    };

    const handleRemoveMember = async (teamId, userId) => {
        if (window.confirm('Are you sure you want to remove this member from the team?')) {
            try {
                await teamService.removeTeamMember(teamId, userId);
                await fetchTeamMembers(teamId, selectedTeam);
                setShowTeamMembers(false);
                setFeedback({
                    type: 'success',
                    message: 'Team member removed successfully'
                });
            } catch (err) {
                console.error('Remove member error:', err);
                setFeedback({
                    type: 'error',
                    message: 'Failed to remove team member'
                });
            }
        }
    };

    if (loading) return <div className="p-5">Loading sessions...</div>;
    if (error) return <div className="p-5 text-red-500">{error}</div>;

    return (
        <div className="min-h-screen bg-gray-900 text-white pb-20">
            <div className="max-w-7xl mx-auto p-4 md:p-8">
                {feedback && (
                    <div className="fixed top-4 right-4 z-50">
                        <Feedback type={feedback.type} message={feedback.message} />
                    </div>
                )}
                <StatsOverview />

                <div className="flex gap-4 mb-6">
                    <button 
                        onClick={() => navigate('/dashboard')}
                        className="px-4 py-2 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700"
                    >
                        Switch to User Dashboard
                    </button>
                    <button
                        onClick={() => setActiveView('sessions')}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                            activeView === 'sessions' 
                            ? 'bg-gray-600 text-white' 
                            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                        }`}
                    >
                        Session Management
                    </button>
                    <button
                        onClick={() => setActiveView('teams')}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                            activeView === 'teams' 
                            ? 'bg-gray-600 text-white' 
                            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                        }`}
                    >
                        Team Management
                    </button>
                    <button
                        onClick={() => setActiveView('database')}
                        className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                            activeView === 'database' 
                            ? 'bg-gray-600 text-white' 
                            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                        }`}
                    >
                        Database Overview
                    </button>
                </div>

                {activeView === 'teams' && (
                    <div className="mt-6">
                        <TeamsList 
                            teams={teamsWithValidSessions} 
                            onTeamClick={fetchTeamMembers}
                            onDeleteClick={(teamId) => {
                                setTeamToDelete(teamId);
                                setShowDeleteConfirm(true);
                            }}
                        />
                    </div>
                )}

                {activeView === 'sessions' && (
                    <div className="mt-6">
                        <SessionList 
                            sessions={sessions}
                            view={view}
                            setView={setView}
                            sortOrder={sortOrder}
                            setSortOrder={setSortOrder}
                        />
                    </div>
                )}

                {activeView === 'database' && (
                    <div className="mt-6">
                        <DatabaseOverview />
                    </div>
                )}
            </div>
            <NavBar />
            {showTeamMembers && selectedTeamObj && (
                <TeamMembersModal
                    team={selectedTeamObj}
                    members={teamMembers}
                    onClose={() => setShowTeamMembers(false)}
                    onRemoveMember={handleRemoveMember}
                    userEmail={user?.email}
                />
            )}
            {showDeleteConfirm && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-gray-800 p-6 rounded-lg max-w-md w-full mx-4">
                        <h3 className="text-xl font-bold mb-4">Delete Team</h3>
                        <p className="text-gray-300 mb-6">Are you sure you want to delete this team? This action cannot be undone.</p>
                        <div className="flex justify-end gap-4">
                            <button
                                onClick={() => {
                                    setShowDeleteConfirm(false);
                                    setTeamToDelete(null);
                                }}
                                className="px-4 py-2 rounded bg-gray-700 hover:bg-gray-600"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => handleDeleteTeam(teamToDelete)}
                                className="px-4 py-2 rounded bg-red-500 hover:bg-red-600"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

// Helper functions
function getDaysWaiting(createdAt) {
    const days = Math.floor((new Date() - new Date(createdAt)) / (1000 * 60 * 60 * 24));
    return days;
}

function getTurnaroundTime(createdAt, completedAt) {
    const hours = Math.floor((new Date(completedAt) - new Date(createdAt)) / (1000 * 60 * 60));
    return `${hours}h`;
}

function getSourceType(url) {
    if (url.includes('veo')) return '🎥 Veo';
    if (url.includes('youtube')) return '📺 YouTube';
    return '🔗 Other';
}

export default CompanyDashboard;