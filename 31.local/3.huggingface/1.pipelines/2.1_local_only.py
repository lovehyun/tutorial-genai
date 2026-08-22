# HuggingFace를 사용하지 않고 오직 로컬 모델만 사용하려면 local_files_only=True 옵션을 추가하면 됩니다.

# from transformers import AutoModel, AutoTokenizer

# local_model_path = "./my_local_model"

# model = AutoModel.from_pretrained(local_model_path, local_files_only=True)
# tokenizer = AutoTokenizer.from_pretrained(local_model_path, local_files_only=True)


import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from huggingface_hub.constants import HUGGINGFACE_HUB_CACHE

# Hugging Face 캐시 디렉토리 설정
os.environ["TRANSFORMERS_CACHE"] = HUGGINGFACE_HUB_CACHE

# 캐시에 저장된 모델을 로드 (이미 다운로드된 모델 사용)
model_name = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"  # 여기에 원하는 모델명을 입력

tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=True)

print("로컬 모델 로드 완료!")


# 입력 문장
text = "I love this product! It's amazing."

# 토큰화 (PyTorch 텐서 변환)
inputs = tokenizer(text, return_tensors="pt")

# 모델 추론 (GPU 사용 가능)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device) # gpu (또는 cpu) 로 이동

with torch.no_grad():
    outputs = model(**{k: v.to(device) for k, v in inputs.items()})
    
# 결과 해석
logits = outputs.logits
predicted_class = torch.argmax(logits, dim=-1).item()

# 감성 라벨 매핑
label_map = {0: "NEGATIVE", 1: "POSITIVE"}  # 모델마다 다를 수 있음
print(f"📢 입력: {text} → 🎯 예측: {label_map[predicted_class]}")


# 참고:
# DistilBERT(Distilled BERT)는 BERT 모델을 경량화한 버전으로, 속도를 높이면서도 성능을 유지하는 것을 목표로 하는 사전 훈련된 NLP 모델입니다.
# DistilBERT의 특징: 
#  - BERT보다 가볍고 빠름 (Bert-base는 110M -> 66M 파라미터)
#  - DistilBERT는 BERT 모델보다 40% 적은 파라미터를 가지며, 속도가 60% 더 빠름.
#  - 메모리 사용량이 적어 모바일 및 임베디드 시스템에서도 실행 가능.
