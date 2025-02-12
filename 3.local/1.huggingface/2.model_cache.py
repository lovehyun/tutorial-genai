# Hugging Face는 기본적으로 다음 경로에 모델을 저장합니다.
# Linux/macOS: ~/.cache/huggingface/
# Windows: C:\Users\<사용자>\.cache\huggingface\

import huggingface_hub

print(huggingface_hub.__version__)

from huggingface_hub.constants import HUGGINGFACE_HUB_CACHE

print("Hugging Face 캐시 디렉토리:", HUGGINGFACE_HUB_CACHE)
