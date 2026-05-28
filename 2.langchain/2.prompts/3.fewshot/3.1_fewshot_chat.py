from dotenv import load_dotenv

from langchain_core.prompts import (
    PromptTemplate,
    FewShotPromptTemplate,
    ChatPromptTemplate,    # few-shot 과의 대조군으로 시험하기 위해...
)
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Few-Shot 프롬프팅: 모델에게 예제 몇 개를 먼저 보여준 뒤, 같은 패턴으로 답하게 한다.
#
# ─── 언제 쓰면 좋은가? ─────────────────────────────────────
#   ✅ 출력 형식을 글로 설명하기 까다로울 때 (예제로 보여주는 게 빠름)
#   ✅ 모호한 경계의 분류 기준 (긍정/부정/중립 같은) 을 예시로 고정하고 싶을 때
#   ✅ 회사 내부 톤/스타일을 강제하고 싶을 때
#
# ─── 안 쓰는 게 더 나은 경우 ──────────────────────────────
#   ❌ 모델이 이미 너무 잘 하는 작업 (예: 한→영 번역). 그냥 시키면 됨.
#   ❌ 단순 Q&A — 예제가 prompt 길이만 늘림.
#
# ─── 이 예제 ──────────────────────────────────────────────
# 문장의 감정을 분석하되, "긍정/부정/중립 + 1~10 점수" 라는 정해진 형식으로 답하게 한다.
# 그냥 "감정 분석해줘" 라고 시키면 모델은 자유로운 자연어 ("이 문장은 매우 긍정적이고
# 만족감이 느껴집니다...") 로 답한다. 우리는 파싱하기 쉬운 정해진 형식이 필요하다.
# → 예제 몇 개로 형식을 보여주면 모델이 그대로 따라온다.
# ─────────────────────────────────────────────────────────

load_dotenv()

# 1. 예제 데이터 — 우리가 원하는 출력 형식을 보여주는 샘플
examples = [
    {"sentence": "오늘 정말 최고의 하루였어!", "result": "감정: 긍정 / 점수: 9"},
    {"sentence": "이거 진짜 별로네요. 시간 낭비였어요.", "result": "감정: 부정 / 점수: 2"},
    {"sentence": "그냥 평범했어요. 특별히 좋지도 나쁘지도 않았네요.", "result": "감정: 중립 / 점수: 5"},
    {"sentence": "와 진짜 감동받았어요. 눈물이 날 정도였어요.", "result": "감정: 긍정 / 점수: 10"},
    {"sentence": "기대했던 것보단 별로지만 그래도 쓸만은 해요.", "result": "감정: 중립 / 점수: 6"},
]

# 2. 예제 한 건을 어떤 문자열로 만들지 정의
example_prompt = PromptTemplate(
    input_variables=["sentence", "result"],
    template="문장: {sentence}\n분석: {result}",
)

# 3. 예제들을 합쳐서 하나의 큰 prompt 문자열로 만들어주는 템플릿
#    - example_separator 로 예제 간 구분
#    - suffix 안에 구분선을 넣어 "예제 끝 / 진짜 질문 시작" 을 명확히 표시
fewshot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="다음은 문장의 감정을 분석한 예시입니다. 같은 형식으로 새 문장을 분석하세요.\n\n=== 예시 시작 ===",
    suffix="=== 예시 끝 ===\n\n=== 새로 분석할 문장 ===\n문장: {sentence}\n분석:",
    input_variables=["sentence"],
    example_separator="\n────────────\n",
)

# 4. 위 결과(긴 문자열)를 chat 프롬프트의 user 메시지로 감싸기
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 한국어 감정 분석기입니다. 예시와 '정확히 같은 형식' 으로만 답하세요."),
    ("user",   "{fewshot_text}"),
])

# 5. LLM + 체인
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = chat_prompt | llm | StrOutputParser()

# 6. 실행 — 모델에 실제 들어가는 텍스트 확인
target = "오랜만에 만난 친구랑 좋은 시간 보냈어요. 다음에 또 보고싶네요."
fewshot_text = fewshot_prompt.format(sentence=target)

print("=" * 60)
print("== 모델에 실제 들어가는 few-shot 텍스트 ==")
print("=" * 60)
print(fewshot_text)
print("=" * 60)

result = chain.invoke({"fewshot_text": fewshot_text})
print(f"\n[문장] {target}")
print(f"[분석] {result.strip()}")


# ─── 비교 실험: few-shot 없이 그냥 시키면? ────────────────
print("\n" + "=" * 60)
print("== [비교] few-shot 없이 그냥 시키면 ==")
print("=" * 60)
plain_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "당신은 한국어 감정 분석기입니다."),
        ("user",   "다음 문장의 감정을 분석해주세요: {sentence}"),
    ])
    | llm
    | StrOutputParser()
)
print(plain_chain.invoke({"sentence": target}))
# → 자유 자연어로 길게 설명함. "감정: ... / 점수: ..." 같은 형식이 안 나옴.
# → 파싱이 어렵고, 점수 스케일도 매번 달라짐.
