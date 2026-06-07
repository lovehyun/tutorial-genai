# (파이프라인) 제로샷 분류(zero-shot-classification) — 학습 없이 임의 라벨로 분류
# pip install transformers torch
#
# 실무에서 매우 유용: 분류 라벨을 '코드에서 정하면', 그 라벨로 바로 분류한다.
#   → 라벨이 자주 바뀌거나, 학습 데이터를 만들 수 없을 때 강력.
#   원리: 자연어 추론(NLI) 모델이 "이 문장은 {라벨}에 관한 것이다" 의 참 정도를 판단.

from transformers import pipeline

# NLI 로 학습된 모델 (zero-shot 표준)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

text = "I just upgraded my computer's graphics card and CPU for better performance."
candidate_labels = ["technology", "sports", "cooking", "politics"]

result = classifier(text, candidate_labels=candidate_labels)

print(f"문장: {text}\n")
print("라벨별 점수 (학습 전혀 안 했는데도 분류됨):")
for label, score in zip(result["labels"], result["scores"]):
    print(f"  {label:12} {score:.3f}")
print(f"\n→ 최종 분류: {result['labels'][0]}")

# [관전 포인트] candidate_labels 만 바꾸면 같은 모델로 전혀 다른 분류가 된다 (재학습 0).
#   multi_label=True 를 주면 '여러 라벨 동시 해당' 도 가능.
