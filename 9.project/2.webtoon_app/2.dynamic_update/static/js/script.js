let intervalId;

function checkImagesLoaded(images) {
    return images.every((src) => src !== '/static/placeholder.png');
}

function updateImages() {
    const text = document.getElementById('text').value;
    fetch('/update_images', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
    })
        .then((response) => response.json())
        .then((data) => {
            let loadedCount = 0;
            for (let i = 0; i < data.length; i++) {
                if (data[i] !== '/static/placeholder.png') {
                    loadedCount++;
                }
                document.getElementById(`image-${i}`).src = data[i];
            }
            document.getElementById('status').textContent = `Images Loaded: ${loadedCount}/5`;
            if (checkImagesLoaded(data)) {
                clearInterval(intervalId);
                document.getElementById('status').textContent = 'All images loaded!';
            }
        });
}

function generateImages() {
    const text = document.getElementById('text').value;
    fetch('/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            text: text,
        }),
    })
        .then((response) => response.text())
        .then((data) => {
            document.getElementById('images').innerHTML = `
                <img id="image-0" src="/static/placeholder.png" width="200">
                <img id="image-1" src="/static/placeholder.png" width="200">
                <img id="image-2" src="/static/placeholder.png" width="200">
                <img id="image-3" src="/static/placeholder.png" width="200">
                <img id="image-4" src="/static/placeholder.png" width="200">
            `;
            document.getElementById('status').textContent = 'Images Loaded: 0/5';
            intervalId = setInterval(updateImages, 5000); // 5초마다 이미지 업데이트
        });
}
