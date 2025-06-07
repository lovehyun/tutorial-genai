const express = require('express');
const router = express.Router();
const chatModel = require('../models/chatModel');

// 채팅 API 엔드포인트
router.post('/chat', async (req, res) => {
    try {
        const { grade, curriculum_title, user_input } = req.body;

        if (!grade || !curriculum_title || !user_input) {
            return res.status(400).json({
                error: '필수 파라미터가 누락되었습니다. (grade, curriculum_title, user_input)',
            });
        }

        // chatModel을 통해 OpenAI 응답 가져오기
        const result = await chatModel.getChatResponse(grade, curriculum_title, user_input);

        if (result.success) {
            return res.json({ response: result.response });
        } else {
            return res.status(500).json({ error: result.error });
        }
    } catch (error) {
        console.error('요청 처리 중 오류 발생:', error);
        return res.status(500).json({
            error: '요청 처리 중 오류가 발생했습니다.',
            details: error.message,
        });
    }
});

// 미래에 추가될 수 있는 API 엔드포인트들
// router.get('/curriculums', async (req, res) => {
//     // 모든 커리큘럼 목록 가져오기 로직
// });

// router.get('/progress/:userId', async (req, res) => {
//     // 사용자 진행 상황 가져오기 로직
// });

module.exports = router;
