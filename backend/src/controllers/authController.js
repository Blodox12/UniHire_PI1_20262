const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { get, run } = require('../database/db');

exports.register = async (req, res) => {
  const { role, name, email, password, university, career, semester, companyName } = req.body;

  if (!role || !email || !password) {
    return res.status(400).json({ message: 'Missing required fields' });
  }

  const existingStudent = await get('SELECT id FROM students WHERE email = ?', [email]);
  const existingCompany = await get('SELECT id FROM companies WHERE email = ?', [email]);

  if (existingStudent || existingCompany) {
    return res.status(400).json({ message: 'User already exists' });
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  if (role === 'student') {
    await run(
      'INSERT INTO students (name, email, password, university, career, semester, skills, certifications, resume_filename) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [name || '', email, hashedPassword, university || '', career || '', semester || '', '', '', '']
    );
  } else if (role === 'company') {
    await run('INSERT INTO companies (company_name, email, password) VALUES (?, ?, ?)', [companyName || name || '', email, hashedPassword]);
  } else {
    return res.status(400).json({ message: 'Invalid role' });
  }

  res.status(201).json({ message: 'Account created successfully' });
};

exports.login = async (req, res) => {
  const { role, email, password } = req.body;

  if (!role || !email || !password) {
    return res.status(400).json({ message: 'Missing required fields' });
  }

  let user = null;
  if (role === 'student') {
    user = await get('SELECT id, name, email, password FROM students WHERE email = ?', [email]);
  } else if (role === 'company') {
    user = await get('SELECT id, company_name as name, email, password FROM companies WHERE email = ?', [email]);
  } else {
    return res.status(400).json({ message: 'Invalid role' });
  }

  if (!user) {
    return res.status(404).json({ message: 'User not found' });
  }

  const isValid = await bcrypt.compare(password, user.password);
  if (!isValid) {
    return res.status(401).json({ message: 'Invalid password' });
  }

  const token = jwt.sign({ id: user.id, role }, process.env.JWT_SECRET || 'unihire-secret', { expiresIn: '7d' });

  res.json({
    token,
    user: {
      id: user.id,
      role,
      name: user.name,
      email: user.email
    }
  });
};
