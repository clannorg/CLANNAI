import api from './api';

const databaseService = {
    getDatabaseContent: async () => {
        try {
            const response = await api.get('/sessions/database-content');
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Failed to fetch database content');
        }
    }
};

export default databaseService; 