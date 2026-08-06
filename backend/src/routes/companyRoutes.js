const express = require('express');
const { getProfile, updateProfile, getJobs } = require('../controllers/companyController');
const { protect, authorize } = require('../middleware/authMiddleware');

const router = express.Router();

router.get('/profile', protect, authorize('company'), getProfile);
router.put('/profile', protect, authorize('company'), updateProfile);
router.get('/jobs', protect, authorize('company'), getJobs);

module.exports = router;
