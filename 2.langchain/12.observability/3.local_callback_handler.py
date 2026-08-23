"""
3단계 — LangSmith 없이 로컬에서만 관찰하기 (계정 가입 불필요, 100% 무료)

회사 정책상 외부로 데이터를 못 보내거나, 그냥 가입 없이 바로 써보고 싶을 수 있다.
LangChain의 콜백(Callback) 시스템은 LangSmith와 별개로 동작하며, 호출의 시작/끝/에러 시점에
내가 원하는 코드(로컬 로그 출력, 파일 저장, 사내 모니터링 시스템 전송 등)를 끼워넣을 수 있다.

1~2단계(LangSmith)와 이 단계(콜백)는 대체 관계가 아니라 **함께 쓸 수 있는 관계**다 —
LangSmith는 예쁜 대시보드, 콜백은 내가 원하는 대로 커스터마이즈 가능한 로컬 훅.
"""

import time
from dotenv import load_dotenv
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


# [관전 포인트] BaseCallbackHandler를 상속하고 필요한 훅만 오버라이드한다.
class LocalTimingHandler(BaseCallbackHandler):
    def __init__(self):
        self._start_time = None

    def on_llm_start(self, serialized, prompts, **kwargs):
        self._start_time = time.time()
        print(f"  [콜백] LLM 호출 시작 — 모델: {serialized.get('kwargs', {}).get('model_name', '?')}")

    def on_llm_end(self, response, **kwargs):
        elapsed = time.time() - self._start_time
        usage = response.llm_output.get("token_usage", {}) if response.llm_output else {}
        print(f"  [콜백] LLM 호출 종료 — {elapsed:.2f}초, "
              f"입력 {usage.get('prompt_tokens', '?')} + 출력 {usage.get('completion_tokens', '?')} 토큰")

    def on_llm_error(self, error, **kwargs):
        print(f"  [콜백] LLM 호출 실패: {error}")


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
prompt = ChatPromptTemplate.from_template("{topic}을 한 문장으로 설명해줘.")
chain = prompt | llm

if __name__ == "__main__":
    handler = LocalTimingHandler()

    # [관전 포인트] config={"callbacks":[...]} 로 이 호출에만 콜백을 붙인다.
    #   (LLM 생성 시 callbacks=[handler]로 넘기면 그 LLM의 모든 호출에 항상 적용된다.)
    result = chain.invoke({"topic": "임베딩"}, config={"callbacks": [handler]})
    print(f"\n답변: {result.content}")

    print("\n👉 LangSmith 계정 없이도 지연시간·토큰 사용량을 직접 확인했다.")
    print("   실전에서는 on_llm_end 안에서 파일에 로그를 쓰거나, 사내 모니터링(Datadog 등)으로 전송하면 된다.")
