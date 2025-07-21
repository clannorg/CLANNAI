import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import sessionService from '../../services/sessionService';
import TeamMetricsForm from '../../components/TeamMetricsForm';
import SessionDataUpload from '../../components/SessionDataUpload';

function SessionAnalysis() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [session, setSession] = useState({
        team_metrics: {},
        session_data: {},
        team_name: '',
        created_at: '',
        footage_url: '',
        status: '',
        id: '',
        team_id: ''
    });
    const [uploading, setUploading] = useState({});
    const [isEditingTitle, setIsEditingTitle] = useState(false);
    const [newTitle, setNewTitle] = useState('');
    const [showTeamMembers, setShowTeamMembers] = useState(false);
    const [teamMembers, setTeamMembers] = useState([]);

    useEffect(() => {
        fetchSession();
    }, [id]);

    const fetchSession = async () => {
        try {
            const data = await sessionService.getSessionDetails(id);
            setSession(data);
            setNewTitle(data.team_name);
        } catch (err) {
            console.error('Failed to fetch session:', err);
        }
    };

    const handleFileUpload = async (type) => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = type.startsWith('VIDEO') ? 'video/*' : 'image/*';

        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            setUploading(prev => ({ ...prev, [type]: true }));
            try {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('sessionId', session.id);
                formData.append('type', type);

                await sessionService.addAnalysis(formData);
                fetchSession();
            } catch (err) {
                console.error('Upload failed:', err);
            } finally {
                setUploading(prev => ({ ...prev, [type]: false }));
            }
        };
        input.click();
    };

    const handleDeleteAnalysis = async (type) => {
        try {
            await sessionService.deleteAnalysis(session.id, type);
            fetchSession();
        } catch (err) {
            console.error('Delete failed:', err);
        }
    };

    const handleTitleUpdate = async () => {
        if (!newTitle.trim()) {
            return; // Don't update if empty
        }

        try {
            await sessionService.updateSessionTitle(session.id, newTitle.trim());
            setIsEditingTitle(false);
            await fetchSession(); // Refresh the session data
        } catch (err) {
            console.error('Failed to update title:', err);
        }
    };

    const handleTitleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleTitleUpdate();
        } else if (e.key === 'Escape') {
            setIsEditingTitle(false);
            setNewTitle(session.team_name); // Reset to current title
        }
    };

    const handleStatusToggle = async () => {
        try {
            await sessionService.toggleSessionStatus(session.id);
            fetchSession();
        } catch (err) {
            console.error('Failed to update status:', err);
        }
    };

    const fetchTeamMembers = async (teamId) => {
        try {
            const response = await fetch(`/api/teams/${teamId}/members`);
            const data = await response.json();
            setTeamMembers(data);
            setShowTeamMembers(true);
        } catch (err) {
            console.error('Error fetching team members:', err);
        }
    };

    const getSourceType = (url) => {
        if (!url) return 'Unknown';
        try {
            const hostname = new URL(url).hostname;
            if (hostname.includes('veo.co')) return '🎥 Veo';
            if (hostname.includes('youtu')) return '🔗 YouTube';
            return '🔗 Other';
        } catch {
            return '🔗 Other';
        }
    };

    const TeamMembersModal = () => (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div className="bg-gray-800 p-6 rounded-lg max-w-lg w-full">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold text-white">Team Members</h3>
                    <button
                        onClick={() => setShowTeamMembers(false)}
                        className="text-gray-400 hover:text-white"
                    >
                        ✕
                    </button>
                </div>
                <div className="space-y-2">
                    {teamMembers.map((member, i) => (
                        <div key={i} className="flex justify-between items-center p-2 bg-gray-700 rounded">
                            <span className="text-white">{member.email}</span>
                            {member.is_admin && (
                                <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                                    Admin
                                </span>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );

    if (!session) return <div>Loading...</div>;

    return (
        <div className="max-w-7xl mx-auto p-4 md:p-8">
            <div className="mb-6">
                <button
                    onClick={() => navigate('/company')}
                    className="text-blue-400 hover:text-blue-300"
                >
                    ← Back to Dashboard
                </button>
            </div>

            <div className="bg-gray-900 p-6 rounded-lg mb-8">
                {isEditingTitle ? (
                    <div className="flex gap-2 items-center">
                        <input
                            type="text"
                            value={newTitle}
                            onChange={(e) => setNewTitle(e.target.value)}
                            onKeyDown={handleTitleKeyDown}
                            className="bg-gray-800 text-white px-3 py-2 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            autoFocus
                        />
                        <button
                            onClick={handleTitleUpdate}
                            className="bg-blue-500/20 text-blue-300 px-4 py-2 rounded hover:bg-blue-500/30"
                        >
                            Save
                        </button>
                        <button
                            onClick={() => {
                                setIsEditingTitle(false);
                                setNewTitle(session.team_name);
                            }}
                            className="text-gray-400 px-4 py-2 rounded hover:text-gray-300"
                        >
                            Cancel
                        </button>
                    </div>
                ) : (
                    <div className="flex justify-between items-center">
                        <h2
                            className="text-2xl font-bold text-white cursor-pointer hover:text-gray-300"
                            onClick={() => fetchTeamMembers(session.team_id)}
                        >
                            {session?.team_name}
                        </h2>
                        <button
                            onClick={() => setIsEditingTitle(true)}
                            className="text-blue-400 hover:text-blue-300"
                        >
                            Edit
                        </button>
                    </div>
                )}
                <div className="flex justify-between items-center mt-4">
                    <div className="text-sm text-gray-300 space-y-2">
                        <p>Uploaded: {new Date(session.created_at).toLocaleDateString()}</p>
                        <p>Source: {getSourceType(session.footage_url)}</p>
                        <p>
                            <a href={session.footage_url} target="_blank" rel="noopener noreferrer"
                                className="text-blue-300 hover:text-blue-200 hover:underline">
                                View Game Footage
                            </a>
                        </p>
                    </div>
                    <button
                        onClick={handleStatusToggle}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${session.status === 'PENDING'
                            ? 'bg-red-600/20 text-red-400 border border-red-600 hover:bg-red-600/30'
                            : 'bg-green-600/20 text-green-400 border border-green-600 hover:bg-green-600/30'
                            }`}
                    >
                        {session.status}
                    </button>
                </div>
            </div>

            <div className="grid gap-6">
                <div>
                    <h3 className="text-xl font-bold text-white mb-4">Analysis Images</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {['HEATMAP', 'SPRINT_MAP', 'GAME_MOMENTUM'].map(type => (
                            <div key={type} className="bg-gray-900 p-4 rounded-lg">
                                <div className="flex justify-between items-center mb-4">
                                    <h4 className="text-lg text-white">{type.replace('_', ' ')}</h4>
                                    {session[`analysis_image${type === 'HEATMAP' ? '1' : type === 'SPRINT_MAP' ? '2' : '3'}_url`] && (
                                        <button
                                            onClick={() => handleDeleteAnalysis(type)}
                                            className="text-red-400 hover:text-red-300 px-2 py-1"
                                        >
                                            Delete
                                        </button>
                                    )}
                                </div>
                                {session[`analysis_image${type === 'HEATMAP' ? '1' : type === 'SPRINT_MAP' ? '2' : '3'}_url`] ? (
                                    <img
                                        src={session[`analysis_image${type === 'HEATMAP' ? '1' : type === 'SPRINT_MAP' ? '2' : '3'}_url`]}
                                        alt={type}
                                        className="w-full rounded-lg"
                                    />
                                ) : (
                                    <button
                                        onClick={() => handleFileUpload(type)}
                                        disabled={uploading[type]}
                                        className="w-full p-4 border-2 border-dashed border-gray-600 rounded text-gray-300 hover:text-white"
                                    >
                                        {uploading[type] ? 'Uploading...' : `Upload ${type.replace('_', ' ')}`}
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                <div>
                    <h3 className="text-xl font-bold text-white mb-4">Video Analysis</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {[1, 2, 3, 4, 5].map(index => (
                            <div key={index} className="bg-gray-800 p-4 rounded-lg">
                                <div className="flex justify-between items-center mb-4">
                                    <h4 className="text-lg text-white">Video {index}</h4>
                                    {session[`analysis_video${index}_url`] && (
                                        <button
                                            onClick={() => handleDeleteAnalysis(`VIDEO_${index}`)}
                                            className="text-red-400 hover:text-red-300 px-2 py-1"
                                        >
                                            Delete
                                        </button>
                                    )}
                                </div>
                                {session[`analysis_video${index}_url`] ? (
                                    <div>
                                        <video 
                                            controls 
                                            className="w-full rounded-lg"
                                            playsInline
                                            preload="metadata"
                                        >
                                            <source 
                                                src={session[`analysis_video${index}_url`]} 
                                                type="video/mp4"
                                            />
                                            <track kind="captions" />
                                        </video>
                                        
                                        {/* Add a direct download link for testing */}
                                        <a 
                                            href={session[`analysis_video${index}_url`]}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-xs text-blue-400 mt-2 block"
                                        >
                                            Direct link
                                        </a>
                                        
                                        {/* Add a debug button */}
                                        <button
                                            onClick={async () => {
                                                try {
                                                    const response = await fetch(session[`analysis_video${index}_url`], {
                                                        method: 'HEAD',
                                                        mode: 'cors',
                                                        credentials: 'omit'
                                                    });
                                                } catch (err) {
                                                    console.error('Debug fetch failed:', err);
                                                }
                                            }}
                                            className="text-xs text-gray-400 mt-1 block"
                                        >
                                            Debug Headers
                                        </button>
                                    </div>
                                ) : (
                                    <button
                                        onClick={() => handleFileUpload(`VIDEO_${index}`)}
                                        disabled={uploading[`VIDEO_${index}`]}
                                        className="w-full p-4 border-2 border-dashed border-gray-600 rounded text-gray-300 hover:text-white"
                                    >
                                        {uploading[`VIDEO_${index}`] ? 'Uploading...' : `Upload Video ${index}`}
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                <TeamMetricsForm session={session} onUpdate={fetchSession} />
                <SessionDataUpload session={session} onUpdate={fetchSession} />
            </div>
            {showTeamMembers && <TeamMembersModal />}
        </div>
    );
}

export default SessionAnalysis; 