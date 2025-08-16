// static/js/problem.js
// 문제 페이지 전용 JavaScript

'use strict';

class ProblemPage {
    constructor(problemId) {
        this.problemId = problemId;
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupKeyboardShortcuts();
        this.loadSavedAnswer();
    }

    bindEvents() {
        // 답안 제출 버튼
        const submitBtn = document.querySelector('button.btn-success[data-requires-service="true"]');
        if (submitBtn) {
            submitBtn.onclick = () => this.checkAnswer();
        }

        // 풀이 보기 버튼
        const solutionBtn = document.querySelector('button.btn-warning[data-requires-service="true"]');
        if (solutionBtn) {
            solutionBtn.onclick = () => this.getSolution();
        }

        // 힌트 버튼
        const hintBtn = document.querySelector('button.btn-info[data-requires-service="true"]');
        if (hintBtn) {
            hintBtn.onclick = () => this.getHint();
        }

        // 자동 저장 설정
        const answerTextarea = document.getElementById('userAnswer');
        if (answerTextarea) {
            window.MathQA?.AutoSave.enable('userAnswer', `problem_${this.problemId}_answer`);
        }
    }

    setupKeyboardShortcuts() {
        // 키보드 단축키 설정
        window.MathQA?.KeyboardShortcuts.register('Enter', () => {
            this.checkAnswer();
        }, '답안 제출');
        
        window.MathQA?.KeyboardShortcuts.register('h', () => {
            this.getHint();
        }, '힌트 요청');
        
        window.MathQA?.KeyboardShortcuts.register('s', () => {
            this.getSolution();
        }, '풀이 보기');
    }

    loadSavedAnswer() {
        const savedAnswer = window.MathQA?.Utils.loadFromStorage(`problem_${this.problemId}_answer`);
        const textarea = document.getElementById('userAnswer');
        if (savedAnswer && textarea && !textarea.value.trim()) {
            textarea.value = savedAnswer;
        }
    }

    async checkAnswer() {
        const userAnswer = document.getElementById('userAnswer').value.trim();
        if (!userAnswer) {
            window.MathQA?.Utils.showMessage('답안을 입력해주세요.', 'warning');
            return;
        }

        window.MathQA?.Utils.showLoading('답안을 평가하는 중입니다...');
        
        try {
            const response = await fetch('/api/check-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    problem_id: this.problemId,
                    user_answer: userAnswer
                })
            });

            const data = await response.json();
            
            if (data.error) {
                window.MathQA?.Utils.showMessage(`오류: ${data.error}`, 'danger');
            } else {
                this.displayFeedback(data);
                this.saveSubmission();
            }
        } catch (error) {
            window.MathQA?.Utils.showMessage('요청 처리 중 오류가 발생했습니다.', 'danger');
        } finally {
            window.MathQA?.Utils.hideLoading();
        }
    }

    async getSolution() {
        window.MathQA?.Utils.showLoading('AI 풀이를 생성하는 중입니다...');
        
        try {
            const response = await fetch('/api/solution', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    problem_id: this.problemId
                })
            });

            const data = await response.json();
            
            if (data.error) {
                window.MathQA?.Utils.showMessage(`오류: ${data.error}`, 'danger');
            } else {
                this.displaySolution(data);
            }
        } catch (error) {
            window.MathQA?.Utils.showMessage('요청 처리 중 오류가 발생했습니다.', 'danger');
        } finally {
            window.MathQA?.Utils.hideLoading();
        }
    }

    async getHint() {
        window.MathQA?.Utils.showLoading('추가 힌트를 생성하는 중입니다...');
        
        try {
            const response = await fetch('/api/hint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    problem_id: this.problemId
                })
            });

            const data = await response.json();
            
            if (data.error) {
                window.MathQA?.Utils.showMessage(`오류: ${data.error}`, 'danger');
            } else {
                this.displayHint(data);
            }
        } catch (error) {
            window.MathQA?.Utils.showMessage('요청 처리 중 오류가 발생했습니다.', 'danger');
        } finally {
            window.MathQA?.Utils.hideLoading();
        }
    }

    displayFeedback(data) {
        const feedbackContent = document.getElementById('feedbackContent');
        const scoreDisplay = document.getElementById('scoreDisplay');
        const feedbackArea = document.getElementById('feedbackArea');
        
        if (feedbackContent) {
            feedbackContent.innerHTML = data.feedback.replace(/\n/g, '<br>');
        }
        
        if (scoreDisplay) {
            scoreDisplay.textContent = data.score;
            scoreDisplay.className = window.MathQA?.Utils.getScoreClass(data.score) || '';
        }
        
        if (feedbackArea) {
            feedbackArea.style.display = 'block';
            // MathJax 렌더링을 안전하게 처리
            this.safeMathRender(feedbackArea);
        }
    }

    displaySolution(data) {
        const solutionContent = document.getElementById('solutionContent');
        const solutionArea = document.getElementById('solutionArea');
        
        if (solutionContent) {
            solutionContent.innerHTML = data.solution.replace(/\n/g, '<br>');
        }
        
        if (solutionArea) {
            solutionArea.style.display = 'block';
            // MathJax 렌더링을 안전하게 처리
            this.safeMathRender(solutionArea);
        }
    }

    displayHint(data) {
        const hintContent = document.getElementById('hintContent');
        const hintArea = document.getElementById('hintArea');
        
        if (hintContent) {
            hintContent.innerHTML = data.hint.replace(/\n/g, '<br>');
        }
        
        if (hintArea) {
            hintArea.style.display = 'block';
            // MathJax 렌더링을 안전하게 처리
            this.safeMathRender(hintArea);
        }
    }

    saveSubmission() {
        // 답안 제출 상태 저장
        window.MathQA?.Utils.saveToStorage(`problem_${this.problemId}_submitted`, true);
        
        // 자동 저장 비활성화 (제출 완료)
        window.MathQA?.AutoSave.disable('userAnswer');
    }

    safeMathRender(element) {
        // MathRenderer가 사용 가능한지 확인
        if (window.MathQA?.MathRenderer) {
            try {
                window.MathQA.MathRenderer.render(element);
            } catch (error) {
                console.warn('MathRenderer failed:', error);
                // MathJax가 직접 사용 가능한지 확인
                this.fallbackMathRender(element);
            }
        } else {
            // MathRenderer가 없으면 직접 MathJax 사용
            this.fallbackMathRender(element);
        }
    }

    fallbackMathRender(element) {
        // MathJax를 직접 사용하는 대체 방법
        if (window.MathJax) {
            try {
                if (window.MathJax.typesetPromise) {
                    window.MathJax.typesetPromise([element]).catch(error => {
                        console.warn('MathJax typesetPromise failed:', error);
                    });
                } else if (window.MathJax.typeset) {
                    window.MathJax.typeset([element]).catch(error => {
                        console.warn('MathJax typeset failed:', error);
                    });
                }
            } catch (error) {
                console.warn('MathJax fallback failed:', error);
            }
        }
    }
}

// 전역 함수들 (기존 HTML과의 호환성을 위해)
function checkAnswer() {
    if (window.problemPage) {
        window.problemPage.checkAnswer();
    }
}

function getSolution() {
    if (window.problemPage) {
        window.problemPage.getSolution();
    }
}

function getHint() {
    if (window.problemPage) {
        window.problemPage.getHint();
    }
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    const problemIdElement = document.querySelector('script');
    const problemIdMatch = problemIdElement?.textContent.match(/const problemId = (\d+);/);
    
    if (problemIdMatch) {
        const problemId = parseInt(problemIdMatch[1]);
        window.problemPage = new ProblemPage(problemId);
    }
});
