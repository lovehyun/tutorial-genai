export class Navbar extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.render();
        this.updateAuthStatus();
    }

    connectedCallback() {
        // 인증 상태 변경 감지
        window.addEventListener('storage', (e) => {
            if (e.key === 'token') {
                this.updateAuthStatus();
            }
        });
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    background-color: #1f2937;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .navbar {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1rem 2rem;
                    max-width: 1200px;
                    margin: 0 auto;
                }
                .brand {
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: #f3f4f6;
                    text-decoration: none;
                }
                .nav-links {
                    display: flex;
                    gap: 1.5rem;
                }
                .nav-link {
                    color: #d1d5db;
                    text-decoration: none;
                    font-weight: 500;
                }
                .nav-link:hover {
                    color: #f3f4f6;
                }
                .nav-link.active {
                    color: #f3f4f6;
                }
                .auth-buttons {
                    display: flex;
                    gap: 1rem;
                }
                .btn {
                    padding: 0.5rem 1rem;
                    border-radius: 0.375rem;
                    font-weight: 500;
                    cursor: pointer;
                    text-decoration: none;
                    border: none;
                    font-size: 0.875rem;
                }
                .btn-primary {
                    background-color: #3b82f6;
                    color: white;
                }
                .btn-primary:hover {
                    background-color: #2563eb;
                }
                .btn-outline {
                    background-color: transparent;
                    border: 1px solid #4b5563;
                    color: #d1d5db;
                }
                .btn-outline:hover {
                    background-color: #374151;
                    color: #f3f4f6;
                }
                .btn-danger {
                    background-color: #3b82f6;
                    color: white;
                }
                .btn-danger:hover {
                    background-color: #2563eb;
                }
            </style>
            <nav class="navbar">
                <a href="/" class="brand">ML Model Serving</a>
                <div class="nav-links">
                    <a href="/models.html" class="nav-link">Models</a>
                    <a href="/api-keys.html" class="nav-link" id="apiKeysLink" style="display: none;">API Keys</a>
                    <a href="/endpoints.html" class="nav-link">Endpoints</a>
                    <a href="/inference.html" class="nav-link">Inference</a>
                    <a href="/docs" class="nav-link" target="_blank">API Docs</a>
                </div>
                <div class="auth-buttons">
                    <a href="/login.html" class="btn btn-outline" id="loginBtn">Login</a>
                    <a href="/register.html" class="btn btn-primary" id="registerBtn">Register</a>
                    <button class="btn btn-danger" id="logoutBtn" style="display: none;">Logout</button>
                </div>
            </nav>
        `;

        // 로그아웃 버튼 이벤트 리스너
        const logoutBtn = this.shadowRoot.getElementById('logoutBtn');
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('token');
            window.location.href = '/login.html';
        });
    }

    updateAuthStatus() {
        const token = localStorage.getItem('token');
        const loginBtn = this.shadowRoot.getElementById('loginBtn');
        const registerBtn = this.shadowRoot.getElementById('registerBtn');
        const logoutBtn = this.shadowRoot.getElementById('logoutBtn');
        const apiKeysLink = this.shadowRoot.getElementById('apiKeysLink');

        if (token) {
            loginBtn.style.display = 'none';
            registerBtn.style.display = 'none';
            logoutBtn.style.display = 'block';
            apiKeysLink.style.display = 'block';
        } else {
            loginBtn.style.display = 'block';
            registerBtn.style.display = 'block';
            logoutBtn.style.display = 'none';
            apiKeysLink.style.display = 'none';
        }
    }
}

customElements.define('nav-bar', Navbar); 