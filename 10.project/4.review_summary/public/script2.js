let reviews = [];

async function submitReview() {
    const rating = document.querySelector('input[name="rating"]:checked');
    const opinion = document.getElementById('opinion').value;

    if (!rating || !opinion.trim()) {
        alert('Please provide a rating and your opinion.');
        return;
    }

    const review = {
        rating: parseInt(rating.value),
        opinion
    };

    try {
        // Submit the review to the server
        const response = await fetch('/api/reviews', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(review)
        });

        if (!response.ok) {
            throw new Error('Failed to submit review');
        }

        // Fetch updated reviews and AI summary
        await fetchReviews();
        await fetchAISummary();

        // Clear form fields
        document.querySelectorAll('input[name="rating"]').forEach(radio => radio.checked = false);
        document.getElementById('opinion').value = '';
    } catch (error) {
        console.error(error);
        alert('Error submitting review.');
    }
}

async function fetchReviews() {
    try {
        const response = await fetch('/api/reviews');
        if (!response.ok) {
            throw new Error('Failed to fetch reviews');
        }

        const data = await response.json();
        reviews = data.reviews;
        displayReviews();
    } catch (error) {
        console.error(error);
        alert('Error fetching reviews.');
    }
}

async function fetchAISummary() {
    const lang = document.getElementById('languageSelect').value;

    try {
        const response = await fetch(`/api/ai-summary?lang=${lang}`);
        if (!response.ok) {
            throw new Error('Failed to fetch AI summary');
        }

        const data = await response.json();
        displayAISummary(data.summary, data.averageRating);
    } catch (error) {
        console.error(error);
        alert('Error fetching AI summary.');
    }
}

function displayReviews() {
    const reviewsContainer = document.getElementById('reviews-container');

    // Remove existing review elements except the AI summary
    reviewsContainer.querySelectorAll('.review-box').forEach(box => box.remove());

    // Add each review
    reviews.forEach(review => {
        const reviewBox = document.createElement('div');
        reviewBox.className = 'review-box';
        reviewBox.innerHTML = `
            <p class="review-header">Rating: ${review.rating}</p>
            <p>${review.opinion}</p>
        `;
        reviewsContainer.appendChild(reviewBox);
    });
}

// 다국어 라벨 정의
const i18n = {
    ko: { summaryLabel: "AI 요약", avgLabel: "평균 별점" },
    en: { summaryLabel: "AI Summary", avgLabel: "Average Rating" },
    ja: { summaryLabel: "AI要約", avgLabel: "平均評価" },
    zh: { summaryLabel: "AI总结", avgLabel: "平均评分" },
    fr: { summaryLabel: "Résumé IA", avgLabel: "Note Moyenne" },
    it: { summaryLabel: "Riepilogo IA", avgLabel: "Valutazione Media" }
};

// AI 요약 및 평균 별점 렌더링
function displayAISummary(summary, averageRating) {
    const lang = document.getElementById('languageSelect').value;
    const labels = i18n[lang] || i18n['ko'];  // 기본값은 한국어

    const summaryBox = document.querySelector('.ai-summary');
    summaryBox.innerHTML = `
        <p><strong>${labels.summaryLabel}:</strong> ${summary}</p>
        <p><strong>${labels.avgLabel}:</strong> ${averageRating.toFixed(2)}</p>
    `;
}

// Initial fetch of reviews and AI summary
window.onload = async () => {
    await fetchReviews();
    await fetchAISummary();
};
