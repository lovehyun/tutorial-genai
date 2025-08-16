// static/js/utils.js
// 유틸리티 기능들

'use strict';

// 전역 객체가 이미 존재하는지 확인
if (typeof window.MathQAUtils === 'undefined') {
    // 키보드 단축키 관리
    const KeyboardShortcuts = {
        shortcuts: new Map(),

        register(key, callback, description = '') {
            this.shortcuts.set(key, { callback, description });
        },

        init() {
            document.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + 키 조합만 처리
                if (!(e.ctrlKey || e.metaKey)) return;

                const key = e.key.toLowerCase();
                const shortcut = this.shortcuts.get(key);
                
                if (shortcut) {
                    e.preventDefault();
                    shortcut.callback(e);
                }
            });

            // 도움말 표시 (Ctrl + ?)
            this.register('/', () => this.showHelp(), '단축키 도움말');
        },

        showHelp() {
            const shortcuts = Array.from(this.shortcuts.entries())
                .map(([key, {description}]) => `Ctrl+${key.toUpperCase()}: ${description}`)
                .join('\n');
            
            if (window.MathQA?.Utils) {
                window.MathQA.Utils.showMessage(`
                    <strong>키보드 단축키:</strong><br>
                    ${shortcuts.replace(/\n/g, '<br>')}
                `, 'info', 10000);
            }
        }
    };

    // 학습 진도 계산
    const ProgressCalculator = {
        calculateProgress(solvedCount, totalCount) {
            const solvedPercentage = totalCount > 0 ? Math.round((solvedCount / totalCount) * 100) : 0;
            
            return {
                solved: solvedCount,
                total: totalCount,
                solvedPercentage,
                next: solvedCount < totalCount ? solvedCount + 1 : null
            };
        },

        estimateTime(difficulty, topics) {
            const baseTime = {
                '초급': 15,
                '중급': 25,
                '고급': 40
            };
            
            const topicMultiplier = Math.max(1, topics.length * 0.2);
            return Math.round(baseTime[difficulty] * topicMultiplier);
        }
    };

    // 문제 상태 관리
    const ProblemManager = {
        getProblemStatus(problemId) {
            const storageKey = `problem_${problemId}_answer`;
            const submissionKey = `problem_${problemId}_submitted`;
            
            if (window.MathQA?.Utils?.loadFromStorage) {
                if (window.MathQA.Utils.loadFromStorage(submissionKey)) {
                    return { status: '완료', badgeClass: 'bg-success' };
                } else if (window.MathQA.Utils.loadFromStorage(storageKey)) {
                    return { status: '진행중', badgeClass: 'bg-warning text-dark' };
                }
            }
            return { status: '대기', badgeClass: '' };
        },

        updateProblemStatuses() {
            for (let i = 1; i <= 5; i++) {
                const statusBadge = document.getElementById(`status-${i}`);
                const statusText = document.getElementById(`statusText-${i}`);
                
                const { status, badgeClass } = this.getProblemStatus(i);
                
                if (statusBadge) {
                    statusBadge.textContent = status;
                    statusBadge.className = `badge ${badgeClass}`;
                }
                
                if (statusText) {
                    statusText.textContent = status;
                }
            }
        }
    };

    // 필터링 기능
    const FilterManager = {
        init() {
            document.querySelectorAll('[data-filter]').forEach(button => {
                button.addEventListener('click', (e) => {
                    const filter = e.target.dataset.filter;
                    this.applyFilter(filter);
                    this.updateButtonStates(e.target);
                });
            });
        },

        applyFilter(filter) {
            const items = document.querySelectorAll('.problem-item');
            
            items.forEach(item => {
                const difficulty = item.dataset.difficulty;
                const shouldShow = filter === 'all' || difficulty === filter;
                
                if (shouldShow) {
                    item.style.display = 'block';
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'scale(1)';
                    }, 50);
                } else {
                    item.style.opacity = '0';
                    item.style.transform = 'scale(0.9)';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 200);
                }
            });
        },

        updateButtonStates(activeButton) {
            const buttons = document.querySelectorAll('[data-filter]');
            buttons.forEach(btn => btn.classList.remove('active'));
            activeButton.classList.add('active');
        }
    };

    // 홈페이지 전용 기능
    const HomePage = {
        init() {
            this.updateProgressDisplay();
            this.updateProblemStatuses();
            this.updateEstimatedTimes();
            FilterManager.init();
        },

        updateProgressDisplay() {
            const progress = ProgressCalculator.calculateProgress(0, 5);
            
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            const solvedCount = document.getElementById('solvedCount');
            const attemptedCount = document.getElementById('attemptedCount');
            
            if (progressBar) {
                progressBar.style.width = progress.solvedPercentage + '%';
                progressBar.setAttribute('aria-valuenow', progress.solvedPercentage);
                progressBar.textContent = progress.solvedPercentage + '%';
            }
            
            if (progressText) {
                if (progress.solved === 0) {
                    progressText.textContent = '아직 해결한 문제가 없습니다. 첫 번째 문제부터 시작해보세요!';
                } else if (progress.solved === progress.total) {
                    progressText.textContent = '모든 문제를 완료했습니다! 훌륭합니다!';
                } else {
                    progressText.textContent = `${progress.solved}개 문제를 해결했습니다. 다음 문제: ${progress.next}번`;
                }
            }
            
            if (solvedCount) solvedCount.textContent = progress.solved;
            if (attemptedCount) attemptedCount.textContent = progress.attempted;
        },

        updateProblemStatuses() {
            ProblemManager.updateProblemStatuses();
        },

        updateEstimatedTimes() {
            document.querySelectorAll('.estimated-time').forEach(element => {
                const topics = element.dataset.topics.split(',');
                const difficulty = element.closest('.problem-item').dataset.difficulty;
                
                const time = ProgressCalculator.estimateTime(difficulty, topics);
                element.textContent = time + '분';
            });
        }
    };

    // 인쇄 기능
    const PrintManager = {
        printPage() {
            // 인쇄 전 스타일 조정
            const originalStyles = this.prepareForPrint();
            
            // 인쇄 실행
            window.print();
            
            // 인쇄 후 스타일 복원
            setTimeout(() => {
                this.restoreStyles(originalStyles);
            }, 1000);
        },

        prepareForPrint() {
            const originalStyles = {};
            
            // 인쇄 시 숨길 요소들
            const elementsToHide = [
                '.navbar',
                '.service-status',
                '.btn',
                '.loading-overlay',
                '.alert'
            ];
            
            elementsToHide.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    originalStyles[el] = el.style.display;
                    el.style.display = 'none';
                });
            });
            
            // 인쇄용 스타일 추가
            const printStyle = document.createElement('style');
            printStyle.id = 'print-style';
            printStyle.textContent = `
                @media print {
                    body { margin: 0; padding: 20px; }
                    .card { border: 1px solid #ddd; box-shadow: none; }
                    .problem-statement { font-size: 14pt; }
                    .solution-area, .feedback-area { page-break-inside: avoid; }
                }
            `;
            document.head.appendChild(printStyle);
            
            return originalStyles;
        },

        restoreStyles(originalStyles) {
            // 숨긴 요소들 복원
            Object.entries(originalStyles).forEach(([element, display]) => {
                element.style.display = display;
            });
            
            // 인쇄용 스타일 제거
            const printStyle = document.getElementById('print-style');
            if (printStyle) {
                printStyle.remove();
            }
        }
    };

    // 테마 관리
    const ThemeManager = {
        currentTheme: 'light',

        init() {
            this.loadTheme();
            this.setupThemeToggle();
        },

        loadTheme() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            this.setTheme(savedTheme);
        },

        setTheme(theme) {
            this.currentTheme = theme;
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            
            // 테마 변경 이벤트 발생
            window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
        },

        toggleTheme() {
            const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
            this.setTheme(newTheme);
        },

        setupThemeToggle() {
            // window.MathQA가 준비된 후에 키보드 단축키 등록
            const registerThemeShortcut = () => {
                if (window.MathQA?.KeyboardShortcuts) {
                    window.MathQA.KeyboardShortcuts.register('t', () => {
                        this.toggleTheme();
                    }, '테마 변경');
                } else {
                    // 아직 준비되지 않았으면 잠시 후 다시 시도
                    setTimeout(registerThemeShortcut, 100);
                }
            };
            registerThemeShortcut();
        }
    };

    // 전역 객체로 내보내기
    window.MathQAUtils = {
        KeyboardShortcuts,
        ProgressCalculator,
        ProblemManager,
        FilterManager, // 필터링 기능 추가
        PrintManager,
        ThemeManager,
        HomePage // 홈페이지 전용 기능 추가
    };

    // 초기화
    document.addEventListener('DOMContentLoaded', function() {
        // 키보드 단축키만 초기화 (나머지는 main.js에서 처리)
        KeyboardShortcuts.init();
    });
}

