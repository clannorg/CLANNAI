import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Cancel() {
    const navigate = useNavigate();

    useEffect(() => {
        // Short delay then redirect to dashboard
        setTimeout(() => {
            navigate('/dashboard');
        }, 2000);
    }, [navigate]);

    return (
        <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center">
            <h1 className="text-3xl font-bold mb-4">Payment Cancelled</h1>
            <p className="text-gray-400 mb-8">No changes have been made to your account</p>
            <p className="mt-4 text-gray-400">Redirecting to your dashboard...</p>
        </div>
    );
}

export default Cancel; 