import { useEffect, useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import JobCard from '../components/JobCard';

function RecommendedJobs() {
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    const loadRecommended = async () => {
      const token = localStorage.getItem('token');
      const { data } = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/jobs/recommended`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setJobs(data.jobs || []);
    };
    loadRecommended();
  }, []);

  return (
    <>
      <Navbar />
      <main className="page-shell">
        <div className="container">
          <h2>Recommended Jobs</h2>
          {jobs.length === 0 ? <p className="empty-state">No recommendation available right now.</p> : jobs.map((job) => <JobCard key={job.id} job={job} />)}
        </div>
      </main>
      <Footer />
    </>
  );
}

export default RecommendedJobs;
