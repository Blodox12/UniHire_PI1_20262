import { useEffect, useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function Profile() {
  const [form, setForm] = useState({
    name: '',
    university: '',
    career: '',
    semester: '',
    skills: '',
    certifications: '',
    resume_filename: ''
  });
  const [message, setMessage] = useState('');

  useEffect(() => {
    const loadProfile = async () => {
      const token = localStorage.getItem('token');
      const { data } = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/students/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setForm({
        name: data.student.name || '',
        university: data.student.university || '',
        career: data.student.career || '',
        semester: data.student.semester || '',
        skills: data.student.skills || '',
        certifications: data.student.certifications || '',
        resume_filename: data.student.resume_filename || ''
      });
    };
    loadProfile();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    try {
      await axios.put(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/students/profile`, form, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage('Profile updated successfully.');
    } catch (err) {
      setMessage(err.response?.data?.message || 'Profile update failed.');
    }
  };

  return (
    <>
      <Navbar />
      <main className="page-shell">
        <div className="container">
          <div className="card form-card">
            <h2>Edit Profile</h2>
            {message && <p style={{ color: 'green' }}>{message}</p>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>University</label>
                <input value={form.university} onChange={(e) => setForm({ ...form, university: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Career</label>
                <input value={form.career} onChange={(e) => setForm({ ...form, career: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Semester</label>
                <input value={form.semester} onChange={(e) => setForm({ ...form, semester: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Skills</label>
                <input value={form.skills} onChange={(e) => setForm({ ...form, skills: e.target.value })} placeholder="React, Node.js, SQL" />
              </div>
              <div className="form-group">
                <label>Certifications</label>
                <input value={form.certifications} onChange={(e) => setForm({ ...form, certifications: e.target.value })} placeholder="AWS, Google Data Analytics" />
              </div>
              <div className="form-group">
                <label>Resume Filename</label>
                <input value={form.resume_filename} onChange={(e) => setForm({ ...form, resume_filename: e.target.value })} />
              </div>
              <button className="btn btn-primary" type="submit">Save Profile</button>
            </form>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

export default Profile;
