"""
StrOutputParser 체인의 중간 결과 다루기

체인 중간 단계 값(예: 회사명)을 확인/활용하는 두 가지 패턴을 비교합니다.
  - 방법 B : lambda/함수의 부수효과(print)로 관찰 — 디버깅 용도
  - 방법 C : RunnablePassthrough.assign — 중간/최종 값을 모두 결과로 반환
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt_name = ChatPromptTemplate.from_template(
    "{product}을(를) 만드는 회사의 이름을 하나만 추천해주세요. 이름만 답하세요."
)
prompt_slogan = ChatPromptTemplate.from_template(
    "'{company_name}' 회사의 캐치프레이즈를 만들어주세요. 캐치프레이즈만 답하세요."
)


# ===== 방법 B: 중간 단계 함수에서 print =====
# 체인 흐름은 그대로 두고, 중간 단계에서 부수효과(print)로 값을 관찰합니다.
# 디버깅/학습 시 가장 직관적입니다.
print("=" * 50)
print("방법 B: 중간 단계에서 print")
print("=" * 50)

def show_and_pass(name: str) -> dict:
    name = name.strip()
    print(f"  [중간 결과] 회사명: {name}")
    return {"company_name": name}

chain_b = (
    prompt_name
    | llm
    | StrOutputParser()
    | show_and_pass          # ← 여기서 출력 후 다음 단계로 전달
    | prompt_slogan
    | llm
    | StrOutputParser()
)
slogan_b = chain_b.invoke({"product": "친환경 패키징"})
print(f"  슬로건: {slogan_b}")


# ===== 방법 C: RunnablePassthrough.assign =====
# 중간 결과(company_name)와 최종 결과(slogan)를 모두 dict로 반환합니다.
# 두 값 모두 후속 작업에서 사용해야 할 때 권장되는 LCEL 패턴입니다.
print("\n" + "=" * 50)
print("방법 C: RunnablePassthrough.assign")
print("=" * 50)

chain_c = (
    {"company_name": prompt_name | llm | StrOutputParser() | (lambda s: s.strip())}
    | RunnablePassthrough.assign(
        slogan=prompt_slogan | llm | StrOutputParser()
    )
)
result_c = chain_c.invoke({"product": "친환경 패키징"})
print(f"  회사명: {result_c['company_name']}")
print(f"  슬로건: {result_c['slogan']}")
