/**
 * Agent 상태 관리 모듈
 */
class AgentManager {
    constructor() {
        this.agentList = document.getElementById('agentList');
        this.initializeAgentElements();
    }

    /**
     * Agent 요소들 초기화
     */
    initializeAgentElements() {
        this.agents = {
            memory: {
                element: this.agentList.querySelector('[data-agent="memory"]'),
                entries: document.getElementById('memoryEntries'),
                usage: document.getElementById('memoryUsage')
            },
            search: {
                element: this.agentList.querySelector('[data-agent="search"]'),
                query: document.getElementById('searchQuery'),
                results: document.getElementById('searchResults')
            },
            calculation: {
                element: this.agentList.querySelector('[data-agent="calculation"]'),
                expression: document.getElementById('calcExpression'),
                steps: document.getElementById('calcSteps'),
                result: document.getElementById('calcResult')
            },
            chat: {
                element: this.agentList.querySelector('[data-agent="chat"]'),
                thinking: document.getElementById('chatThinking'),
                response: document.getElementById('chatResponse')
            }
        };
    }

    /**
     * Agent 상태 업데이트
     */
    updateAgentStatus(data) {
        if (data.agent && this.agents[data.agent]) {
            const agent = this.agents[data.agent];
            const statusText = agent.element.querySelector('.agent-status-text');
            
            if (data.status === 'processing') {
                agent.element.classList.add('processing');
                statusText.textContent = '처리 중...';
                this.updateAgentDetails(data.agent, data);
            } else if (data.status === 'complete') {
                agent.element.classList.add('complete');
                statusText.textContent = '완료';
                this.updateAgentDetails(data.agent, data);
            }
        }
    }

    /**
     * Agent별 상세 정보 업데이트
     */
    updateAgentDetails(agentName, data) {
        switch(agentName) {
            case 'memory':
                this.updateMemoryDetails(data);
                break;
            case 'search':
                this.updateSearchDetails(data);
                break;
            case 'calculation':
                this.updateCalculationDetails(data);
                break;
            case 'chat':
                this.updateChatDetails(data);
                break;
        }
    }

    /**
     * Memory Agent 상세 정보 업데이트
     */
    updateMemoryDetails(data) {
        const agent = this.agents.memory;
        
        if (data.memory_stats) {
            agent.usage.textContent = `${data.memory_stats.total_entries}/${data.memory_stats.max_memory_size}`;
        }
        
        if (data.recent_messages) {
            let html = '';
            data.recent_messages.forEach(msg => {
                html += `<div class="memory-entry">${msg}</div>`;
            });
            agent.entries.innerHTML = html;
        }
    }

    /**
     * Search Agent 상세 정보 업데이트
     */
    updateSearchDetails(data) {
        const agent = this.agents.search;
        
        if (data.query) {
            agent.query.textContent = data.query;
        }
        
        if (data.results && data.results.length > 0) {
            let html = '';
            data.results.slice(0, 3).forEach(result => {
                html += `<div class="search-result-mini">
                    <strong>${result.title}</strong><br>
                    ${result.snippet ? result.snippet.substring(0, 50) + '...' : ''}
                </div>`;
            });
            agent.results.innerHTML = html;
        } else {
            agent.results.innerHTML = '검색 결과가 없습니다.';
        }
    }

    /**
     * Calculation Agent 상세 정보 업데이트
     */
    updateCalculationDetails(data) {
        const agent = this.agents.calculation;
        
        if (data.expression) {
            agent.expression.textContent = data.expression;
        }
        
        if (data.calculation_steps) {
            agent.steps.textContent = data.calculation_steps;
        }
        
        if (data.result !== undefined) {
            agent.result.textContent = data.result;
        }
    }

    /**
     * Chat Agent 상세 정보 업데이트
     */
    updateChatDetails(data) {
        const agent = this.agents.chat;
        
        if (data.thinking_process) {
            agent.thinking.textContent = data.thinking_process.join(', ');
        }
        
        if (data.response) {
            agent.response.textContent = data.response.substring(0, 100) + (data.response.length > 100 ? '...' : '');
        }
    }

    /**
     * 모든 Agent 상태 초기화
     */
    resetAllAgents() {
        Object.values(this.agents).forEach(agent => {
            agent.element.classList.remove('active', 'processing', 'complete');
            const statusText = agent.element.querySelector('.agent-status-text');
            statusText.textContent = '대기 중';
        });
    }
}
