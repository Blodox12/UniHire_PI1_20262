function JobCard({ job, onApply, showApply = true }) {
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
      {showApply && (
        <button className="btn btn-primary" onClick={() => onApply(job.id)}>
          Apply Now
        </button>
      )}
    </article>
  );
}

export default JobCard;
