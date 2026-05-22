const imageInput = document.getElementById('imageInput');
const preview = document.getElementById('preview');
const uploadForm = document.getElementById('uploadForm');

const resultBox = document.getElementById('result');
const submitBtn = document.getElementById("submitBtn");
const progressBar = document.getElementById("progressBar");

// 이미지 미리보기
imageInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
});

// 설명 생성 요청 (fetch로 전송)
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData();
    const imageFile = imageInput.files[0];
    if (!imageFile) {
        alert('이미지를 선택해주세요!');
        return;
    }

    formData.append('image', imageFile);

    // 버튼 비활성화 및 로딩 표시
    submitBtn.disabled = true;
    resultBox.textContent = "GPT 응답을 기다리는 중...";
    progressBar.style.display = "block";

    try {
        const res = await fetch('/generate', {
            method: 'POST',
            body: formData,
        });
        const data = await res.json();
        resultBox.innerHTML = `<strong>GPT 설명:</strong><br>${data.answer}`;
    } catch (err) {
        console.error(err);
        resultBox.innerHTML = '오류 발생!';
    } finally {
        // 버튼 다시 활성화
        submitBtn.disabled = false;
        submitBtn.textContent = "설명 생성";
        progressBar.style.display = "none";
    }
});
