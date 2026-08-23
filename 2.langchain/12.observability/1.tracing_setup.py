"""
1단계 — LangSmith 자동 트레이싱 (코드 변경 없이 환경변수만으로)

지금까지 만든 체인들은 잘 동작했지만 "왜 느린지", "토큰을 얼마나 썼는지",
"중간 단계에서 프롬프트가 정확히 어떻게 만들어졌는지"는 print문을 넣기 전엔 알 수 없었다.

LangSmith는 LangChain 팀이 만든 무료 트레이싱 대시보드다. 아래 3개 환경변수만 켜면
기존 체인 코드를 한 줄도 안 고쳐도 모든 호출이 자동으로 기록된다.

무료 가입: https://smith.langchain.com (Developer 플랜 — 월 5,000 트레이스, 1인 사용 기준 충분)
API 키 발급 후 .env에 LANGSMITH_API_KEY=... 추가하면 끝.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# [관전 포인트] 이 3줄이 트레이싱의 전부다 — 체인 코드는 평소와 완전히 동일하다.
os.environ["LANGSMITH_TRACING"] = "true"
os.environ.setdefault("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
os.environ.setdefault("LANGSMITH_PROJECT", "tutorial-genai-observability")
# LANGSMITH_API_KEY 는 .env 에서 이미 로드됨 (load_dotenv)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
prompt = ChatPromptTemplate.from_template("{topic}에 대해 세 문장으로 설명해줘.")
chain = prompt | llm | StrOutputParser()

if __name__ == "__main__":
    if not os.environ.get("LANGSMITH_API_KEY"):
        print("⚠️  LANGSMITH_API_KEY 가 없습니다 — https://smith.langchain.com 에서 무료 발급 후 .env에 추가하세요.")
        print("    키가 없어도 아래 체인 자체는 정상 동작합니다(트레이싱만 안 됨).\n")

    result = chain.invoke({"topic": "벡터 데이터베이스"})
    print(result)

    print("\n👉 https://smith.langchain.com 대시보드 → 프로젝트 'tutorial-genai-observability'")
    print("   에서 방금 이 호출의 프롬프트 전문·지연시간·토큰 사용량을 확인할 수 있다.")
