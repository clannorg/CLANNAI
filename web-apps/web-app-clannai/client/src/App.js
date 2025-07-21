import { Routes, Route } from 'react-router-dom';
import Sessions from './pages/Sessions';
import SessionDetails from './pages/SessionDetails';
import CompanyDashboard from './pages/CompanyDashboard';
import Success from './pages/Success';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Sessions />} />
      <Route path="/session/:sessionId" element={<SessionDetails />} />
      <Route path="/company" element={<CompanyDashboard />} />
      <Route path="/success" element={<Success />} />
    </Routes>
  );
}

export default App;