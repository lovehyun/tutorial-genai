document.addEventListener('DOMContentLoaded', () => {
    const generateForm = document.getElementById('generateForm');
    const promptInput = document.getElementById('promptInput');
    const generateBtn = document.getElementById('generateBtn');
    const loadingDiv = document.getElementById('loading');
    const gallery = document.getElementById('gallery');
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const modalPrompt = document.getElementById('modalPrompt');
    const closeBtn = document.getElementsByClassName('close')[0];
    const notification = document.getElementById('notification');

    // Handle form submission
    generateForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const prompt = promptInput.value.trim();
        if (!prompt) return;

        // Show loading state
        generateBtn.disabled = true;
        loadingDiv.style.display = 'block';

        // Create form data
        const formData = new FormData();
        formData.append('prompt', prompt);

        try {
            // Send API request
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (data.success) {
                // Show notification
                notification.textContent = 'Image generated successfully!';
                notification.classList.remove('error-notification');
                notification.style.display = 'block';
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 3000);

                // Update gallery with new images
                updateGallery(data.gallery_images);

                // Clear input
                promptInput.value = '';
            } else {
                throw new Error(data.error || 'Failed to generate image');
            }
        } catch (error) {
            console.error('Error:', error);
            notification.textContent = `Error: ${error.message}`;
            notification.classList.add('error-notification');
            notification.style.display = 'block';
            setTimeout(() => {
                notification.style.display = 'none';
            }, 5000);
        } finally {
            // Hide loading state
            generateBtn.disabled = false;
            loadingDiv.style.display = 'none';
        }
    });

    // Update gallery with new images
    function updateGallery(images) {
        gallery.innerHTML = '';

        images.forEach((image) => {
            const galleryItem = document.createElement('div');
            galleryItem.className = 'gallery-item';
            galleryItem.dataset.fullsize = image.fullsize;
            galleryItem.dataset.prompt = image.prompt;

            galleryItem.innerHTML = `
                        <img src="${image.thumbnail}" alt="Generated image" class="gallery-thumbnail">
                        <div class="gallery-info">
                            <div class="gallery-prompt">${image.prompt}</div>
                            <div class="gallery-date">${image.created_at ? image.created_at.split('T')[0] : ''}</div>
                        </div>
                    `;

            gallery.appendChild(galleryItem);
        });

        // Reattach click handlers to new gallery items
        attachGalleryClickHandlers();
    }

    // Attach click handlers to gallery items
    function attachGalleryClickHandlers() {
        const galleryItems = document.querySelectorAll('.gallery-item');

        galleryItems.forEach((item) => {
            item.addEventListener('click', () => {
                modal.style.display = 'block';
                modalImg.src = item.dataset.fullsize;
                modalPrompt.textContent = item.dataset.prompt;
            });
        });
    }

    // Initial attachment of click handlers
    attachGalleryClickHandlers();

    // Close modal when clicking the x
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside the image
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});
