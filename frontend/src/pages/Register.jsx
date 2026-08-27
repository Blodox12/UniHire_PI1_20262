import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function Register() {
  const [role, setRole] = useState('student');
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    university: '',
    career: '',
    semester: '',
    skills: '',
    certifications: '',
    resume_filename: '',
    companyName: ''
  });
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/register`, {
        role,
        name: role === 'student' ? form.name : form.companyName,
        email: form.email,
        password: form.password,
        university: form.university,
        career: form.career,
        semester: form.semester,
        skills: form.skills,
        certifications: form.certifications,
        resume_filename: form.resume_filename,
        companyName: form.companyName
      });
      setMessage('Account created successfully. Please log in.');
      setTimeout(() => navigate('/login'), 800);
    } catch (err) {
      setMessage(err.response?.data?.message || 'Registration failed');
    }
  };

  return (
    <>
      <Navbar />
      <main className="page-shell">
        <div className="container">
          <div className="card form-card">
            <h2>Register</h2>
            <div className="hero-actions" style={{ marginBottom: '1rem' }}>
              <button className={`btn ${role === 'student' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setRole('student')}>Student</button>
              <button className={`btn ${role === 'company' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setRole('company')}>Company</button>
            </div>
            {message && <p style={{ color: message.includes('success') ? 'green' : 'crimson' }}>{message}</p>}
            <form onSubmit={handleSubmit}>
              {role === 'student' ? (
                <>
                  <div className="form-group">
                    <label>Name</label>
                    <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
                  </div>
                  <div className="form-group">
                    <label>Email</label>
                    <input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
                  </div>
                  <div className="form-group">
                    <label>Password</label>
                    <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
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
                    <input value={form.resume_filename} onChange={(e) => setForm({ ...form, resume_filename: e.target.value })} placeholder="resume.pdf" />
                  </div>
                </>
              ) : (
                <>
                  <div className="form-group">
                    <label>Company Name</label>
                    <input value={form.companyName} onChange={(e) => setForm({ ...form, companyName: e.target.value })} required />
                  </div>
                  <div className="form-group">
                    <label>Email</label>
                    <input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
                  </div>
                  <div className="form-group">
                    <label>Password</label>
                    <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
                  </div>
                </>
              )}
              <button className="btn btn-primary" type="submit">Create Account</button>
            </form>
            <p style={{ marginTop: '1rem' }}>
              Already have an account? <Link to="/login">Login</Link>
            </p>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

export default Register;
