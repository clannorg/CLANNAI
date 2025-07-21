import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import SpiderChart from './SpiderChart';

function MatchesSection({ sessions }) {
  const [filter, setFilter] = useState('All');
  
  const filteredSessions = sessions.filter(session => {
    if (filter === 'All') return true;
    if (filter === 'Reviewed') return session.status === 'REVIEWED';
    if (filter === 'Pending') return session.status === 'PENDING';
    return true;
  });

  return (
    <div className="space-y-8">
      {/* Header with filter tabs - responsive */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <h2 className="text-2xl font-bold">Your Matches</h2>
        <div className="flex overflow-x-auto hide-scrollbar bg-gray-800/50 rounded-lg p-1">
          {['All', 'Reviewed', 'Pending'].map(option => (
            <button
              key={option}
              className={`px-4 py-2 text-sm font-medium rounded-md whitespace-nowrap transition-colors ${
                filter === option 
                  ? 'bg-gray-700 text-white' 
                  : 'text-white hover:text-white hover:bg-gray-700/50'
              }`}
              onClick={() => setFilter(option)}
            >
              {option}
            </button>
          ))}
        </div>
      </div>
      
      {filteredSessions.length === 0 ? (
        <div className="bg-gray-800/50 rounded-xl border border-gray-700/50 p-8 text-center">
          <p className="text-gray-400">No {filter !== 'All' ? filter.toLowerCase() : ''} matches found.</p>
        </div>
      ) : (
        filteredSessions.map(session => {
          const team1 = session.session_data?.match_info?.team1;
          const team2 = session.session_data?.match_info?.team2;
          const score = session.session_data?.match_info?.score;
          const isReviewed = session.status === 'REVIEWED';

          return (
            <div
              key={session.id}
              className="bg-gray-800/50 rounded-xl border border-gray-700/50 transition-all overflow-hidden"
            >
              {/* Match Header - responsive */}
              <div className="p-4 sm:p-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                  <div className="flex items-center gap-3">
                    <span className={`w-2 h-2 rounded-full ${
                      session.status === 'PENDING'
                        ? 'bg-yellow-400'
                        : 'bg-green-400'
                    }`} />
                    <span className="text-sm font-medium text-white">
                      {session.status}
                    </span>
                  </div>
                  <span className="text-sm font-medium text-white">
                    {new Date(session.created_at).toLocaleString()}
                  </span>
                </div>

                {/* Teams and Score - responsive */}
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                  {/* Team 1 - Mobile: full width, Desktop: left aligned */}
                  <div className="text-center sm:text-left sm:flex-1">
                    <div className="flex items-center justify-center sm:justify-start gap-2">
                      <div 
                        className="w-4 h-4 rounded-md border border-white/30" 
                        style={{ backgroundColor: session.team_color || '#D1FB7A' }}
                      />
                      <h3 className="text-xl font-bold text-white">
                        {team1?.name || session.team_name}
                      </h3>
                    </div>
                  </div>
                  
                  {/* Score - Centered on both mobile and desktop */}
                  <div className="flex items-center justify-center gap-6 px-4">
                    <span className="text-3xl font-bold text-white">
                      {score?.team1 || '-'}
                    </span>
                    <span className="text-xl text-white">vs</span>
                    <span className="text-3xl font-bold text-white">{score?.team2 || '-'}</span>
                  </div>

                  {/* Team 2 - Mobile: full width, Desktop: right aligned */}
                  <div className="text-center sm:text-right sm:flex-1">
                    <div className="flex items-center justify-center sm:justify-end gap-2">
                      <h3 className="text-xl font-bold text-white">
                        {team2?.name || 'Opponent'}
                      </h3>
                    </div>
                  </div>
                </div>

                {/* Metrics Grid - responsive */}
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
                  {/* Distance */}
                  <div className="text-center">
                    <p className="text-base font-medium text-white mb-3">Distance</p>
                    <div className="flex items-center justify-center gap-3 bg-gray-800/50 p-3 rounded-lg">
                      <span className="font-bold text-white">
                        {team1?.metrics?.total_distance?.toFixed(1) || '-'}
                      </span>
                      <span className="text-gray-400">|</span>
                      <span className="font-bold text-white">
                        {team2?.metrics?.total_distance?.toFixed(1) || '-'}
                      </span>
                      <span className="text-sm text-gray-300">km</span>
                    </div>
                  </div>

                  {/* Energy */}
                  <div className="text-center">
                    <p className="text-base font-medium text-white mb-3">Energy</p>
                    <div className="flex items-center justify-center gap-3 bg-gray-800/50 p-3 rounded-lg">
                      <span className="font-bold text-white">
                        {team1?.metrics?.energy?.toFixed(0) || '-'}
                      </span>
                      <span className="text-gray-400">|</span>
                      <span className="font-bold text-white">
                        {team2?.metrics?.energy?.toFixed(0) || '-'}
                      </span>
                      <span className="text-sm text-gray-300">kJ</span>
                    </div>
                  </div>

                  {/* Sprints */}
                  <div className="text-center">
                    <p className="text-base font-medium text-white mb-3">Sprints</p>
                    <div className="flex items-center justify-center gap-3 bg-gray-800/50 p-3 rounded-lg">
                      <span className="font-bold text-white">
                        {team1?.metrics?.total_sprints || '-'}
                      </span>
                      <span className="text-gray-400">|</span>
                      <span className="font-bold text-white">
                        {team2?.metrics?.total_sprints || '-'}
                      </span>
                    </div>
                  </div>

                  {/* Sprint Dist */}
                  <div className="text-center">
                    <p className="text-base font-medium text-white mb-3">Sprint Dist</p>
                    <div className="flex items-center justify-center gap-3 bg-gray-800/50 p-3 rounded-lg">
                      <span className="font-bold text-white">
                        {team1?.metrics?.sprint_distance?.toFixed(0) || '-'}
                      </span>
                      <span className="text-gray-400">|</span>
                      <span className="font-bold text-white">
                        {team2?.metrics?.sprint_distance?.toFixed(0) || '-'}
                      </span>
                      <span className="text-sm text-gray-300">m</span>
                    </div>
                  </div>

                  {/* Sprint Speed */}
                  <div className="text-center">
                    <p className="text-base font-medium text-white mb-3">Sprint Speed</p>
                    <div className="flex items-center justify-center gap-3 bg-gray-800/50 p-3 rounded-lg">
                      <span className="font-bold text-white">
                        {team1?.metrics?.avg_sprint_speed?.toFixed(1) || '-'}
                      </span>
                      <span className="text-gray-400">|</span>
                      <span className="font-bold text-white">
                        {team2?.metrics?.avg_sprint_speed?.toFixed(1) || '-'}
                      </span>
                      <span className="text-sm text-gray-300">m/s</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Footage Link - responsive */}
              <div className="p-4 bg-gray-800/30 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-2">
                  {isReviewed ? (
                    <Link 
                      to={`/session/${session.id}`}
                      className="px-6 py-2 bg-green-600/20 text-green-400 border border-green-600 rounded-full hover:bg-green-600/30 transition-colors text-sm font-medium"
                    >
                      View Full Analysis
                    </Link>
                  ) : (
                    <div className="flex items-center gap-2 text-yellow-400">
                      <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span className="text-sm">Analysis in progress - check back soon</span>
                    </div>
                  )}
                </div>
                <a
                  href={session.footage_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-6 py-2 bg-gray-700/50 text-gray-300 border border-gray-600 rounded-full hover:bg-gray-700 hover:text-white transition-colors text-sm font-medium text-center sm:text-left"
                  onClick={(e) => e.stopPropagation()}
                >
                  View Uploaded Footage
                </a>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}

export default MatchesSection;
