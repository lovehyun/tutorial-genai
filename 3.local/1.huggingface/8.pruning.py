from transformers import AutoModelForSequenceClassification
import torch.nn.utils.prune as prune

# 원본 모델 로드
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")

# 선형 계층의 가중치를 50% 제거 (프루닝)
for name, module in model.named_modules():
    if isinstance(module, torch.nn.Linear):
        prune.l1_unstructured(module, name="weight", amount=0.5)

# 모델 저장
model.save_pretrained("./pruned_model")
print("✅ 프루닝 완료!")
