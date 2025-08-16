import re
import json
import time
from typing import Dict, List, Any
from .memory_agent import MemoryAgent
from .search_agent import SearchAgent
from .calculation_agent import CalculationAgent
from .chat_agent import ChatAgent

class AgentManager:
    def __init__(self):
        """Agent 매니저 초기화"""
        self.agents = {
            'memory': MemoryAgent(),
            'search': SearchAgent(),
            'calculation': CalculationAgent(),
            'chat': ChatAgent()
        }
        
        self.conversation_history = []
        self.active_agents = []
        
    def detect_agent_needs(self, message: str) -> List[str]:
        """메시지를 분석하여 필요한 agent들을 감지"""
        needed_agents = []
        
        # 검색이 필요한지 확인
        search_keywords = ['검색', '찾아', '정보', '뉴스', '최신', '현재', '어떻게', '무엇']
        if any(keyword in message for keyword in search_keywords):
            needed_agents.append('search')
        
        # 계산이 필요한지 확인
        calc_patterns = [
            r'\d+\s*[\+\-\*\/]\s*\d+',  # 기본 연산
            r'계산', r'더하기', r'빼기', r'곱하기', r'나누기',
            r'평균', r'합계', r'백분율'
        ]
        if any(re.search(pattern, message) for pattern in calc_patterns):
            needed_agents.append('calculation')
        
        # 항상 메모리와 채팅 agent는 필요
        needed_agents.extend(['memory', 'chat'])
        
        return list(set(needed_agents))  # 중복 제거
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """메시지 처리 (기본 버전)"""
        # 필요한 agent들 감지
        needed_agents = self.detect_agent_needs(message)
        self.active_agents = needed_agents
        
        # 메모리에 대화 저장
        memory_result = self.agents['memory'].process(message, self.conversation_history)
        self.conversation_history.append({
            'user': message,
            'timestamp': time.time(),
            'agents_used': needed_agents
        })
        
        # 검색이 필요한 경우
        search_result = None
        if 'search' in needed_agents:
            search_result = self.agents['search'].process(message)
        
        # 계산이 필요한 경우
        calc_result = None
        if 'calculation' in needed_agents:
            calc_result = self.agents['calculation'].process(message)
        
        # 최종 응답 생성
        chat_result = self.agents['chat'].process(
            message, 
            memory_result=memory_result,
            search_result=search_result,
            calc_result=calc_result
        )
        
        # 응답을 메모리에 저장
        self.conversation_history.append({
            'assistant': chat_result['response'],
            'timestamp': time.time(),
            'agents_used': needed_agents,
            'search_result': search_result,
            'calc_result': calc_result
        })
        
        return {
            'response': chat_result['response'],
            'agents_used': needed_agents,
            'search_result': search_result,
            'calc_result': calc_result,
            'memory_context': memory_result.get('context', ''),
            'thinking_process': chat_result.get('thinking_process', '')
        }
    
    def process_message_with_updates(self, message: str, socketio) -> Dict[str, Any]:
        """실시간 업데이트와 함께 메시지 처리"""
        # 처리 시작 알림
        socketio.emit('agent_status', {
            'status': 'processing',
            'message': '메시지를 분석하고 있습니다...'
        })
        
        # 필요한 agent들 감지
        needed_agents = self.detect_agent_needs(message)
        self.active_agents = needed_agents
        
        socketio.emit('agent_status', {
            'status': 'agents_detected',
            'agents': needed_agents,
            'message': f'감지된 Agent들: {", ".join(needed_agents)}'
        })
        
        # 메모리 처리
        socketio.emit('agent_status', {
            'status': 'memory_processing',
            'agent': 'memory',
            'message': '대화 기록을 분석하고 있습니다...',
            'memory_stats': self.agents['memory'].get_memory_stats(),
            'recent_messages': self.agents['memory'].get_recent_messages(3)
        })
        
        memory_result = self.agents['memory'].process(message, self.conversation_history)
        self.conversation_history.append({
            'user': message,
            'timestamp': time.time(),
            'agents_used': needed_agents
        })
        
        # 검색 처리
        search_result = None
        if 'search' in needed_agents:
            socketio.emit('agent_status', {
                'status': 'processing',
                'agent': 'search',
                'message': '외부 정보를 검색하고 있습니다...',
                'query': self.agents['search']._extract_search_query(message)
            })
            search_result = self.agents['search'].process(message)
            socketio.emit('agent_status', {
                'status': 'complete',
                'agent': 'search',
                'query': self.agents['search']._extract_search_query(message),
                'results': search_result.get('results', []) if search_result else []
            })
        
        # 계산 처리
        calc_result = None
        if 'calculation' in needed_agents:
            expression = self.agents['calculation']._extract_calculation(message)
            socketio.emit('agent_status', {
                'status': 'processing',
                'agent': 'calculation',
                'message': '계산을 수행하고 있습니다...',
                'expression': expression
            })
            calc_result = self.agents['calculation'].process(message)
            socketio.emit('agent_status', {
                'status': 'complete',
                'agent': 'calculation',
                'expression': expression,
                'calculation_steps': calc_result.get('steps', '') if calc_result else '',
                'result': calc_result.get('result', '') if calc_result else ''
            })
        
        # 채팅 응답 생성
        socketio.emit('agent_status', {
            'status': 'processing',
            'agent': 'chat',
            'message': '응답을 생성하고 있습니다...'
        })
        
        chat_result = self.agents['chat'].process(
            message, 
            memory_result=memory_result,
            search_result=search_result,
            calc_result=calc_result
        )
        
        socketio.emit('agent_status', {
            'status': 'complete',
            'agent': 'chat',
            'thinking_process': chat_result.get('thinking_process', []),
            'response': chat_result.get('response', '')
        })
        
        # 응답을 메모리에 저장
        self.conversation_history.append({
            'assistant': chat_result['response'],
            'timestamp': time.time(),
            'agents_used': needed_agents,
            'search_result': search_result,
            'calc_result': calc_result
        })
        
        final_response = {
            'response': chat_result['response'],
            'agents_used': needed_agents,
            'search_result': search_result,
            'calc_result': calc_result,
            'memory_context': memory_result.get('context', ''),
            'thinking_process': chat_result.get('thinking_process', '')
        }
        
        socketio.emit('agent_status', {
            'status': 'complete',
            'message': '처리가 완료되었습니다.'
        })
        
        return final_response
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """사용 가능한 agent들의 정보 반환"""
        return [
            {
                'name': 'memory',
                'description': '대화 기록을 저장하고 관리합니다.',
                'capabilities': ['대화 저장', '컨텍스트 유지', '이전 대화 참조']
            },
            {
                'name': 'search',
                'description': '외부 웹 검색을 통해 최신 정보를 제공합니다.',
                'capabilities': ['웹 검색', '뉴스 검색', '정보 수집']
            },
            {
                'name': 'calculation',
                'description': '수학적 계산과 통계를 수행합니다.',
                'capabilities': ['기본 연산', '통계 계산', '수식 해석']
            },
            {
                'name': 'chat',
                'description': '자연스러운 대화 응답을 생성합니다.',
                'capabilities': ['대화 생성', '컨텍스트 이해', '다중 agent 조율']
            }
        ]
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """대화 기록 반환"""
        return self.conversation_history
