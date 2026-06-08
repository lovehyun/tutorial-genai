# (파이프라인) 제로샷 분류(zero-shot-classification) — 학습 없이 임의 라벨로 분류
# pip install transformers torch
#
# 실무에서 매우 유용: 분류 라벨을 '코드에서 정하면', 그 라벨로 바로 분류한다.
#   → 라벨이 자주 바뀌거나, 학습 데이터를 만들 수 없을 때 강력.
#   원리: 자연어 추론(NLI) 모델이 "이 문장은 {라벨}에 관한 것이다" 의 참 정도를 판단.

# BART (Bidirectional and Auto-Regressive Transformers)
#  = BERT + GPT
# MNLI = Multi-Genre Natural Language Inference

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


# -----------------------------------------------
# MNLI의 분류 결과는 항상 3가지
# 1. Entailment
# 2. Contradiction
# 3. Neutral

# 예시 1 - Entailment (함의)
# 문장 A: 오늘 비가 많이 내린다.
# 문장 B: 우산이 필요할 수 있다.
# 관계: Entailment (문장 A가 문장 B를 뒷받침함)
#
# 예시 2 - Contradiction (모순)
# 문장 A: 오늘 비가 많이 내린다.
# 문장 B: 오늘은 맑은 날이다.
# 관계: Contradiction (서로 모순)
#
# 예시 3 - Neutral (중립)
# 문장 A: 오늘 비가 많이 내린다.
# 문장 B: 나는 피자를 좋아한다.
# 관계: Neutral (관련 없음)


# -----------------------------------------------
# BART-MNLI는 어떻게 사용하는가?
# 예를 들어
# text = "삼성전자가 새로운 AI 반도체를 공개했다."
# 후보 라벨
# [
#     "기술",
#     "스포츠",
#     "정치"
# ]
#
# 내부적으로는
#
# 후보 1
# 삼성전자가 새로운 AI 반도체를 공개했다.
# 이 문장은 기술에 관한 것이다.
#
# 후보 2
# 삼성전자가 새로운 AI 반도체를 공개했다.
# 이 문장은 스포츠에 관한 것이다.
#
# 후보 3
# 삼성전자가 새로운 AI 반도체를 공개했다.
# 이 문장은 정치에 관한 것이다.
#
# 그리고 MNLI 모델은 Entailment 확률을 계산합니다.
#
# 예를 들면
# 라벨	Entailment
# 기술	0.98
# 스포츠	0.01
# 정치	0.01
#
# 결과
# {
#   "labels": ["기술", "정치", "스포츠"],
#   "scores": [0.98, 0.01, 0.01]
# }
