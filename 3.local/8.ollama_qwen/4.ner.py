"""
(4) 개체명 인식(NER) — 인물/조직/장소/날짜 추출 (한국어 vs 영어 비교)
ollama SDK + format="json". 카테고리 정의만 주면 추출.
준비: pip install ollama  +  ollama pull qwen2.5:1.5b
"""
import ollama
import json

MODEL = "qwen2.5:1.5b"


def extract_entities(text):
    prompt = (f'다음 텍스트에서 개체명을 추출해 JSON 으로만 답하세요. '
              f'키: entities(배열, 각 항목은 entity 와 type). '
              f'type 은 PER(인물)/ORG(조직)/LOC(장소)/DATE(날짜) 중 하나.\n텍스트: {text}')
    resp = ollama.generate(model=MODEL, prompt=prompt, format="json",
                           options={"temperature": 0.1})
    return json.loads(resp["response"])


# (언어, 텍스트) — 같은 내용을 한국어/영어로
texts = [
    ("ko", "삼성전자 이재용 회장은 2024년 1월 서울에서 갤럭시 S24 행사를 진행했다."),
    ("en", "Samsung chairman Lee Jae-yong held the Galaxy S24 event in Seoul in January 2024."),
]
for lang, t in texts:
    res = extract_entities(t)
    print(f"[{lang}] {t}")
    for e in res.get("entities", []):
        print(f"  - {e.get('entity')} ({e.get('type')})")
    print()

# 핵심: 새 카테고리(FOOD, EVENT 등)도 프롬프트에 한 줄 추가하면 즉시 인식
#
# [관찰 — qwen2.5:1.5b]
#   핵심 개체(인물/조직/장소)는 한국어·영어 모두 잘 잡는 편. 날짜/제품명 등은 가끔 누락된다.
#   짧은 구조화 추출이라 작은 모델로도 비교적 안정적.
