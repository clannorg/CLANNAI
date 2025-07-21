import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import clannLogo from '../../assets/images/clann.ai-white.png';

function TopNav({ onSignInClick, onGetStartedClick, isLoggedIn, onLogout }) {
    const navigate = useNavigate();
    const [isOpen, setIsOpen] = useState(false);

    const handleSignIn = () => {
        if (onSignInClick) {
            onSignInClick();
        } else {
            navigate('/login');
        }
        setIsOpen(false);
    };

    const handleGetStarted = () => {
        if (onGetStartedClick) {
            onGetStartedClick();
        } else {
            navigate('/register');
        }
        setIsOpen(false);
    };

    const handleLogout = () => {
        if (onLogout) {
            onLogout();
        }
        setIsOpen(false);
    };

    return (
        <div className="fixed top-0 left-0 right-0 z-50 bg-gray-800/0 backdrop-blur-sm">
            <div className="max-w-7xl mx-auto px-8 py-4">
                <div className="flex justify-between items-center">
                    {/* Logo */}
                    <div className="cursor-pointer" onClick={() => navigate('/dashboard')}>
                        <img src={clannLogo} alt="Clann" className="h-7" />
                    </div>

                    {/* Desktop Navigation */}
                    {!isLoggedIn && (
                        <div className="hidden md:flex items-center gap-6">
                            <button 
                                onClick={handleSignIn}
                                className="text-white text-base font-medium hover:text-gray-300 px-6 py-2.5 text-[15px]"
                            >
                                Sign in
                            </button>
                            <button 
                                onClick={handleGetStarted}
                                className="bg-black px-6 py-2.5 rounded-lg text-base font-medium text-white hover:bg-gray-900 text-[15px]"
                            >
                                Get started
                            </button>
                        </div>
                    )}

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsOpen(!isOpen)}
                        className="text-white p-2 md:hidden"
                    >
                        {isOpen ? (
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        ) : (
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        )}
                    </button>
                </div>
            </div>

            {/* Mobile Menu */}
            {isOpen && (
                <div className="md:hidden border-t border-gray-700/0">
                    <div className="max-w-7xl mx-auto px-8 py-4 space-y-3">
                        {isLoggedIn ? (
                            <button
                                onClick={handleLogout}
                                className="block w-full text-left text-white hover:text-gray-300 py-2"
                            >
                                Logout
                            </button>
                        ) : (
                            <>
                                <button
                                    onClick={handleSignIn}
                                    className="block w-full text-left text-white hover:text-gray-300 py-2"
                                >
                                    Sign in
                                </button>
                                <button
                                    onClick={handleGetStarted}
                                    className="block w-full text-left text-white hover:text-gray-300 py-2"
                                >
                                    Get started
                                </button>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default TopNav;
