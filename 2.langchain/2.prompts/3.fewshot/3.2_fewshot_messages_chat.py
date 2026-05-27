from dotenv import load_dotenv

from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Chat 모델에 더 자연스러운 few-shot 방식.
# 예제를 한 큰 문자열로 합치지 않고, 각 예제를 "Human → AI" 메시지 쌍으로 만들어
# 진짜 대화처럼 시퀀스로 끼워넣는다.
#
# 6.1 과 같은 작업(감정 분석 + 정해진 형식) 을 chat-native 방식으로 풀어본다.
#
# ─── 6.1 vs 6.2 차이 한눈에 ────────────────────────────────
# 같은 예제 데이터지만 모델에게 "전달되는 메시지 구조" 가 다르다.
#
#   6.1 (FewShotPromptTemplate)
#     [system] 너는 분석기야...
#     [user]   === 예시 시작 === ... === 예시 끝 ===
#              === 새 문장 === ...        ← 예제 전부가 하나의 user 메시지에 박힘
#     → 총 메시지 2개. 모델 입장: "한 사람이 길게 예시 늘어놓고 마지막에 질문함"
#
#   6.2 (FewShotChatMessagePromptTemplate)  ← 이 파일
#     [system] 너는 분석기야...
#     [human]  예시1 입력         [ai] 예시1 답변
#     [human]  예시2 입력         [ai] 예시2 답변
#     ...
#     [human]  새 질문            ← 진짜 질문
#     → 총 메시지 12개. 모델 입장: "이미 5번 대화한 뒤 6번째 차례"
#
# 어떤 걸 쓰나?
#   - Chat 모델(gpt-4o 등) → 6.2 권장 (chat 모델 학습 형식에 맞음, 형식 추종 더 정확)
#   - Legacy completion 모델 → 6.1 만 가능 (단일 문자열만 받으므로)
# ─────────────────────────────────────────────────────────

load_dotenv()

# 1. 예제 데이터 — 6.1 과 동일
examples = [
    {"sentence": "오늘 정말 최고의 하루였어!",
     "result":   "감정: 긍정 / 점수: 9"},
    {"sentence": "이거 진짜 별로네요. 시간 낭비였어요.",
     "result":   "감정: 부정 / 점수: 2"},
    {"sentence": "그냥 평범했어요. 특별히 좋지도 나쁘지도 않았네요.",
     "result":   "감정: 중립 / 점수: 5"},
    {"sentence": "와 진짜 감동받았어요. 눈물이 날 정도였어요.",
     "result":   "감정: 긍정 / 점수: 10"},
    {"sentence": "기대했던 것보단 별로지만 그래도 쓸만은 해요.",
     "result":   "감정: 중립 / 점수: 6"},
]

# 2. 예제 한 건을 어떤 '메시지 쌍' 으로 만들지 정의
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{sentence}"),
    ("ai",    "{result}"),
])

# 3. 예제 리스트를 메시지 시퀀스로 풀어주는 클래스
fewshot_messages = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

# 4. 최종 프롬프트: system + (few-shot 메시지들이 펼쳐짐) + 진짜 user 입력
final_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 한국어 감정 분석기입니다. 사용자 문장에 대해 '감정: X / 점수: N' 형식으로만 답하세요."),
    fewshot_messages,              # ← 예제 5쌍이 여기에 자동으로 펼쳐짐
    ("human", "{sentence}"),
])

# 5. 무엇이 들어가는지 한 번 확인
target = "오랜만에 만난 친구랑 좋은 시간 보냈어요. 다음에 또 보고싶네요."
print("== 실제로 모델에 들어가는 메시지 시퀀스 ==")
for m in final_prompt.format_messages(sentence=target):
    print(f"  [{m.type}] {m.content}")

# 6. LLM + 체인 + 실행
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = final_prompt | llm | StrOutputParser()

result = chain.invoke({"sentence": target})
print(f"\n[문장] {target}")
print(f"[분석] {result.strip()}")

# ─── 6.1 vs 6.2 비교 포인트 ────────────────────────────────
# 6.1 (FewShotPromptTemplate):
#   - 예제들이 하나의 거대한 문자열로 합쳐져서 user 메시지 안에 통째로 들어감.
#   - 모델 입장: "user 한 명이 길게 예시들을 늘어놓고 마지막에 질문함."
#
# 6.2 (FewShotChatMessagePromptTemplate):
#   - 각 예제가 "human → ai" 메시지 쌍으로 분리되어 대화 이력처럼 보임.
#   - 모델 입장: "이미 이런 대화를 5번 나눈 적이 있고, 이제 6번째 차례."
#   - chat 모델이 학습된 형식에 더 가까워서 보통 더 정확한 형식 추종을 보임.
# ─────────────────────────────────────────────────────────
