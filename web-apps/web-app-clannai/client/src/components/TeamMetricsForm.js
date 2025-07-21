import React, { useState, useEffect } from 'react';
import sessionService from '../services/sessionService';

function TeamMetricsForm({ session, onUpdate }) {
    const [metrics, setMetrics] = useState({
        total_distance: 0,
        total_sprints: 0,
        sprint_distance: 0,
        high_intensity_sprints: 0,
        top_sprint_speed: 0
    });

    // Update form when session data changes
    useEffect(() => {
        if (session.session_data?.match_info?.team1?.metrics) {
            const team1Metrics = session.session_data.match_info.team1.metrics;
            setMetrics({
                total_distance: team1Metrics.total_distance || 0,
                total_sprints: team1Metrics.total_sprints || 0,
                sprint_distance: team1Metrics.sprint_distance || 0,
                high_intensity_sprints: 0,
                top_sprint_speed: team1Metrics.avg_sprint_speed || 0
            });
        }
    }, [session.session_data]);

    const handleNumberChange = (field, value, isInteger = false) => {
        const parsedValue = value === '' ? 0 : isInteger ? parseInt(value) : parseFloat(value);
        setMetrics(prev => ({
            ...prev,
            [field]: isNaN(parsedValue) ? 0 : parsedValue
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Convert to new format
            const sessionData = {
                match_info: {
                    team1: {
                        name: session.team_name || '',
                        metrics: {
                            total_distance: metrics.total_distance,
                            sprint_distance: metrics.sprint_distance,
                            total_sprints: metrics.total_sprints,
                            avg_sprint_speed: metrics.top_sprint_speed,
                            energy: 0
                        }
                    },
                    team2: session.session_data?.match_info?.team2 || {
                        name: 'Opponent',
                        metrics: {
                            total_distance: 0,
                            sprint_distance: 0,
                            total_sprints: 0,
                            avg_sprint_speed: 0,
                            energy: 0
                        }
                    },
                    score: session.session_data?.match_info?.score || {
                        team1: 0,
                        team2: 0
                    }
                }
            };

            await sessionService.updateSessionData(session.id, sessionData);
            onUpdate();
        } catch (error) {
            console.error('Failed to update metrics:', error);
        }
    };

    return (
        <div className="bg-gray-900/50 border border-gray-700 p-4 rounded-lg">
            <h4 className="text-blue-400 font-medium mb-4">Team Metrics</h4>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="text-sm text-gray-400">Total Distance (m)</label>
                        <input
                            type="number"
                            min="0"
                            step="any"
                            value={metrics.total_distance || ''}
                            onChange={(e) => handleNumberChange('total_distance', e.target.value)}
                            className="w-full bg-gray-800 text-white px-3 py-2 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        />
                    </div>
                    <div>
                        <label className="text-sm text-gray-400">Total Sprints</label>
                        <input
                            type="number"
                            min="0"
                            step="1"
                            value={metrics.total_sprints || ''}
                            onChange={(e) => handleNumberChange('total_sprints', e.target.value, true)}
                            className="w-full bg-gray-800 text-white px-3 py-2 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        />
                    </div>
                    <div>
                        <label className="text-sm text-gray-400">Sprint Distance (m)</label>
                        <input
                            type="number"
                            min="0"
                            step="any"
                            value={metrics.sprint_distance || ''}
                            onChange={(e) => handleNumberChange('sprint_distance', e.target.value)}
                            className="w-full bg-gray-800 text-white px-3 py-2 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        />
                    </div>
                    <div>
                        <label className="text-sm text-gray-400">High Intensity Sprints</label>
                        <input
                            type="number"
                            min="0"
                            step="1"
                            value={metrics.high_intensity_sprints || ''}
                            onChange={(e) => handleNumberChange('high_intensity_sprints', e.target.value, true)}
                            className="w-full bg-gray-800 text-white px-3 py-2 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        />
                    </div>
                    <div>
                        <label className="text-sm text-gray-400">Top Sprint Speed (km/h)</label>
                        <input
                            type="number"
                            min="0"
                            step="0.1"
                            value={metrics.top_sprint_speed || ''}
                            onChange={(e) => handleNumberChange('top_sprint_speed', e.target.value)}
                            className="w-full bg-gray-800 text-white px-3 py-2 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        />
                    </div>
                </div>
                <button
                    type="submit"
                    className="bg-blue-500/20 text-blue-400 px-4 py-2 rounded hover:bg-blue-500/30"
                >
                    Save Metrics
                </button>
            </form>
        </div>
    );
}

export default TeamMetricsForm; 