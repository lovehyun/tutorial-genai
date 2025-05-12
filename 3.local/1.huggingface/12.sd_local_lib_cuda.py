# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# pip install diffusers transformers accelerate safetensors
# 최소 VRAM 4GB 이상 GPU (NVIDIA) 권장
# CPU도 가능하나 매우 느립니다

from diffusers import StableDiffusionPipeline
import torch

# 모델 로드
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,      # float32도 가능 (CPU에서는 float32)
    revision="fp16",                # fp16이 아닌 경우 생략 가능
).to("cuda")  # 또는 "cpu"

# 이미지 생성
prompt = "A futuristic city at sunset, digital art"
image = pipe(prompt).images[0]

# 저장
image.save("generated.png")
print("이미지가 generated.png에 저장되었습니다.")
