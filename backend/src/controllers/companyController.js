const { get, run, all } = require('../database/db');

exports.getProfile = async (req, res) => {
  const company = await get('SELECT * FROM companies WHERE id = ?', [req.user.id]);
  if (!company) {
    return res.status(404).json({ message: 'Company profile not found' });
  }
  res.json({ company });
};

exports.updateProfile = async (req, res) => {
  const { companyName } = req.body;
  await run('UPDATE companies SET company_name = ? WHERE id = ?', [companyName, req.user.id]);
  res.json({ message: 'Company profile updated successfully' });
};

exports.getJobs = async (req, res) => {
  const jobs = await all('SELECT * FROM jobs WHERE company_id = ? ORDER BY id DESC', [req.user.id]);
  res.json({ jobs });
};
