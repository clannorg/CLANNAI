import React from 'react';

function TeamMembersModal({ team, members, onClose, onRemoveMember, userEmail }) {
    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800/90 rounded-xl p-6 max-w-lg w-full border border-gray-700/50">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-display text-transparent bg-clip-text 
                                 bg-gradient-to-r from-green-400 via-emerald-400 to-blue-500">
                        {team.name} - Team Members
                    </h3>
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        ✕
                    </button>
                </div>

                <div className="space-y-3 max-h-96 overflow-y-auto">
                    {members?.map((member) => (
                        <div key={member.user_id}
                            className="flex justify-between items-center p-3 bg-gray-900/50 
                                      rounded-lg border border-gray-700/50">
                            <div>
                                <span className="text-white">{member.email}</span>
                                {member.email === userEmail && (
                                    <span className="ml-2 text-xs text-gray-400">(you)</span>
                                )}
                            </div>
                            <div className="flex items-center gap-3">
                                {member.is_admin && (
                                    <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                                        Admin
                                    </span>
                                )}
                                {member.email !== userEmail && team.is_admin && (
                                    <button
                                        onClick={() => onRemoveMember(team.id, member.user_id)}
                                        className="text-red-400 hover:text-red-300">
                                        Remove
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default TeamMembersModal; 