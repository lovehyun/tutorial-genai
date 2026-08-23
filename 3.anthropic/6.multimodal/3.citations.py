# pip install anthropic python-dotenv
#
# 3단계: Citations — 답변에 '정확한 출처'를 자동으로 붙인다.
# 2.pdf.py는 문서를 넣고 답만 받았다. 여기서는 문서 블록에 citations.enabled=True를 켜서,
# Claude가 만든 각 주장(claim)이 원문의 '어느 부분'에서 나왔는지까지 구조화된 형태로 받는다.
#
# 프롬프트로 "출처를 인용해줘"라고 부탁하는 것과 뭐가 다른가:
#   - 프롬프트 방식: 모델이 인용문을 직접 '타이핑'해야 함 → 출력 토큰 소비, 인용이 부정확할 수 있음
#   - Citations API : cited_text는 원문에서 그대로 추출 → 출력 토큰 미소비, 항상 원문과 정확히 일치
#
# 문서 타입별 인용 단위: 일반 텍스트=문자 인덱스, PDF=페이지 번호, custom content=블록 인덱스.
# (5.prompt_caching과 함께 쓸 수 있다 — 문서 블록에 cache_control을 얹으면 됨)

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# [관전 포인트 1] 문서 두 개를 각각 다른 title로 넣는다 — document_index로 어느 문서에서 인용됐는지 구분된다.
documents = [
    {
        "type": "document",
        "source": {
            "type": "text",
            "media_type": "text/plain",
            "data": "한국의 수도는 서울이다. 서울의 인구는 약 950만 명이다.",
        },
        "title": "한국 기본 정보",
        "citations": {"enabled": True},
    },
    {
        "type": "document",
        "source": {
            "type": "text",
            "media_type": "text/plain",
            "data": "일본의 수도는 도쿄다. 도쿄의 인구는 약 1400만 명이다.",
        },
        "title": "일본 기본 정보",
        "citations": {"enabled": True},
    },
]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [*documents, {"type": "text", "text": "서울과 도쿄의 인구를 비교해줘."}],
    }],
)

# [관전 포인트 2] 응답은 여러 text 블록으로 쪼개져 오고, 각 블록마다 그 주장을 뒷받침하는
#   citations 리스트가 붙어있다 — cited_text가 원문 그대로인지 확인해볼 것.
for block in response.content:
    print(f"[주장] {block.text}")
    for citation in (block.citations or []):
        print(f"  ↳ 출처: 「{citation.cited_text}」 "
              f"— {citation.document_title} (문자 {citation.start_char_index}~{citation.end_char_index})")
    print()
