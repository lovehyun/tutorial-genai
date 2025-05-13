const curriculumModel = require('../models/curriculumModel');
const chatModel = require('../models/chatModel');

/**
 * 홈페이지 컨트롤러
 */
exports.getHomePage = (req, res) => {
    res.render('home', {
        grades: curriculumModel.getAllGrades(),
        current_grade: null,
    });
};

/**
 * 학년별 커리큘럼 페이지 컨트롤러
 */
exports.getGradePage = (req, res) => {
    const grade = parseInt(req.params.grade);
    const curriculums = curriculumModel.getCurriculumsByGrade(grade);

    if (curriculums) {
        res.render('grade', {
            grade,
            curriculums,
            grades: curriculumModel.getAllGrades(),
            current_grade: grade,
        });
    } else {
        res.status(404).render('error', {
            message: '해당 학년은 존재하지 않습니다.',
            error: { status: 404 },
            grades: curriculumModel.getAllGrades(),
            current_grade: null,
        });
    }
};

/**
 * 특정 커리큘럼 페이지 컨트롤러
 */
exports.getCurriculumPage = (req, res) => {
    const grade = parseInt(req.params.grade);
    const curriculum_id = parseInt(req.params.curriculum_id);

    console.log(`요청된 경로: /grade/${grade}/curriculum/${curriculum_id}`);
    console.log(`존재 여부: ${curriculumModel.curriculumExists(grade, curriculum_id)}`);

    if (curriculumModel.curriculumExists(grade, curriculum_id)) {
        const curriculum_title = curriculumModel.getCurriculumTitle(grade, curriculum_id);
        console.log(`커리큘럼 제목: ${curriculum_title}`);

        res.render('curriculum', {
            grade,
            curriculum_title,
            grades: curriculumModel.getAllGrades(),
            current_grade: grade,
        });
    } else {
        res.status(404).render('error', {
            message: '해당 커리큘럼은 존재하지 않습니다.',
            error: { status: 404 },
            grades: curriculumModel.getAllGrades(),
            current_grade: grade,
        });
    }
};

/**
 * OpenAI와 채팅하기 위한 요청을 처리합니다
 * Node.js 서버에서 Python Flask API로 요청을 전달합니다
 */
exports.handleChatRequest = async (req, res) => {
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
};
