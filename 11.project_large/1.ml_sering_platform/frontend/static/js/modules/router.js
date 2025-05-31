// 페이지 로드 함수
export async function loadPage(path) {
    console.log('Router: Loading page:', path);
    try {
        const response = await fetch(path);
        if (!response.ok) {
            throw new Error(`Failed to load page: ${response.statusText}`);
        }
        const html = await response.text();
        
        // 현재 페이지의 스크립트 제거
        const currentScripts = document.querySelectorAll('script[type="module"]');
        currentScripts.forEach(script => script.remove());
        
        // 새 페이지로 교체
        document.documentElement.innerHTML = html;
        
        // 새 페이지의 스크립트 실행
        const newScripts = document.querySelectorAll('script[type="module"]');
        for (const script of newScripts) {
            const newScript = document.createElement('script');
            newScript.type = 'module';
            newScript.textContent = script.textContent;
            script.parentNode.replaceChild(newScript, script);
        }

        // URL 업데이트
        window.history.pushState({}, '', path);
        
        console.log('Router: Page loaded successfully');
    } catch (error) {
        console.error('Router: Error loading page:', error);
        throw error;
    }
}

// 네비게이션 설정
export function setupNavigation() {
    // 브라우저의 뒤로가기/앞으로가기 버튼 처리
    window.addEventListener('popstate', () => {
        loadPage(window.location.pathname);
    });

    // 링크 클릭 처리
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (link && link.href.startsWith(window.location.origin)) {
            e.preventDefault();
            loadPage(link.pathname);
        }
    });
} 