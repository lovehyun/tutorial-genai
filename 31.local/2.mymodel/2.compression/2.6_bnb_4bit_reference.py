# (2단계-F) 4bit 양자화 로딩(bitsandbytes) — ⚠️ GPU 전용, 이 저장소 환경(CPU-only)에서
# 실행 검증하지 못했다. 코드는 공식 문서 패턴과 대조해서 작성했지만, 직접 실행 전에
# GPU 환경에서 한 번 더 확인할 것.
#
# pip install transformers torch bitsandbytes accelerate
#
# 2.1_quantization.py 의 동적 양자화(torch.quantization.quantize_dynamic)는 CPU에서 동작하고
# "이미 로드된 모델"을 사후에 줄이는 방식이었다. 반면 bitsandbytes 4bit는 **로드하는 순간부터**
# 4bit로 압축된 상태로 GPU 메모리에 올린다 — Mistral 7B(`4.mistral/`)·Llama(`5.llama/`)처럼
# 원본이 크면 클수록 이 방식이 아니면 애초에 GPU 메모리에 안 들어간다(7B fp16 ≈ 14GB인데
# 4bit로 로드하면 ≈ 4~5GB로 줄어든다 — 소비자용 GPU 8~12GB에서도 실행 가능해지는 이유).

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_name = "mistralai/Mistral-7B-Instruct-v0.3"  # 4.mistral/ 과 같은 모델로 비교해볼 것

# [관전 포인트 1] NF4(Normal Float 4) — bitsandbytes가 제안한 4bit 포맷. 단순 반올림보다
#   가중치의 실제 분포(대체로 정규분포에 가까움)에 맞춰 양자화 구간을 나눠서 정확도 손실이 적다.
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,  # 연산 자체는 4bit가 아니라 bf16으로 복원해서 수행
    bnb_4bit_use_double_quant=True,          # 양자화 상수 자체도 한 번 더 압축(추가로 약간 절약)
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",  # GPU가 있어야 의미 있다 — CPU만 있으면 이 옵션 자체가 사실상 무의미
)

inputs = tokenizer("What are good fitness tips?", return_tensors="pt").to(model.device)
with torch.no_grad():
    output = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(output[0], skip_special_tokens=True))

# [관전 포인트 2] QLoRA로 이어가려면 — 위 4bit 모델에 2.mymodel/3.lora/1.lora_vs_full.py의
#   LoraConfig를 그대로 적용하면 된다. "4bit로 얼려서 로드 + LoRA 어댑터만 학습"이 QLoRA다.
#   코드 구조상 새로운 게 아니라 이 두 파일을 합치는 것뿐이라는 걸 확인해두면 좋다.
#
# 정리:
#   - CPU만 있다면 → 2.1_quantization.py(동적 양자화) 또는 10.ollama/(GGUF, CPU 친화적)를 쓸 것.
#   - GPU(8GB+)가 있다면 → 이 파일 그대로 7B급 모델을 소비자용 GPU에서 돌릴 수 있다.
