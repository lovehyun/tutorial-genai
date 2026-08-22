# (2단계-C) 프루닝 — 덜 중요한 가중치를 0으로 만들기
# pip install transformers torch
#
# 2.2(층 통째로 제거) 보다 세밀한 경량화: 가중치 '개별' 을 솎아낸다.
#   각 Linear 층에서 크기가 작은(L1 기준) 가중치 50% 를 0으로 → 희소(sparse) 모델.
#   이 예제: 0의 비율(sparsity)이 실제로 올라가는지 측정한다.
#   ※ import torch 가 반드시 필요 (torch.nn.Linear 사용)

import torch
import torch.nn.utils.prune as prune
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")


def sparsity(m):
    zeros = sum(int((p == 0).sum()) for p in m.parameters())
    total = sum(p.numel() for p in m.parameters())
    return zeros / total * 100


print(f"프루닝 전 0 비율: {sparsity(model):.2f}%")

# [관전 포인트] 모든 Linear 층의 weight 를 50% L1 프루닝
#   prune.remove 로 마스크를 가중치에 '영구 적용' (안 하면 마스크만 걸려 저장이 불완전)
for _, module in model.named_modules():
    if isinstance(module, torch.nn.Linear):
        prune.l1_unstructured(module, name="weight", amount=0.5)
        prune.remove(module, "weight")

print(f"프루닝 후 0 비율: {sparsity(model):.2f}%  ← Linear weight 의 50%를 0으로 (임베딩 등은 그대로라 전체 기준은 더 낮음)")

model.save_pretrained("./pruned_model")
print("\n✅ 프루닝 모델 저장 → ./pruned_model")
print("   (0이 많아져도 파일 크기는 그대로 — 실제 속도/용량 이득은 sparse 전용 런타임 필요)")
print("   다음(2.4): 가중치가 아니라 '어휘(vocab)' 를 줄인다")
