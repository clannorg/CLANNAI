import api from './api';

const userService = {
    async validateUser(email, password) {
        try {
            const response = await api.post('/auth/login', { email, password });
            // Store token and user data
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('user', JSON.stringify(response.data));
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Login failed');
        }
    },

    async createUser(email, password, termsAccepted) {
        if (!termsAccepted) {
            throw new Error('Terms & Conditions must be accepted');
        }
        try {
            const response = await api.post('/auth/register', {
                email,
                password,
                termsAccepted
            });
            console.log('Registration response:', response.data);
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('user', JSON.stringify(response.data));
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || 'Registration failed');
        }
    },

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    }
};

export default userService;
