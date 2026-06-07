#!/usr/bin/env python3
# redshift.py - Redshift Diffusion 모델로 이미지 생성

import os
import torch
from diffusers import StableDiffusionPipeline
import gc

print("\n=== Redshift Diffusion 모델 실행 중... ===")

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
        "nitrosocke/redshift-diffusion",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        safety_checker=None
    )
    
    # 메모리 최적화
    pipe.enable_attention_slicing(1)
    pipe = pipe.to(device)
    
    # 프롬프트 선택 (하나만 활성화하고 나머지는 주석 처리)
    # 프롬프트 1: 사이버네틱 생물체 (Redshift는 SF/블렌더 스타일에 강점)
    prompt = "redshift style, cybernetic alien creature in a futuristic laboratory, holographic displays, neon lighting, 3D render, octane render, blender, sci-fi concept art, hyper detailed, volumetric lighting"
    # 한글 번역: redshift 스타일, 미래적인 실험실에 있는 사이버네틱 외계 생물체, 홀로그램 디스플레이, 네온 조명, 3D 렌더링, 옥테인 렌더, 블렌더, 공상과학 컨셉 아트, 초세밀한 디테일, 볼륨 라이팅
    
    # 프롬프트 2: 미래 도시 (Redshift의 시네마틱 SF 도시 표현력 테스트)
    # prompt = "redshift style, aerial view of a sprawling futuristic megacity, skyscrapers with holographic projections, flying vehicles between buildings, cyberpunk atmosphere, foggy day, cinematic lighting, octane render, high detail, trending on artstation"
    # 한글 번역: redshift 스타일, 광활한 미래 메가시티의 항공 뷰, 홀로그램 투영이 있는 고층 빌딩, 건물 사이를 날아다니는 차량, 사이버펑크 분위기, 안개 낀 날, 영화적 조명, 옥테인 렌더, 높은 디테일, 아트스테이션 트렌딩
    
    # 프롬프트 3: 공상과학 우주선 (Redshift의 하드서피스 렌더링 테스트)
    # prompt = "redshift style, detailed science fiction spaceship interior, command bridge, crew at control stations, holographic star maps, futuristic machinery, advanced technology, dramatic spaceship lighting, 3D modeling, hard surface rendering, unreal engine, highly detailed"
    # 한글 번역: redshift 스타일, 상세한 공상과학 우주선 내부, 조종 브릿지, 제어 스테이션에 있는 승무원, 홀로그램 별자리 지도, 미래적인 기계류, 첨단 기술, 극적인 우주선 조명, 3D 모델링, 하드 서피스 렌더링, 언리얼 엔진, 매우 상세함
    
    print(f"프롬프트: {prompt}")
    
    # 이미지 생성
    image = pipe(
        prompt, 
        height=512, 
        width=512,
        num_inference_steps=30
    ).images[0]
    
    # 이미지 저장
    output_path = "model_outputs/redshift_diffusion_generated.png"
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

print("Redshift Diffusion 스크립트 완료")
