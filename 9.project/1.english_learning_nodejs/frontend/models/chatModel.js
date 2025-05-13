const axios = require('axios');

// Python Flask API 서버 주소
const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5000/api/chat';

/**
 * OpenAI를 통해 채팅 응답을 가져옵니다
 * @param {number} grade - 학년
 * @param {string} curriculumTitle - 커리큘럼 제목
 * @param {string} userInput - 사용자 입력 메시지
 * @returns {Promise<Object>} - 응답 객체 (success, response)
 */
async function getChatResponse(grade, curriculumTitle, userInput) {
    try {
        const response = await axios.post(FLASK_API_URL, {
            grade,
            curriculum_title: curriculumTitle,
            user_input: userInput,
        });

        return {
            success: true,
            response: response.data.response,
        };
    } catch (error) {
        console.error('OpenAI API 요청 중 오류 발생:', error);

        return {
            success: false,
            error: error.message,
        };
    }
}

module.exports = {
    getChatResponse,
};
