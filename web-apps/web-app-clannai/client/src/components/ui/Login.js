const handleLogin = async (e) => {
    e.preventDefault();
    try {
        const response = await userService.validateUser(email, password);
        navigate('/dashboard');
    } catch (error) {
        setError(error.message);
    }
}; 