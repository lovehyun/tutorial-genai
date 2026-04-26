# 오픈소스 AI 음악 생성 모델 비교

오픈소스 AI 음악 생성 모델들의 특징, 요구 사양, 품질을 비교합니다.

## 모델 비교표

| 모델 | GitHub Stars | 보컬 | 최대 길이 | 최소 VRAM | 라이선스 | 품질 (2026 기준) |
|------|-------------|------|----------|----------|---------|-----------------|
| **ACE-Step v1.5** | ~9.5k | O | 10분 | 4GB | MIT | 상용급 (Suno v4.5~v5 수준) |
| **ACE-Step v1** | ~4.4k | O | 4분 | 8GB | Apache 2.0 | 높음 |
| **MusicGen (Meta)** | ~22.8k | X | ~30초 | 4GB (Small) | CC-BY-NC 4.0 | 양호 (기악 전용) |
| **Stable Audio Open** | ~2.5k | X | 47초 | 16GB | Community License | 양호 (루프/SFX) |
| **Bark (Suno)** | ~39.1k | O (음성 위주) | ~13초 | 8GB | MIT | 양호 (TTS 특화) |
| **Riffusion** | ~3.9k | X | 5~10초 | ~8GB | MIT | 구식 |
| **YuE** | ~6.2k | O | 5분 | 24GB | Apache 2.0 | 높음 (느린 추론) |
| **HeartMuLa** | ~4k | O | 4분 | 8GB | Apache 2.0 | 높음 |
| **SongGeneration 2 (Tencent)** | ~1.6k | O | 4분 30초 | 10GB | Apache 2.0 | 매우 높음 (최고 가사 정확도) |

---

## 1. ACE-Step (추천)

> "음악 생성의 Stable Diffusion" — 가장 빠르고 범용적인 오픈소스 음악 생성 모델

