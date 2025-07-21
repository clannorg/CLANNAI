import React from 'react';
import { useNavigate } from 'react-router-dom';


function SessionCard({ session }) {
    const navigate = useNavigate();

    return (
        <div
            onClick={() => navigate(`/session/${session.id}`)}
            className={`bg-gray-900 rounded-lg overflow-hidden border-l-4 cursor-pointer
                       hover:bg-gray-800/70 transition-all duration-200 ${session.status === 'PENDING'
                    ? 'border-yellow-500'
                    : 'border-green-500'
                }`}
        >
            <div className="bg-gray-800/50 p-6">
                <div className="flex justify-between items-start">
                    <div className="flex-1 mr-4">
                        <h3 className="text-xl font-semibold text-white mb-2">
                            {session.team_name}
                        </h3>
                        <div className="space-y-1 text-sm text-gray-400">
                            <p className="break-words">URL: {session.footage_url}</p>
                            <p>Created: {new Date(session.created_at).toLocaleDateString()}</p>
                            <p>Session ID: {session.id.slice(0, 8)}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className={`px-4 py-2 rounded-full text-sm font-medium ${session.status === 'PENDING'
                            ? 'bg-yellow-600/20 text-yellow-400 border border-yellow-600'
                            : 'bg-green-600/20 text-green-400 border border-green-600'
                            }`}>
                            {session.status}
                        </span>
                        <span className="text-blue-400">→</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default SessionCard; 