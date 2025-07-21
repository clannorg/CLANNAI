import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import sessionService from '../services/sessionService';
import NavBar from '../components/ui/NavBar';
import SpiderChart from '../components/SpiderChart';
import clannLogo from '../assets/images/clann.ai-white.png';

function SessionDetails() {
    const [user, setUser] = useState(null);
    const navigate = useNavigate();
    const { id } = useParams();
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedImage, setExpandedImage] = useState(null);

    useEffect(() => {
        const userData = JSON.parse(localStorage.getItem('user'));
        if (!userData) {
            navigate('/');
            return;
        }
        setUser(userData);
    }, [navigate]);

    useEffect(() => {
        const fetchSession = async () => {
            try {
                const data = await sessionService.getSessionDetails(id);
                setSession(data);
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };
        fetchSession();
    }, [id]);

    const handleDelete = async () => {
        if (window.confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
            try {
                await sessionService.deleteSession(id);
                navigate('/');
            } catch (err) {
                console.error('Error deleting session:', err);
            }
        }
    };

    if (loading) return <div className="p-8 text-white">Loading...</div>;
    if (error) return <div className="p-8 text-white">Error: {error}</div>;
    if (!session) return <div className="p-8 text-white">Session not found</div>;

    const metricOrder = ['total_distance', 'energy', 'total_sprints', 'sprint_distance', 'avg_sprint_speed'];
    const metricLabels = {
        energy: 'Energy',
        total_sprints: 'Total Sprints',
        total_distance: 'Total Distance',
        sprint_distance: 'Sprint Distance',
        avg_sprint_speed: 'Av Sprint Speed'  // Updated label
    };

    const metricExplanations = {
        total_distance: "Total distance covered by the team during the game",
        energy: "Overall energy expenditure based on movement intensity",
        total_sprints: "Number of high-intensity running actions",
        sprint_distance: "Total distance covered in sprint actions",
        avg_sprint_speed: "Average speed during sprint actions"
    };

    const isWinningMetric = (metric, team1Value, team2Value) => {
        if (team1Value === team2Value) return null;
        return team1Value > team2Value;
    };

    return (
        <div className="min-h-screen bg-gray-800/50">
            {/* Fixed Header - responsive */}
            <div className="fixed top-0 left-0 right-0 z-50 bg-gray-800/95 backdrop-blur-sm border-b border-gray-700/50">
                <div className="max-w-7xl mx-auto px-4 sm:px-8 py-4 flex justify-between items-center">
                    <button 
                        onClick={() => navigate('/dashboard')}
                        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                    >
                        <span>←</span>
                        <span>Back to Dashboard</span>
                    </button>
                    <img src={clannLogo} alt="Clann" className="h-6" />
                </div>
            </div>

            <div className="relative min-h-screen">
                {/* Add padding-top to account for fixed header */}
                <div className="max-w-7xl mx-auto px-4 sm:px-8 pt-24">
                    {/* Score Section - responsive */}
                    <div className="mb-8 sm:mb-12">
                        <div className="flex flex-col items-center">
                            <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-8 mb-2">
                                <div className="flex items-center gap-2">
                                    <div 
                                        className="w-4 h-4 rounded-md border border-white/30" 
                                        style={{ backgroundColor: session.team_color || '#D1FB7A' }}
                                    />
                                    <span className="text-lg sm:text-xl font-semibold text-white">
                                        {session.session_data?.match_info?.team1?.name}
                                    </span>
                                </div>
                                <div className="text-2xl sm:text-4xl font-bold flex items-center gap-4">
                                    <span className="text-white">
                                        {session.session_data?.match_info?.score?.team1 || '-'}
                                    </span>
                                    <span className="text-gray-400">-</span>
                                    <span className="text-white">{session.session_data?.match_info?.score?.team2 || '-'}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-4 h-4 rounded-md bg-[#B9E8EB]" />
                                    <span className="text-lg sm:text-xl font-semibold text-white">
                                        {session.session_data?.match_info?.team2?.name}
                                    </span>
                                </div>
                            </div>
                            <div className="flex items-center gap-2 text-gray-400 text-sm">
                                <span>{new Date(session.created_at).toLocaleDateString()}</span>
                                <span>•</span>
                                <span>{getSourceType(session.footage_url)} Footage</span>
                            </div>
                        </div>
                    </div>

                    {/* Only show delete button for admins */}
                    {user?.is_admin && (
                        <div className="flex justify-center">
                            <button
                                onClick={handleDelete}
                                className="text-red-400 hover:text-red-300 text-sm"
                            >
                                Delete Session
                            </button>
                        </div>
                    )}

                    {/* Stats Section - responsive grid */}
                    {session.session_data && (
                        <div className="mb-8 sm:mb-12">
                            <div className="flex flex-col sm:flex-row sm:items-start gap-6 sm:gap-8">
                                {/* Team 1 Stats */}
                                <div className="w-full sm:w-1/4">
                                    <div className="flex items-center gap-2 mb-4">
                                        <div 
                                            className="w-4 h-4 rounded-md border border-white/30" 
                                            style={{ backgroundColor: session.team_color || '#D1FB7A' }}
                                        />
                                        <h3 className="text-lg font-semibold text-white">
                                            {session.session_data.match_info.team1.name}
                                        </h3>
                                    </div>
                                    <div className="grid grid-cols-2 sm:grid-cols-1 gap-3">
                                        {Object.entries(session.session_data.match_info.team1.metrics).map(([key, value]) => (
                                            <div key={key} className="flex items-center gap-3">
                                                <div className="flex-grow mb-3 bg-gray-800/50 p-3 sm:p-4 rounded-lg border border-gray-700/50">
                                                    <div className="relative group">
                                                        <div className="text-sm text-gray-400">
                                                            {key.replace(/_/g, ' ')}
                                                        </div>
                                                        <div 
                                                            className="text-lg font-bold text-white" 
                                                        >
                                                            {typeof value === 'number' ? value.toFixed(1) : value}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Spider Chart - responsive */}
                                <div className="w-full sm:w-2/4 mb-6 sm:mb-0">
                                    <div className="bg-gray-800/50 p-4 rounded-lg border border-gray-700/50 h-full flex flex-col">
                                        <h3 className="text-lg font-semibold mb-4 text-white text-center">Performance Comparison</h3>
                                        <div className="flex-grow flex justify-center items-center">
                                            <SpiderChart 
                                                sessionData={session.session_data}
                                                colors={{ team1: "#D1FB7A", team2: "#B9E8EB" }}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Team 2 Stats */}
                                <div className="w-full sm:w-1/4">
                                    <div className="flex items-center gap-2 mb-4">
                                        <div className="w-4 h-4 rounded-md bg-[#B9E8EB]" />
                                        <h3 className="text-lg font-semibold text-white">
                                            {session.session_data.match_info.team2.name}
                                        </h3>
                                    </div>
                                    <div className="grid grid-cols-2 sm:grid-cols-1 gap-3">
                                        {Object.entries(session.session_data.match_info.team2.metrics).map(([key, value]) => (
                                            <div key={key} className="flex items-center gap-3">
                                                <div className="flex-grow mb-3 bg-gray-800/50 p-3 sm:p-4 rounded-lg border border-gray-700/50">
                                                    <div className="relative group">
                                                        <div className="text-sm text-gray-400">
                                                            {key.replace(/_/g, ' ')}
                                                        </div>
                                                        <div className="text-lg font-bold text-white">
                                                            {typeof value === 'number' ? value.toFixed(1) : value}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* After Performance Analysis Section */}
                    <div className="w-full h-px bg-gray-700/50 my-12" />

                    {/* Analysis Images Section */}
                    <div className="mb-12">
                        <h2 className="text-xl font-semibold mb-6 text-white">Analysis</h2>
                        {(session.analysis_image1_url || session.analysis_image2_url || session.analysis_image3_url) && (
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                                {[
                                    { type: 'HEATMAP', icon: '🔥', url: session.analysis_image1_url },
                                    { type: 'SPRINT MAP', icon: '⚡', url: session.analysis_image2_url },
                                    { type: 'GAME MOMENTUM', icon: '📈', url: session.analysis_image3_url }
                                ].map(analysis => analysis.url && (
                                    <div key={analysis.type}
                                        className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50 hover:border-blue-500/30 transition-all">
                                        <div className="flex items-center gap-3 mb-4">
                                            <span className="text-2xl">{analysis.icon}</span>
                                            <h3 className="text-xl text-white">{analysis.type}</h3>
                                        </div>
                                        <div onClick={() => setExpandedImage(analysis.url)} className="cursor-zoom-in">
                                            <img src={analysis.url}
                                                alt={analysis.type}
                                                className="w-full h-auto object-contain rounded-lg bg-black/30 transition-transform hover:scale-105" />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* After Analysis Section */}
                    <div className="w-full h-px bg-gray-700/50 my-12" />

                    {/* Highlights Section */}
                    <div className="mb-12">
                        <h2 className="text-xl font-semibold mb-6 text-white">Highlights</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
                            {[1, 2, 3, 4, 5].map(index => {
                                const videoUrl = session[`analysis_video${index}_url`];
                                return videoUrl && (
                                    <div key={index}
                                        className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50 hover:border-purple-500/30 
                                                  transition-all transform hover:-translate-y-1">
                                        <div className="flex items-center gap-3 mb-4">
                                            <span className="text-2xl">🎬</span>
                                            <h3 className="text-xl text-white">Highlight {index}</h3>
                                        </div>
                                        <div className="bg-black/30 rounded-lg overflow-hidden">
                                            <video 
                                                controls 
                                                className="w-full h-auto"
                                            >
                                                <source src={videoUrl} type="video/mp4" />
                                                Your browser does not support the video tag.
                                            </video>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
                <NavBar />
            </div>
            {expandedImage && (
                <div 
                    className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 cursor-pointer"
                    onClick={() => setExpandedImage(null)}
                >
                    <img 
                        src={expandedImage} 
                        alt="Enlarged view"
                        className="max-w-[90%] max-h-[90vh] object-contain"
                    />
                </div>
            )}
        </div>
    );
}

// Helper function from Sessions.js
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

export default SessionDetails; 