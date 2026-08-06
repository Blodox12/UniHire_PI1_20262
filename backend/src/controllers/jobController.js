const { all, get, run } = require('../database/db');

exports.getAllJobs = async (req, res) => {
  const jobs = await all('SELECT * FROM jobs ORDER BY id DESC');
  res.json({ jobs });
};

exports.createJob = async (req, res) => {
  const { title, description, required_skills, location, job_type } = req.body;

  if (!title || !description || !required_skills || !location) {
    return res.status(400).json({ message: 'Missing job fields' });
  }

  await run(
    'INSERT INTO jobs (company_id, title, description, required_skills, location, job_type) VALUES (?, ?, ?, ?, ?, ?)',
    [req.user.id, title, description, required_skills, location, job_type || 'Remote']
  );

  res.status(201).json({ message: 'Job created successfully' });
};

exports.getRecommendedJobs = async (req, res) => {
  const student = await get('SELECT skills FROM students WHERE id = ?', [req.user.id]);
  const studentSkills = (student?.skills || '').split(',').map((skill) => skill.trim().toLowerCase()).filter(Boolean);
  const jobs = await all('SELECT * FROM jobs ORDER BY id DESC');

  const scoredJobs = jobs
    .map((job) => {
      const requiredSkills = (job.required_skills || '').split(',').map((skill) => skill.trim().toLowerCase()).filter(Boolean);
      const matchCount = requiredSkills.filter((skill) => studentSkills.includes(skill)).length;
      return { ...job, matchCount };
    })
    .sort((a, b) => b.matchCount - a.matchCount);

  res.json({ jobs: scoredJobs });
};

exports.updateJob = async (req, res) => {
  const job = await get('SELECT id FROM jobs WHERE id = ? AND company_id = ?', [req.params.id, req.user.id]);
  if (!job) {
    return res.status(404).json({ message: 'Job not found' });
  }

  const { title, description, required_skills, location, job_type } = req.body;
  await run(
    'UPDATE jobs SET title = ?, description = ?, required_skills = ?, location = ?, job_type = ? WHERE id = ?',
    [title, description, required_skills, location, job_type, req.params.id]
  );

  res.json({ message: 'Job updated successfully' });
};

exports.deleteJob = async (req, res) => {
  const job = await get('SELECT id FROM jobs WHERE id = ? AND company_id = ?', [req.params.id, req.user.id]);
  if (!job) {
    return res.status(404).json({ message: 'Job not found' });
  }

  await run('DELETE FROM jobs WHERE id = ?', [req.params.id]);
  await run('DELETE FROM applications WHERE job_id = ?', [req.params.id]);
  res.json({ message: 'Job deleted successfully' });
};
