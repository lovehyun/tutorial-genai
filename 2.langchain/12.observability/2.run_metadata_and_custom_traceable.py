"""
2단계 — 트레이스 정리하기: run_name/tags/metadata + @traceable로 내 함수도 추적

1단계는 "일단 다 기록되게" 만들었다. 트레이스가 쌓이기 시작하면 대시보드에서
"이게 무슨 호출이었는지"를 구분할 방법이 필요하다 — 그게 이 단계다.

  ① config={"run_name":..., "tags":[...], "metadata":{...}} — LCEL 체인 호출에 이름표를 붙인다.
  ② @traceable — LLM 호출이 아닌 '내 파이썬 함수'도 트레이스 트리에 같이 넣는다.
     (예: 검색 함수, 후처리 함수 등 — LangSmith에서 전체 파이프라인을 하나의 트리로 본다)
"""

import os
from dotenv import load_dotenv
from langsmith import traceable
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"
os.environ.setdefault("LANGSMITH_PROJECT", "tutorial-genai-observability")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
prompt = ChatPromptTemplate.from_template("{topic}에 대해 한 문장으로 설명해줘.")
chain = prompt | llm | StrOutputParser()


# [관전 포인트 1] @traceable — LLM 호출이 없는 순수 파이썬 함수도 트레이스에 잡힌다.
#   실전에서는 여기가 '검색', '문서 청킹', 'DB 조회' 같은 RAG 파이프라인의 다른 단계가 된다.
@traceable(name="키워드_후처리")
def postprocess(text: str) -> str:
    return text.strip().replace("  ", " ")


def explain_topic(topic: str, user_id: str) -> str:
    # [관전 포인트 2] run_name/tags/metadata — 대시보드에서 검색·필터링할 수 있는 이름표.
    #   tags: 카테고리별 필터(예: "prod" vs "dev"). metadata: 임의의 부가 정보(사용자 ID 등).
    result = chain.invoke(
        {"topic": topic},
        config={
            "run_name": f"주제설명-{topic}",
            "tags": ["demo", "topic-explainer"],
            "metadata": {"user_id": user_id},
        },
    )
    return postprocess(result)


if __name__ == "__main__":
    answer = explain_topic("LangGraph", user_id="user-42")
    print(answer)

    print("\n👉 대시보드에서 이번 실행은 이름표('주제설명-LangGraph', 태그 'demo')로 바로 찾을 수 있고,")
    print("   트레이스를 펼치면 '키워드_후처리' 함수 호출까지 같은 트리 안에서 보인다.")
