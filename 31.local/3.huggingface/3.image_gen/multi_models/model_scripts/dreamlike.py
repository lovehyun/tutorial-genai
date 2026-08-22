#!/usr/bin/env python3
# dreamlike.py - Dreamlike Photoreal 2.0 모델로 이미지 생성

import os
import torch
from diffusers import StableDiffusionPipeline
import gc

print("\n=== Dreamlike Photoreal 2.0 모델 실행 중... ===")

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
        "dreamlike-art/dreamlike-photoreal-2.0",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        safety_checker=None
    )
    
    # 메모리 최적화
    pipe.enable_attention_slicing(1)
    pipe = pipe.to(device)
    
    # 프롬프트 선택 (하나만 활성화하고 나머지는 주석 처리)
    # 프롬프트 1: 실사적인 풍경 (Dreamlike는 사실적인 사진 스타일이 강점)
    prompt = "Ultra realistic photograph of an ancient temple hidden in a lush jungle, sunbeams streaming through dense foliage, high detail, cinematic lighting, National Geographic style, Sony A7R IV, 90mm f/1.4 lens"
    # 한글 번역: 울창한 정글에 숨겨진 고대 사원의 초현실적인 사진, 빽빽한 나뭇잎 사이로 비치는 햇살, 높은 디테일, 영화적 조명, 내셔널 지오그래픽 스타일, 소니 A7R IV, 90mm f/1.4 렌즈
    
    # 프롬프트 2: 사실적인 인물 사진 (Dreamlike의 인물 표현 테스트)
    # prompt = "Photorealistic portrait of a rugged mountain climber with weathered face, piercing blue eyes, and salt and pepper beard, late afternoon golden light, shallow depth of field, ultra-detailed skin texture, Hasselblad camera, Fujifilm Pro 400H, professional photography"
    # 한글 번역: 풍화된 얼굴, 날카로운 파란 눈, 흑백의 수염을 가진 거친 산악인의 사실적인 초상화, 오후 늦게 내리쬐는 황금빛 조명, 얕은 심도, 초세밀한 피부 질감, 하셀블라드 카메라, 후지필름 Pro 400H, 전문 사진
    
    # 프롬프트 3: 도시 풍경 사진 (Dreamlike의 도시 풍경 표현력 테스트)
    # prompt = "Hyper-realistic cityscape of Venice at dusk, reflections in canal water, warm evening light, historical architecture, tourists and locals on bridges, Canon EOS R5, 24-70mm lens, F/8, HDR, travel photography masterpiece"
    # 한글 번역: 황혼의 베니스 초현실적 도시 풍경, 운하 물에 비치는 반사, 따뜻한 저녁 빛, 역사적인 건축물, 다리 위의 관광객과 현지인들, 캐논 EOS R5, 24-70mm 렌즈, F/8, HDR, 여행 사진 걸작
    
    print(f"프롬프트: {prompt}")
    
    # 이미지 생성
    image = pipe(
        prompt, 
        height=512, 
        width=512,
        num_inference_steps=30
    ).images[0]
    
    # 이미지 저장
    output_path = "model_outputs/dreamlike_photoreal_generated.png"
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

print("Dreamlike Photoreal 스크립트 완료")
