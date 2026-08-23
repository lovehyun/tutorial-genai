# 2.mymodel/3.lora — LoRA (Low-Rank Adaptation)

`1.finetune/`은 **전체 파라미터**를 학습했다. 여기서는 원본 가중치는 얼려두고(freeze) 아주 작은
어댑터만 학습하는 **LoRA**를 같은 토이 데이터로 직접 비교한다 — Mistral 7B·Llama 8B처럼 전체
파인튜닝이 현실적으로 어려운 큰 모델을 커스터마이즈하려면 사실상 필수적인 기법이다.

## 파일
| 파일 | 내용 |
|---|---|
| `1.lora_vs_full.py` | `1.finetune/1.1_train.py`와 **완전히 같은 데이터·같은 모델**로 LoRA 학습 — 학습 파라미터 비율과 저장 용량을 직접 비교 |

## 실행 (실측 결과)
```bash
pip install transformers torch datasets peft
python 1.lora_vs_full.py
```
```
전체 파라미터:      66,955,010
LoRA 학습 파라미터:  813,314 (1.215%)
✅ LoRA 어댑터 저장 완료 → ./my_lora_adapter   (3.2MB)
```
`1.finetune/1.1_train.py`가 저장하는 전체 모델은 약 **257MB** — 같은 걸 배우는데 LoRA 어댑터는
**약 1/80 크기**다.

## 관전 포인트
- **`target_modules`가 핵심** — `LoraConfig(target_modules=["q_lin", "k_lin", "v_lin"])`처럼
  "어느 레이어 옆에 어댑터를 붙일지"를 모델 아키텍처에 맞게 지정해야 한다. 이름은 모델마다
  다르다(distilbert는 `q_lin`/`k_lin`/`v_lin`, Llama류는 보통 `q_proj`/`k_proj`/`v_proj`).
- **`r`(랭크)이 표현력과 크기의 트레이드오프** — 여기선 8을 썼다. 크게 잡을수록(예: 64) 더 복잡한
  패턴을 학습할 수 있지만 어댑터 크기와 연산량도 커진다.
- **원본 모델은 전혀 안 바뀐다** — 어댑터만 따로 저장되므로, 같은 원본 모델에 용도별 어댑터를
  여러 개 만들어두고 상황에 따라 갈아끼울 수 있다(전체 모델을 용도마다 복제 안 해도 됨).
- 정확도는 `1.finetune`와 마찬가지로 낮다(토이 데이터 8개뿐이라 구조 학습용) — 실전에서는
  최소 수백 건 이상의 데이터가 필요하다.
- **QLoRA(4bit 양자화 + LoRA)는 이 저장소 환경(CPU-only)에서 다루지 않는다** — `bitsandbytes`의
  4bit 양자화는 사실상 GPU 전용이다. GPU가 있다면 `BitsAndBytesConfig(load_in_4bit=True)`로
  모델을 로드한 뒤 이 파일의 `LoraConfig`를 그대로 적용하면 QLoRA가 된다(코드 구조는 동일).

## 다음 단계
- 전체 파인튜닝과 다시 비교 → [`../1.finetune/`](../1.finetune/)
- 이미 있는 경량화 기법(양자화·프루닝 등)과 함께 → [`../2.compression/`](../2.compression/)
