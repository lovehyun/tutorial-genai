from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Prompt Composition: 두 개의 프롬프트를 `+` 로 합쳐서 새 프롬프트 만들기.
# 시스템 프롬프트 / 페르소나 / 출력 형식 같이 재사용되는 조각을 모듈화하기 좋다.

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


# ─── 재사용 가능한 조각들 ─────────────────────────────────
# (a) 페르소나/역할 부분
persona = ChatPromptTemplate.from_messages([
    ("system", "You are a senior {role}. Be precise and concise."),
])

# (b) 출력 형식 강제 부분
output_format = ChatPromptTemplate.from_messages([
    ("system", "Always respond as a bullet list (- ...) with at most 3 items."),
])

# (c) 실제 사용자 입력 부분
user_question = ChatPromptTemplate.from_messages([
    ("user", "{question}"),
])


# ─── 합쳐서 다양한 조합 만들기 ────────────────────────────
# 같은 조각을 재사용하면서 페르소나만 바꿔 두 가지 어시스턴트 만들기
cook_assistant   = persona + output_format + user_question
travel_assistant = persona + output_format + user_question  # 같은 합치기, 채우는 값만 다름

# 1) 요리 전문가 버전
chain1 = cook_assistant | llm | StrOutputParser()
print("== 합성 (요리 어시스턴트) ==")
print(chain1.invoke({
    "role": "Korean chef",
    "question": "김치찌개에 꼭 들어가야 하는 재료는?",
}))

# 2) 여행 전문가 버전 — 같은 템플릿, role 만 교체
chain2 = travel_assistant | llm | StrOutputParser()
print("\n== 합성 (여행 어시스턴트) ==")
print(chain2.invoke({
    "role": "travel guide",
    "question": "서울에서 꼭 가봐야 할 장소는?",
}))


# ─── 합쳐진 결과 메시지 시퀀스를 직접 확인 ─────────────────
print("\n== composition 결과 — system 두 개가 user 앞에 쌓인다 ==")
for m in cook_assistant.format_messages(role="Korean chef", question="testing"):
    print(f"  [{m.type}] {m.content}")