// 전역 함수들
function showSystemInfo() {
    if (window.MathQA?.ServiceStatus) {
        window.MathQA.ServiceStatus.check()
            .then(data => {
                const info = `
                    <strong>시스템 정보:</strong><br>
                    상태: ${data.status}<br>
                    도구 수: ${data.usage_stats?.tools_available || 0}개<br>
                    메모리: ${data.usage_stats?.memory_size || 0}개 대화
                `;
                window.MathQA.Utils.showMessage(info, 'info', 8000);
            })
            .catch(() => {
                window.MathQA?.Utils.showMessage('시스템 정보를 가져올 수 없습니다.', 'warning');
            });
    }
}

function showKeyboardShortcuts() {
    const shortcuts = `
        <strong>키보드 단축키:</strong><br>
        <kbd>Ctrl + Enter</kbd> 답안 제출<br>
        <kbd>Ctrl + H</kbd> 힌트 요청<br>
        <kbd>Ctrl + S</kbd> 풀이 보기<br>
        <kbd>Ctrl + T</kbd> 테마 변경<br>
        <kbd>Ctrl + /</kbd> 도움말
    `;
    window.MathQA?.Utils.showMessage(shortcuts, 'info', 10000);
}

function previewProblem(problemId) {
    window.MathQA?.Utils.showMessage(`문제 ${problemId} 미리보기 기능은 개발 중입니다.`, 'info');
}

function printPage() {
    if (window.MathQAUtils?.PrintManager) {
        window.MathQAUtils.PrintManager.printPage();
    }
}
