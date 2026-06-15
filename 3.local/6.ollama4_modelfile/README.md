# 6.ollama4_modelfile — Ollama 모델 커스터마이즈 (Modelfile)

앞선 `6.ollama1~3` 은 **모델을 그대로 호출**하는 방법이었습니다.
여기서는 **모델 자체를 내 입맛대로 바꾸는** 가장 가벼운 튜닝, **Modelfile** 을 다룹니다.

> **이게 파인튜닝인가요?** 아닙니다. 가중치를 다시 학습하는 [`../2.mymodel/1.finetune`](../2.mymodel) 과 달리,
> Modelfile 은 **베이스 모델 위에 "역할(SYSTEM) + 추론옵션(PARAMETER)" 설정만 얹는** 방식입니다.
> GPU·데이터·학습시간이 **0** 이고 즉시 만들어지지만, 동작은 확 달라집니다.
> "내 데이터로 학습"이 필요하면 → `2.mymodel`, "성격/형식만 고정"이면 → 여기.

## Modelfile 3줄 핵심

```dockerfile
FROM qwen3.5:4b               # ① 어떤 베이스 모델 위에 만들지
PARAMETER temperature 0.2     # ② 추론 옵션을 모델에 내장 (매번 안 줘도 됨)
SYSTEM """당신은 한국어 비서…"""  # ③ 항상 적용될 역할/규칙
```

생성·실행은 단 두 줄:

```bash
ollama create qwen-korean -f Modelfile.korean   # 만들기
ollama run    qwen-korean                        # 쓰기
```

## 파일

| 파일 | 내용 |
|---|---|
| `Modelfile.korean` | 베이스(qwen3.5:4b)를 **한국어 비서**로 — SYSTEM + PARAMETER 기본형 |
| `Modelfile.reasoning` | gemma4:e4b 를 **`<think>`/`<answer>` 형식**으로 출력하게 고정 |
| `build.sh` | 위 두 Modelfile 을 `ollama create` 로 한 번에 빌드 |
| `1.create_run.py` | Modelfile **파일 없이 파이썬 SDK** 로 커스텀 모델 생성+실행 |
| `2.compare.py` | **베이스 vs 커스텀** — 영어로 물어도 커스텀은 한국어로 (튜닝 효과 체감) |
| `3.params.py` | `temperature` 만 바꾼 두 모델로 **파라미터 영향** 비교 |
| `4.reasoning_parse.py` | `<think>`/`<answer>` 태그를 **정규식으로 분리**해 활용 |

## CLI vs SDK — 같은 일, 두 방법

| | CLI (`Modelfile` 파일) | 파이썬 SDK (`ollama.create`) |
|---|---|---|
| `FROM qwen3.5:4b` | 파일에 작성 | `from_="qwen3.5:4b"` |
| `PARAMETER temperature 0.2` | 파일에 작성 | `parameters={"temperature": 0.2}` |
| `SYSTEM """…"""` | 파일에 작성 | `system="…"` |
| 만들기 | `ollama create 이름 -f Modelfile` | `ollama.create(model="이름", …)` |

→ 팀에 공유·버전관리할 땐 **Modelfile**, 앱 안에서 동적으로 만들 땐 **SDK**.

## 실행

```bash
pip install ollama
ollama pull qwen3.5:4b            # 한국어/파라미터 예제 베이스
ollama pull gemma4:e4b           # reasoning(<think>/<answer>) 예제 베이스

bash build.sh                     # 커스텀 모델 2개 생성
python 2.compare.py               # 효과 비교
```

## 커스텀 모델 관리

```bash
ollama list                       # qwen-korean / gemma4-korean 확인
ollama show qwen-korean --modelfile   # 어떤 설정으로 만들어졌는지 보기
ollama rm   qwen-korean gemma4-korean # 삭제 (설정만 지움, 베이스는 남음)
```

## 자주 쓰는 PARAMETER

| 파라미터 | 의미 | 보통 값 |
|---|---|---|
| `temperature` | 무작위성 — 낮을수록 일관, 높을수록 창의 | 0.1 ~ 1.0 |
| `num_ctx` | 컨텍스트 길이(토큰) — 길수록 많이 기억, 메모리↑ | 2048 ~ 8192 |
| `top_p` | 누적확률 샘플링 범위 | 0.9 |
| `repeat_penalty` | 같은 말 반복 억제 | 1.1 |
| `stop` | 생성을 멈출 문자열 | `"<|im_end|>"` 등 |

## 핵심 정리
- **Modelfile = 학습 없는 튜닝.** SYSTEM(역할) + PARAMETER(옵션)만 얹어 즉시 "나만의 모델".
- `ollama create … -f Modelfile` 로 만들면 이후 호출 시 **system/옵션을 매번 안 붙여도** 적용됨.
- 진짜 가중치 학습이 필요하면 → [`../2.mymodel`](../2.mymodel) (파인튜닝/경량화).
