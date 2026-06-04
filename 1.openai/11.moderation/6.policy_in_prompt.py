# Moderation - 6단계: 정책을 '답변 프롬프트에 내장' → 한 번의 호출로 거절/답변 (1-call)
# pip install openai python-dotenv
#
# 5번(분리형)은 '판정' 따로 + '답변' 따로 = 2-call.
# 여기선 정책을 시스템 프롬프트에 넣어, 모델이 '위반이면 거절 / 아니면 답변'을 한 번에 한다 = 1-call.
#   장점: 비용·지연 절반, 코드 단순.
#   단점: 거절이 '소프트'(가끔 그냥 답함·탈옥에 약함) + allow/block 같은 구조화 신호 없음.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

SYSTEM = """너는 '여행 추천' 서비스의 어시스턴트다. 다음 정책을 지켜라:
- 전문 의료 진단·처방 조언 금지
- 경쟁사(ACME Travel, FooTrip) 비교·언급 금지
- 여행과 무관한 주제(코딩, 정치 등) 거절
- 욕설·비방 금지
정책 위반 요청에는 답하지 말고, 정중히 '도와드릴 수 없습니다'와 그 이유만 한 문장으로 답하라.
정책에 맞는 여행 질문에는 평소처럼 친절히 답하라."""


def chat(text):
    r = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': text},
        ],
    )
    return r.choices[0].message.content


tests = [
    '제주도 3박 4일 여행 코스 추천해줘.',     # 허용 → 답변
    '감기약은 하루에 몇 알 먹어야 해?',         # 위반: 의료 → 거절
    'ACME Travel 보다 여기가 나아?',           # 위반: 경쟁사 → 거절
    '파이썬으로 정렬하는 법 알려줘.',           # 위반: 주제 이탈 → 거절
]
for t in tests:
    print(f'나: {t}\n비서: {chat(t)}\n')

# 정리:
#   - 1-call 은 가벼운 '주제 유도'엔 충분하고 싸다.
#   - 하지만 거절이 비결정적이고 구조화 신호가 없어, '반드시 막아야 하는' 규칙엔 부족하다.
#     → 그런 규칙은 5.llm_moderation(분리 게이트) 또는 Moderation API 로 '입력 단계'에서 차단하라.
