
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store/store';
import MainLayout from './layouts/MainLayout';
import Login from './pages/Login';
import Signup from './pages/Signup';
import SubmitPetition from './pages/SubmitPetition';
import Dashboard from './pages/Dashboard';
import OfficerDashboard from './pages/OfficerDashboard';
import AdminDashboard from './pages/AdminDashboard';

function App() {
  return (
    <Provider store={store}>
      <Router>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<div className="text-center mt-20"><h1 className="text-4xl font-bold text-gray-900">Welcome to AI Petition System</h1><p className="mt-4 text-xl text-gray-500">Submit and track your grievances with AI-powered efficiency.</p></div>} />
            <Route path="login" element={<Login />} />
            <Route path="signup" element={<Signup />} />
            <Route path="submit-petition" element={<SubmitPetition />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="officer" element={<OfficerDashboard />} />
            <Route path="admin" element={<AdminDashboard />} />
          </Route>
        </Routes>
      </Router>
    </Provider>
  );
}

export default App;
