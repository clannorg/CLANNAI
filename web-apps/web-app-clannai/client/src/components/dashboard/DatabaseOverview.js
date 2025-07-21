import React, { useState, useEffect } from 'react';
import databaseService from '../../services/databaseService';

function DatabaseOverview() {
    const [data, setData] = useState({
        userDetails: [],
        teamDetails: [],
        teamMemberDetails: [],
        sessionDetails: []
    });
    const [loading, setLoading] = useState(true);
    const [expandedSessions, setExpandedSessions] = useState(new Set());

    useEffect(() => {
        const fetchData = async () => {
            try {
                const result = await databaseService.getDatabaseContent();
                setData({
                    userDetails: result.userDetails || [],
                    teamDetails: result.teamDetails || [],
                    teamMemberDetails: result.teamMemberDetails || [],
                    sessionDetails: result.sessionDetails || []
                });
            } catch (error) {
                setData({
                    userDetails: [],
                    teamDetails: [],
                    teamMemberDetails: [],
                    sessionDetails: []
                });
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const toggleSessionExpand = (sessionId) => {
        const newExpanded = new Set(expandedSessions);
        if (newExpanded.has(sessionId)) {
            newExpanded.delete(sessionId);
        } else {
            newExpanded.add(sessionId);
        }
        setExpandedSessions(newExpanded);
    };

    if (loading) return <div className="p-6">Loading database content...</div>;

    return (
        <div className="space-y-8 p-6">
            {/* User Details Table */}
            <div className="bg-gray-800 rounded-lg p-6">
                <h2 className="text-xl font-bold mb-4 text-gray-200">USER DETAILS</h2>
                <div className="overflow-x-auto">
                    <table className="min-w-full">
                        <thead className="border-b border-gray-700">
                            <tr>
                                <th className="text-left py-3 px-4">Email</th>
                                <th className="text-left py-3 px-4">Role</th>
                                <th className="text-left py-3 px-4">Cognito ID</th>
                                <th className="text-left py-3 px-4">Created At</th>
                                <th className="text-left py-3 px-4">Team Count</th>
                                <th className="text-left py-3 px-4">Uploaded Sessions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.userDetails.map((user, idx) => (
                                <tr key={idx} className="border-b border-gray-700">
                                    <td className="py-2 px-4">{user.email}</td>
                                    <td className="py-2 px-4">
                                        <span className={`px-2 py-1 rounded text-sm ${
                                            user.role === 'COMPANY_MEMBER' ? 'bg-purple-500' : 'bg-blue-500'
                                        }`}>
                                            {user.role}
                                        </span>
                                    </td>
                                    <td className="py-2 px-4">{user.cognito_id || 'N/A'}</td>
                                    <td className="py-2 px-4">{new Date(user.created_at).toLocaleString()}</td>
                                    <td className="py-2 px-4">{user.team_count}</td>
                                    <td className="py-2 px-4">{user.uploaded_sessions}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Teams Table */}
            <div className="bg-gray-800 rounded-lg p-6">
                <h2 className="text-xl font-bold mb-4 text-gray-200">TEAMS</h2>
                <div className="overflow-x-auto">
                    <table className="min-w-full">
                        <thead className="border-b border-gray-700">
                            <tr>
                                <th className="text-left py-3 px-4">Name</th>
                                <th className="text-left py-3 px-4">Team Code</th>
                                <th className="text-left py-3 px-4">Premium</th>
                                <th className="text-left py-3 px-4">Subscription Status</th>
                                <th className="text-left py-3 px-4">Trial Ends At</th>
                                <th className="text-left py-3 px-4">Created At</th>
                                <th className="text-left py-3 px-4">Updated At</th>
                                <th className="text-left py-3 px-4">Member Count</th>
                                <th className="text-left py-3 px-4">Session Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.teamDetails?.map((team, idx) => (
                                <tr key={idx} className="border-b border-gray-700">
                                    <td className="py-2 px-4">{team.name}</td>
                                    <td className="py-2 px-4">{team.team_code}</td>
                                    <td className="py-2 px-4">
                                        <span className={`px-2 py-1 rounded text-sm ${
                                            team.is_premium ? 'bg-green-500' : 'bg-gray-500'
                                        }`}>
                                            {team.is_premium ? 'Yes' : 'No'}
                                        </span>
                                    </td>
                                    <td className="py-2 px-4">{team.subscription_status || 'FREE'}</td>
                                    <td className="py-2 px-4">{team.trial_ends_at ? new Date(team.trial_ends_at).toLocaleString() : 'N/A'}</td>
                                    <td className="py-2 px-4">{new Date(team.created_at).toLocaleString()}</td>
                                    <td className="py-2 px-4">{new Date(team.updated_at).toLocaleString()}</td>
                                    <td className="py-2 px-4">{team.member_count}</td>
                                    <td className="py-2 px-4">{team.session_count}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Team Membership Details */}
            <div className="bg-gray-800 rounded-lg p-6">
                <h2 className="text-xl font-bold mb-4 text-gray-200">TEAM MEMBERSHIP DETAILS</h2>
                <div className="overflow-x-auto">
                    <table className="min-w-full">
                        <thead className="border-b border-gray-700">
                            <tr>
                                <th className="text-left py-3 px-4">Team Name</th>
                                <th className="text-left py-3 px-4">Team Code</th>
                                <th className="text-left py-3 px-4">Premium</th>
                                <th className="text-left py-3 px-4">Subscription</th>
                                <th className="text-left py-3 px-4">Trial Ends</th>
                                <th className="text-left py-3 px-4">Subscription ID</th>
                                <th className="text-left py-3 px-4">Member Email</th>
                                <th className="text-left py-3 px-4">Admin</th>
                                <th className="text-left py-3 px-4">Joined At</th>
                                <th className="text-left py-3 px-4">Team Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.teamMemberDetails.map((member, idx) => (
                                <tr key={idx} className="border-b border-gray-700">
                                    <td className="py-2 px-4">{member.team_name}</td>
                                    <td className="py-2 px-4">{member.team_code}</td>
                                    <td className="py-2 px-4">
                                        <span className={`px-2 py-1 rounded text-sm ${
                                            member.is_premium ? 'bg-green-500' : 'bg-gray-500'
                                        }`}>
                                            {member.is_premium ? 'Yes' : 'No'}
                                        </span>
                                    </td>
                                    <td className="py-2 px-4">{member.subscription_status || 'FREE'}</td>
                                    <td className="py-2 px-4">
                                        {member.trial_ends_at ? new Date(member.trial_ends_at).toLocaleString() : 'N/A'}
                                    </td>
                                    <td className="py-2 px-4">{member.subscription_id || 'N/A'}</td>
                                    <td className="py-2 px-4">{member.member_email}</td>
                                    <td className="py-2 px-4">
                                        <span className={`px-2 py-1 rounded text-sm ${
                                            member.is_admin ? 'bg-yellow-500' : 'bg-gray-500'
                                        }`}>
                                            {member.is_admin ? 'Yes' : 'No'}
                                        </span>
                                    </td>
                                    <td className="py-2 px-4">{new Date(member.joined_at).toLocaleString()}</td>
                                    <td className="py-2 px-4">{new Date(member.team_created_at).toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Session Details */}
            <div className="bg-gray-800 rounded-lg p-6">
                <h2 className="text-xl font-bold mb-4 text-gray-200">SESSION DETAILS</h2>
                <div className="overflow-x-auto">
                    <table className="min-w-full">
                        <thead className="border-b border-gray-700">
                            <tr>
                                <th className="text-left py-3 px-4">Team Name</th>
                                <th className="text-left py-3 px-4">Uploaded By</th>
                                <th className="text-left py-3 px-4">Reviewed By</th>
                                <th className="text-left py-3 px-4">Status</th>
                                <th className="text-left py-3 px-4">Game Date</th>
                                <th className="text-left py-3 px-4">Created At</th>
                                <th className="text-left py-3 px-4">Updated At</th>
                                <th className="text-left py-3 px-4">Analysis</th>
                                <th className="text-left py-3 px-4">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.sessionDetails.map((session, idx) => (
                                <React.Fragment key={idx}>
                                    <tr className="border-b border-gray-700">
                                        <td className="py-2 px-4">{session.team_name}</td>
                                        <td className="py-2 px-4">{session.uploaded_by}</td>
                                        <td className="py-2 px-4">{session.reviewed_by || 'N/A'}</td>
                                        <td className="py-2 px-4">
                                            <span className={`px-2 py-1 rounded text-sm ${
                                                session.status === 'REVIEWED' ? 'bg-green-500' : 'bg-yellow-500'
                                            }`}>
                                                {session.status}
                                            </span>
                                        </td>
                                        <td className="py-2 px-4">{new Date(session.game_date).toLocaleDateString()}</td>
                                        <td className="py-2 px-4">{new Date(session.created_at).toLocaleString()}</td>
                                        <td className="py-2 px-4">{new Date(session.updated_at).toLocaleString()}</td>
                                        <td className="py-2 px-4">
                                            <span className={`px-2 py-1 rounded text-sm ${
                                                session.has_analysis === 'Yes' ? 'bg-green-500' : 'bg-gray-500'
                                            }`}>
                                                {session.has_analysis}
                                            </span>
                                        </td>
                                        <td className="py-2 px-4">
                                            <button
                                                onClick={() => toggleSessionExpand(idx)}
                                                className="text-blue-400 hover:text-blue-300"
                                            >
                                                {expandedSessions.has(idx) ? 'Hide Details' : 'Show Details'}
                                            </button>
                                        </td>
                                    </tr>
                                    {expandedSessions.has(idx) && (
                                        <tr className="bg-gray-900">
                                            <td colSpan="9" className="py-4 px-6">
                                                <div className="space-y-2">
                                                    <p><strong>Footage URL:</strong> <a href={session.footage_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">{session.footage_url}</a></p>
                                                    <p><strong>Distance Covered:</strong> {session.distance_covered || 'N/A'}</p>
                                                    <p><strong>Analysis Description:</strong> {session.analysis_description || 'N/A'}</p>
                                                    
                                                    <div className="grid grid-cols-3 gap-4 mt-2">
                                                        {session.analysis_image1_url && (
                                                            <a href={session.analysis_image1_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Analysis Image 1</a>
                                                        )}
                                                        {session.analysis_image2_url && (
                                                            <a href={session.analysis_image2_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Analysis Image 2</a>
                                                        )}
                                                        {session.analysis_image3_url && (
                                                            <a href={session.analysis_image3_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">Analysis Image 3</a>
                                                        )}
                                                    </div>

                                                    {session.team_metrics && (
                                                        <div className="mt-4">
                                                            <h4 className="font-bold mb-2">Team Metrics:</h4>
                                                            <pre className="bg-gray-800 p-2 rounded overflow-x-auto">
                                                                {JSON.stringify(session.team_metrics, null, 2)}
                                                            </pre>
                                                        </div>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </React.Fragment>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default DatabaseOverview; 