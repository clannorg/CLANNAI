import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

function NavBar() {
  const navigate = useNavigate();
  const location = useLocation();
  
  return (
    <div style={{
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      height: '60px',
      backgroundColor: '#333333',
      display: 'flex',
      justifyContent: 'space-between',
      padding: '0 40px',
      boxShadow: '0 -2px 10px rgba(0,0,0,0.2)'
    }}>
      <button
        onClick={() => navigate('/sessions')}
        style={{
          background: 'none',
          border: 'none',
          color: location.pathname === '/sessions' ? '#016F33' : '#888888',
          fontSize: '16px',
          cursor: 'pointer',
          padding: '0 20px',
          height: '100%'
        }}
      >
        Sessions
      </button>
      <button
        onClick={() => navigate('/profile')}
        style={{
          background: 'none',
          border: 'none',
          color: location.pathname === '/profile' ? '#016F33' : '#888888',
          fontSize: '16px',
          cursor: 'pointer',
          padding: '0 20px',
          height: '100%'
        }}
      >
        Profile
      </button>
    </div>
  );
}

export default NavBar;
