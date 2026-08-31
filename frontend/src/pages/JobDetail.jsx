import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function JobDetail() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [message, setMessage] = useState('');
  const [isApplying, setIsApplying] = useState(false);
  const [hasApplied, setHasApplied] = useState(false);
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  useEffect(() => {
    const loadJob = async () => {
      try {
        const { data } = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/jobs/${jobId}`);
        setJob(data.job);
      } catch (err) {
        setMessage(err.response?.data?.message || 'Job not found.');
      }
    };
    loadJob();
    if (token && role === 'student') {
      const checkApplication = async () => {
        try {
          const { data } = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/applications`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          const applied = data.applications.some((app) => app.job_id === Number(jobId) || app.title === job?.title);
          setHasApplied(applied);
        } catch (_err) {}
      };
      if (job) checkApplication();
    }
  }, [jobId, token, role, job?.title]);

  const handleApply = async () => {
    if (!token) {
      setMessage('Please log in to apply.');
      return;
    }
    if (role !== 'student') {
      setMessage('Only students can apply to jobs.');
      return;
    }
    if (isApplying) return;
    try {
      setIsApplying(true);
      await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/applications`, { jobId: Number(jobId) }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage('Application submitted successfully!');
      setHasApplied(true);
    } catch (err) {
      setMessage(err.response?.data?.message || 'Unable to submit application.');
    } finally {
      setIsApplying(false);
    }
  };

  if (message && message.includes('not found')) {
    return (
      <>
        <Navbar />
        <main className="page-shell">
          <div className="container">
            <p style={{ color: 'crimson' }}>{message}</p>
            <Link to="/jobs" className="btn btn-primary">Back to Jobs</Link>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  if (!job) {
    return (
      <>
        <Navbar />
        <main className="page-shell">
          <div className="container">
            <p>Loading job details...</p>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Navbar />
      <main className="page-shell">
        <div className="container">
          <div className="card">
            <Link to="/jobs" className="btn btn-secondary" style={{ marginBottom: '1rem' }}>← Back to Jobs</Link>
            <div className="card-header">
              <h2>{job.title}</h2>
              <span className="badge">{job.job_type}</span>
            </div>
            <p><strong>Company:</strong> {job.company_name}</p>
            <p><strong>Location:</strong> {job.location}</p>
            <hr />
            <h3>Description</h3>
            <p>{job.description}</p>
            <h3>Required Skills</h3>
            <p>{job.required_skills}</p>
            {message && <p style={{ color: message.includes('success') ? 'green' : 'crimson' }}>{message}</p>}
            <div className="hero-actions" style={{ marginTop: '2rem' }}>
              {role === 'student' && (
                <button
                  className="btn btn-primary"
                  onClick={handleApply}
                  disabled={isApplying || hasApplied}
                >
                  {isApplying ? 'Submitting...' : hasApplied ? 'Already Applied' : 'Apply Now'}
                </button>
              )}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

export default JobDetail;
