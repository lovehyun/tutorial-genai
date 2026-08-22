# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# pip install diffusers transformers accelerate safetensors
# 최소 VRAM 4GB 이상 GPU (NVIDIA) 권장
# CPU도 가능하나 매우 느립니다

from diffusers import StableDiffusionPipeline
import torch
import os

# GPU 확인 및 설정
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cuda":
    print(f"GPU를 사용합니다: {torch.cuda.get_device_name(0)}")
    print(f"사용 가능한 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024 / 1024 / 1024:.2f} GB")
else:
    print("GPU를 찾을 수 없어 CPU를 사용합니다. 처리 속도가 매우 느릴 수 있습니다.")

# 결과 저장 폴더 생성
os.makedirs("model_outputs", exist_ok=True)

def generate_stable_diffusion_v1_5():
    """기본 Stable Diffusion v1.5 모델로 이미지 생성"""
    print("\n=== runwayml/stable-diffusion-v1-5 모델 실행 중... ===")
    
    # 모델 로드
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    ).to(device)
    
    # 이미지 생성
    prompt = "A serene mountain lake at dawn, with mist rising from the water and rays of sunlight filtering through the trees, photorealistic quality"
    print(f"프롬프트: {prompt}")
    
    image = pipe(prompt).images[0]
    
    # 저장
    output_path = "model_outputs/sd_v1_5_generated.png"
    image.save(output_path)
    print(f"이미지가 {output_path}에 저장되었습니다.")
    
    # 메모리 정리
    del pipe
    if device == "cuda":
        torch.cuda.empty_cache()

def generate_stable_diffusion_v2_1():
    """Stable Diffusion v2.1 모델로 이미지 생성"""
    print("\n=== stabilityai/stable-diffusion-2-1 모델 실행 중... ===")
    
    # 모델 로드
    pipe = StableDiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-2-1",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    ).to(device)
    
    # 이미지 생성
    prompt = "Highly detailed portrait of a Renaissance nobleman wearing ornate clothing with intricate patterns, dramatic lighting, detailed face, 8k resolution, studio photography"
    print(f"프롬프트: {prompt}")
    
    image = pipe(prompt).images[0]
    
    # 저장
    output_path = "model_outputs/sd_v2_1_generated.png"
    image.save(output_path)
    print(f"이미지가 {output_path}에 저장되었습니다.")
    
    # 메모리 정리
    del pipe
    if device == "cuda":
        torch.cuda.empty_cache()

def generate_dreamlike_photoreal():
    """Dreamlike Photoreal 2.0 모델로 이미지 생성"""
    print("\n=== dreamlike-art/dreamlike-photoreal-2.0 모델 실행 중... ===")
    
    # 모델 로드
    pipe = StableDiffusionPipeline.from_pretrained(
        "dreamlike-art/dreamlike-photoreal-2.0",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    ).to(device)
    
    # 이미지 생성
    prompt = "Ultra realistic photograph of an ancient temple hidden in a lush jungle, sunbeams streaming through dense foliage, high detail, cinematic lighting, National Geographic style, Sony A7R IV, 90mm f/1.4 lens"
    print(f"프롬프트: {prompt}")
    
    image = pipe(prompt).images[0]
    
    # 저장
    output_path = "model_outputs/dreamlike_photoreal_generated.png"
    image.save(output_path)
    print(f"이미지가 {output_path}에 저장되었습니다.")
    
    # 메모리 정리
    del pipe
    if device == "cuda":
        torch.cuda.empty_cache()

