const { all, get, run } = require('../database/db');

exports.createApplication = async (req, res) => {
  const { jobId } = req.body;
  if (!jobId) {
    return res.status(400).json({ message: 'Job id is required' });
  }

  const existing = await get('SELECT id FROM applications WHERE student_id = ? AND job_id = ?', [req.user.id, jobId]);
  if (existing) {
    return res.status(400).json({ message: 'You already applied to this job' });
  }

  await run('INSERT INTO applications (student_id, job_id, status) VALUES (?, ?, ?)', [req.user.id, jobId, 'Pending']);
  res.status(201).json({ message: 'Application submitted successfully' });
};

exports.getStudentApplications = async (req, res) => {
  const applications = await all(
    `SELECT a.id, a.status, a.applied_at, j.title, j.description
     FROM applications a
     JOIN jobs j ON j.id = a.job_id
     WHERE a.student_id = ?
     ORDER BY a.id DESC`,
    [req.user.id]
  );
  res.json({ applications });
};

exports.getCompanyApplicants = async (req, res) => {
  const applicants = await all(
    `SELECT a.id, a.status, a.applied_at, j.title, s.name AS student_name
     FROM applications a
     JOIN jobs j ON j.id = a.job_id
     JOIN students s ON s.id = a.student_id
     WHERE j.company_id = ?
     ORDER BY a.id DESC`,
    [req.user.id]
  );
  res.json({ applicants });
};