### 개요
- **개발**: ACE Studio + StepFun AI
- **아키텍처**: Diffusion Transformer (DiT) + Deep Compression AutoEncoder (DCAE)
- **v1.5**: LM Planner 추가 (Chain-of-Thought → 노래 설계도 → DiT 합성)
- **GitHub**: [ace-step/ACE-Step](https://github.com/ace-step/ACE-Step) / [ace-step/ACE-Step-1.5](https://github.com/ace-step/ACE-Step-1.5)

### VRAM 요구사항 (v1.5 상세)

| GPU VRAM | DiT 모델 | LM 모델 | 비고 |
|----------|---------|---------|------|
| 4~6 GB | 2B turbo | 없음 | INT8 양자화 + CPU 오프로드 |
| 6~8 GB | 2B turbo | 0.6B LM | PyTorch 백엔드 |
| 8~16 GB | 2B turbo/sft | 0.6B~1.7B LM | vllm 백엔드 |
| 16~20 GB | 2B sft / XL turbo | 1.7B LM | XL은 20GB 미만 시 CPU 오프로드 |
| 20~24 GB | XL turbo/sft | 1.7B LM | XL 오프로드 없이 동작 |
| 24+ GB | XL sft | 4B LM | 최고 품질 |

### 추론 성능

| GPU | 1분 오디오 생성 시간 |
|-----|-------------------|
| RTX 4090 | 1.74초 |
| A100 | 2.20초 |
| RTX 3090 | 4.70초 |
| M2 Max | 26.43초 |

### 주요 기능
- **텍스트→음악**: 스타일 태그 + 가사로 음악 생성
- **50+ 언어** 지원 (한국어 포함)
- **10초~10분** 길이 생성
- **1000+ 악기/스타일**
- **Retake** (변형), **Repaint** (부분 재생성), **Edit** (태그/가사 수정), **Extend** (연장)
- **커버 생성**, **레퍼런스 오디오** 스타일 전이
- **트랙 분리** (보컬/반주 스템)
- **LoRA 학습**: 8곡, RTX 3090에서 1시간
- **플랫폼**: CUDA, ROCm (AMD), MLX (Apple Silicon), Intel XPU, CPU

### 설치

```bash
# v1 (pip 설치 — 간단한 API)
pip install ace-step

# v1.5 (uv 기반 — 고급 기능)
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/ACE-Step/ACE-Step-1.5.git
cd ACE-Step-1.5
uv sync
uv run acestep          # Gradio UI
uv run acestep-api      # REST API 서버
```

---

## 2. MusicGen (Meta AudioCraft)

- **아키텍처**: 단일 단계 자기회귀 Transformer + EnCodec
- **모델**: Small (300M), Medium (1.5B), Melody (1.5B), Large (3.3B)
- **VRAM**: Small 4~6GB / Medium 8~10GB / Large ~16GB
- **특징**: 텍스트→음악, 멜로디 컨디셔닝 / 기악 전용 (보컬 X)
- **라이선스**: 코드 MIT, 가중치 CC-BY-NC 4.0 (비상업)
- **GitHub**: [facebookresearch/audiocraft](https://github.com/facebookresearch/audiocraft)

```python
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

model = MusicGen.get_pretrained('facebook/musicgen-large')
model.set_generation_params(duration=8)
wav = model.generate(['happy rock', 'energetic EDM'])
for idx, one_wav in enumerate(wav):
    audio_write(f'{idx}', one_wav.cpu(), model.sample_rate)
```

---

## 3. Stable Audio Open (Stability AI)

- **아키텍처**: Latent Diffusion + Transformer + T5 텍스트 컨디셔닝 (1.21B)
- **VRAM**: ~16GB 권장
- **특징**: 텍스트→오디오, 루프/사운드 디자인 특화 / 기악 전용 (보컬 X)
- **라이선스**: Stability AI Community License (상업 사용 별도 라이선스)
- **GitHub**: [Stability-AI/stable-audio-tools](https://github.com/Stability-AI/stable-audio-tools)

---

## 4. Bark (Suno)

- **아키텍처**: GPT 스타일 + EnCodec
- **VRAM**: ~12GB (Full) / ~8GB (Small)
- **특징**: TTS 특화, 노래/웃음/비언어 사운드 생성 가능 / 음악 전용 X
- **라이선스**: MIT
- **GitHub**: [suno-ai/bark](https://github.com/suno-ai/bark)

---

## 5. YuE (HKUST / M-A-P)

- **아키텍처**: LLM 기반, 보컬 + 반주 동시 생성
- **VRAM**: 최소 24GB (2세션) / 80GB+ 권장 (전체 곡)
- **특징**: 가사→노래, 보이스 클로닝, CoT/ICL 모드
- **라이선스**: Apache 2.0
- **GitHub**: [multimodal-art-projection/YuE](https://github.com/multimodal-art-projection/YuE)

---

## 6. HeartMuLa

- **아키텍처**: Music Language Model (3B) + HeartCodec + HeartCLAP
- **VRAM**: ~8~12GB
- **특징**: 가사 + 태그 컨디셔닝, 다국어, RL 강화 스타일 제어
- **라이선스**: Apache 2.0
- **GitHub**: [HeartMuLa/heartlib](https://github.com/HeartMuLa/heartlib)

---

## 7. SongGeneration 2 / LeVo 2 (Tencent)

- **아키텍처**: 하이브리드 LLM-Diffusion (4B) — Composer Brain + Hi-Fi Renderer
- **VRAM**: Base 10~16GB / Large 22~28GB
- **특징**: 최고 가사 정확도 (PER 8.55%, Suno v5는 12.4%), 트랙 분리 출력
- **라이선스**: Apache 2.0
- **GitHub**: [tencent-ailab/SongGeneration](https://github.com/tencent-ailab/SongGeneration)

---

## 결론: 어떤 모델을 선택해야 하는가?

| 목적 | 추천 모델 | 이유 |
|------|----------|------|
| **보컬 포함 풀 음악 생성** | ACE-Step v1.5 | 최저 VRAM, 최빠른 속도, 가장 많은 기능 |
| **기악 스케치** | MusicGen | 간단한 API, HuggingFace 생태계 |
| **가사 정확도 최우선** | SongGeneration 2 | 최고 PER 점수 |
| **Apple Silicon** | ACE-Step v1.5 | MLX 네이티브 지원 |
| **저사양 (4~6GB)** | ACE-Step v1.5 (2B turbo) | INT8 + CPU 오프로드 |

## 예제

| 폴더 | 파일 | 설명 | 환경 |
|------|------|------|------|
| `1.ace_local/` | `ace_step_demo.py` | ACE-Step v1 로컬 실행 (기본 + 고급) | GPU 8GB+ |
| `1.ace_colab/` | `ace_step_colab.ipynb` | Colab 노트북 (T4 GPU 무료) | Google Colab |

### 실행

```bash
# 로컬 (GPU 필요)
pip install ace-step soundfile
python 1.ace_local/ace_step_demo.py           # 기본: K-Pop, Lo-fi, 록 발라드
python 1.ace_local/ace_step_demo.py advanced   # 고급: Retake, Repaint, Edit, Extend

# Colab (GPU 없어도 OK)
# 1.ace_colab/ace_step_colab.ipynb 을 Google Colab에서 열기
```
