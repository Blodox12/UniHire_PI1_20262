const express = require('express');
const { createApplication, getStudentApplications, getCompanyApplicants } = require('../controllers/applicationController');
const { protect, authorize } = require('../middleware/authMiddleware');

const router = express.Router();

router.post('/', protect, authorize('student'), createApplication);
router.get('/', protect, authorize('student'), getStudentApplications);
router.get('/company', protect, authorize('company'), getCompanyApplicants);

module.exports = router;
