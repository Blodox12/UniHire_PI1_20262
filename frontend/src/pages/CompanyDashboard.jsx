import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import '../App.css';

function CompanyDashboard() {
  const [activeView, setActiveView] = useState('jobs');
  const [jobs, setJobs] = useState([]);
  const [applicants, setApplicants] = useState([]);
  const [message, setMessage] = useState('');

  const loadData = async () => {
    const token = localStorage.getItem('token');
    const [jobsRes, applicantsRes] = await Promise.all([
      axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/companies/jobs`, { headers: { Authorization: `Bearer ${token}` } }),
      axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/applications/company`, { headers: { Authorization: `Bearer ${token}` } })
    ]);
    setJobs(jobsRes.data.jobs || []);
    setApplicants(applicantsRes.data.applicants || []);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDelete = async (jobId) => {
    const token = localStorage.getItem('token');
    try {
      await axios.delete(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/jobs/${jobId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage('Job deleted successfully.');
      loadData();
    } catch (err) {
      setMessage(err.response?.data?.message || 'Unable to delete job.');
    }
  };

  return (
    <>
      <Navbar />
      <main className="dashboard-shell">
        <div className="container dashboard-layout">
          <aside className="sidebar">
            <h3>Company Panel</h3>
            <button className={activeView === 'jobs' ? 'active' : ''} onClick={() => setActiveView('jobs')}>My Jobs</button>
            <button className={activeView === 'applicants' ? 'active' : ''} onClick={() => setActiveView('applicants')}>Applicants</button>
            <Link to="/create-job" className="btn btn-primary" style={{ display: 'inline-block', marginTop: '1rem' }}>Create Job</Link>
          </aside>
          <section>
            {message && <p style={{ color: 'green' }}>{message}</p>}
            {activeView === 'jobs' && (
              <div className="dashboard-card">
                <h2>My Jobs</h2>
                {jobs.length === 0 ? <p className="empty-state">No jobs posted yet.</p> : jobs.map((job) => (
                  <div key={job.id} className="list-item">
                    <strong>{job.title}</strong>
                    <p>{job.description}</p>
                    <div className="hero-actions">
                      <Link to={`/edit-job/${job.id}`} className="btn btn-secondary">Edit</Link>
                      <button className="btn btn-secondary" onClick={() => handleDelete(job.id)}>Delete</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {activeView === 'applicants' && (
              <div className="dashboard-card">
                <h2>Applicants</h2>
                {applicants.length === 0 ? <p className="empty-state">No applicants yet.</p> : applicants.map((app) => (
                  <div key={app.id} className="list-item">
                    <strong>{app.student_name}</strong>
                    <p>{app.title} — {app.status}</p>
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

export default CompanyDashboard;
