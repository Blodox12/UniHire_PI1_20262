import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function Home() {
  return (
    <>
      <Navbar />
      <main>
        <section className="hero">
          <div className="container hero-grid">
            <div>
              <h1>Find your first professional experience with UniHire.</h1>
              <p>We match students with internships and entry-level roles based on academic background, skills, certifications, and interests.</p>
              <div className="hero-actions">
                <Link to="/register" className="btn btn-primary">Register</Link>
                <Link to="/jobs" className="btn btn-secondary">Browse Jobs</Link>
              </div>
            </div>
            <div className="card">
              <h3>Why UniHire?</h3>
              <ul>
                <li>Personalized opportunities</li>
                <li>Fast student-company matching</li>
                <li>Professional profile and applications</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="section">
          <div className="container">
            <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>Features</h2>
            <div className="grid-3">
              <div className="card">
                <h3>Smart Matching</h3>
                <p>Discover jobs aligned with your academic and technical profile.</p>
              </div>
              <div className="card">
                <h3>Simple Applications</h3>
                <p>Apply to internships and entry-level jobs in a few clicks.</p>
              </div>
              <div className="card">
                <h3>Company Tools</h3>
                <p>Post openings, manage applicants, and track hiring progress.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="section" style={{ background: '#fff' }}>
          <div className="container">
            <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>How It Works</h2>
            <div className="grid-3">
              <div className="card">
                <h3>1. Create Profile</h3>
                <p>Share your university, career path, skills, and certifications.</p>
              </div>
              <div className="card">
                <h3>2. Discover Roles</h3>
                <p>Browse all openings or receive tailored recommendations.</p>
              </div>
              <div className="card">
                <h3>3. Apply</h3>
                <p>Send your application and track your progress in one place.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="section">
          <div className="container">
            <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>Testimonials</h2>
            <div className="grid-3">
              <div className="card">
                <p>“I landed my first internship through UniHire in less than two weeks.”</p>
                <strong>— Ana, Computer Science Student</strong>
              </div>
              <div className="card">
                <p>“The platform made it easy to connect with companies that fit my background.”</p>
                <strong>— Daniel, Business Student</strong>
              </div>
              <div className="card">
                <p>“A professional experience that felt simple, modern, and effective.”</p>
                <strong>— Sofia, Marketing Student</strong>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

export default Home;
