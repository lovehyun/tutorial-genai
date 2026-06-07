# (2단계-A) 양자화 — 가중치를 32bit → 8bit 로. 가장 쉬운 경량화
# pip install transformers torch
#
# 경량화 첫 단계: 동적 양자화(dynamic quantization).
#   Linear 층의 가중치를 float32 → int8 로 바꿔 '크기↓ 속도↑' (정확도는 거의 유지).
#   이 예제: 크기 변화를 직접 재고, 추론이 그대로 되는지 확인한다.

import io
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# 실제 감성 지식이 있는 모델 (추론 결과를 비교해 보려고)
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()


# [관전 포인트 1] state_dict 를 메모리 버퍼에 직렬화해 크기(MB) 측정
def size_mb(m):
    buf = io.BytesIO()
    torch.save(m.state_dict(), buf)
    return buf.getbuffer().nbytes / 1e6


before = size_mb(model)

# [관전 포인트 2] 동적 양자화 — Linear 층만 int8 로
quantized = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
after = size_mb(quantized)

print(f"원본     : {before:6.1f} MB")
print(f"양자화 후 : {after:6.1f} MB   ({(1 - after / before) * 100:.0f}% 감소)\n")


# [관전 포인트 3] 추론은 그대로 동작 — 원본/양자화 예측 비교
def predict(m, text):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        logits = m(**inputs).logits
    return m.config.id2label[int(logits.argmax())]


for t in ["I love this!", "This is awful.", "Best purchase ever."]:
    print(f"  {t:24} 원본={predict(model, t):8} 양자화={predict(quantized, t)}")

# 정리:
#   - 동적 양자화는 코드 한 줄로 크기를 크게 줄인다 (CPU 추론에 특히 유용)
#   - 단, HF save_pretrained 는 qint8 저장을 지원하지 않는다
#     → 보통 '로드 후 런타임에 양자화' 하거나 torchao/bitsandbytes 같은 도구를 쓴다
#   - 다음(2.2): 아예 '층 수' 를 줄여 모델을 작게 만든다
