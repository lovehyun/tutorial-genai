const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let startX, startY, isDrawing = false, imgData;
const coordinates = [];

function loadImage(url) {
    const img = new Image();
    img.onload = () => {
        // Set canvas size to match the image
        canvas.width = img.width;
        canvas.height = img.height;
        
        // Clear canvas and draw the image
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
        
        // Store the image data for later use
        imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        
        // Clear the coordinates array when loading a new image
        coordinates.length = 0;
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
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        loadImage(url);
    })
    .catch(error => {
        console.error('Error uploading image:', error);
        alert('Error uploading image: ' + error.message);
    });
});

document.getElementById('generateForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    fetch('/generate', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        loadImage(url);
    })
    .catch(error => {
        console.error('Error generating image:', error);
        alert('Error generating image: ' + error.message);
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
        
        // Calculate width and height (allow negative values for drawing in any direction)
        const width = x - startX;
        const height = y - startY;
        
        // Redraw the image
        ctx.putImageData(imgData, 0, 0);
        
        // Draw all saved coordinates
        coordinates.forEach(coord => {
            ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
            ctx.fillRect(coord.x, coord.y, coord.width, coord.height);
        });
        
        // Draw the current selection
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
        
        // Calculate width and height
        const width = x - startX;
        const height = y - startY;
        
        // Store the coordinates (allowing negative width/height)
        coordinates.push({ 
            x: startX, 
            y: startY, 
            width: width, 
            height: height 
        });
        
        // Draw the selection
        ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
        ctx.fillRect(startX, startY, width, height);
    }
});

document.getElementById('generateMask').addEventListener('click', function() {
    if (coordinates.length === 0) {
        alert('Please select at least one area on the image first.');
        return;
    }
    
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
        alert('Mask generated successfully! Areas marked in red will be edited.');
        
        // You can optionally display the mask
        const maskImg = document.getElementById('maskImage');
        maskImg.src = data.mask_path + '?t=' + new Date().getTime(); // Add timestamp to prevent caching
        maskImg.style.display = 'block';
    })
    .catch(error => {
        console.error('Error generating mask:', error);
        alert('Error generating mask: ' + error.message);
    });
});

document.getElementById('clearMask').addEventListener('click', function() {
    // Clear the coordinates array
    coordinates.length = 0;
    
    // Redraw the original image without selections
    if (imgData) {
        ctx.putImageData(imgData, 0, 0);
    }
    
    // Hide the mask image
    document.getElementById('maskImage').style.display = 'none';
});

document.getElementById('editForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    if (coordinates.length === 0) {
        alert('Please select at least one area and generate a mask before editing.');
        return;
    }
    
    const formData = new FormData(this);
    
    // Show loading indication
    const submitButton = this.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Editing...';
    submitButton.disabled = true;
    
    fetch('/edit', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        loadImage(url);
        alert('Image edited successfully!');
    })
    .catch(error => {
        console.error('Error editing image:', error);
        alert('Error editing image: ' + error.message);
    })
    .finally(() => {
        // Reset button state
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    });
});
