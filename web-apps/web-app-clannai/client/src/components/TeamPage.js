import React, { useState } from 'react';
import teamService from '../services/teamService';

function TeamPage({ 
  sessions, 
  teamMembers, 
  onUploadClick, 
  onJoinClick, 
  generateInviteMessage, 
  copyInviteMessage 
}) {
  const teamName = sessions[0]?.team_name;
  const [teamColor, setTeamColor] = useState(sessions[0]?.team_color || '#D1FB7A');
  const [showColorModal, setShowColorModal] = useState(false);

  const colorOptions = [
    { name: 'Team Green', value: '#016F32' },  // Deep team green
    { name: 'Navy', value: '#1B365D' },        // Classic football navy
    { name: 'Maroon', value: '#7A263A' },      // Traditional team maroon
    { name: 'Royal Blue', value: '#0047AB' },  // Classic royal blue
    { name: 'Forest Green', value: '#228B22' }, // Forest green
    { name: 'Deep Purple', value: '#4B0082' }  // Deep purple
  ];

  const handleColorChange = async (color) => {
    try {
      setTeamColor(color);
      await teamService.updateTeamColor(sessions[0]?.team_id, color);
    } catch (err) {
      console.error('Failed to update team color:', err);
    }
  };

  const handleCopyTeamCode = () => {
    if (sessions[0]?.team_code) {
      navigator.clipboard.writeText(sessions[0].team_code);
      // Using the existing feedback system through copyInviteMessage
      copyInviteMessage(sessions[0].team_code, teamName, true);
    }
  };

  if (!teamName) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">No Team Yet</h2>
        <p className="text-gray-600 mb-4">Upload your first match or join an existing team to get started.</p>
        <div className="flex gap-4">
          <button 
            onClick={onUploadClick} 
            className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium"
          >
            Upload Match
          </button>
          <button 
            onClick={onJoinClick}
            className="bg-[#B9E8EB] text-gray-900 px-6 py-2.5 rounded-lg font-medium"
          >
            Join Team
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-2xl font-bold text-gray-900">{teamName}</h2>
          <button
            onClick={() => setShowColorModal(true)}
            className="px-4 py-2 rounded-lg text-sm bg-[#9FEB3] text-gray-900 hover:bg-[#9FEB3]/90 transition-colors"
          >
            🎨 Team Color
          </button>
        </div>

        {/* Color Modal */}
        {showColorModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-sm w-full">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Choose Team Color</h3>
              <div className="grid grid-cols-3 gap-4 mb-6">
                {colorOptions.map((color) => (
                  <button
                    key={color.value}
                    onClick={() => {
                      handleColorChange(color.value);
                      setShowColorModal(false);
                    }}
                    className="flex flex-col items-center gap-2 p-2 rounded-lg hover:bg-gray-50"
                  >
                    <div 
                      className={`w-12 h-12 rounded-full border-2 ${
                        teamColor === color.value ? 'border-gray-900' : 'border-transparent'
                      }`}
                      style={{ backgroundColor: color.value }}
                    />
                    <span className="text-sm text-gray-600">{color.name}</span>
                  </button>
                ))}
              </div>
              <button
                onClick={() => setShowColorModal(false)}
                className="w-full px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-4">
            <p className="text-gray-600">
              Team Code: <span 
                onClick={handleCopyTeamCode}
                className="font-medium cursor-pointer hover:text-gray-900 transition-colors"
              >
                {sessions[0]?.team_code}
              </span>
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600 whitespace-pre-line mb-3">
              {generateInviteMessage(sessions[0]?.team_code, teamName)}
            </p>
            <button 
              onClick={() => copyInviteMessage(sessions[0]?.team_code, teamName)}
              className="text-sm px-4 py-2 bg-[#016F32]/20 text-[#016F32] rounded-lg border border-[#016F32]/30 hover:bg-[#016F32]/30"
            >
              📋 Copy Invite Message
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Team Members</h3>
        <div className="space-y-2">
          {teamMembers.map(member => (
            <div key={member.user_id} className="flex justify-between items-center py-2">
              <span className="text-gray-600">{member.email}</span>
              {member.is_admin && (
                <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">Admin</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default TeamPage; 