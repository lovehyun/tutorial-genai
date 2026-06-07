import os
import torch
from diffusers import StableDiffusionPipeline
import gc

# 결과 폴더 생성
os.makedirs("model_outputs", exist_ok=True)

# GPU 확인
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"장치: {device}")

# GPU 메모리 초기화
if device == "cuda":
    torch.cuda.empty_cache()
    gc.collect()

# 메모리 확보를 위한 설정
torch.cuda.empty_cache()
if device == "cuda":
    # GPU 메모리의 70%만 사용 (선택적)
    # torch.cuda.set_per_process_memory_fraction(0.7)
    pass

try:
    # 모델 로드
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        safety_checker=None
    )
    
    # 메모리 최적화
    pipe.enable_attention_slicing(1)
    if device == "cuda":
        pipe = pipe.to("cuda")
    else:
        pipe = pipe.to("cpu")
    
    # 프롬프트 선택 (하나만 활성화하고 나머지는 주석 처리)
    # 프롬프트 1: 자연 풍경 (SD 1.5는 자연 풍경 표현이 잘 됨)
    prompt = "A serene mountain lake at dawn, with mist rising from the water and rays of sunlight filtering through the trees, photorealistic quality"
    # 한글 번역: 새벽녘의 고요한 산속 호수, 물 위로 피어오르는 안개와 나무 사이로 필터링되는 햇살, 사진과 같은 사실적인 품질
    
    # 프롬프트 2: 상상의 캐릭터 (SD 1.5는 캐릭터 표현도 균형 있게 잘 표현)
    # prompt = "Portrait of a steampunk explorer with brass goggles, intricate mechanical backpack, standing in front of a zeppelin, detailed illustration, warm lighting, artstation trending"
    # 한글 번역: 황동 고글을 쓰고 정교한 기계식 배낭을 맨 스팀펑크 탐험가의 초상화, 제플린 비행선 앞에 서 있는 모습, 세부 묘사가 풍부한 일러스트레이션, 따뜻한 조명, 아트스테이션 트렌딩
    
    # 프롬프트 3: 도시 풍경 (SD 1.5의 균형 잡힌 표현력 테스트)
    # prompt = "Wide shot of a futuristic Tokyo at night, neon signs reflecting in rain puddles, cyberpunk atmosphere, highly detailed, cinematic lighting, 8k resolution"
    # 한글 번역: 밤의 미래적인 도쿄를 넓게 담은 장면, 빗물 웅덩이에 반사되는 네온 사인, 사이버펑크 분위기, 매우 상세한 표현, 영화적 조명, 8k 해상도
    
    print(f"프롬프트: {prompt}")
    
    # 이미지 생성
    image = pipe(
        prompt, 
        height=512, 
        width=512,
        num_inference_steps=30
    ).images[0]
    
    # 이미지 저장
    output_path = "model_outputs/sd_v1_5_generated.png"
    image.save(output_path)
    print(f"이미지가 {output_path}에 저장되었습니다.")
    
except Exception as e:
    print(f"오류 발생: {e}")
finally:
    # 메모리 정리
    if 'pipe' in locals():
        del pipe
    
    # 그래픽 메모리 비우기
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()

print("SD 1.5 스크립트 완료")
