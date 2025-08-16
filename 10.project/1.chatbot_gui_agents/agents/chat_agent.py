import random
from typing import Dict, List, Any

class ChatAgent:
    def __init__(self):
        """채팅 Agent 초기화"""
        self.responses = {
            'greeting': [
                "안녕하세요! 무엇을 도와드릴까요?",
                "반갑습니다! 질문이나 도움이 필요한 것이 있으시면 말씀해 주세요.",
                "안녕하세요! 저는 다양한 기능을 가진 AI 어시스턴트입니다."
            ],
            'farewell': [
                "안녕히 가세요! 또 궁금한 것이 있으시면 언제든 말씀해 주세요.",
                "도움이 되었다니 기쁩니다. 다음에 또 만나요!",
                "좋은 하루 되세요!"
            ],
            'thanks': [
                "천만에요! 도움이 되어서 기쁩니다.",
                "별 말씀을요! 더 필요한 것이 있으시면 언제든 말씀해 주세요.",
                "감사합니다! 저도 도움이 되어서 기쁩니다."
            ],
            'confused': [
                "죄송합니다. 질문을 정확히 이해하지 못했어요. 다시 한 번 말씀해 주시겠어요?",
                "조금 더 구체적으로 말씀해 주시면 더 정확한 답변을 드릴 수 있을 것 같아요.",
                "이해하기 어려운 부분이 있어요. 다른 방식으로 질문해 주시겠어요?"
            ],
            'calculation': [
                "계산 결과를 확인해 보세요.",
                "수학적 계산이 완료되었습니다.",
                "계산이 성공적으로 수행되었습니다."
            ],
            'search': [
                "검색 결과를 확인해 보세요.",
                "관련 정보를 찾았습니다.",
                "요청하신 정보를 검색했습니다."
            ]
        }
        
    def process(self, message: str, memory_result: Dict[str, Any] = None, 
                search_result: Dict[str, Any] = None, calc_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """메시지를 처리하고 응답 생성"""
        
        # 생각 과정 기록
        thinking_process = []
        
        # 메모리 컨텍스트 확인
        if memory_result and memory_result.get('context'):
            thinking_process.append(f"메모리 컨텍스트: {memory_result['context'][:100]}...")
        
        # 검색 결과 확인
        if search_result and search_result.get('status') == 'success':
            thinking_process.append(f"검색 결과: {search_result['query']}에 대한 {len(search_result['results'])}개 결과 발견")
        
        # 계산 결과 확인
        if calc_result and calc_result.get('status') == 'success':
            thinking_process.append(f"계산 결과: {calc_result['expression']} = {calc_result['result']}")
        
        # 응답 생성
        response = self._generate_response(message, search_result, calc_result)
        
        return {
            'response': response,
            'thinking_process': thinking_process,
            'agents_used': self._get_used_agents(search_result, calc_result)
        }
    
    def _generate_response(self, message: str, search_result: Dict[str, Any] = None, 
                          calc_result: Dict[str, Any] = None) -> str:
        """응답 생성"""
        
        # 인사말 처리
        if self._is_greeting(message):
            return random.choice(self.responses['greeting'])
        
        # 작별 인사 처리
        if self._is_farewell(message):
            return random.choice(self.responses['farewell'])
        
        # 감사 표현 처리
        if self._is_thanks(message):
            return random.choice(self.responses['thanks'])
        
        # 계산 결과가 있는 경우
        if calc_result and calc_result.get('status') == 'success':
            calc_response = f"{random.choice(self.responses['calculation'])} {calc_result['message']}"
            
            # 추가 설명
            if calc_result.get('expression'):
                calc_response += f"\n\n수식: {calc_result['expression']}"
                calc_response += f"\n결과: {calc_result['result']}"
            
            return calc_response
        
        # 검색 결과가 있는 경우
        if search_result and search_result.get('status') == 'success':
            search_response = f"{random.choice(self.responses['search'])} {search_result['message']}"
            
            # 검색 결과 요약
            if search_result.get('results'):
                results = search_result['results'][:3]  # 상위 3개 결과만
                search_response += "\n\n주요 결과:"
                for i, result in enumerate(results, 1):
                    search_response += f"\n{i}. {result.get('title', '제목 없음')}"
                    if result.get('snippet'):
                        search_response += f" - {result['snippet'][:100]}..."
            
            return search_response
        
        # 일반적인 응답
        return self._generate_general_response(message)
    
    def _is_greeting(self, message: str) -> bool:
        """인사말인지 확인"""
        greetings = ['안녕', '반가워', 'hello', 'hi', '안녕하세요', '반갑습니다']
        return any(greeting in message.lower() for greeting in greetings)
    
    def _is_farewell(self, message: str) -> bool:
        """작별 인사인지 확인"""
        farewells = ['안녕', '잘가', 'goodbye', 'bye', '안녕히', '다음에', '나중에']
        return any(farewell in message.lower() for farewell in farewells)
    
    def _is_thanks(self, message: str) -> bool:
        """감사 표현인지 확인"""
        thanks = ['고마워', '감사', 'thank', 'thanks', '고맙습니다', '감사합니다']
        return any(thank in message.lower() for thank in thanks)
    
    def _generate_general_response(self, message: str) -> str:
        """일반적인 응답 생성"""
        # 질문 패턴에 따른 응답
        if '?' in message or '무엇' in message or '어떻게' in message:
            return self._generate_question_response(message)
        elif '설명' in message or '알려' in message:
            return self._generate_explanation_response(message)
        else:
            return self._generate_conversation_response(message)
    
    def _generate_question_response(self, message: str) -> str:
        """질문에 대한 응답 생성"""
        responses = [
            "좋은 질문이네요! 더 구체적으로 말씀해 주시면 더 정확한 답변을 드릴 수 있을 것 같아요.",
            "흥미로운 질문입니다. 어떤 부분에 대해 더 알고 싶으신가요?",
            "이 질문에 대해 더 자세히 알아보고 싶으시군요. 어떤 관점에서 궁금하신가요?"
        ]
        return random.choice(responses)
    
    def _generate_explanation_response(self, message: str) -> str:
        """설명 요청에 대한 응답 생성"""
        responses = [
            "물론이죠! 어떤 부분에 대해 설명해 드릴까요?",
            "기꺼이 설명해 드리겠습니다. 어떤 점이 궁금하신가요?",
            "좋습니다! 더 자세한 설명이 필요하시군요. 어떤 부분부터 시작할까요?"
        ]
        return random.choice(responses)
    
    def _generate_conversation_response(self, message: str) -> str:
        """일반 대화 응답 생성"""
        responses = [
            "흥미로운 이야기네요! 더 자세히 들려주세요.",
            "그렇군요. 어떤 생각이 드시나요?",
            "좋은 관점입니다. 다른 측면도 고려해 보시는 건 어떨까요?",
            "이해했습니다. 더 구체적으로 말씀해 주시면 더 나은 대화를 나눌 수 있을 것 같아요."
        ]
        return random.choice(responses)
    
    def _get_used_agents(self, search_result: Dict[str, Any] = None, 
                        calc_result: Dict[str, Any] = None) -> List[str]:
        """사용된 agent들 목록 반환"""
        agents = ['chat']
        
        if search_result and search_result.get('status') == 'success':
            agents.append('search')
        
        if calc_result and calc_result.get('status') == 'success':
            agents.append('calculation')
        
        return agents
    
    def get_response_templates(self) -> Dict[str, List[str]]:
        """응답 템플릿 반환"""
        return self.responses
    
    def add_response_template(self, category: str, response: str):
        """응답 템플릿 추가"""
        if category not in self.responses:
            self.responses[category] = []
        
        self.responses[category].append(response)
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Agent의 능력 반환"""
        return {
            'conversation': [
                '자연스러운 대화',
                '질문 응답',
                '감정 인식',
                '컨텍스트 이해'
            ],
            'integration': [
                '다중 agent 조율',
                '결과 통합',
                '응답 생성'
            ]
        }
