# Hugging Face를 사용하지 않고 오직 로컬 모델만 사용하려면 local_files_only=True 옵션을 추가하면 됩니다.

# from transformers import AutoModel, AutoTokenizer

# local_model_path = "./my_local_model"

# model = AutoModel.from_pretrained(local_model_path, local_files_only=True)
# tokenizer = AutoTokenizer.from_pretrained(local_model_path, local_files_only=True)


import os
from transformers import AutoModel, AutoTokenizer
from huggingface_hub.constants import HUGGINGFACE_HUB_CACHE

# Hugging Face 캐시 디렉토리 설정
os.environ["TRANSFORMERS_CACHE"] = HUGGINGFACE_HUB_CACHE

# 캐시에 저장된 모델을 로드 (이미 다운로드된 모델 사용)
model_name = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"  # 여기에 원하는 모델명을 입력

model = AutoModel.from_pretrained(model_name, local_files_only=True)
tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)

print("로컬 모델 로드 완료!")
