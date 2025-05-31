export class Footer extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    background-color: #1f2937;
                    color: #f3f4f6;
                    padding: 2rem 0;
                    margin-top: 4rem;
                }
                .footer {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 0 2rem;
                    text-align: center;
                }
                .footer-content {
                    margin-bottom: 1rem;
                }
                .footer-content p {
                    color: #d1d5db;
                    margin-bottom: 0.5rem;
                }
                .footer-bottom {
                    padding-top: 1rem;
                    border-top: 1px solid #374151;
                    color: #9ca3af;
                }
            </style>
            <footer class="footer">
                <div class="footer-content">
                    <p>ML Model Serving Platform</p>
                    <p>A platform for deploying and managing machine learning models</p>
                </div>
                <div class="footer-bottom">
                    <p>&copy; 2024 ML Model Serving Platform. All rights reserved.</p>
                </div>
            </footer>
        `;
    }
}

customElements.define('app-footer', Footer); 