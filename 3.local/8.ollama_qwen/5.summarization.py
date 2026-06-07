"""
(5) 요약 — 긴 글을 N문장 / 불릿으로 (한국어 vs 영어 비교)
ollama SDK 사용.
준비: pip install ollama  +  ollama pull qwen2.5:1.5b
"""
import ollama

MODEL = "qwen2.5:1.5b"


def summarize(text, instruction):
    resp = ollama.generate(model=MODEL, options={"temperature": 0.3},
                           prompt=f"{instruction}\n\n텍스트:\n{text}\n\n결과:")
    return resp["response"].strip()


article_ko = """인공지능 기술의 발전이 가속화되면서 한국 기업들도 자체 AI 모델 개발에
박차를 가하고 있다. LG는 EXAONE, 네이버는 HyperCLOVA 를 개발하며 경쟁에 뛰어들었다.
정부도 소버린 AI 프로젝트에 예산을 투입해 한국어 특화 모델 개발을 지원하고 있다."""

article_en = """As AI technology accelerates, Korean companies are racing to build their own
models. LG developed EXAONE and Naver developed HyperCLOVA to join the competition.
The government is also funding a sovereign AI project to support Korean-specialized models."""

print("[한국어 — 3문장 요약]")
print(summarize(article_ko, "다음 글을 3문장 이내로 요약하세요. 요약만 출력."))

print("\n[English — 3-sentence summary]")
print(summarize(article_en, "Summarize the text below in 3 sentences. Output only the summary."))

# 핵심: 출력 형식(문장 수/불릿)을 프롬프트로 지시, temperature 낮게(0.3)로 사실 유지
#
# [관찰 — qwen2.5:1.5b]
#   요약 '내용'은 두 언어 모두 핵심을 잡지만, 한국어 출력엔 영어 단어가 섞이거나(예: "observed")
#   문장이 어색할 때가 있다. 영어 요약이 더 매끄럽다 → 한국어는 큰 모델 권장.
