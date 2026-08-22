#!/usr/bin/env python3
# sd_v2_1.py - Stable Diffusion v2.1 모델로 이미지 생성

import os
import torch
from diffusers import StableDiffusionPipeline
import gc

print("\n=== Stable Diffusion v2.1 모델 실행 중... ===")

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
    # 모델 로드 (FP16 버전으로 메모리 절약)
    pipe = StableDiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-2-1",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        revision="fp16" if device == "cuda" else "main",
        safety_checker=None
    )
    
    # 메모리 최적화
    pipe.enable_attention_slicing(1)
    pipe = pipe.to(device)
    
    # 프롬프트 선택 (하나만 활성화하고 나머지는 주석 처리)
    # 프롬프트 1: 초상화 (SD 2.1은 인물 상세 표현이 향상됨)
    prompt = "Highly detailed portrait of a Renaissance nobleman wearing ornate clothing with intricate patterns, dramatic lighting, detailed face, 8k resolution, studio photography"
    # 한글 번역: 정교한 패턴이 있는 화려한 의상을 입은 르네상스 시대 귀족의 매우 상세한 초상화, 극적인 조명, 세밀한 얼굴 표현, 8k 해상도, 스튜디오 사진촬영
    
    # 프롬프트 2: 세부 묘사가 필요한 판타지 장면 (SD 2.1의 세부 표현력 테스트)
    # prompt = "Ancient library filled with magical artifacts, floating books, glowing crystals, intricate architecture, golden hour lighting, dust particles in the air, ultra detailed, hyperrealistic, 8K"
    # 한글 번역: 마법 유물로 가득 찬 고대 도서관, 공중에 떠 있는 책들, 빛나는 크리스털, 정교한 건축 양식, 황금빛 조명, 공기 중의 먼지 입자, 초세밀한 표현, 초현실적, 8K
    
    # 프롬프트 3: 복잡한 기계적 디자인 (SD 2.1의 복잡한 구조물 표현력 테스트)
    # prompt = "Detailed technical cross-section of a futuristic space station, cutaway view showing multiple levels, mechanical components, living quarters, hydroponics, engineering sections, highly detailed engineering illustration style, schematic"
    # 한글 번역: 미래적인 우주 정거장의 상세한 기술적 단면도, 여러 층과 기계적 구성 요소, 거주 구역, 수경재배 시설, 공학 구역이 보이는 절개도, 매우 상세한 공학 일러스트레이션 스타일, 도식화
    
    print(f"프롬프트: {prompt}")
    
    # 이미지 생성 (작은 크기로 메모리 절약)
    image = pipe(
        prompt, 
        height=512, 
        width=512,
        num_inference_steps=30
    ).images[0]
    
    # 이미지 저장
    output_path = "model_outputs/sd_v2_1_generated.png"
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

print("SD 2.1 스크립트 완료")
