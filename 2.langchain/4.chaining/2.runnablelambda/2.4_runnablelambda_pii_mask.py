"""
RunnableLambda — 임의의 파이썬 함수를 체인 단계로 끼우는 Runnable.
이 예제: LLM 으로 보내기 전에 입력 텍스트의 이메일/전화번호를 자동 마스킹합니다.

운영 환경에서 외부 LLM API 로 개인정보(PII) 가 그대로 흘러가는 것을 막기 위한
전처리 패턴. 입력단의 RunnableLambda 가 입력 dict 자체를 변환해서 다음 단계로 넘김.
"""

import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")


def mask_pii(text: str) -> str:
    """이메일, 한국식 전화번호 마스킹"""
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[EMAIL]", text)
    text = re.sub(r"\b0\d{1,2}-\d{3,4}-\d{4}\b", "[PHONE]", text)
    return text


prompt = ChatPromptTemplate.from_template(
    "다음 고객 문의를 한 줄로 요약해줘:\n{complaint}"
)

# 입력 dict 의 complaint 값에만 마스킹을 적용해서 다시 dict 로 흘려보냄
mask_input = RunnableLambda(lambda x: {"complaint": mask_pii(x["complaint"])})

chain = mask_input | prompt | llm | StrOutputParser()

original = {
    "complaint": (
        "안녕하세요. 제 이메일은 hong@example.com 이고 010-1234-5678 로 연락 주세요. "
        "지난주에 주문한 상품이 아직 안 왔어요."
    )
}

print("[원본 문의]")
print(original["complaint"])
print("\n[마스킹 후 — LLM 에 실제로 전송되는 텍스트]")
print(mask_pii(original["complaint"]))
print("\n[LLM 요약 결과]")
print(chain.invoke(original))
