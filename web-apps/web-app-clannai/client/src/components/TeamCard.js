import React from 'react';

function TeamCard({ team, onUpgrade, onShare, onViewMembers }) {
    return (
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50 hover:border-green-500/30 
                      transition-all">
            <div className="flex justify-between items-start mb-4">
                <h4 className="text-xl font-medium">{team.name}</h4>
                {!team.is_premium && (
                    <button onClick={() => onUpgrade(team.id)}
                        className="text-sm px-3 py-1 bg-green-400/10 text-green-400 rounded-lg 
                                     border border-green-400 hover:bg-green-400/20">
                        Upgrade
                    </button>
                )}
            </div>

            <div className="space-y-3">
                <div className="flex items-center justify-between text-sm text-gray-300">
                    <span>Team Code:</span>
                    <span className="font-mono">{team.team_code}</span>
                </div>

                <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-300">Status:</span>
                    {team.is_premium ? (
                        <span className="px-2 py-1 bg-green-400/10 text-green-400 rounded-full text-xs">
                            ⭐️ PREMIUM
                        </span>
                    ) : (
                        <span className="px-2 py-1 bg-gray-400/10 text-gray-400 rounded-full text-xs">
                            FREE
                        </span>
                    )}
                </div>
            </div>

            <div className="flex gap-2 mt-4">
                <button onClick={onShare}
                    className="flex-1 text-sm px-3 py-2 bg-blue-400/10 text-blue-400 rounded-lg 
                                 hover:bg-blue-400/20 transition-all">
                    Share Code
                </button>
                {team.team_code !== 'STMARY' && (
                    <button onClick={onViewMembers}
                        className="flex-1 text-sm px-3 py-2 bg-purple-400/10 text-purple-400 rounded-lg 
                                     hover:bg-purple-400/20 transition-all">
                        View Members
                    </button>
                )}
            </div>
        </div>
    );
}

export default TeamCard; 