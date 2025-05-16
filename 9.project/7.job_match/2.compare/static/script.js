document.getElementById('pdfForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const res = await fetch('/upload_pdf', { method: 'POST', body: formData });
    const data = await res.json();
    document.getElementById('pdfPreview').innerText = data.text || 'PDF 텍스트를 가져올 수 없습니다.';
});

document.getElementById('urlForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const res = await fetch('/fetch_url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            url: form.url.value,
            xpath: form.xpath.value
        })
    });
    const data = await res.json();
    document.getElementById('urlPreview').innerText = data.text || 'URL 텍스트를 가져올 수 없습니다.';
});

document.getElementById("compareButton").addEventListener("click", async () => {
    const leftText = document.getElementById("pdfPreview").innerText;
    const rightText = document.getElementById("urlPreview").innerText;
    const resultBox = document.getElementById("compareResult");
    resultBox.innerText = "서버에 요청 중...";

    const res = await fetch('/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ left: leftText, right: rightText })
    });

    // 스트리밍 응답 처리
    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    resultBox.innerText = "";

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        resultBox.innerText += decoder.decode(value, { stream: true });
    }
});

document.getElementById("gptCompareButton").addEventListener("click", async () => {
    const leftText = document.getElementById("pdfPreview").innerText;
    const rightText = document.getElementById("urlPreview").innerText;
    const resultBox = document.getElementById("compareResult");
    resultBox.innerText = "GPT 분석 중...\n";

    const res = await fetch('/gpt_compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ left: leftText, right: rightText })
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    resultBox.innerText = "";

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        resultBox.innerText += decoder.decode(value, { stream: true });
    }
});
