const express = require('express');
const path = require('path');
const dotenv = require('dotenv');
const morgan = require('morgan');

// 환경 변수 로드
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// 미들웨어 설정
app.use(morgan('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// 템플릿 엔진 설정
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// 라우트 모듈 가져오기
const indexRouter = require('./routes/index');
const curriculumRoutes = require('./routes/curriculumRoutes');
const apiRoutes = require('./routes/apiRoutes');

// 라우트 설정
app.use('/', indexRouter);
app.use('/', curriculumRoutes); // grade, curriculum 라우트
app.use('/api', apiRoutes); // API 라우트

// 404 에러 처리
app.use((req, res) => {
    console.log(`404 에러 발생: ${req.url}`);
    const curriculumModel = require('./models/curriculumModel');
    res.status(404).render('error', {
        message: '페이지를 찾을 수 없습니다',
        error: { status: 404 },
        grades: curriculumModel.getAllGrades(),
        current_grade: null,
    });
});

// 500 에러 처리
app.use((err, req, res, next) => {
    console.error('서버 오류 발생:', err);
    const curriculumModel = require('./models/curriculumModel');
    res.status(500).render('error', {
        message: '서버 오류가 발생했습니다',
        error: { status: 500, stack: process.env.NODE_ENV === 'development' ? err.stack : '' },
        grades: curriculumModel.getAllGrades(),
        current_grade: null,
    });
});

// 서버 시작
app.listen(PORT, () => {
    console.log(`서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
    console.log(`NODE_ENV: ${process.env.NODE_ENV || 'development'}`);
});
