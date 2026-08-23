# pip install torch transformers accelerate sentencepiece

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# 1. TinyLlama 로드 — 실제 Llama 아키텍처를 쓰는 오픈(비-게이트) 모델.
#    meta-llama/Llama-2-7b-chat-hf 는 (a) HuggingFace 라이선스 승인이 별도로 필요한 게이트 모델이고
#    (b) 7B는 VRAM 8GB+ 없이 CPU로 돌리면 비현실적으로 느리다 — 그래서 강의/실습용으로는
#    같은 계열이면서 승인 없이 바로 받아지는 1.1B 모델을 쓴다. 진짜 Llama-2-7b를 쓰려면
#    huggingface-cli login 으로 먼저 라이선스에 동의해야 한다(README 참고).
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# CPU에서 돌릴 거라 float32 + 명시적 .to("cpu") — GPU가 있다면 주석의 대안으로 바꾼다.
model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float32).to("cpu")
# GPU 버전(VRAM 8GB+ 권장):
#   model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float16, device_map="auto")
#   inputs = tokenizer(input_text, return_tensors="pt").to("cuda")

# 2. 사용자 입력 생성
input_text = "Hello, how are you?"
inputs = tokenizer(input_text, return_tensors="pt").to("cpu")  # 모델과 입력의 디바이스가 같아야 한다

# 3. 모델 실행 (텍스트 생성)
with torch.no_grad():
    output = model.generate(**inputs, max_new_tokens=50)

# 4. 출력 결과 디코딩
response = tokenizer.decode(output[0], skip_special_tokens=True)
print("Llama Response:", response)
