import React, { useState, useEffect } from 'react';
import sessionService from '../services/sessionService';

function SessionDataUpload({ session, onUpdate }) {
    const [jsonData, setJsonData] = useState('');

    // Update textarea when session data changes
    useEffect(() => {
        if (session.session_data) {
            setJsonData(JSON.stringify(session.session_data, null, 2));
        }
    }, [session.session_data]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const data = JSON.parse(jsonData);
            await sessionService.updateSessionData(session.id, data);
            onUpdate();
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <div className="bg-gray-900/50 border border-gray-700 p-4 rounded-lg mt-4">
            <h4 className="text-blue-400 font-medium mb-4">Session Data (JSON)</h4>
            <form onSubmit={handleSubmit} className="space-y-4">
                <textarea
                    value={jsonData}
                    onChange={(e) => setJsonData(e.target.value)}
                    className="w-full h-64 bg-gray-800 text-white px-3 py-2 rounded font-mono text-sm"
                    placeholder="Paste JSON here..."
                />
                <button
                    type="submit"
                    className="bg-blue-500/20 text-blue-400 px-4 py-2 rounded hover:bg-blue-500/30"
                >
                    Update Session Data
                </button>
            </form>
        </div>
    );
}

export default SessionDataUpload; 