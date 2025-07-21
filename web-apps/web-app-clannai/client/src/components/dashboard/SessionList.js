import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SessionList = ({ sessions, view, setView, sortOrder, setSortOrder }) => {
    const navigate = useNavigate();
    const [currentPage, setCurrentPage] = useState(1);
    const sessionsPerPage = 10;

    const organizedSessions = {
        pending: sessions.filter(s => s.status === 'PENDING')
            .sort((a, b) => {
                const dateA = new Date(a.created_at);
                const dateB = new Date(b.created_at);
                return sortOrder === 'oldest' ? dateA - dateB : dateB - dateA;
            }),
        completed: sessions.filter(s => s.status === 'REVIEWED')
            .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    };

    // Calculate pagination
    const currentSessions = view === 'PENDING' ? organizedSessions.pending : organizedSessions.completed;
    const indexOfLastSession = currentPage * sessionsPerPage;
    const indexOfFirstSession = indexOfLastSession - sessionsPerPage;
    const currentPageSessions = currentSessions.slice(indexOfFirstSession, indexOfLastSession);
    const totalPages = Math.ceil(currentSessions.length / sessionsPerPage);

    const handlePageChange = (pageNumber) => {
        setCurrentPage(pageNumber);
    };

    const getSourceType = (url) => {
        if (!url) return 'Unknown';
        if (url.includes('veo')) return '🎥 Veo';
        if (url.includes('youtube')) return '📺 YouTube';
        return '🔗 Other';
    };

    const getDaysWaiting = (createdAt) => {
        const days = Math.floor((new Date() - new Date(createdAt)) / (1000 * 60 * 60 * 24));
        return days;
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-5">
                <div className="flex gap-2">
                    <button
                        onClick={() => {
                            setView('PENDING');
                            setCurrentPage(1);
                        }}
                        className={`px-4 py-2 rounded ${view === 'PENDING' ? 'bg-yellow-500' : 'bg-gray-700'}`}
                    >
                        Pending ({organizedSessions.pending.length})
                    </button>
                    <button
                        onClick={() => {
                            setView('COMPLETED');
                            setCurrentPage(1);
                        }}
                        className={`px-4 py-2 rounded ${view === 'COMPLETED' ? 'bg-green-500' : 'bg-gray-700'}`}
                    >
                        Completed ({organizedSessions.completed.length})
                    </button>
                </div>
                <button
                    onClick={() => setSortOrder(current => current === 'oldest' ? 'newest' : 'oldest')}
                    className="bg-gray-700 px-4 py-2 rounded hover:bg-gray-600 transition-colors"
                >
                    {sortOrder === 'oldest' ? '⬆️ Oldest First' : '⬇️ Newest First'}
                </button>
            </div>

            <div className="space-y-4">
                {currentPageSessions.map(session => (
                    <div
                        key={session.id}
                        onClick={() => navigate(`/company/analysis/${session.id}`)}
                        className={`bg-gray-800 p-6 rounded-lg border-l-4 cursor-pointer 
                                 hover:bg-gray-750 transition-colors ${
                                     view === 'PENDING' ? 'border-yellow-500' : 'border-green-500'
                                 }`}
                    >
                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="text-xl font-bold text-white">{session.team_name}</h3>
                                <div className="text-sm text-gray-400 mt-2 space-y-1">
                                    {view === 'PENDING' ? (
                                        <>
                                            <p>Waiting: {getDaysWaiting(session.created_at)} days</p>
                                            <p>Source: {getSourceType(session.footage_url)}</p>
                                            <p>URL: <a href={session.footage_url} target="_blank" rel="noopener noreferrer"
                                                className="text-blue-400 hover:underline"
                                                onClick={e => e.stopPropagation()}>
                                                {session.footage_url}
                                            </a></p>
                                            <p>Uploaded by: {session.uploaded_by_email || 'Unknown'}</p>
                                        </>
                                    ) : (
                                        <>
                                            <p>Completed: {new Date(session.updated_at).toLocaleDateString()}</p>
                                            <p>Analyst: {session.analyst_name || 'Unknown'}</p>
                                        </>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
                <div className="flex justify-center items-center gap-2 mt-6">
                    <button
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        className={`px-4 py-2 rounded ${
                            currentPage === 1 
                            ? 'bg-gray-700 text-gray-500 cursor-not-allowed' 
                            : 'bg-gray-700 text-white hover:bg-gray-600'
                        }`}
                    >
                        Previous
                    </button>
                    
                    <div className="flex gap-2">
                        {[...Array(totalPages)].map((_, index) => (
                            <button
                                key={index + 1}
                                onClick={() => handlePageChange(index + 1)}
                                className={`w-10 h-10 rounded ${
                                    currentPage === index + 1
                                    ? 'bg-green-500 text-white'
                                    : 'bg-gray-700 text-white hover:bg-gray-600'
                                }`}
                            >
                                {index + 1}
                            </button>
                        ))}
                    </div>

                    <button
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        className={`px-4 py-2 rounded ${
                            currentPage === totalPages 
                            ? 'bg-gray-700 text-gray-500 cursor-not-allowed' 
                            : 'bg-gray-700 text-white hover:bg-gray-600'
                        }`}
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
};

export default SessionList;
