import React from 'react';
import {
    Radar,
    RadarChart,
    PolarGrid,
    PolarAngleAxis
} from 'recharts';

function SpiderChart({ sessionData, colors = { team1: "#4F46E5", team2: "#EF4444" } }) {
    // Normalize values to a 0-100 scale based on expected maximum values.
    const normalizeValue = (value, metric) => {
        switch (metric) {
            case 'energy': 
                // Maximum energy assumed to be 28,242 kJ
                return (value / 28242) * 100;
            case 'total_sprints': 
                return (value / 120) * 100; // max ~120 sprints
            case 'total_distance': 
                return (value / 90) * 100;  // max ~90 km
            case 'sprint_distance': 
                return (value / 1500) * 100; // max ~1500 m sprint distance
            case 'avg_sprint_speed':
                // Using 10 m/s as the expected maximum
                return (value / 10) * 100;
            default: 
                return value;
        }
    };

    // Define metrics order with total distance at the top and swapping total_sprints and avg_sprint_speed.
    const metricOrder = ['total_distance', 'energy', 'avg_sprint_speed', 'sprint_distance', 'total_sprints'];
    // Retain all metric labels—units have been removed from the labels themselves.
    const metricLabels = {
        total_distance: 'Total Distance',
        energy: 'Energy',
        total_sprints: 'Total Sprints',
        sprint_distance: 'Sprint Distance',
        avg_sprint_speed: 'Avg Sprint Speed'
    };

    // Format data for RadarChart in the specific order.
    const chartData = metricOrder.map(key => ({
        metric: metricLabels[key],
        team: normalizeValue(sessionData?.match_info?.team1?.metrics[key] || 0, key),
        opponent: normalizeValue(sessionData?.match_info?.team2?.metrics[key] || 0, key)
    }));

    return (
        <div className="w-full flex justify-center">
            <RadarChart width={500} height={400} data={chartData}>
                <PolarGrid gridType="polygon" />
                <PolarAngleAxis dataKey="metric" />
                <Radar
                    name={sessionData?.match_info?.team1?.name || 'Team'}
                    dataKey="team"
                    stroke={colors.team1}
                    fill={colors.team1}
                    fillOpacity={0.3}
                />
                <Radar
                    name={sessionData?.match_info?.team2?.name || 'Opponent'}
                    dataKey="opponent"
                    stroke={colors.team2}
                    fill={colors.team2}
                    fillOpacity={0.3}
                />
            </RadarChart>
        </div>
    );
}

export default SpiderChart; 