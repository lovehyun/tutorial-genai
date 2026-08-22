# (파이프라인) 번역(translation) — 언어 간 변환
# pip install transformers torch sentencepiece
#
# 실무 단골 태스크. 번역도 seq2seq 모델.
#   Helsinki-NLP/opus-mt-* = 언어쌍별 경량 번역 모델 (이름에 언어쌍이 박혀 있음).
#   모델 하나가 '한 방향(예: ko→en)' 을 담당 → 방향마다 다른 모델을 쓴다.

from transformers import pipeline

# 1) 한국어 → 영어
ko_en = pipeline("translation", model="Helsinki-NLP/opus-mt-ko-en")
ko_text = "허깅페이스는 다양한 AI 모델을 제공하는 플랫폼입니다."
print("[ko→en]")
print(f"  원문: {ko_text}")
print(f"  번역: {ko_en(ko_text)[0]['translation_text']}")

# 2) 영어 → 프랑스어 (가장 널리 쓰이는 검증된 쌍)
en_fr = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")
en_text = "Hugging Face provides many pre-trained AI models."
print("\n[en→fr]")
print(f"  원문: {en_text}")
print(f"  번역: {en_fr(en_text)[0]['translation_text']}")

# [관전 포인트] 번역기는 '언어쌍 전용' — 다른 언어로 가려면 그 쌍의 모델로 교체.
#   다국어 한 모델로 처리하려면 facebook/nllb-200, facebook/m2m100 등을 사용.
