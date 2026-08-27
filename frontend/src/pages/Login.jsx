import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function Login() {
  const [role, setRole] = useState('student');
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;
    setError('');
    try {
      setIsSubmitting(true);
      const { data } = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/login`, {
        role,
        email: form.email,
        password: form.password
      });
      localStorage.setItem('token', data.token);
      localStorage.setItem('role', data.user.role);
      localStorage.setItem('user', JSON.stringify(data.user));
      navigate(data.user.role === 'company' ? '/company-dashboard' : '/student-dashboard');
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed');
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
            <h2>Login</h2>
            <div className="hero-actions" style={{ marginBottom: '1rem' }}>
              <button className={`btn ${role === 'student' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setRole('student')}>Student</button>
              <button className={`btn ${role === 'company' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setRole('company')}>Company</button>
            </div>
            {error && <p style={{ color: 'crimson' }}>{error}</p>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
              </div>
              <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Signing in...' : 'Login'}
              </button>
            </form>
            <p style={{ marginTop: '1rem' }}>
              No account yet? <Link to="/register">Register</Link>
            </p>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

export default Login;
