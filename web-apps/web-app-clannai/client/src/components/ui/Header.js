import { useNavigate } from 'react-router-dom';
import clannLogo from '../../assets/images/clann.ai-white.png';

function Header() {
    const navigate = useNavigate();

    return (
        <nav className="absolute top-0 left-0 right-0 pt-8 z-50">
            <div className="max-w-7xl mx-auto px-8 flex justify-between items-center">
                <div className="cursor-pointer">
                    <img src={clannLogo} alt="Clann" className="h-7" />
                </div>
                <div className="flex items-center gap-6">
                    <button 
                        onClick={() => navigate('/login')}
                        className="text-white text-base font-medium hover:text-gray-300 px-6 py-2.5 text-[15px]"
                    >
                        Sign in
                    </button>
                    <button 
                        onClick={() => navigate('/register')}
                        className="bg-black px-6 py-2.5 rounded-lg text-base font-medium text-white hover:bg-gray-900 text-[15px]"
                    >
                        GET STARTED
                    </button>
                </div>
            </div>
        </nav>
    );
}

export default Header; 