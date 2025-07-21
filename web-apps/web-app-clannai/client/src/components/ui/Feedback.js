import React from 'react';

function Feedback({ type, message }) {
    const getBackgroundColor = () => {
        switch (type) {
            case 'success':
                return 'bg-green-500/90';
            case 'error':
                return 'bg-red-500/90';
            case 'info':
                return 'bg-blue-500/90';
            default:
                return 'bg-gray-500/90';
        }
    };

    return (
        <div className={`${getBackgroundColor()} text-white px-4 py-2 rounded-lg shadow-lg`}>
            {message}
        </div>
    );
}

export default Feedback; 