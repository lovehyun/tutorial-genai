# LCEL 체이닝 (LangChain Expression Language)

LangChain 의 **LCEL 파이프(`|`) 문법**으로 체인을 조립하는 다양한 패턴을 학습합니다.

## 폴더 구조 (역할별 분리 + 논리 순서)

```
4.chaining/
├── 0.legacy(instruct)/        ← 비교 학습용 legacy completion 버전
├── 1.basics/                  ← PromptTemplate + LLM 기본 체인
├── 2.runnablelambda/          ← RunnableLambda — 커스텀 함수를 체인에 끼우기
├── 3.runnablepassthrough/     ← RunnablePassthrough — 입력값을 그대로 흘려보내며 누적
├── 4.runnableparallel/        ← RunnableParallel — 여러 체인 병렬 실행
├── 5.runnablemap/             ← RunnableMap — 필드별로 다른 체인 매핑
├── 6.runnablebranch/          ← RunnableBranch — 조건에 따라 다른 체인으로 라우팅
├── 7.output_format/           ← OutputParser — 결과를 list / JSON 등 형식으로 변환
├── 8.execution_modes/         ← .invoke / .stream / .batch / .astream 호출 방식
├── 9.config_retry/            ← .with_config() / .with_retry() 메타 설정과 자동 재시도
├── 10.production/             ← 프로덕션 패턴 (fallback / timeout / 수동 재시도)
└── README.md                  ← 이 파일
```

> **방침**
> - 메인 폴더들에는 **현재 표준인 chat 모델(`ChatOpenAI` + `gpt-4o-mini`)** 기반 예제만 둡니다.
> - `0.legacy(instruct)/` 에는 옛 `OpenAI` + `gpt-3.5-turbo-instruct` 기반 예제 보존.
> - 폴더 번호 = 파일 번호 prefix 가 일치합니다. (예: `6.runnablebranch/` 안의 파일은 `6.x_...py`)

## 전체 학습 흐름

```
1.basics              ─ 가장 단순한 체인 (prompt | llm | parser)
        ↓
2.runnablelambda      ─ 체인 중간에 함수 끼우기
        ↓
3.runnablepassthrough ─ 입력 그대로 통과시키며 상태 누적
        ↓
4.runnableparallel    ─ 여러 체인 동시에 실행
        ↓
5.runnablemap         ─ 필드별로 다른 체인 매핑
        ↓
6.runnablebranch      ─ 조건 분기 (라우터)
        ↓
7.output_format       ─ 결과 형식 변환 (CSV/JSON)
        ↓
8.execution_modes     ─ invoke 외에 stream / batch / astream
        ↓
9.config_retry        ─ 메타데이터 부착 + 자동 재시도
        ↓
10.production         ─ 실전 fallback + timeout 패턴
```

## 핵심 Runnable 한눈에

| Runnable | 한 줄 요약 | 폴더 |
|----------|----------|------|
| `RunnableLambda` | **임의의 파이썬 함수**를 체인 단계로 끼움 | `2.` |
| `RunnablePassthrough` | 입력을 그대로 흘려보냄 (`.assign()` 으로 키 추가) | `3.` |
| `RunnableParallel` | 같은 입력을 **여러 체인에 병렬 분배** | `4.` |
| `RunnableMap` | 입력 dict 의 키별로 다른 처리 (`RunnableParallel` 의 변형) | `5.` |
| `RunnableBranch` | **조건에 따라** 다른 체인으로 라우팅 | `6.` |

## 폴더별 상세

### `1.basics/` — 가장 단순한 체인
| 파일 | 설명 |
|------|------|
| `1.2_prompttemplate_chat.py` | `prompt | llm | StrOutputParser()` — 가장 기본형 |
| `1.3_template_chaining_chat.py` | LCEL 파이프(\|) 기본 (2.prompts 에서 이동) |
| `1.4_template_chaining_lambda_chat.py` | RunnableLambda intro (2.prompts 에서 이동) |
| `1.5_template_chaining_customfunc_chat.py` | 커스텀 함수 체이닝 (2.prompts 에서 이동) |

### `2.runnablelambda/` — 함수를 체인에 끼우기
| 파일 | 설명 |
|------|------|
| `2.2_runnablelambda2_chat.py` | `RunnableLambda` 다단계 파이프라인 |
| `2.3_runnablelambda3_chat_allprocess.py` | `RunnableLambda` + `RunnableParallel` 조합 |
| `2.4_runnablelambda4_chat_scoring.py` | JSON 스코어링/Top-N 선택 |

### `3.runnablepassthrough/` — 상태 누적
| 파일 | 설명 |
|------|------|
| `3.2_runnablepassthrough2_chat.py` | `RunnablePassthrough.assign()` 으로 키 추가 |
| `3.3_runnablepassthrough3_3chains.py` | 3-chain 으로 상태 누적 |

