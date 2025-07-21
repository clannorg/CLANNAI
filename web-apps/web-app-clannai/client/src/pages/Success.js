import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import teamService from '../services/teamService';

function Success() {
    const navigate = useNavigate();
    const [status, setStatus] = useState('processing');
    const [user] = useState(() => JSON.parse(localStorage.getItem('user')));

    useEffect(() => {
        if (!user?.teamId) {
            navigate('/dashboard');
            return;
        }

        let attempts = 0;
        const maxAttempts = 5; // 5 seconds max wait

        const pollTeamStatus = async () => {
            try {
                const status = await teamService.getTeamStatus(user.teamId);
                if (status.isPremium) {
                    setStatus('completed');
                    setTimeout(() => navigate('/dashboard'), 1000);
                    return;
                }
                
                attempts++;
                if (attempts >= maxAttempts) {
                    // If we've waited 5 seconds, just go to dashboard
                    navigate('/dashboard');
                    return;
                }
                
                // Poll again in 1 second
                setTimeout(pollTeamStatus, 1000);
            } catch (err) {
                console.error('Error polling status:', err);
                // On error, wait brief moment then go to dashboard
                setTimeout(() => navigate('/dashboard'), 2000);
            }
        };

        pollTeamStatus();
    }, [navigate, user]);

    return (
        <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center">
            <h1 className="text-3xl font-bold mb-4">Payment Successful!</h1>
            <p className="text-gray-400 mb-8">Your team is now premium with a 7-day free trial</p>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
            <p className="mt-4 text-gray-400">
                {status === 'completed' ? 'Taking you to dashboard...' : 'Confirming your upgrade...'}
            </p>
        </div>
    );
}

export default Success; 