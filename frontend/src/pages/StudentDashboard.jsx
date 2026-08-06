import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import JobCard from '../components/JobCard';
import '../App.css';

function StudentDashboard() {
  const [activeView, setActiveView] = useState('profile');
  const [profile, setProfile] = useState(null);
  const [recommendedJobs, setRecommendedJobs] = useState([]);
  const [applications, setApplications] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const loadData = async () => {
      const [profileRes, recommendedRes, applicationsRes] = await Promise.all([
        axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/students/profile`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/jobs/recommended`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/applications`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      setProfile(profileRes.data.student);
      setRecommendedJobs(recommendedRes.data.jobs || []);
      setApplications(applicationsRes.data.applications || []);
    };
    loadData();
  }, []);

  return (
    <>
      <Navbar />
      <main className="dashboard-shell">
        <div className="container dashboard-layout">
          <aside className="sidebar">
            <h3>Student Panel</h3>
            <button className={activeView === 'profile' ? 'active' : ''} onClick={() => setActiveView('profile')}>Profile</button>
            <button className={activeView === 'recommended' ? 'active' : ''} onClick={() => setActiveView('recommended')}>Recommended Jobs</button>
            <button className={activeView === 'applications' ? 'active' : ''} onClick={() => setActiveView('applications')}>My Applications</button>
            <Link to="/profile" className="btn btn-primary" style={{ display: 'inline-block', marginTop: '1rem' }}>Edit Profile</Link>
          </aside>
          <section>
            {activeView === 'profile' && profile && (
              <div className="dashboard-card">
                <h2>Welcome, {profile.name}</h2>
                <p><strong>University:</strong> {profile.university}</p>
                <p><strong>Career:</strong> {profile.career}</p>
                <p><strong>Semester:</strong> {profile.semester}</p>
                <p><strong>Skills:</strong> {profile.skills || 'Add your skills'}</p>
                <p><strong>Certifications:</strong> {profile.certifications || 'Add certifications'}</p>
              </div>
            )}
            {activeView === 'recommended' && (
              <div className="dashboard-card">
                <h2>Recommended Jobs</h2>
                {recommendedJobs.length === 0 ? <p className="empty-state">No recommendations yet.</p> : recommendedJobs.map((job) => <JobCard key={job.id} job={job} showApply={false} />)}
              </div>
            )}
            {activeView === 'applications' && (
              <div className="dashboard-card">
                <h2>My Applications</h2>
                {applications.length === 0 ? <p className="empty-state">You have not applied yet.</p> : applications.map((app) => (
                  <div key={app.id} className="list-item">
                    <strong>{app.title}</strong>
                    <p>Status: {app.status}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </main>
      <Footer />
    </>
  );
}

export default StudentDashboard;
