/**
 * 커리큘럼 데이터 모델
 * 실제 애플리케이션에서는 데이터베이스에서 이 정보를 가져올 수 있습니다.
 */
const curriculums = {
    1: ['기초 인사', '간단한 문장', '동물 이름'],
    2: ['학교 생활', '가족 소개', '자기 소개'],
    3: ['취미와 운동', '날씨 묘사', '간단한 이야기'],
    4: ['쇼핑과 가격', '음식 주문', '여행 이야기'],
    5: ['역사와 문화', '과학과 자연', '사회 이슈'],
    6: ['미래 계획', '진로 탐색', '세계 여행'],
};

/**
 * 모든 학년 정보를 가져옵니다
 * @returns {Array} 학년 목록 (문자열 배열)
 */
function getAllGrades() {
    return Object.keys(curriculums);
}

/**
 * 특정 학년의 모든 커리큘럼을 가져옵니다
 * @param {number} grade - 학년 번호
 * @returns {Array|null} 커리큘럼 목록 또는 학년이 존재하지 않을 경우 null
 */
function getCurriculumsByGrade(grade) {
    const gradeNum = parseInt(grade);
    if (curriculums.hasOwnProperty(gradeNum)) {
        return curriculums[gradeNum].map((title, index) => ({
            index,
            title,
        }));
    }
    return null;
}

/**
 * 특정 학년과 커리큘럼 ID에 해당하는 커리큘럼 제목을 가져옵니다
 * @param {number} grade - 학년 번호
 * @param {number} curriculumId - 커리큘럼 ID
 * @returns {string|null} 커리큘럼 제목 또는 존재하지 않을 경우 null
 */
function getCurriculumTitle(grade, curriculumId) {
    const gradeNum = parseInt(grade);
    const currId = parseInt(curriculumId);

    console.log(`getCurriculumTitle 호출: grade=${gradeNum}, curriculumId=${currId}`);
    console.log(`학년 존재 여부: ${curriculums.hasOwnProperty(gradeNum)}`);

    if (curriculums.hasOwnProperty(gradeNum)) {
        console.log(`해당 학년 커리큘럼 개수: ${curriculums[gradeNum].length}`);

        if (currId >= 0 && currId < curriculums[gradeNum].length) {
            console.log(`찾은 커리큘럼 제목: ${curriculums[gradeNum][currId]}`);
            return curriculums[gradeNum][currId];
        }
    }

    console.log('커리큘럼을 찾을 수 없음');
    return null;
}

/**
 * 커리큘럼이 존재하는지 확인합니다
 * @param {number} grade - 학년 번호
 * @param {number} curriculumId - 커리큘럼 ID
 * @returns {boolean} 존재 여부
 */
function curriculumExists(grade, curriculumId) {
    const gradeNum = parseInt(grade);
    const currId = parseInt(curriculumId);

    console.log(`curriculumExists 호출: grade=${gradeNum}, curriculumId=${currId}`);

    const exists = curriculums.hasOwnProperty(gradeNum) && currId >= 0 && currId < curriculums[gradeNum].length;

    console.log(`존재 여부 결과: ${exists}`);
    return exists;
}

module.exports = {
    getAllGrades,
    getCurriculumsByGrade,
    getCurriculumTitle,
    curriculumExists,
};
