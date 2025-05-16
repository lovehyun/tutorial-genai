// PDF 업로드 폼 제출 이벤트 처리
document.getElementById('pdfForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // 기본 폼 제출 막기

    const formData = new FormData(e.target); // FormData 객체 생성 (PDF 파일 포함)
    const button = e.target.querySelector('button'); // 폼 내의 버튼 요소 찾기
    toggleButtonState(button, true); // 버튼 비활성화 및 로딩 상태로 전환

    // 서버로 PDF 업로드 요청
    const res = await fetch('/upload_pdf', {
        method: 'POST',
        body: formData
    });

    // 응답 결과 처리
    const data = await res.json();
    document.getElementById('pdfPreview').innerText = data.text || 'PDF 텍스트를 가져올 수 없습니다.';

    toggleButtonState(button, false); // 버튼 상태 원래대로 복원
});

// URL + XPath 입력 폼 제출 이벤트 처리
document.getElementById('urlForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // 기본 폼 제출 막기

    const form = e.target;
    const button = form.querySelector('button'); // 버튼 요소 가져오기
    toggleButtonState(button, true); // 버튼 비활성화 및 로딩 상태 표시

    // 서버로 URL 텍스트 추출 요청
    const res = await fetch('/fetch_url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            url: form.url.value,
            xpath: form.xpath.value
        })
    });

    // 응답 결과 처리
    const data = await res.json();
    document.getElementById('urlPreview').innerText = data.text || 'URL 텍스트를 가져올 수 없습니다.';

    toggleButtonState(button, false); // 버튼 상태 복원
});

// 조건비교 버튼 클릭 시 실행
document.getElementById("compareButton").addEventListener("click", async () => {
    // 좌측(PDF) 및 우측(URL) 텍스트 가져오기
    const button = document.getElementById("compareButton");
    const leftText = document.getElementById("pdfPreview").innerText;
    const rightText = document.getElementById("urlPreview").innerText;
    const resultBox = document.getElementById("finalResult");

    resultBox.innerText = "서버에 요청 중...\n";

    toggleButtonState(button, true); // 버튼 비활성화 및 로딩 표시

    // 서버에 비교 요청
    const res = await fetch('/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ left: leftText, right: rightText })
    });

    // 응답 스트리밍 처리
    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    resultBox.innerText = "";

    // 스트리밍으로 전달된 텍스트를 순차적으로 출력
    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        resultBox.innerText += decoder.decode(value, { stream: true });
        resultBox.scrollTop = resultBox.scrollHeight; // 결과창 자동 스크롤
    }

    toggleButtonState(button, false); // 버튼 복원
});

// GPT 분석 버튼 클릭 시 실행
document.getElementById("gptCompareButton").addEventListener("click", async () => {
    // 좌측(PDF) 및 우측(URL) 텍스트 가져오기
    const button = document.getElementById("gptCompareButton");
    const leftText = document.getElementById("pdfPreview").innerText;
    const rightText = document.getElementById("urlPreview").innerText;
    const resultBox = document.getElementById("finalResult");

    resultBox.innerText = "GPT 분석 중...\n";

    toggleButtonState(button, true); // 버튼 비활성화 및 로딩 표시

    // 서버에 GPT 분석 요청
    const res = await fetch('/gpt_compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ left: leftText, right: rightText })
    });

    // 응답 스트리밍 처리
    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    resultBox.innerText = "";

    // GPT 응답을 순차적으로 출력
    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        resultBox.innerText += decoder.decode(value, { stream: true });
        resultBox.scrollTop = resultBox.scrollHeight; // 결과창 자동 스크롤
    }

    toggleButtonState(button, false); // 버튼 복원
});

// 버튼 활성/비활성 상태를 전환하는 함수
function toggleButtonState(button, isLoading) {
    if (!button) return;

    button.disabled = isLoading; // 클릭 방지
    button.classList.toggle("opacity-50", isLoading); // 반투명 효과
    button.classList.toggle("cursor-not-allowed", isLoading); // 커서 비활성화

    const label = button.dataset.label || button.innerText; // 원래 텍스트 기억

    if (isLoading) {
        // 로딩 중일 때 스피너와 함께 로딩 텍스트 표시
        button.innerHTML = `<svg class="animate-spin h-5 w-5 inline mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                               <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                               <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                            </svg> 로딩 중...`;
    } else {
        // 원래 텍스트로 복원
        button.innerHTML = label;
    }
}
