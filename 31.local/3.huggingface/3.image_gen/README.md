# 3.image_gen — Stable Diffusion 이미지 생성

텍스트 → 이미지(Stable Diffusion 등). **API 호출** vs **로컬 실행** 두 갈래이며,
로컬은 GPU 가 사실상 필요합니다(CPU 는 매우 느림).

## 학습 순서

| 파일 | 내용 | 비용/자원 |
|---|---|---|
| `1.1_api.py` | HF Inference API 로 이미지 생성 (FLUX 등) | 💳 크레딧 차감 |
| `1.2_inference_client.py` | `InferenceClient` 로 이미지 생성 | 💳 크레딧 차감 |
| `2.1_local_cuda.py` | `diffusers` 로 **로컬** SD 실행 (여러 모델) | ✅ 무료, ⚠️ GPU 필요 |
| `2.2_prompts.py` | 모델별 프롬프트 스타일 비교 | ⚠️ GPU |
| `2.3_offloading.py` | CPU offload·attention slicing 등 **저VRAM 최적화** | ⚠️ 저VRAM 환경 |
| `2.4_cpu.py` | CPU 전용 최소 예제 (느림, 동작 확인용) | ✅ 무료(매우 느림) |
| `multi_models/` | 모델별 standalone 스크립트 + `run_models.py` 실행기 | ⚠️ GPU |

## 핵심
- **1.x = API(서버가 생성, 크레딧 차감)** vs **2.x = 로컬(내 GPU)**.
- 로컬 SD 는 모델 가중치가 수 GB + GPU VRAM 이 필요. VRAM 이 부족하면 `2.3_offloading.py` 기법 사용.
- GPU 인스턴스 비용/세팅은 [AWS.md](AWS.md) 참고.
- `multi_models/` 는 모델별로 거의 같은 보일러플레이트라 중복이 있습니다 — 한 모델만 바꿔 보고 싶을 때 사용.

## 실행
```bash
pip install diffusers transformers torch accelerate
# API 예제: HUGGINGFACEHUB_API_TOKEN 필요
python 2.4_cpu.py     # GPU 없이 동작 확인 (느림)
```
> 생성된 이미지(`*.png`)는 커밋되지 않습니다(.gitignore).
