import { createBrowserRouter } from 'react-router-dom';
import Login from './pages/Login';
import Sessions from './pages/Sessions';
import SessionDetails from './pages/SessionDetails';
import Profile from './pages/Profile';
import Success from './pages/Success';
import CompanyDashboard from './pages/company/Dashboard';
import Terms from './pages/Terms';
import Privacy from './pages/Privacy';
import SessionAnalysis from './pages/company/SessionAnalysis';
import UserDashboard from './pages/UserDashboard';

const router = createBrowserRouter([
    {
        path: '/',
        element: <Login />,
        errorElement: <div className="min-h-screen bg-gray-900 text-white p-8 flex items-center justify-center">
            <div className="text-center">
                <h1 className="text-2xl font-bold mb-4">Oops! Something went wrong</h1>
                <p className="text-gray-400">Please try again or contact support if the problem persists.</p>
            </div>
        </div>
    },
    {
        path: '/dashboard',
        element: <UserDashboard />
    },
    {
        path: '/sessions',
        element: <Sessions />
    },
    {
        path: '/session/:id',
        element: <SessionDetails />
    },
    {
        path: '/profile',
        element: <Profile />
    },
    {
        path: '/success',
        element: <Success />
    },
    {
        path: '/company',
        element: <CompanyDashboard />
    },
    {
        path: '/terms',
        element: <Terms />
    },
    {
        path: '/privacy',
        element: <Privacy />
    },
    {
        path: '/company/analysis/:id',
        element: <SessionAnalysis />
    }
]);

export default router;