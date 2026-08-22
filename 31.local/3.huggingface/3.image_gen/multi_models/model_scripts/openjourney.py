#!/usr/bin/env python3
# openjourney.py - OpenJourney v4 모델로 이미지 생성

import os
import torch
from diffusers import StableDiffusionPipeline
import gc

print("\n=== OpenJourney v4 모델 실행 중... ===")

# 결과 폴더 생성
os.makedirs("model_outputs", exist_ok=True)

# GPU 확인
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"장치: {device}")

# GPU 메모리 초기화
if device == "cuda":
    torch.cuda.empty_cache()
    gc.collect()

try:
    # 모델 로드
    pipe = StableDiffusionPipeline.from_pretrained(
        "prompthero/openjourney-v4",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        safety_checker=None
    )
    
    # 메모리 최적화
    pipe.enable_attention_slicing(1)
    pipe = pipe.to(device)
    
    # 프롬프트 선택 (하나만 활성화하고 나머지는 주석 처리)
    # 프롬프트 1: 판타지 캐릭터 (OpenJourney는 판타지/미드저니 스타일에 강점)
    prompt = "mdjrny-v4 style, cosmic divine being, ethereal entity, ornate glowing armor, celestial background, floating magical particles, vibrant colors, highly detailed, fantasy concept art, trending on artstation, by Greg Rutkowski and Alphonse Mucha"
    # 한글 번역: mdjrny-v4 스타일, 우주의 신성한 존재, 초월적 개체, 화려하고 빛나는 갑옷, 천체 배경, 공중에 떠 있는 마법 입자, 생생한 색상, 매우 상세한, 판타지 컨셉 아트, 아트스테이션 트렌딩, 그렉 루트코프스키와 알폰스 무하 스타일
    
    # 프롬프트 2: 판타지 풍경 (OpenJourney의 환상적인 풍경 표현력 테스트)
    # prompt = "mdjrny-v4 style, floating islands in the sky, waterfalls cascading off the edges, lush vegetation, crystal formations, ancient stone temples, dragons flying between islands, epic fantasy landscape, golden hour lighting, unreal engine 5, 8k, artstation trending"
    # 한글 번역: mdjrny-v4 스타일, 하늘에 떠 있는 섬들, 가장자리에서 떨어지는 폭포, 울창한 식물, 수정 형성물, 고대 석조 사원, 섬들 사이를 날아다니는 드래곤, 웅장한 판타지 풍경, 황금빛 시간대 조명, 언리얼 엔진 5, 8k, 아트스테이션 트렌딩
    
    # 프롬프트 3: 미래적 캐릭터 (OpenJourney의 SF 판타지 혼합 스타일 테스트)
    # prompt = "mdjrny-v4 style, cybernetic shaman, half human half machine, glowing tribal markings, futuristic ceremonial outfit, holographic projections, surrounded by technological spirits, bioluminescent plants, dark mystical atmosphere, intricate details, digital art, trending on artstation"
    # 한글 번역: mdjrny-v4 스타일, 사이버네틱 샤먼, 반은 인간 반은 기계, 빛나는 부족 문양, 미래적인 의식용 의상, 홀로그램 투영, 기술적 영혼들에 둘러싸임, 생체 발광 식물, 어두운 신비한 분위기, 복잡한 세부 묘사, 디지털 아트, 아트스테이션 트렌딩
    
    print(f"프롬프트: {prompt}")
    
    # 이미지 생성
    image = pipe(
        prompt, 
        height=512, 
        width=512,
        num_inference_steps=30
    ).images[0]
    
    # 이미지 저장
    output_path = "model_outputs/openjourney_v4_generated.png"
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

print("OpenJourney v4 스크립트 완료")
