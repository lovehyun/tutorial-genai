"""
(2) 감성 분석 — 프롬프트만으로 긍정/부정/중립 (한국어 vs 영어 비교)
ollama SDK + format="json" 으로 JSON 출력을 강제해 바로 파싱.
준비: pip install ollama  +  ollama pull qwen2.5:1.5b
"""
import ollama
import json

MODEL = "qwen2.5:1.5b"


def sentiment(text):
    prompt = (f'다음 리뷰의 감성을 분석해 JSON 으로만 답하세요. '
              f'키: sentiment("긍정"/"부정"/"중립"), keywords(배열).\n리뷰: {text}')
    resp = ollama.generate(model=MODEL, prompt=prompt, format="json",
                           options={"temperature": 0.1})
    return json.loads(resp["response"])


# (언어, 리뷰) — 한국어/영어 동일 의미 쌍으로 결과 비교
reviews = [
    ("ko", "이 제품 정말 좋아요! 배송도 빠르고 품질도 훌륭합니다."),
    ("en", "This product is great! Fast delivery and excellent quality."),
    ("ko", "최악이에요. 돈 아까워요. 다시는 안 삽니다."),
    ("en", "Terrible. Waste of money. Never buying again."),
]
for lang, rv in reviews:
    res = sentiment(rv)
    print(f"[{lang}] {rv}\n  → {res['sentiment']} / 키워드: {res.get('keywords')}\n")

# 핵심: ollama.generate(..., format="json") + temperature 낮게 → 구조화 결과를 바로 사용
#
# [관찰 — qwen2.5:1.5b]
#   감성 라벨(긍/부/중립)은 한국어·영어 모두 비교적 정확. format="json" 의 짧은 출력은
#   작은 모델로도 안정적이다(대화/번역 같은 '긴 한국어 생성'보다 훨씬 잘 됨).
