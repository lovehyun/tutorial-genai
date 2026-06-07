"""
(3) 텍스트 분류 — 카테고리 중 하나로 (zero-shot, 한국어 vs 영어 비교)
ollama SDK + format="json". 카테고리 목록만 바꾸면 어떤 도메인이든 분류.
준비: pip install ollama  +  ollama pull qwen2.5:1.5b
"""
import ollama
import json

MODEL = "qwen2.5:1.5b"


def classify(text, categories):
    prompt = (f'다음 텍스트를 카테고리 {categories} 중 하나로 분류해 JSON 으로만 답하세요. '
              f'키: category, reason(한 줄).\n텍스트: {text}')
    resp = ollama.generate(model=MODEL, prompt=prompt, format="json",
                           options={"temperature": 0.1})
    return json.loads(resp["response"])


CATEGORIES = ["정치", "경제", "스포츠", "기술", "연예"]
# (언어, 기사) — 같은 주제를 한국어/영어로
news = [
    ("ko", "코스피가 3% 급등하며 2,800선을 돌파했다."),
    ("en", "The KOSPI surged 3%, breaking past the 2,800 level."),
    ("ko", "손흥민이 시즌 15호 골을 터뜨렸다."),
    ("en", "Son Heung-min scored his 15th goal of the season."),
]
for lang, n in news:
    res = classify(n, CATEGORIES)
    print(f"[{lang}] {n}\n  → {res['category']} ({res.get('reason')})\n")

# 핵심: 카테고리 리스트만 교체하면 뉴스/고객문의/이메일 등 즉시 적용 (학습 0)
#
# [관찰 — qwen2.5:1.5b]
#   분류 라벨은 한국어·영어 모두 대체로 정확. 단, reason 설명에 가끔 다른 언어(중국어 등)가
#   섞일 수 있다(작은 모델 특성). 라벨만 쓰면 실용상 문제 없음.
