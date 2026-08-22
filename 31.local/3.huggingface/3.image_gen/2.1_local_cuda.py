# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# pip install diffusers transformers accelerate safetensors
# 최소 VRAM 4GB 이상 GPU (NVIDIA) 권장
# CPU도 가능하나 매우 느립니다

from diffusers import StableDiffusionPipeline
import torch

# 모델 로드
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    # "stabilityai/stable-diffusion-2-1",
    # "dreamlike-art/dreamlike-photoreal-2.0",
    # "prompthero/openjourney-v4",
    # "nitrosocke/redshift-diffusion",
    # "wavymulder/analog-diffusion",
    torch_dtype=torch.float16,  # GPU 사용 시 float16
).to("cuda")  # 또는 "cpu"

# 추천 모델 목록 (8GB VRAM 기준)
# 모델 이름	특징	메모
# runwayml/stable-diffusion-v1-5	가장 안정적, 기본 SD 1.5
# stabilityai/stable-diffusion-2-1	SD 2.1 버전, 더 넓은 해상도 (768x768) 지원	프롬프트 정밀도 높음
# dreamlike-art/dreamlike-photoreal-2.0	사진처럼 사실적인 스타일	인물, 풍경 모두 좋음
# prompthero/openjourney-v4	미드저니 스타일, 디지털 아트에 적합	캐릭터, 배경 아트용
# nitrosocke/redshift-diffusion	시네마틱, SF 풍, 블렌더 스타일	창의적 콘셉트 아트 제작용
# wavymulder/analog-diffusion	빈티지/아날로그 필름 스타일	고전 감성 사진 느낌

# 이미지 생성
prompt = "A futuristic city at sunset, digital art"
image = pipe(prompt).images[0]

# 저장
image.save("generated.png")
print("이미지가 generated.png에 저장되었습니다.")
