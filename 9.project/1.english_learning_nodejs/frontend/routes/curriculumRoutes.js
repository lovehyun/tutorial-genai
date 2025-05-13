const express = require('express');
const router = express.Router();
const curriculumModel = require('../models/curriculumModel');

// 학년별 커리큘럼 페이지
router.get('/grade/:grade', (req, res) => {
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
});

// 특정 커리큘럼 페이지
router.get('/grade/:grade/curriculum/:curriculum_id', (req, res) => {
    const grade = parseInt(req.params.grade);
    const curriculum_id = parseInt(req.params.curriculum_id);

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
});

module.exports = router;
