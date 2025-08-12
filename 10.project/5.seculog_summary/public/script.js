// public/script.js
// RAW와 요약을 완전히 분리해서, 먼저 오는 쪽부터 각자 DOM에 즉시 반영

const rawBox = document.getElementById('rawBox');
const summaryBox = document.getElementById('summaryBox');
const updatedAtEl = document.getElementById('updatedAt');
const logPathEl = document.getElementById('logPath');
const logModeEl = document.getElementById('logMode');
const lineCountEl = document.getElementById('lineCount');
const btnRefresh = document.getElementById('btnRefresh');

// --- API ---
async function fetchRawLog(n) {
    const res = await fetch(`/api/authlog/raw?n=${n}`, { cache: 'no-store' });
    if (!res.ok) throw new Error('RAW API error');
    return res.json();
}

async function fetchSummary(n) {
    const res = await fetch(`/api/authlog/summary?n=${n}`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Summary API error');
    return res.json();
}

// --- UI 업데이트 ---
function updateRawUI(data) {
    rawBox.textContent = (data.raw || []).join('\n');
    updatedAtEl.textContent = `업데이트: ${data.updatedAt || '-'}`;
    logPathEl.textContent = `경로: ${data.path || '-'}`;
    logModeEl.textContent = `모드: ${data.usingSample ? '샘플 파일' : '실제 파일'}`;
}

function updateSummaryUI(data) {
    summaryBox.innerHTML = (data.summary || '');
    // summaryBox.innerHTML = (data.summary || '').replace(/\n/g, '<br>');
}

// --- 유틸 ---
function clampLineCount(n) {
    if (Number.isNaN(n)) return 10;
    return Math.max(5, Math.min(200, n));
}

// --- 각각 독립적으로 호출/갱신 ---
async function refreshRaw() {
    const n = clampLineCount(parseInt(lineCountEl.value, 10));
    try {
        const data = await fetchRawLog(n);
        updateRawUI(data); // RAW 먼저 도착하면 먼저 그림
    } catch (e) {
        console.error(e);
        updatedAtEl.textContent = '업데이트: - (RAW 로드 실패)';
    }
}

async function refreshSummary() {
    const n = clampLineCount(parseInt(lineCountEl.value, 10));
    try {
        const data = await fetchSummary(n);
        updateSummaryUI(data); // 요약은 나중에 와도 따로 갱신
    } catch (e) {
        console.error(e);
        summaryBox.textContent = '보안 해설을 불러오지 못했습니다.';
    }
}

// --- 초기 로드: 둘 다 동시에 시작하지만, 완료는 독립적으로 처리 ---
window.addEventListener('load', () => {
    lineCountEl.value = clampLineCount(parseInt(lineCountEl.value, 10));

    refreshRaw(); // RAW 먼저 뜸
    refreshSummary(); // 요약은 완료되는 대로 따로 뜸

    // 주기 갱신도 각자 따로 (원하면 주기 다르게 설정 가능)
    setInterval(refreshRaw, 10000);
    setInterval(refreshSummary, 10000);
});

// --- 수동 새로고침도 각자 호출 ---
btnRefresh.addEventListener('click', () => {
    lineCountEl.value = clampLineCount(parseInt(lineCountEl.value, 10));
    refreshRaw();
    refreshSummary();
});
