import React, { useState } from 'react';

const TeamsList = ({ teams, onTeamClick, onDeleteClick }) => {
    const [currentPage, setCurrentPage] = useState(1);
    const [showTeamMembers, setShowTeamMembers] = useState(false);
    const [selectedTeam, setSelectedTeam] = useState(null);
    const [sortDirection, setSortDirection] = useState('desc'); // 'desc' for newest first
    const teamsPerPage = 10;
    
    // Get current user from localStorage
    const user = JSON.parse(localStorage.getItem('user'));
    const isCompanyMember = user?.role === 'COMPANY_MEMBER';
    
    // Sort teams by creation date
    const sortedTeams = [...teams].sort((a, b) => {
        const comparison = new Date(b.created_at) - new Date(a.created_at);
        return sortDirection === 'desc' ? comparison : -comparison;
    });
    
    // Calculate pagination with sorted teams
    const indexOfLastTeam = currentPage * teamsPerPage;
    const indexOfFirstTeam = indexOfLastTeam - teamsPerPage;
    const currentTeams = sortedTeams.slice(indexOfFirstTeam, indexOfLastTeam);
    const totalPages = Math.ceil(teams.length / teamsPerPage);

    const handlePageChange = (pageNumber) => {
        setCurrentPage(pageNumber);
    };

    const toggleSortDirection = () => {
        setSortDirection(prev => prev === 'desc' ? 'asc' : 'desc');
    };

    const handleTeamClick = (team) => {
        setSelectedTeam(team);
        onTeamClick(team.id, team.name);
        setShowTeamMembers(true);
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-GB'); // This will format as DD/MM/YYYY
    };

    return (
        <div>
            <div className="mb-4 flex justify-end">
                <button
                    onClick={toggleSortDirection}
                    className="px-4 py-2 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors"
                >
                    Sort by Date: {sortDirection === 'desc' ? 'Newest First' : 'Oldest First'}
                </button>
            </div>
            <div className="space-y-4">
                {currentTeams.map(team => (
                    <div key={team.id} 
                         className="bg-gray-800 p-6 rounded-lg border-l-4 border-green-500 
                                  hover:bg-gray-750 transition-colors">
                        <div className="flex flex-col h-full">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="text-xl font-bold text-white">{team.name}</h3>
                                    <div className="text-sm text-gray-400 mt-2 space-y-1">
                                        <p>Team Code: {team.team_code}</p>
                                        <p>Created: {formatDate(team.created_at)}</p>
                                        <p>Valid Sessions: {team.valid_session_count}</p>
                                        <div className="space-y-2">
                                            <button
                                                onClick={() => handleTeamClick(team)}
                                                className="text-blue-400 hover:text-blue-300 block"
                                            >
                                                View Team Members
                                            </button>
                                            {isCompanyMember && (
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        onDeleteClick(team.id);
                                                    }}
                                                    className="text-red-400 hover:text-red-300 block"
                                                >
                                                    Delete Team
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                                <span className={`px-4 py-2 rounded-full text-sm font-medium ${
                                    team.subscription_status === 'ACTIVE' 
                                    ? 'bg-green-600/20 text-green-400 border border-green-600' 
                                    : 'bg-yellow-600/20 text-yellow-400 border border-yellow-600'
                                }`}>
                                    {team.subscription_status}
                                </span>
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

export default TeamsList;