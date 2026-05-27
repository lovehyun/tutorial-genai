"""
7_agentops_monitoring.py - AgentOps 모니터링

이 파일은 LangChain/LangGraph 에이전트의 운영 모니터링 방법을 보여줍니다.
커스텀 콜백 핸들러로 토큰 사용량, 비용, 레이턴시를 추적하고,
LangSmith 연동 설정 방법을 안내합니다.

주요 내용:
- 커스텀 CallbackHandler로 실시간 메트릭 수집
- 토큰 사용량 및 예상 비용 계산
- 호출별 레이턴시 측정
- LangSmith 환경변수 설정 가이드
"""

import time
from dotenv import load_dotenv
from typing import Any, Dict, List

from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage
from langchain_core.outputs import LLMResult
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

print("=" * 60)
print("AgentOps 모니터링: 토큰/비용/레이턴시 추적")
print("=" * 60)


# ============================================================
# 1. 커스텀 콜백 핸들러 — 메트릭 수집
# ============================================================
class AgentOpsCallback(BaseCallbackHandler):
    """LLM 호출의 토큰, 비용, 레이턴시를 추적하는 콜백 핸들러"""

    # GPT-4o-mini 가격 (2025년 기준, USD per 1M tokens)
    PRICING = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4o": {"input": 2.50, "output": 10.00},
    }

    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.call_count = 0
        self.call_latencies: List[float] = []
        self._start_time = 0.0
        self.model_name = "gpt-4o-mini"

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """LLM 호출 시작 시 타이머 시작"""
        self._start_time = time.time()
        self.call_count += 1
        # 모델 이름 추출
        model = kwargs.get("invocation_params", {}).get("model_name", self.model_name)
        self.model_name = model

    def on_llm_end(self, response: LLMResult, **kwargs):
        """LLM 호출 완료 시 메트릭 수집"""
        latency = time.time() - self._start_time
        self.call_latencies.append(latency)

        # 토큰 사용량 추출
        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens

            # 비용 계산
            pricing = self.PRICING.get(self.model_name, self.PRICING["gpt-4o-mini"])
            cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
            self.total_cost += cost

            print(f"  [메트릭] 호출 #{self.call_count}: "
                  f"입력={input_tokens}tk, 출력={output_tokens}tk, "
                  f"비용=${cost:.6f}, 레이턴시={latency:.2f}s")

    def on_llm_error(self, error: BaseException, **kwargs):
        """LLM 에러 발생 시 기록"""
        print(f"  [에러] 호출 #{self.call_count}: {error}")

    def print_summary(self):
        """최종 사용량 요약 출력"""
        avg_latency = sum(self.call_latencies) / len(self.call_latencies) if self.call_latencies else 0

        print("\n" + "─" * 50)
        print("AgentOps 모니터링 요약")
        print("─" * 50)
        print(f"  모델: {self.model_name}")
        print(f"  총 호출 횟수: {self.call_count}")
        print(f"  총 입력 토큰: {self.total_input_tokens:,}")
        print(f"  총 출력 토큰: {self.total_output_tokens:,}")
        print(f"  총 토큰: {self.total_input_tokens + self.total_output_tokens:,}")
        print(f"  총 비용: ${self.total_cost:.6f}")
        print(f"  평균 레이턴시: {avg_latency:.2f}s")
        if self.call_latencies:
            print(f"  최소 레이턴시: {min(self.call_latencies):.2f}s")
            print(f"  최대 레이턴시: {max(self.call_latencies):.2f}s")
        print("─" * 50)


# ============================================================
# 2. 콜백 핸들러를 사용한 LLM 호출
# ============================================================
print("\n[예제 1] 콜백 핸들러로 메트릭 추적")
print("-" * 50)

callback = AgentOpsCallback()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, callbacks=[callback])
parser = StrOutputParser()

# 여러 번 LLM 호출하여 메트릭 누적
prompts = [
    "Python의 장점 3가지를 한 줄씩 설명해주세요.",
    "머신러닝과 딥러닝의 차이를 2줄로 설명해주세요.",
    "REST API의 핵심 원칙 3가지를 간단히 설명해주세요.",
]

for i, prompt_text in enumerate(prompts, 1):
    print(f"\n호출 {i}: {prompt_text}")
    response = llm.invoke([HumanMessage(content=prompt_text)])
    print(f"응답: {response.content[:100]}...")

callback.print_summary()

# ============================================================
# 3. LCEL 체인에서 콜백 사용
# ============================================================
print("\n[예제 2] LCEL 체인에서 콜백 추적")
print("-" * 50)

callback2 = AgentOpsCallback()
llm2 = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, callbacks=[callback2])

prompt = ChatPromptTemplate.from_template(
    "{topic}에 대한 핵심 포인트 3가지를 정리해주세요."
)
chain = prompt | llm2 | parser

topics = ["클라우드 컴퓨팅", "사이버 보안"]
for topic in topics:
    print(f"\n토픽: {topic}")
    result = chain.invoke({"topic": topic})
    print(f"결과: {result[:100]}...")

callback2.print_summary()

# ============================================================
# 4. LangSmith 연동 가이드
# ============================================================
print("\n" + "=" * 60)
print("LangSmith 연동 가이드")
print("=" * 60)
print("""
LangSmith는 LangChain 공식 관측성(Observability) 플랫폼입니다.
환경변수만 설정하면 자동으로 트레이스가 수집됩니다.

1. .env 파일에 다음을 추가:

   LANGSMITH_API_KEY=ls_your_api_key_here
   LANGSMITH_TRACING=true
   LANGSMITH_PROJECT=my-project-name

2. 코드 변경 없이 자동 추적:
   - 모든 LLM 호출의 입출력
   - 체인 실행 과정 (각 단계별 입출력)
   - 토큰 사용량, 레이턴시
   - 에러 및 재시도 정보

3. LangSmith 대시보드 (https://smith.langchain.com):
   - 트레이스 시각화 (워터폴 뷰)
   - 비용 분석 및 토큰 사용량 추이
   - 에러율 및 성능 모니터링
   - 데이터셋 기반 평가(Evaluation) 실행

4. 프로덕션 팁:
   - 개발: LANGSMITH_TRACING=true (전체 트레이스)
   - 운영: 샘플링 비율 조절 또는 에러만 수집
   - 민감 데이터: input/output 마스킹 설정 활용
""")

print("설명:")
print("1. BaseCallbackHandler를 상속하여 커스텀 메트릭 수집이 가능합니다.")
print("2. on_llm_start/on_llm_end 훅으로 각 호출의 레이턴시와 토큰을 측정합니다.")
print("3. callbacks 파라미터로 LLM이나 체인에 핸들러를 주입합니다.")
print("4. LangSmith는 환경변수 설정만으로 자동 트레이싱을 제공합니다.")
