const express = require('express');
const router = express.Router();
const curriculumController = require('../controllers/curriculumController');

// 디버깅을 위한 미들웨어
router.use((req, res, next) => {
    console.log(`요청 경로: ${req.method} ${req.path}`);
    next();
});

// 학년별 커리큘럼 페이지
router.get('/grade/:grade', curriculumController.getGradePage);

// 특정 커리큘럼 페이지
router.get('/grade/:grade/curriculum/:curriculum_id', curriculumController.getCurriculumPage);

module.exports = router;
