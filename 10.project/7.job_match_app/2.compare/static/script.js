// PDF 업로드 폼 제출 이벤트 처리
document.getElementById('pdfForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // 기본 폼 제출 막기

    const formData = new FormData(e.target); // FormData 객체 생성 (PDF 파일 포함)

    // 서버로 PDF 업로드 요청
    const res = await fetch('/upload_pdf', {
        method: 'POST',
        body: formData
    });

    // 응답 결과 처리
    const data = await res.json();
    document.getElementById('pdfPreview').innerText = data.text || 'PDF 텍스트를 가져올 수 없습니다.';
});

// URL + XPath 입력 폼 제출 이벤트 처리
document.getElementById('urlForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // 기본 폼 제출 막기

    const form = e.target;

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
});

// 조건비교 버튼 클릭 시 실행
document.getElementById("compareButton").addEventListener("click", async () => {
    // 좌측(PDF) 및 우측(URL) 텍스트 가져오기
    const leftText = document.getElementById("pdfPreview").innerText;
    const rightText = document.getElementById("urlPreview").innerText;
    const resultBox = document.getElementById("compareResult");

    resultBox.innerText = "서버에 요청 중...";

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
});

// GPT 분석 버튼 클릭 시 실행
document.getElementById("gptCompareButton").addEventListener("click", async () => {
    // 좌측(PDF) 및 우측(URL) 텍스트 가져오기
    const leftText = document.getElementById("pdfPreview").innerText;
    const rightText = document.getElementById("urlPreview").innerText;
    const resultBox = document.getElementById("compareResult");

    resultBox.innerText = "GPT 분석 중...\n";

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
});
