import api from './api';
import axios from 'axios';

const teamService = {
    async getUserTeams() {
        try {
            const response = await api.get('/teams/user');
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to fetch teams');
        }
    },

    createTeam: async (name, teamCode) => {
        try {
            const response = await api.post('/teams/create', {
                name,
                team_code: teamCode
            });
            return response.data;
        } catch (error) {
            throw error.response?.data?.error || 'Failed to create team';
        }
    },

    joinTeam: async (teamCode) => {
        try {
            const response = await api.post('/teams/join', {
                team_code: teamCode.trim().toUpperCase()
            });
            return response.data;
        } catch (error) {
            if (error.response?.data?.team_id) {
                return error.response.data;
            }
            if (error.response?.status === 404) {
                throw new Error('Team not found. Please check the team code.');
            }
            throw new Error(error.response?.data?.error || 'Failed to join team');
        }
    },

    getTeamMembers: async (teamId) => {
        try {
            const response = await api.get(`/teams/${teamId}/members`);
            return response.data;
        } catch (error) {
            console.error('Team service error:', error);
            throw error;
        }
    },

    async removeTeamMember(teamId, userId) {
        console.log('teamService.removeTeamMember called with:', { teamId, userId });
        
        try {
            // Ensure both parameters are strings
            const teamIdStr = String(teamId);
            const userIdStr = String(userId);
            
            console.log('Making API call to:', `/teams/${teamIdStr}/members/${userIdStr}`);
            
            const response = await api.delete(`/teams/${teamIdStr}/members/${userIdStr}`);
            console.log('API response:', response);
            
            return response.data;
        } catch (error) {
            console.error('removeTeamMember error:', error);
            console.error('Error response:', error.response);
            throw new Error(error.response?.data?.error || 'Failed to remove team member');
        }
    },

    async toggleAdminStatus(teamId, userId, isAdmin) {
        try {
            const response = await api.patch(`/teams/${teamId}/members/${userId}/admin`, { isAdmin });
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to update admin status');
        }
    },

    async deleteTeam(teamId) {
        try {
            const response = await api.delete(`/teams/${teamId}`);
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to delete team');
        }
    },

    leaveTeam: async (teamId) => {
        try {
            await api.post(`/teams/${teamId}/leave`);
        } catch (error) {
            throw error.response?.data?.error || 'Failed to leave team';
        }
    },

    updateTeamColor: async (teamId, color) => {
        try {
            const response = await axios.patch(`/api/teams/${teamId}/color`, { color });
            return response.data;
        } catch (error) {
            throw error.response?.data || error;
        }
    }
};

export default teamService;