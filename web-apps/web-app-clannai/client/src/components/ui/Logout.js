import userService from '../services/userService';
import { useNavigate } from 'react-router-dom';

function Logout() {
    const navigate = useNavigate();

    const handleLogout = () => {
        userService.logout();
        navigate('/login');
    };

    return (
        <button onClick={handleLogout}>
            Logout
        </button>
    );
} 