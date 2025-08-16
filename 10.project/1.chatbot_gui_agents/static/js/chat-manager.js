/**
 * 채팅 메시지 관리 모듈
 */
class ChatManager {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.processingIndicator = document.getElementById('processingIndicator');
        this.processingText = document.getElementById('processingText');
    }

    /**
     * 사용자 메시지 추가
     */
    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.innerHTML = `
            <div class="message-avatar">나</div>
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(message)}</div>
                <div class="message-meta">${new Date().toLocaleTimeString()}</div>
            </div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * 어시스턴트 메시지 추가
     */
    addAssistantMessage(data) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        
        let content = `<div class="message-text">${this.escapeHtml(data.response)}</div>`;
        
        // 사용된 Agent들 표시
        if (data.agents_used && data.agents_used.length > 0) {
            content += '<div class="agents-used">';
            data.agents_used.forEach(agent => {
                content += `<span class="agent-tag">${agent}</span>`;
            });
            content += '</div>';
        }
        
        // 검색 결과 표시
        if (data.search_result && data.search_result.status === 'success') {
            content += this.createSearchResultsHTML(data.search_result);
        }
        
        // 계산 결과 표시
        if (data.calc_result && data.calc_result.status === 'success') {
            content += this.createCalculationResultsHTML(data.calc_result);
        }
        
        // 생각 과정 표시
        if (data.thinking_process && data.thinking_process.length > 0) {
            content += '<div class="thinking-process">';
            content += '<strong>생각 과정:</strong><br>';
            data.thinking_process.forEach(process => {
                content += `• ${this.escapeHtml(process)}<br>`;
            });
            content += '</div>';
        }
        
        content += `<div class="message-meta">${new Date().toLocaleTimeString()}</div>`;
        
        messageDiv.innerHTML = `
            <div class="message-avatar">AI</div>
            <div class="message-content">${content}</div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * 오류 메시지 추가
     */
    addErrorMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        messageDiv.innerHTML = `
            <div class="message-avatar">AI</div>
            <div class="message-content">
                <div class="message-text" style="color: #dc3545;">❌ ${this.escapeHtml(message)}</div>
                <div class="message-meta">${new Date().toLocaleTimeString()}</div>
            </div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * 검색 결과 HTML 생성
     */
    createSearchResultsHTML(searchResult) {
        let html = '<div class="search-results">';
        html += '<div class="results-title">🔍 검색 결과</div>';
        
        if (searchResult.results && searchResult.results.length > 0) {
            searchResult.results.forEach(result => {
                html += '<div class="result-item">';
                html += `<div class="result-title">${this.escapeHtml(result.title)}</div>`;
                if (result.snippet) {
                    html += `<div class="result-snippet">${this.escapeHtml(result.snippet)}</div>`;
                }
                html += '</div>';
            });
        }
        
        html += '</div>';
        return html;
    }

    /**
     * 계산 결과 HTML 생성
     */
    createCalculationResultsHTML(calcResult) {
        let html = '<div class="calculation-result">';
        html += '<div class="results-title">🧮 계산 결과</div>';
        html += `<div class="calculation-expression">${this.escapeHtml(calcResult.expression)}</div>`;
        html += `<div class="calculation-answer">= ${calcResult.result}</div>`;
        html += '</div>';
        return html;
    }

    /**
     * 처리 중 표시
     */
    showProcessingIndicator() {
        this.processingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    /**
     * 처리 중 숨김
     */
    hideProcessingIndicator() {
        this.processingIndicator.style.display = 'none';
    }

    /**
     * 처리 상태 업데이트
     */
    updateProcessingStatus(message) {
        this.processingText.textContent = message || '메시지를 처리하고 있습니다...';
    }

    /**
     * 스크롤을 맨 아래로
     */
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    /**
     * HTML 이스케이프
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
