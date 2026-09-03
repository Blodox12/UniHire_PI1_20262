import { Link } from 'react-router-dom';

function JobCard({ job, onApply, showApply = true }) {
  const applied = job.applied || job.isApplied || job.hasApplied || false;
  return (
    <article className="card job-card">
      <div className="card-header">
        <h3>{job.title}</h3>
        <span className="badge">{job.job_type}</span>
      </div>
      <p>{job.description}</p>
      <div className="meta-row">
        <span>Skills: {job.required_skills}</span>
        <span>Location: {job.location}</span>
      </div>
      <div className="hero-actions">
        <Link to={`/job/${job.id}`} className="btn btn-secondary">View Details</Link>
        {showApply && (
          applied ? (
            <button className="btn" disabled style={{ background: '#28a745', color: '#fff' }}>
              ✓ Applied
            </button>
          ) : (
            <button className="btn btn-primary" onClick={() => onApply(job.id)}>
              Apply Now
            </button>
          )
        )}
      </div>
    </article>
  );
}

export default JobCard;
