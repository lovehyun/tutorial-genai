"""
(6) 번역 — 한↔영 양방향 (+ 문체 지정)
ollama SDK 사용. 프롬프트 언어가 곧 출력 언어를 유도한다.
준비: pip install ollama  +  ollama pull qwen2.5:1.5b
"""
import ollama

MODEL = "qwen2.5:1.5b"


def translate(prompt):
    resp = ollama.generate(model=MODEL, prompt=prompt, options={"temperature": 0.2})
    return resp["response"].strip()


# 한 → 영 (영어로 지시)
ko = "인공지능 기술이 빠르게 발전하고 있습니다."
print("[한→영]")
print(translate(f"Translate to natural English. Output only the translation.\nKorean: {ko}\nEnglish:"))

# 영 → 한 (한국어로 지시)
en = "Please submit the report by Friday."
print("\n[영→한]")
print(translate(f"다음을 자연스러운 한국어로 번역하세요. 번역만 출력.\nEnglish: {en}\n한국어:"))

# 문체 지정 — 같은 원문, 다른 말투
print("\n[문체 지정: 존댓말 vs 반말]")
for style in ["정중한 존댓말", "친구끼리 반말"]:
    out = translate(f"다음 영어 문장을 {style} 한국어로 번역하세요. 한국어 번역문만 출력.\nEnglish: {en}\n한국어:")
    print(f"  ({style}) {out}")

# 핵심: 프롬프트 언어=출력 언어 유도, 문체 지정은 전통 번역기에 없는 LLM 강점
#
# [관찰 — qwen2.5:1.5b]
#   한→영은 잘 되는 편. 영→한은 오역이 생기고(예: "by Friday" 를 엉뚱하게),
#   문체 지정(존댓말/반말)은 작은 모델이 지시를 못 따라 영어를 그대로 뱉기도 한다.
#   → 번역 품질은 모델 크기에 민감. qwen2.5:7b / qwen3 또는 전용 번역모델 권장.