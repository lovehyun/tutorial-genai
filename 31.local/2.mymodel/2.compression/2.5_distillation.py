# (2단계-E) 지식 증류 — 큰 모델(교사)의 '지식' 을 작은 모델(학생)로
# pip install transformers torch
#
# 경량화의 가장 정교한 방법. 작은 학생 모델이 큰 교사 모델의 '출력 분포(soft label)' 를
#   따라 하도록 학습한다 → 정답 라벨만 배우는 것보다 교사의 미묘한 판단까지 흡수.
# 이 예제: 교사(SST-2 파인튜닝)의 logits 를 학생(미학습 distilbert)이 모방하도록
#   실제 학습 루프를 돌린다. (손실이 줄어드는지 확인)

import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# 교사: 감성분석을 이미 잘하는 모델 / 학생: 같은 토크나이저의 미학습 분류기
teacher = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english")
student = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased", num_labels=2,
    id2label={0: "NEGATIVE", 1: "POSITIVE"})
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
teacher.eval()

# 학습 데이터 (라벨은 정답, 교사는 soft label 제공)
texts = ["I love this!", "This is terrible!", "Absolutely fantastic!",
         "Worst experience ever.", "I am so happy.", "I really hate it."]
labels = torch.tensor([1, 0, 1, 0, 1, 0])
enc = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

# [관전 포인트] 증류 손실 = soft loss(교사 모방) + hard loss(정답)
#   T(temperature): 분포를 부드럽게 해 '교사의 자신없음' 까지 학습. alpha: 두 손실 비중.
T, alpha = 2.0, 0.5
optimizer = torch.optim.AdamW(student.parameters(), lr=5e-5)

with torch.no_grad():
    teacher_logits = teacher(**enc).logits          # 교사 출력은 고정

print("증류 학습 (손실이 줄어드는지 관찰):")
for epoch in range(8):
    student.train()
    student_logits = student(**enc).logits

    soft = F.kl_div(
        F.log_softmax(student_logits / T, dim=-1),
        F.softmax(teacher_logits / T, dim=-1),
        reduction="batchmean",
    ) * (T * T)                                      # soft label 모방
    hard = F.cross_entropy(student_logits, labels)   # 정답 라벨
    loss = alpha * soft + (1 - alpha) * hard

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    print(f"  epoch {epoch+1}: loss={loss.item():.4f}  (soft={soft.item():.4f}, hard={hard.item():.4f})")

# 학습된 학생으로 예측
student.eval()
with torch.no_grad():
    preds = student(**enc).logits.argmax(dim=-1)
print("\n학생 예측 vs 정답:")
for t, p, y in zip(texts, preds, labels):
    mark = "✅" if int(p) == int(y) else "❌"
    print(f"  {mark} {t:24} 예측={student.config.id2label[int(p)]}")

print("\n→ 학생(작은 모델)이 교사의 판단을 모방해 감성분석을 학습했다 = 지식 증류")
