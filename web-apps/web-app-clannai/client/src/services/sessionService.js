import api from './api';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

const sessionService = {
    getSessions: async () => {
        try {
            const response = await api.get('/sessions');
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to fetch sessions');
        }
    },

    createSession: async (url, teamName, teamColor) => {
        try {
            const response = await api.post('/sessions/create', {
                footage_url: url,
                team_name: teamName,
                team_color: teamColor
            });
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to create session');
        }
    },

    deleteSession: async (sessionId) => {
        try {
            await api.delete(`/sessions/${sessionId}`);
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to delete session');
        }
    },

    getAllSessions: async () => {
        try {
            const response = await api.get('/sessions/all');
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to fetch all sessions');
        }
    },

    getTeamsWithValidSessions: async () => {
        try {
            const response = await api.get('/sessions/teams-with-valid-sessions');
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to fetch teams with valid sessions');
        }
    },

    toggleSessionStatus: async (sessionId) => {
        try {
            const response = await api.put(`/sessions/${sessionId}/toggle-status`);
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to toggle session status');
        }
    },

    addAnalysis: async (formData) => {
        try {
            const response = await api.post('/sessions/analysis', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to add analysis');
        }
    },

    deleteAnalysis: async (sessionId, type) => {
        try {
            const response = await api.delete(`/sessions/analysis/${sessionId}/${type}`);
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to delete analysis');
        }
    },

    updateSessionStatus: async (sessionId, newStatus) => {
        try {
            const response = await api.patch(`/sessions/${sessionId}/toggle-status`);
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to update session status');
        }
    },

    getUserSessions: async () => {
        try {
            const response = await api.get('/sessions/user');
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to fetch sessions');
        }
    },

    getSessionDetails: async (id) => {
        try {
            const response = await api.get(`/sessions/${id}`);
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to fetch session details');
        }
    },

    updateTeamMetrics: async (sessionId, metrics) => {
        try {
            const response = await api.put(`/sessions/${sessionId}/metrics`, metrics);
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to update metrics');
        }
    },

    getSessionStats: async () => {
        try {
            const response = await api.get('/sessions/stats');
            return response.data;
        } catch (err) {
            throw err;
        }
    },

    updateSessionTitle: async (sessionId, newTitle) => {
        try {
            const response = await api.put(`/sessions/${sessionId}/title`, {
                team_name: newTitle
            });
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to update session title');
        }
    },

    updateSessionData: async (sessionId, sessionData) => {
        try {
            const response = await api.put(`/sessions/${sessionId}/session-data`, sessionData);
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to update session data');
        }
    },
};

export default sessionService; 