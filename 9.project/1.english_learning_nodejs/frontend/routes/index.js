const express = require('express');
const router = express.Router();
const curriculumController = require('../controllers/curriculumController');

// 홈페이지 라우트
router.get('/', curriculumController.getHomePage);

module.exports = router;
