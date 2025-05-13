#!/usr/bin/env python3
# analog.py - Analog Diffusion 모델로 이미지 생성

import os
import torch
from diffusers import StableDiffusionPipeline
import gc

print("\n=== Analog Diffusion 모델 실행 중... ===")

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
        "wavymulder/analog-diffusion",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        safety_checker=None
    )
    
    # 메모리 최적화
    pipe.enable_attention_slicing(1)
    pipe = pipe.to(device)
    
    # 프롬프트 설정
    prompt = "analog style, vintage film photograph of a young couple at a 1970s diner, grain, dust, scratches, vibrant colors, Kodak Portra 400, shot on 35mm, nostalgic mood, soft focus"
    print(f"프롬프트: {prompt}")
    
    # 이미지 생성
    image = pipe(
        prompt, 
        height=512, 
        width=512,
        num_inference_steps=30
    ).images[0]
    
    # 이미지 저장
    output_path = "model_outputs/analog_diffusion_generated.png"
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

print("Analog Diffusion 스크립트 완료")
