import React, { useState, useEffect } from 'react';
import sessionService from '../../services/sessionService';

function StatsOverview() {
    const [stats, setStats] = useState({
        total_teams: 0,
        total_accounts: 0,
        all_sessions: 0,
        valid_sessions: 0,
        pending_valid: 0,
        completed_valid: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const sessionStats = await sessionService.getSessionStats();

            setStats({
                total_teams: Number(sessionStats.total_teams),
                total_accounts: Number(sessionStats.total_accounts),
                all_sessions: Number(sessionStats.all_sessions),
                pending_valid: Number(sessionStats.pending_valid),
                completed_valid: Number(sessionStats.completed_valid),
                valid_sessions: Number(sessionStats.pending_valid) + Number(sessionStats.completed_valid)
            });
        } catch (err) {
            // Remove this line: console.error('Failed to fetch stats:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="animate-pulse">Loading stats...</div>;

    const completionPercentage = Math.round(
        (stats.completed_valid / (stats.valid_sessions || 1)) * 100
    );

    return (
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h3 className="text-xl font-bold mb-4 text-center">CLANN ANALYSIS STATUS</h3>

            {/* Top Stats Grid */}
            <div className="grid grid-cols-3 gap-4 text-center mb-6">
                <div>
                    <div className="text-gray-400 text-sm">Total Teams</div>
                    <div className="text-2xl font-bold">{stats.total_teams || 0}</div>
                </div>
                <div>
                    <div className="text-gray-400 text-sm">Total Users</div>
                    <div className="text-2xl font-bold">{stats.total_accounts || 0}</div>
                </div>
                <div>
                    <div className="text-gray-400 text-sm">Total Videos</div>
                    <div className="text-2xl font-bold">{stats.all_sessions || 0}</div>
                </div>
            </div>

            {/* Progress Circle and Stats */}
            <div className="flex items-center justify-between">
                <div className="text-center">
                    <div className="text-3xl font-bold text-yellow-500">
                        {stats.pending_valid || 0}
                    </div>
                    <div className="text-sm text-gray-400">Pending</div>
                </div>

                {/* Progress Circle */}
                <div className="relative w-32 h-32">
                    <svg className="w-full h-full transform -rotate-90">
                        <circle
                            className="text-gray-700"
                            strokeWidth="8"
                            stroke="currentColor"
                            fill="transparent"
                            r="58"
                            cx="64"
                            cy="64"
                        />
                        <circle
                            className="text-green-500"
                            strokeWidth="8"
                            strokeLinecap="round"
                            stroke="currentColor"
                            fill="transparent"
                            r="58"
                            cx="64"
                            cy="64"
                            strokeDasharray={`${2 * Math.PI * 58}`}
                            strokeDashoffset={`${2 * Math.PI * 58 * (1 - completionPercentage / 100)}`}
                        />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-2xl font-bold">{completionPercentage || 0}%</span>
                    </div>
                </div>

                <div className="text-center">
                    <div className="text-3xl font-bold text-green-500">
                        {stats.completed_valid || 0}
                    </div>
                    <div className="text-sm text-gray-400">Complete</div>
                </div>
            </div>
        </div>
    );
}

export default StatsOverview;
