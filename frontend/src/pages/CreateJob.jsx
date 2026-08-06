import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function CreateJob() {
  const [form, setForm] = useState({
    title: '',
    description: '',
    required_skills: '',
    location: '',
    job_type: 'Remote'
  });
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    try {
      await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/jobs`, form, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage('Job posted successfully.');
      setTimeout(() => navigate('/company-dashboard'), 800);
    } catch (err) {
      setMessage(err.response?.data?.message || 'Unable to create job.');
    }
  };

  return (
    <>
      <Navbar />
      <main className="page-shell">
        <div className="container">
          <div className="card form-card">
            <h2>Create Job</h2>
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
              <button className="btn btn-primary" type="submit">Publish Job</button>
            </form>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

export default CreateJob;
