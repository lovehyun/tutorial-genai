const express = require('express');
const router = express.Router();
const curriculumController = require('../controllers/curriculumController');

// 채팅 API 엔드포인트
router.post('/chat', curriculumController.handleChatRequest);

// 미래에 추가될 수 있는 API 엔드포인트들
// router.get('/curriculums', curriculumController.getAllCurriculums);
// router.get('/progress/:userId', curriculumController.getUserProgress);

module.exports = router;
