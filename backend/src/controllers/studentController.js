const { get, run } = require('../database/db');

exports.getProfile = async (req, res) => {
  const student = await get('SELECT * FROM students WHERE id = ?', [req.user.id]);
  if (!student) {
    return res.status(404).json({ message: 'Student profile not found' });
  }
  res.json({ student });
};

exports.updateProfile = async (req, res) => {
  const { name, university, career, semester, skills, certifications, resume_filename } = req.body;
  await run(
    'UPDATE students SET name = ?, university = ?, career = ?, semester = ?, skills = ?, certifications = ?, resume_filename = ? WHERE id = ?',
    [name, university, career, semester, skills, certifications, resume_filename, req.user.id]
  );
  res.json({ message: 'Profile updated successfully' });
};
