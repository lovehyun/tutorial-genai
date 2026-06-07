# (2단계-B) 층 축소 — 트랜스포머 레이어 수를 줄여 모델을 작게
# pip install transformers torch
#
# 2.1(양자화=값의 정밀도↓) 과 다른 방향의 경량화: '구조' 자체를 줄인다.
#   BERT-base 는 인코더 층이 12개. 상위 절반을 떼어내 6층으로 만든다.
#   이 예제: 층을 줄이면 파라미터 수가 실제로 얼마나 주는지 확인한다.
#   ※ 그냥 떼면 성능은 떨어진다 — 보통 떼어낸 뒤 재학습(또는 증류 2.5)으로 회복한다.

from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")


def n_params(m):
    return sum(p.numel() for p in m.parameters())


before_layers = len(model.bert.encoder.layer)
before = n_params(model)
print(f"원본 : 인코더 {before_layers}층, 파라미터 {before:,}")

# [관전 포인트] 상위 6개 층 제거 → 앞쪽 6개만 남김 + config 도 맞춰 갱신
KEEP = 6
model.bert.encoder.layer = model.bert.encoder.layer[:KEEP]
model.config.num_hidden_layers = KEEP

after = n_params(model)
print(f"축소 : 인코더 {KEEP}층, 파라미터 {after:,}  ({(1 - after / before) * 100:.0f}% 감소)")

model.save_pretrained("./reduced_model")
print("\n✅ 층 축소 모델 저장 → ./reduced_model")
print("   (성능 회복이 필요하면 이 모델을 데이터로 재학습하거나, 2.5 지식증류 사용)")
