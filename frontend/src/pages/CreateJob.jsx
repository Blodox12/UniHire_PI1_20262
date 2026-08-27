import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function CreateJob() {
  const { jobId } = useParams();
  const isEditing = Boolean(jobId);
  const [form, setForm] = useState({
    title: '',
    description: '',
    required_skills: '',
    location: '',
    job_type: 'Remote'
  });
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isEditing) return;
    const loadJob = async () => {
      try {
        const token = localStorage.getItem('token');
        const { data } = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/companies/jobs`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const job = data.jobs.find((item) => item.id === Number(jobId));
        if (!job) {
          setMessage('Job not found.');
          return;
        }
        setForm({
          title: job.title,
          description: job.description,
          required_skills: job.required_skills,
          location: job.location,
          job_type: job.job_type
        });
      } catch (err) {
        setMessage(err.response?.data?.message || 'Unable to load job.');
      }
    };
    loadJob();
  }, [isEditing, jobId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;
    const token = localStorage.getItem('token');
    try {
      setIsSubmitting(true);
      setMessage('');
      const method = isEditing ? 'put' : 'post';
      const url = isEditing ? `/api/jobs/${jobId}` : '/api/jobs';
      await axios[method](`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}${url}`, form, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage(isEditing ? 'Job updated successfully.' : 'Job posted successfully.');
      setTimeout(() => navigate('/company-dashboard'), 800);
    } catch (err) {
      setMessage(err.response?.data?.message || 'Unable to create job.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="page-shell">
        <div className="container">
          <div className="card form-card">
            <h2>{isEditing ? 'Edit Job' : 'Create Job'}</h2>
            {message && <p style={{ color: 'green' }}>{message}</p>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Title</label>
                <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows="4" required />
              </div>
              <div className="form-group">
                <label>Required Skills</label>
                <input value={form.required_skills} onChange={(e) => setForm({ ...form, required_skills: e.target.value })} placeholder="React, SQL, UX" required />
              </div>
              <div className="form-group">
                <label>Location</label>
                <input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Work Type</label>
                <select value={form.job_type} onChange={(e) => setForm({ ...form, job_type: e.target.value })}>
                  <option value="Remote">Remote</option>
                  <option value="Hybrid">Hybrid</option>
                  <option value="On-site">On-site</option>
                </select>
              </div>
              <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Saving...' : isEditing ? 'Save Changes' : 'Publish Job'}
              </button>
            </form>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

export default CreateJob;
