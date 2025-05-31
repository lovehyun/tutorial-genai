// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    // 네비게이션 바 활성화
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}); 