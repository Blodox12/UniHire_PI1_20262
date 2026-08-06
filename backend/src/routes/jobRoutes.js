const express = require('express');
const { getAllJobs, createJob, getRecommendedJobs, updateJob, deleteJob } = require('../controllers/jobController');
const { protect, authorize } = require('../middleware/authMiddleware');

const router = express.Router();

router.get('/', getAllJobs);
router.get('/recommended', protect, authorize('student'), getRecommendedJobs);
router.post('/', protect, authorize('company'), createJob);
router.put('/:id', protect, authorize('company'), updateJob);
router.delete('/:id', protect, authorize('company'), deleteJob);

module.exports = router;
