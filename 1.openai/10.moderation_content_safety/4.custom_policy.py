# Moderation - 4단계: 내 정책으로 커스터마이즈 (임계값 · 카테고리별 허용/차단)
# pip install openai python-dotenv
#
# Moderation API 의 '카테고리'는 고정(추가 불가)이지만, '판정 정책'은 내가 정한다:
#   · flagged(기본 임계값) 대신 category_scores(0~1) 에 '내 임계값'을 적용 → 더 엄격/더 관대하게
#   · 정책 dict 에 없는 카테고리는 '검사 안 함(허용)'
# 예: 폭력은 아주 엄격, 성적 표현은 비교적 관대, 자해는 (의료/정보 맥락 위해) 검사 제외.

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 내 정책: 카테고리별 '차단 임계값' (낮을수록 엄격). 여기 없는 카테고리는 허용(무시).
#   ※ 사용 가능한 키는 results[0].category_scores.model_dump() 출력으로 확인 (예: violence, harassment, hate, sexual, self_harm ...)
MY_THRESHOLDS = {
    'violence': 0.30,      # 폭력은 아주 엄격 (0.3만 넘어도 차단)
    'harassment': 0.50,
    'hate': 0.50,
    'sexual': 0.70,        # 성적 표현은 비교적 관대
    # 'self_harm': 0.50,   # ← 줄을 빼면 그 카테고리는 검사 안 함(허용)
}


def check(text):
    r = client.moderations.create(model='omni-moderation-latest', input=text)
    scores = r.results[0].category_scores.model_dump()
    violations = []
    for cat, limit in MY_THRESHOLDS.items():
        score = scores.get(cat, 0.0)          # 정책에 있는 카테고리만 본다
        if score >= limit:
            violations.append((cat, round(score, 3), limit))
    return (len(violations) == 0), violations


tests = [
    '안녕! 오늘 점심 뭐 먹을까?',
    '너를 가만 안 두겠어, 때려눕힐 거야.',
    '그 사람 진짜 멍청하고 한심해.',
]
for t in tests:
    ok, v = check(t)
    print(f'\n[{"통과" if ok else "차단"}] {t}')
    for cat, score, limit in v:
        print(f'    - {cat}: {score} >= 임계값 {limit}')

# 정리:
#   - 같은 입력도 임계값을 낮추면(엄격) 더 많이 차단, 높이면(관대) 덜 차단된다.
#   - 카테고리를 빼면 그 주제는 '허용'. 즉 '무엇을 얼마나 막을지'는 전적으로 내 정책.
