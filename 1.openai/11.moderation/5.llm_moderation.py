# Moderation - 5단계: '완전 커스텀' 규칙은 LLM 으로 (Moderation API 가 못 잡는 정책)
# pip install openai python-dotenv
#
# Moderation API 는 카테고리가 고정 → "의료 조언 금지", "경쟁사 언급 금지", "주제 이탈 금지" 같은
# '우리 서비스만의 규칙'은 표현할 수 없다. 이런 커스텀 정책은 LLM 을 분류기로 써서 구현한다.
# (구조화 출력으로 allow/block + 위반 규칙 + 사유를 받음)
# 흐름(2-call): ① 정책 판정(moderate) → ② '통과한 것만' 실제 답변(answer).
#   → 판정과 답변을 분리해서, 차단된 입력은 답변 모델에 아예 닿지 않는다(견고). 1-call 버전은 6.policy_in_prompt.py.
#
# 실전 권장: (1) Moderation API(무료·빠름)로 보편적 위반을 먼저 거르고
#            (2) 통과한 것만 이 LLM 정책 심사로 '우리 규칙'을 추가 검사 → 2단 방어.

import os
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 우리 서비스 정책 — 자유롭게 추가·수정 (이게 곧 '내 기준')
POLICY = """우리는 '여행 추천' 서비스다. 아래를 위반하면 차단한다:
1. 전문 의료 진단·처방 등 의료 조언 요청
2. 경쟁사(ACME Travel, FooTrip) 비교·언급 유도
3. 여행과 무관한 주제 (코딩 질문, 정치 토론 등)
4. 욕설·비방"""


class Decision(BaseModel):
    allow: bool = Field(description="정책상 허용 여부")
    rule: str = Field(description="위반한 규칙 번호 (허용이면 'none')")
    reason: str = Field(description="판단 이유 한 문장")


def moderate(text):
    completion = client.beta.chat.completions.parse(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system',
             'content': f'너는 콘텐츠 정책 심사관이다.\n\n[정책]\n{POLICY}\n\n사용자 입력이 정책에 맞는지 심사하라.'},
            {'role': 'user', 'content': text},
        ],
        response_format=Decision,     # 구조화 출력 — 파싱 불필요 (9.structured_output 참고)
    )
    return completion.choices[0].message.parsed


# ② 2번째 콜: 정책을 통과한 질문에만 '실제로 답변'한다 (판정과 답변 분리)
def answer(text):
    r = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': '너는 친절한 여행 추천 어시스턴트야. 한국어로 답해.'},
            {'role': 'user', 'content': text},
        ],
    )
    return r.choices[0].message.content


tests = [
    '제주도 3박 4일 여행 코스 추천해줘.',     # 허용
    '감기약은 하루에 몇 알 먹어야 해?',         # 위반: 의료
    'ACME Travel 보다 여기가 나아?',           # 위반: 경쟁사
    '파이썬으로 정렬하는 법 알려줘.',           # 위반: 주제 이탈
]
for t in tests:
    d = moderate(t)                          # ① 정책 판정 (1st call)
    if d.allow:
        print(f'[통과] {t}')
        print(f'    답변: {answer(t)}\n')      # ② 통과 시에만 실제 답변 (2nd call)
    else:
        print(f'[차단(규칙 {d.rule})] {t}')
        print(f'    → {d.reason}\n')           # 차단이면 2번째 콜 없이 거절 사유만

# 정리:
#   - POLICY 텍스트만 바꾸면 '내 규칙'을 얼마든지 추가/수정/허용 설정 가능 (Moderation API 로는 불가능한 부분).
#   - 2-call(판정→답변): 차단된 입력은 답변 모델에 닿지 않아 견고. 단 통과 시 호출 2회(비용·지연↑).
#     한 호출로 처리하는 1-call 은 6.policy_in_prompt.py (싸지만 거절이 소프트).
#   - 보편 위반은 Moderation API(무료) 로 먼저 거르면 LLM 판정 호출도 아낀다.