### `4.runnableparallel/` — 병렬 체인
| 파일 | 설명 |
|------|------|
| `4.1_runnableparallel_chat.py` | `RunnableParallel` + `with_fallbacks` 결합 |

### `5.runnablemap/` — 필드 매핑
| 파일 | 설명 |
|------|------|
| `5.1_runnablemap_chat.py` | `RunnableMap` + `.batch()` + `RunnableConfig` |

### `6.runnablebranch/` — 조건 분기 (NEW)
| 파일 | 설명 |
|------|------|
| `6.1_runnablebranch_chat.py` | 질문 유형에 따라 코드/요리/일반 체인으로 라우팅 |

```python
branch = RunnableBranch(
    (lambda x: "코드" in x["question"], code_chain),
    (lambda x: "요리" in x["question"], cooking_chain),
    general_chain,    # default
)
```

### `7.output_format/` — 결과 형식 변환
| 파일 | 설명 |
|------|------|
| `7.1_outputformat_chat.py` | `CommaSeparatedListOutputParser`, `JsonOutputParser` |

> **참고**: 본격적인 구조화 출력(PydanticOutputParser, `.with_structured_output()` 등) 은 [`../3.structured_output/`](../3.structured_output/) 에서 다룹니다.

### `8.execution_modes/` — 호출 방식 (NEW)
| 파일 | 설명 |
|------|------|
| `8.1_invoke_stream_batch.py` | `.invoke()` vs `.stream()` vs `.batch()` 비교. 같은 체인을 세 방식으로 호출 |
| `8.2_streaming.py` | 동기 `.stream()`, 비동기 `.astream()`, 이벤트 `.astream_events()` 스트리밍 심화 |

| 호출 | 용도 |
|------|------|
| `.invoke(input)` | 입력 하나 → 출력 하나 (가장 기본) |
| `.stream(input)` | 토큰 단위로 받기 (챗봇 UX) |
| `.batch([inputs])` | 여러 입력 동시 처리 (병렬, 빠름) |
| `.astream(input)` | 비동기 토큰 스트림 (FastAPI 등) |
| `.astream_events(input)` | 체인 내부 step 이벤트 추적 (디버깅) |

### `9.config_retry/` — 메타 설정 + 자동 재시도 (NEW)
| 파일 | 설명 |
|------|------|
| `9.1_with_config_retry.py` | `.with_retry()` 자동 재시도 / `.with_config()` tags/metadata 부착 |

```python
chain.with_retry(stop_after_attempt=3, wait_exponential_jitter=True)
chain.with_config({"tags": ["production"], "run_name": "MyChain"})
```

→ 수동 `try/except + time.sleep` 짤 필요 없음. LangSmith 같은 trace 도구와도 자동 연동.

### `10.production/` — 실전 프로덕션 패턴
| 파일 | 설명 |
|------|------|
| `10.1_production_fallback_retry.py` | async retry / timeout / fallback 체인 (수동 패턴) |

> **참고**: 수동 retry 보다 `9.config_retry/` 의 `.with_retry()` 가 더 깔끔합니다. 이 파일은 "더 세밀한 컨트롤이 필요한 경우" 패턴.

### `0.legacy(instruct)/` — 옛 instruct 버전
| 파일 | 짝지 |
|------|------|
| `1.1_prompttemplate_instruct.py` | ↔ `1.basics/1.2_prompttemplate_chat.py` |
| `1.3_template_chaining_instruct.py` | ↔ `1.basics/1.3_template_chaining_chat.py` (2.prompts 에서 이동) |
| `1.4_template_chaining_lambda_instruct.py` | ↔ `1.basics/1.4_template_chaining_lambda_chat.py` (2.prompts 에서 이동) |
| `1.5_template_chaining_customfunc_instruct.py` | ↔ `1.basics/1.5_template_chaining_customfunc_chat.py` (2.prompts 에서 이동) |
| `2.1_runnablelambda_instruct.py` | ↔ `2.runnablelambda/2.2_*_chat.py` |
| `3.1_runnablepassthrough_instruct.py` | ↔ `3.runnablepassthrough/3.2_*_chat.py` |

## 어떤 순서로 따라가야 하나?

1. **새로 배우는 사람** → `1.basics/` → `2.runnablelambda/` → `3.runnablepassthrough/` 까지 차근차근
2. **여러 체인 조합** → `4.runnableparallel/` → `5.runnablemap/` → `6.runnablebranch/`
3. **출력 형식 / 실행 방식** → `7.output_format/` → `8.execution_modes/`
4. **실전 운영** → `9.config_retry/` → `10.production/`

## 실행

```bash
pip install langchain langchain-openai python-dotenv

python "6.runnablebranch/6.1_runnablebranch_chat.py"
python "8.execution_modes/8.1_invoke_stream_batch.py"
```

> 폴더 / 파일명에 괄호나 점이 있으면 shell 에서 따옴표로 감싸 실행하세요.
