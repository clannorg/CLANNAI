import React from 'react';
import playerIcon from '../assets/images/icon-player.png';

function TeamSection({ sessions, teamMembers, onCopyInvite, onUploadClick, onJoinClick }) {
  const isOnlyDemo = sessions.length === 1 && sessions[0]?.team_name === "ClannAI demo";
  const teamName = sessions[0]?.team_name;
  const teamCode = sessions[0]?.team_code;

  if (isOnlyDemo) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Create or Join Team</h2>
        <p className="text-gray-600 mb-4">
          Upload your first match or join an existing team to get started.
        </p>
        <div className="flex gap-4">
          <button 
            onClick={onUploadClick} 
            className="bg-[#016F32] text-white px-6 py-2.5 rounded-lg font-medium"
          >
            Upload a match
          </button>
          <button 
            onClick={onJoinClick}
            className="bg-[#B9E8EB] text-gray-900 px-6 py-2.5 rounded-lg font-medium"
          >
            Join team
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Team Info */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{teamName}</h2>
            <p className="text-gray-600">Team Code: <span className="font-mono">{teamCode}</span></p>
          </div>
          <button
            onClick={() => onCopyInvite(teamCode, teamName)}
            className="text-sm px-4 py-2 bg-[#016F32]/20 text-[#016F32] rounded-lg border border-[#016F32]/30 hover:bg-[#016F32]/30"
          >
            📋 Copy Invite Link
          </button>
        </div>
      </div>

      {/* Team Members */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Team Members</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {teamMembers.map(member => (
            <div key={member.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <img 
                src={member.profile_image || playerIcon} 
                alt={member.name} 
                className="w-10 h-10 rounded-full object-cover"
              />
              <div>
                <p className="font-medium text-gray-900">{member.name}</p>
                <p className="text-sm text-gray-500">{member.email}</p>
              </div>
              {member.is_admin && (
                <span className="ml-auto text-xs bg-[#016F32]/20 text-[#016F32] px-2 py-1 rounded">
                  Admin
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default TeamSection; 