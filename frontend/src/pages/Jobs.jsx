import { useEffect, useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import JobCard from '../components/JobCard';

function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [search, setSearch] = useState('');
  const [jobType, setJobType] = useState('');
  const [location, setLocation] = useState('');
  const [message, setMessage] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    const performSearch = async () => {
      setIsSearching(true);
      try {
        const params = new URLSearchParams();
        if (search) params.append('q', search);
        if (jobType) params.append('job_type', jobType);
        if (location) params.append('location', location);
        const { data } = await axios.get(
          `${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/jobs/search?${params}` 
        );
        setJobs(data.jobs || []);
      } catch (err) {
        console.error(err);
      } finally {
        setIsSearching(false);
      }
    };
    performSearch();
  }, [search, jobType, location]);

  const handleApply = async (jobId) => {
    const token = localStorage.getItem('token');
    if (!token) {
      setMessage('Please log in as a student to apply.');
      return;
    }
    try {
      await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/applications`, { jobId }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage('Application submitted successfully.');
      // mark job as applied locally so UI updates immediately
      setJobs((prev) => prev.map((j) => (j.id === jobId ? { ...j, applied: true } : j)));
    } catch (err) {
      setMessage(err.response?.data?.message || 'Unable to submit application.');
    }
  };

  const clearFilters = () => {
    setSearch('');
    setJobType('');
    setLocation('');
  };

  return (
    <>
      <Navbar />
      <main className="page-shell">
        <div className="container">
          <h2>Explore Opportunities</h2>
          <p>Search internships and entry-level jobs aligned with your profile.</p>
          {message && <p style={{ color: 'green' }}>{message}</p>}
          <div className="card" style={{ marginBottom: '1rem' }}>
            <div className="grid-2">
              <div className="form-group">
                <label>Search</label>
                <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Skills, title, or keywords" />
              </div>
              <div className="form-group">
                <label>Job Type</label>
                <select value={jobType} onChange={(e) => setJobType(e.target.value)}>
                  <option value="">All</option>
                  <option value="Remote">Remote</option>
                  <option value="Hybrid">Hybrid</option>
                  <option value="On-site">On-site</option>
                </select>
              </div>
              <div className="form-group">
                <label>Location</label>
                <input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="City or country" />
              </div>
            </div>
            {(search || jobType || location) && (
              <button className="btn btn-secondary" onClick={clearFilters} style={{ marginTop: '0.5rem' }}>
                Clear Filters
              </button>
            )}
          </div>
          <p style={{ color: '#666' }}>
            {isSearching ? 'Searching...' : `Found ${jobs.length} job${jobs.length !== 1 ? 's' : ''}`}
          </p>
          {jobs.length === 0 && !isSearching && (
            <p style={{ color: 'crimson', textAlign: 'center' }}>No jobs match your search. Try adjusting your filters.</p>
          )}
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} onApply={handleApply} />
          ))}
        </div>
      </main>
      <Footer />
    </>
  );
}

export default Jobs;
