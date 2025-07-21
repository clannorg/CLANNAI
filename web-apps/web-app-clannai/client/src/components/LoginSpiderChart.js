import React, { useEffect, useRef, useState } from 'react';
import {
    Radar,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    ResponsiveContainer
} from 'recharts';

function LoginSpiderChart({ sessionData, colors = { team1: "#D1FB7A", team2: "#B9E8EB" } }) {
    const chartRef = useRef(null);
    const [chartSize, setChartSize] = useState({ width: 0, height: 0 });
    const [points, setPoints] = useState([]);
    
    // Normalize values to a 0-100 scale based on expected maximum values
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

    // Define metrics order (clockwise from top)
    const metricOrder = ['total_distance', 'energy', 'avg_sprint_speed', 'sprint_distance', 'total_sprints'];
    
    // Labels for the metrics - shortened for better fit
    const metricLabels = {
        total_distance: 'Total Distance',
        energy: 'Energy',
        total_sprints: 'Total Sprints',
        sprint_distance: 'Sprint Distance',
        avg_sprint_speed: 'Avg Sprint Speed'
    };
    
    // Units for each metric
    const metricUnits = {
        total_distance: 'km',
        energy: 'kJ',
        total_sprints: '',
        sprint_distance: 'm',
        avg_sprint_speed: 'm/s'
    };

    // Format data for RadarChart
    const chartData = metricOrder.map(key => ({
        metric: metricLabels[key],
        team: normalizeValue(sessionData?.match_info?.team1?.metrics[key] || 0, key),
        opponent: normalizeValue(sessionData?.match_info?.team2?.metrics[key] || 0, key),
        rawTeam: sessionData?.match_info?.team1?.metrics[key] || 0,
        rawOpponent: sessionData?.match_info?.team2?.metrics[key] || 0,
        unit: metricUnits[key]
    }));

    // Calculate positions for labels based on chart size
    useEffect(() => {
        if (!chartRef.current) return;
        
        const calculatePoints = () => {
            const container = chartRef.current;
            if (!container) return;
            
            const rect = container.getBoundingClientRect();
            const width = rect.width;
            const height = rect.height;
            
            setChartSize({ width, height });
            
            // Calculate points for a pentagon
            const centerX = width / 2;
            const centerY = height / 2;
            
            // Use a smaller radius for the chart to give more space for labels
            const radius = Math.min(width, height) * 0.30; // Slightly smaller base radius
            
            const angleStep = (2 * Math.PI) / 5;
            const startAngle = -Math.PI / 2;
            
            const newPoints = metricOrder.map((metric, index) => {
                const angle = startAngle + index * angleStep;
                
                // Custom distance multipliers for each vertex to prevent overlap
                let distanceMultiplier;
                
                // Adjust based on metric position - bring Total Distance closer
                if (metric === 'total_distance') {
                    distanceMultiplier = 1.25; // Top - reduced from 1.5 to bring closer
                } else if (metric === 'energy') {
                    distanceMultiplier = 1.25; // Right side - unchanged
                } else if (metric === 'avg_sprint_speed') {
                    distanceMultiplier = 1.6; // Bottom right - unchanged
                } else if (metric === 'sprint_distance') {
                    distanceMultiplier = 1.6; // Bottom left - unchanged
                } else if (metric === 'total_sprints') {
                    distanceMultiplier = 1.25; // Left side - unchanged
                }
                
                return {
                    x: centerX + radius * Math.cos(angle) * distanceMultiplier,
                    y: centerY + radius * Math.sin(angle) * distanceMultiplier,
                    angle,
                    metric
                };
            });
            
            setPoints(newPoints);
        };
        
        calculatePoints();
        window.addEventListener('resize', calculatePoints);
        
        return () => {
            window.removeEventListener('resize', calculatePoints);
        };
    }, [chartRef]);

    return (
        <div className="relative w-full" style={{ height: '500px' }} ref={chartRef}>
            {/* Team Legend - positioned at the top of the chart */}
            <div className="flex justify-center gap-6 mb-4">
                <span className="text-lg font-medium" style={{ color: colors.team1 }}>Home</span>
                <span className="text-lg font-medium" style={{ color: colors.team2 }}>Away</span>
            </div>
            
            {/* The Radar Chart - make it slightly smaller */}
            <ResponsiveContainer width="90%" height="90%" className="mx-auto">
                <RadarChart data={chartData} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <PolarGrid gridType="polygon" />
                    <PolarAngleAxis 
                        dataKey="metric" 
                        tick={false} // Hide default labels
                    />
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
            </ResponsiveContainer>
            
            {/* Custom Labels at Vertices */}
            {points.map((point, index) => {
                const metric = metricOrder[index];
                const data = chartData[index];
                const team1Better = data.rawTeam > data.rawOpponent;
                
                // All labels should be center-aligned for consistency
                const textAlign = 'center';
                
                // Adjust width for side labels to prevent overflow
                const maxWidth = 
                    (metric === 'energy' || metric === 'total_sprints') ? '120px' : '140px';
                
                return (
                    <div 
                        key={metric}
                        className="absolute transform -translate-x-1/2 -translate-y-1/2"
                        style={{ 
                            left: point.x, 
                            top: point.y,
                            textAlign,
                            maxWidth
                        }}
                    >
                        <div className="font-medium text-white mb-2 text-base">{metricLabels[metric]}</div>
                        <div className="flex items-center gap-3 justify-center">
                            {/* Team 1 Value with underline if better */}
                            <div className="relative">
                                <span className="font-bold text-lg text-white">
                                    {data.rawTeam}
                                    {data.unit && <span className="ml-1 text-xs">{data.unit}</span>}
                                </span>
                                {team1Better && (
                                    <div 
                                        className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full" 
                                        style={{ backgroundColor: colors.team1 }}
                                    ></div>
                                )}
                            </div>
                            
                            <span className="text-gray-500">|</span>
                            
                            {/* Team 2 Value with underline if better */}
                            <div className="relative">
                                <span className="font-bold text-lg text-white">
                                    {data.rawOpponent}
                                    {data.unit && <span className="ml-1 text-xs">{data.unit}</span>}
                                </span>
                                {!team1Better && (
                                    <div 
                                        className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full" 
                                        style={{ backgroundColor: colors.team2 }}
                                    ></div>
                                )}
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

export default LoginSpiderChart; 