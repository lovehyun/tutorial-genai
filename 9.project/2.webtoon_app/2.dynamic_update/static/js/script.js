let intervalId;
let selectedModel = 'dall-e-2'; // 기본값은 DALL-E 2

// 모델 선택 함수
function selectModel(model) {
    selectedModel = model === 'dalle2' ? 'dall-e-2' : 'dall-e-3';
    
    // 버튼 스타일 업데이트
    document.getElementById('dalle2-btn').classList.toggle('active', model === 'dalle2');
    document.getElementById('dalle3-btn').classList.toggle('active', model === 'dalle3');
    
    console.log(`Selected model: ${selectedModel}`);
}

function checkImagesLoaded(images) {
    return images.every(src => src !== '/static/placeholder.png');
}

function updateImages() {
    fetch('/update_images', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    })
        .then(res => res.json())
        .then(data => {
            data.forEach((src, i) => {
                const img = document.getElementById(`image-${i}`);
                img.src = src;

                // 클릭 시 원본 이미지 새 탭으로 열기
                img.style.cursor = 'pointer';  // 마우스 커서 변경
                img.onclick = () => {
                    if (src !== '/static/placeholder.png') {
                        window.open(src, '_blank');
                    }
                };
            });

            const count = data.filter(src => src !== '/static/placeholder.png').length;
            document.getElementById('status').textContent = `Images Loaded: ${count}/5`;

            if (checkImagesLoaded(data)) {
                clearInterval(intervalId);
                document.getElementById('status').textContent = '✅ All images loaded!';
            }
        });
}

function generateImages() {
    const text = document.getElementById('text').value;
    
    if (!text.trim()) {
        alert('텍스트를 입력해주세요.');
        return;
    }

    // 상태 초기화
    document.getElementById('status').textContent = '요청 처리 중...';
    for (let i = 0; i < 5; i++) {
        document.getElementById(`image-${i}`).src = '/static/placeholder.png';
    }

    fetch('/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            text: text,
            model: selectedModel  // 선택된 모델 정보 추가
        })
    })
        .then(res => res.json())
        .then(data => {
            const summaryEl = document.getElementById('summary');
            summaryEl.innerHTML = '';
            data.prompts.forEach(p => {
                const li = document.createElement('li');
                li.textContent = p;
                summaryEl.appendChild(li);
            });

            document.getElementById('status').textContent = 'Images Loaded: 0/5';
            clearInterval(intervalId); // 기존 인터벌 제거
            intervalId = setInterval(updateImages, 3000); // 3초마다 업데이트
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('status').textContent = '오류가 발생했습니다.';
        });
}
