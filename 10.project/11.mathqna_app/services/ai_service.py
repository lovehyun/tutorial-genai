# services/ai_service.py
"""AI 서비스 모듈 - 통합 설정 기반"""

import os
import re
import logging
from typing import Tuple, Dict, Any, Optional
from contextlib import nullcontext

# 통합 설정 임포트
from config.settings import AISettings, PromptTemplates, EvaluationCriteria, ResponseFormatting

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIService:
    """통합 설정 기반 LangChain Agent AI 서비스"""
    
    def __init__(self):
        """AI 서비스 초기화"""
        self.agent = None
        self.llm = None
        self.tools = None
        self.memory = None
        
        # 통합 설정 클래스들 초기화
        self.settings = AISettings()
        self.prompts = PromptTemplates()
        self.evaluation = EvaluationCriteria()
        self.formatting = ResponseFormatting()
        
        # LangChain 초기화
        self.is_initialized = self._initialize_langchain()
        
        if not self.is_initialized:
            raise Exception("LangChain 초기화에 실패했습니다. OpenAI API 키와 패키지 설치를 확인하세요.")
    
    def _initialize_langchain(self) -> bool:
        """LangChain 초기화"""
        try:
            # API 키 확인
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.error("OPENAI_API_KEY가 환경변수에 설정되지 않았습니다.")
                return False
            
            # LangChain 모듈 임포트
            logger.info("LangChain 모듈을 로드하는 중...")
            from langchain.agents import initialize_agent, AgentType
            from langchain_community.agent_toolkits.load_tools import load_tools
            from langchain_openai import ChatOpenAI
            from langchain.memory import ConversationBufferWindowMemory
            
            # LLM 초기화 (ChatCompletion 모델 사용)
            logger.info("OpenAI ChatCompletion LLM을 초기화하는 중...")
            self.llm = ChatOpenAI(
                openai_api_key=api_key,
                **self.settings.LLM_CONFIG
            )
            
            # 도구 로드
            logger.info("LangChain 도구들을 로드하는 중...")
            self.tools = load_tools(
                self.settings.AVAILABLE_TOOLS, 
                llm=self.llm
            )
            
            # 메모리 설정
            logger.info("대화 메모리를 설정하는 중...")
            self.memory = ConversationBufferWindowMemory(
                memory_key=self.settings.MEMORY_CONFIG["memory_key"],
                return_messages=self.settings.MEMORY_CONFIG["return_messages"],
                k=self.settings.MEMORY_CONFIG["k"]
            )
            
            # Agent 초기화
            logger.info("Conversational Agent를 초기화하는 중...")
            self.agent = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                memory=self.memory,
                **self.settings.AGENT_CONFIG
            )
            
            logger.info("LangChain 초기화가 완료되었습니다!")
            return True
            
        except ImportError as e:
            logger.error(f"LangChain 패키지 임포트 실패: {e}")
            logger.error("다음 명령으로 패키지를 설치하세요: pip install -r requirements.txt")
            return False
        except Exception as e:
            logger.error(f"LangChain 초기화 실패: {e}")
            return False
    
    def generate_solution(self, problem: Dict[str, Any]) -> str:
        """문제 풀이 생성"""
        if not self.is_initialized:
            return "AI 서비스가 초기화되지 않았습니다."
        
        # 프롬프트 템플릿 포맷팅 (시스템 메시지 포함)
        prompt = f"{self.settings.SYSTEM_MESSAGE}\n\n{self.prompts.SOLUTION_PROMPT.format(
            problem=problem['problem'],
            topics=', '.join(problem['topics']),
            difficulty=problem['difficulty']
        )}"
        
        try:
            logger.info(f"문제 {problem['id']} 풀이 생성 시작...")
            
            with self._get_openai_callback() as cb:
                solution = self.agent.run(prompt)
                if cb:
                    logger.info(f"토큰 사용량 - Total: {cb.total_tokens}, Cost: ${cb.total_cost:.4f}")
            
            logger.info(f"문제 {problem['id']} 풀이 생성 완료")
            return self._format_response(solution, 'solution')
            
        except Exception as e:
            logger.error(f"풀이 생성 중 오류: {e}")
            return f"풀이 생성 중 오류가 발생했습니다: {str(e)}"
    
    def check_answer(self, problem: Dict[str, Any], user_answer: str) -> Tuple[str, int]:
        """답안 채점 및 피드백"""
        if not self.is_initialized:
            return "AI 서비스가 초기화되지 않았습니다.", 0
        
        # 평가 기준과 피드백 톤 가져오기
        evaluation_criteria = self._get_evaluation_criteria(problem)
        feedback_tone = self.settings.FEEDBACK_TONES.get(
            problem['difficulty'], 
            self.settings.FEEDBACK_TONES['중급']
        )
        
        # 프롬프트 템플릿 포맷팅 (시스템 메시지 포함)
        prompt = f"{self.settings.SYSTEM_MESSAGE}\n\n{self.prompts.FEEDBACK_PROMPT.format(
            problem=problem['problem'],
            topics=', '.join(problem['topics']),
            difficulty=problem['difficulty'],
            user_answer=user_answer,
            evaluation_criteria=evaluation_criteria,
            feedback_tone=feedback_tone
        )}"
        
        try:
            logger.info(f"문제 {problem['id']} 답안 채점 시작...")
            
            with self._get_openai_callback() as cb:
                feedback = self.agent.run(prompt)
                if cb:
                    logger.info(f"토큰 사용량 - Total: {cb.total_tokens}, Cost: ${cb.total_cost:.4f}")
            
            score = self._extract_score(feedback)
            formatted_feedback = self._format_response(feedback, 'feedback')
            
            logger.info(f"문제 {problem['id']} 채점 완료 - 점수: {score}")
            return formatted_feedback, score
            
        except Exception as e:
            logger.error(f"답안 채점 중 오류: {e}")
            return f"답안 채점 중 오류가 발생했습니다: {str(e)}", 0
    
    def generate_hint(self, problem: Dict[str, Any]) -> str:
        """힌트 생성"""
        if not self.is_initialized:
            return "AI 서비스가 초기화되지 않았습니다."
        
        # 힌트 원칙과 구조 가져오기
        hint_principles = '\n'.join([f"- {principle}" for principle in self.settings.HINT_PRINCIPLES])
        hint_structure = '\n'.join(self.settings.HINT_STRUCTURE)
        
        # 프롬프트 템플릿 포맷팅 (시스템 메시지 포함)
        prompt = f"{self.settings.SYSTEM_MESSAGE}\n\n{self.prompts.HINT_PROMPT.format(
            problem=problem['problem'],
            topics=', '.join(problem['topics']),
            basic_hint=problem['hint'],
            hint_principles=hint_principles,
            hint_structure=hint_structure
        )}"
        
        try:
            logger.info(f"문제 {problem['id']} 힌트 생성 시작...")
            
            with self._get_openai_callback() as cb:
                hint = self.agent.run(prompt)
                if cb:
                    logger.info(f"토큰 사용량 - Total: {cb.total_tokens}, Cost: ${cb.total_cost:.4f}")
            
            logger.info(f"문제 {problem['id']} 힌트 생성 완료")
            return self._format_response(hint, 'hint')
            
        except Exception as e:
            logger.error(f"힌트 생성 중 오류: {e}")
            return f"힌트 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _get_evaluation_criteria(self, problem: Dict[str, Any]) -> str:
        """문제에 맞는 평가 기준 생성"""
        # 기본 평가 기준
        criteria = self.evaluation.DEFAULT_CRITERIA
        
        # 주제별 특별 기준 추가
        for topic in problem['topics']:
            if topic.lower() in self.evaluation.SUBJECT_SPECIFIC_CRITERIA:
                criteria += "\n" + self.evaluation.SUBJECT_SPECIFIC_CRITERIA[topic.lower()]
        
        return criteria
    
    def _get_openai_callback(self):
        """OpenAI 사용량 추적을 위한 콜백"""
        try:
            from langchain.callbacks import get_openai_callback
            return get_openai_callback()
        except:
            return nullcontext()
    
    def _extract_score(self, feedback: str) -> int:
        """피드백에서 점수 추출"""
        for pattern in self.formatting.SCORE_PATTERNS:
            match = re.search(pattern, feedback, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                if 0 <= score <= 100:
                    return score
        
        logger.warning("피드백에서 점수를 추출할 수 없어 기본값 50점을 사용합니다.")
        return 50
    
    def _format_response(self, response: str, response_type: str) -> str:
        """응답 포맷팅"""
        formatted = response.strip()
        
        # 응답 타입에 따른 키워드 선택
        keywords = {
            'solution': self.formatting.STEP_KEYWORDS,
            'feedback': self.formatting.EVALUATION_KEYWORDS,
            'hint': self.formatting.HINT_KEYWORDS
        }.get(response_type, [])
        
        # 키워드를 굵게 포맷팅
        for keyword in keywords:
            pattern = f'({keyword}[:\\s]*)'
            replacement = self.formatting.MARKDOWN_PATTERNS['bold'].format(r'\1')
            formatted = re.sub(pattern, replacement, formatted, flags=re.IGNORECASE)
        
        return formatted
    
    def reset_memory(self):
        """대화 메모리 초기화"""
        if self.memory:
            self.memory.clear()
            logger.info("대화 메모리가 초기화되었습니다.")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """사용량 통계 반환"""
        return {
            "is_initialized": self.is_initialized,
            "tools_available": len(self.tools) if self.tools else 0,
            "memory_size": len(self.memory.chat_memory.messages) if self.memory else 0,
            "available_tools": self.settings.AVAILABLE_TOOLS,
            "llm_config": self.settings.LLM_CONFIG
        }
    
    def get_current_settings(self) -> Dict[str, Any]:
        """현재 설정 조회"""
        return {
            "llm_config": self.settings.LLM_CONFIG,
            "agent_config": self.settings.AGENT_CONFIG,
            "memory_config": self.settings.MEMORY_CONFIG,
            "available_tools": self.settings.AVAILABLE_TOOLS,
            "feedback_tones": list(self.settings.FEEDBACK_TONES.keys())
        }
