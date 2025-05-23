const express = require('express');
const router = express.Router();
const curriculumModel = require('../models/curriculumModel');

// 홈페이지 라우트
router.get('/', (req, res) => {
    res.render('home', {
        grades: curriculumModel.getAllGrades(),
        current_grade: null,
    });
});

module.exports = router;
