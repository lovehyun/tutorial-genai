// 토스트 컨테이너 생성
function createToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 64px;  /* 네비게이션 바 높이 */
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
            width: 100%;
            max-width: 1200px;
            padding: 0 20px;
            pointer-events: none;
        `;
        document.body.insertBefore(container, document.body.firstChild);
    }
    return container;
}

// 토스트 메시지를 표시하는 함수
export function showToast(message, type = 'info') {
    // 토스트 컨테이너가 없으면 생성
    const toastContainer = createToastContainer();

    // 토스트 메시지 생성
    const toast = document.createElement('div');
    toast.style.cssText = `
        padding: 12px 24px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: ${type === 'success' ? '#10B981' : type === 'error' ? '#EF4444' : '#3B82F6'};
        min-width: 200px;
        max-width: 400px;
        transform: translateY(-100%);
        transition: transform 0.3s ease-out;
        display: flex;
        align-items: center;
        justify-content: space-between;
        pointer-events: auto;
    `;

    // 메시지 텍스트
    const messageSpan = document.createElement('span');
    messageSpan.textContent = message;
    toast.appendChild(messageSpan);

    // 닫기 버튼
    const closeButton = document.createElement('button');
    closeButton.innerHTML = `
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
    `;
    closeButton.style.cssText = `
        margin-left: 12px;
        cursor: pointer;
        opacity: 0.7;
        transition: opacity 0.2s;
        background: none;
        border: none;
        color: white;
        padding: 0;
    `;
    closeButton.onmouseover = () => closeButton.style.opacity = '1';
    closeButton.onmouseout = () => closeButton.style.opacity = '0.7';
    closeButton.onclick = () => {
        toast.style.transform = 'translateY(-100%)';
        setTimeout(() => toast.remove(), 300);
    };
    toast.appendChild(closeButton);

    // 토스트 컨테이너에 추가
    toastContainer.appendChild(toast);

    // 애니메이션 시작
    requestAnimationFrame(() => {
        toast.style.transform = 'translateY(0)';
    });

    // 3초 후 자동으로 제거
    setTimeout(() => {
        toast.style.transform = 'translateY(-100%)';
        setTimeout(() => {
            if (toast.parentNode === toastContainer) {
                toast.remove();
            }
        }, 300);
    }, 3000);
}

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            transform: translateY(-100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    @keyframes slideUp {
        from {
            transform: translateY(0);
            opacity: 1;
        }
        to {
            transform: translateY(-100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style); 