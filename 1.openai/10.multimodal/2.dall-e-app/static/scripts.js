const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let startX, startY, isDrawing = false, imgData;
const coordinates = [];

function loadImage(url) {
    const img = new Image();
    img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
        imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    };
    img.src = url;
}

document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        loadImage(url);
    });
});

document.getElementById('generateForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    fetch('/generate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        loadImage(url);
    });
});

canvas.addEventListener('mousedown', function(e) {
    const rect = canvas.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;
    isDrawing = true;
});

canvas.addEventListener('mousemove', function(e) {
    if (isDrawing) {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const width = x - startX;
        const height = y - startY;
        ctx.putImageData(imgData, 0, 0);
        coordinates.forEach(coord => {
            ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
            ctx.fillRect(coord.x, coord.y, coord.width, coord.height);
        });
        ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
        ctx.fillRect(startX, startY, width, height);
    }
});

canvas.addEventListener('mouseup', function(e) {
    if (isDrawing) {
        isDrawing = false;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const width = x - startX;
        const height = y - startY;
        coordinates.push({ x: startX, y: startY, width: width, height: height });
        ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
        ctx.fillRect(startX, startY, width, height);
    }
});

document.getElementById('generateMask').addEventListener('click', function() {
    fetch('/generate_mask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ coordinates: coordinates })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        alert('Mask generated successfully');
        document.getElementById('maskImage').src = data.mask_path;
        document.getElementById('maskImage').style.display = 'block';
    });
});

document.getElementById('clearMask').addEventListener('click', function() {
    coordinates.length = 0;
    ctx.putImageData(imgData, 0, 0);
});

document.getElementById('editForm').addEventListener('submit', function(e) {
    e.preventDefault();
    document.getElementById('maskCoordinates').value = JSON.stringify(coordinates);
    const formData = new FormData(this);
    fetch('/edit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        loadImage(url);
    });
});
