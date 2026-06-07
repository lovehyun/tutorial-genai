# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# pip install diffusers transformers accelerate safetensors
# 최소 VRAM 4GB 이상 GPU (NVIDIA) 권장
# CPU도 가능하나 매우 느립니다

from diffusers import StableDiffusionPipeline
import torch

# 모델 로드
# runwayml/stable-diffusion-v1-5	가장 안정적이고 범용적인 모델
# stabilityai/stable-diffusion-2-1	더 선명한 결과 제공
# stabilityai/stable-diffusion-xl-base-1.0	SDXL 모델, VRAM 8GB 이상 권장
pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5").to("cpu")

# 이미지 생성
prompt = "A futuristic city at sunset, digital art"
image = pipe(prompt).images[0]

# 저장
image.save("generated.png")
print("이미지가 generated.png에 저장되었습니다.")
