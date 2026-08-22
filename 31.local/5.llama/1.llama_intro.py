# pip install torch transformers accelerate sentencepiece

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# 1. LLaMA 2 7B 모델 로드 (Hugging Face에서 다운로드됨)
model_name = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32, map_location="cpu")
# CPU 모드: 속도가 매우 느려질 수 있음 → LLaMA 2 7B는 VRAM 8GB 이상 필요!

# 2️. 사용자 입력 생성 (Hello, World!)
input_text = "Hello, how are you?"
inputs = tokenizer(input_text, return_tensors="pt").to("cuda")

# 3️. 모델 실행 (텍스트 생성)
with torch.no_grad():
    output = model.generate(**inputs, max_length=50)

# 4️. 출력 결과 디코딩
response = tokenizer.decode(output[0], skip_special_tokens=True)
print("LLaMA Response:", response)
