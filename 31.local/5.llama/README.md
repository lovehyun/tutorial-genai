# 5.llama — Llama 계열을 로컬에서

Llama 아키텍처의 모델을 `transformers`로 직접 로드해 생성한다.

## 파일

| 파일 | 내용 |
|---|---|
| `1.llama_intro.py` | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` 로드 → 생성 (최소형) |

## 왜 `Llama-2-7b-chat-hf`가 아니라 TinyLlama인가

원래 이 예제는 `meta-llama/Llama-2-7b-chat-hf`를 썼는데, 실제로 확인해보니 두 가지 문제가 있었다:

1. **게이트 모델** — Meta 라이선스에 별도로 동의해야 다운로드가 되고(`huggingface-cli login` +
   HuggingFace에서 접근 승인), 승인 없이는 그냥 실행이 막힌다.
2. **CPU로 못 돌린다** — 7B는 VRAM 8GB 이상을 전제로 한 크기라, 이 저장소 환경(CPU-only)에서는
   비현실적으로 느리다.

`TinyLlama-1.1B-Chat-v1.0`은 **같은 Llama 아키텍처**를 쓰면서 승인 없이 바로 받아지고, CPU에서도
합리적인 시간 안에 실제로 돌아간다 — 그래서 이걸로 바꿨다. 실제 Llama-2-7b를 쓰고 싶다면 주석의
GPU 버전 코드로 바꾸고 먼저 라이선스에 동의하면 된다.

## 관전 포인트 (실제로 겪은 버그)

원래 코드에 실행하면 바로 깨지는 버그가 두 개 있었다 — 고치면서 배울 만해서 기록해둔다:
- `from_pretrained(..., map_location="cpu")` — `map_location`은 `torch.load()`의 인자지
  `from_pretrained()`엔 없는 인자다. **디바이스는 `.to("cpu")`로 모델 자체에 지정**해야 한다.
- 모델은 `device_map` 없이 로드해 기본 CPU에 있는데, 입력(`inputs`)만 `.to("cuda")`로 GPU에
  보내고 있었다 — **모델과 입력의 디바이스가 어긋나면 실행 시 바로 에러**가 난다. 지금은 모델·
  입력 둘 다 명시적으로 `.to("cpu")`로 맞춰뒀다.

## 실행 (실측 확인됨)
```bash
pip install torch transformers accelerate sentencepiece
python 1.llama_intro.py
```
CPU에서 몇 초~수십 초 안에 응답이 나온다(모델이 작아서 `4.mistral/`의 7B와 달리 실습에 적합하다).

## 다음 단계
- 더 큰 Llama 계열(Mistral 7B)로 — [`../4.mistral/`](../4.mistral/)(단, CPU에선 느림)
- 양자화된 GGUF 형식으로 가볍게 — [`../10.ollama/`](../10.ollama/)
