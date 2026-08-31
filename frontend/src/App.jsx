import { Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Jobs from './pages/Jobs';
import StudentDashboard from './pages/StudentDashboard';
import CompanyDashboard from './pages/CompanyDashboard';
import Profile from './pages/Profile';
import CreateJob from './pages/CreateJob';
import RecommendedJobs from './pages/RecommendedJobs';
import JobDetail from './pages/JobDetail';

function ProtectedRoute({ children, role }) {
  const token = localStorage.getItem('token');
  const storedRole = localStorage.getItem('role');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  if (role && storedRole !== role) {
    return <Navigate to={storedRole === 'company' ? '/company-dashboard' : '/student-dashboard'} replace />;
  }
  return children;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/jobs" element={<Jobs />} />
      <Route path="/student-dashboard" element={<ProtectedRoute role="student"><StudentDashboard /></ProtectedRoute>} />
      <Route path="/company-dashboard" element={<ProtectedRoute role="company"><CompanyDashboard /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute role="student"><Profile /></ProtectedRoute>} />
      <Route path="/recommended-jobs" element={<ProtectedRoute role="student"><RecommendedJobs /></ProtectedRoute>} />
      <Route path="/job/:jobId" element={<JobDetail />} />
      <Route path="/create-job" element={<ProtectedRoute role="company"><CreateJob /></ProtectedRoute>} />
      <Route path="/edit-job/:jobId" element={<ProtectedRoute role="company"><CreateJob /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
