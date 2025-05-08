import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# 양자화는 모델의 가중치를 32비트에서 8비트로 변환하여 크기를 줄이는 방법입니다.

# 1. 원본 모델 로드
model_name = "bert-base-uncased"
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# 2. 양자화 적용 (선형 계층만 8비트 변환)
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)

# 3. 모델 저장 (X)
# quantized_model.save_pretrained("./quantized_model")
# 결과적으로, Hugging Face의 save_pretrained()는 32비트(float32) 가중치만 지원하므로, 양자화 모델(qint8)을 저장할 수 없음.

# 4. Hugging Face 설정 파일 저장 (메타데이터 유지)
# model.config.save_pretrained(save_path)


# 3. 모델 저장 (Hugging Face 방식 대신 PyTorch 방식 사용)
save_path = "./quantized_model"
torch.save({
    "model_state_dict": quantized_model.state_dict(),
    "classifier_weight": model.classifier.weight.detach().cpu(),
    "classifier_bias": model.classifier.bias.detach().cpu(),
}, f"{save_path}/pytorch_model.bin")

# 4. 토크나이저 저장 (이건 그대로 사용 가능)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.save_pretrained(save_path)

# 모델 저장
print(f"✅ 양자화된 모델이 {save_path} 에 저장되었습니다!")