def generate_openjourney_v4():
    """OpenJourney v4 모델로 이미지 생성"""
    print("\n=== prompthero/openjourney-v4 모델 실행 중... ===")
    
    # 모델 로드
    pipe = StableDiffusionPipeline.from_pretrained(
        "prompthero/openjourney-v4",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    ).to(device)
    
    # 이미지 생성
    prompt = "mdjrny-v4 style, cosmic divine being, ethereal entity, ornate glowing armor, celestial background, floating magical particles, vibrant colors, highly detailed, fantasy concept art, trending on artstation, by Greg Rutkowski and Alphonse Mucha"
    print(f"프롬프트: {prompt}")
    
    image = pipe(prompt).images[0]
    
    # 저장
    output_path = "model_outputs/openjourney_v4_generated.png"
    image.save(output_path)
    print(f"이미지가 {output_path}에 저장되었습니다.")
    
    # 메모리 정리
    del pipe
    if device == "cuda":
        torch.cuda.empty_cache()

def generate_redshift_diffusion():
    """Redshift Diffusion 모델로 이미지 생성"""
    print("\n=== nitrosocke/redshift-diffusion 모델 실행 중... ===")
    
    # 모델 로드
    pipe = StableDiffusionPipeline.from_pretrained(
        "nitrosocke/redshift-diffusion",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    ).to(device)
    
    # 이미지 생성
    prompt = "redshift style, cybernetic alien creature in a futuristic laboratory, holographic displays, neon lighting, 3D render, octane render, blender, sci-fi concept art, hyper detailed, volumetric lighting"
    print(f"프롬프트: {prompt}")
    
    image = pipe(prompt).images[0]
    
    # 저장
    output_path = "model_outputs/redshift_diffusion_generated.png"
    image.save(output_path)
    print(f"이미지가 {output_path}에 저장되었습니다.")
    
    # 메모리 정리
    del pipe
    if device == "cuda":
        torch.cuda.empty_cache()

def generate_analog_diffusion():
    """Analog Diffusion 모델로 이미지 생성"""
    print("\n=== wavymulder/analog-diffusion 모델 실행 중... ===")
    
    # 모델 로드
    pipe = StableDiffusionPipeline.from_pretrained(
        "wavymulder/analog-diffusion",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    ).to(device)
    
    # 이미지 생성
    prompt = "analog style, vintage film photograph of a young couple at a 1970s diner, grain, dust, scratches, vibrant colors, Kodak Portra 400, shot on 35mm, nostalgic mood, soft focus"
    print(f"프롬프트: {prompt}")
    
    image = pipe(prompt).images[0]
    
    # 저장
    output_path = "model_outputs/analog_diffusion_generated.png"
    image.save(output_path)
    print(f"이미지가 {output_path}에 저장되었습니다.")
    
    # 메모리 정리
    del pipe
    if device == "cuda":
        torch.cuda.empty_cache()

def run_all_models():
    """모든 모델을 순차적으로 실행"""
    print("모든 모델을 순차적으로 실행합니다. 이 작업은 시간이 오래 걸릴 수 있습니다.")
    
    generate_stable_diffusion_v1_5()
    generate_stable_diffusion_v2_1()
    generate_dreamlike_photoreal()
    generate_openjourney_v4()
    generate_redshift_diffusion()
    generate_analog_diffusion()
    
    print("\n모든 모델 실행이 완료되었습니다. 결과는 model_outputs 폴더에 저장되었습니다.")

if __name__ == "__main__":
    print("실행할 모델을 선택하세요. 아래 함수 중 하나의 주석을 해제하여 실행하세요.")
    
    # 원하는 함수의 주석을 해제하여 실행하세요
    # generate_stable_diffusion_v1_5()     # 기본 SD 1.5
    # generate_stable_diffusion_v2_1()     # SD 2.1 (더 높은 해상도)
    # generate_dreamlike_photoreal()       # 사진처럼 사실적인 스타일
    # generate_openjourney_v4()            # 미드저니 스타일 (판타지, 디지털 아트)
    # generate_redshift_diffusion()        # 시네마틱, SF 풍, 블렌더 스타일
    # generate_analog_diffusion()          # 빈티지/아날로그 필름 스타일
    
    # 또는 모든 모델을 순차적으로 실행 (시간이 오래 걸릴 수 있음)
    run_all_models()
    
    print("\n스크립트가 완료되었습니다.")
