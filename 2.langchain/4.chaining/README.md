# LCEL 체이닝 (LangChain Expression Language)

LangChain 의 **LCEL 파이프(`|`) 문법**으로 체인을 조립하는 다양한 패턴을 학습합니다.

각 폴더는 한 가지 Runnable / 개념에 집중하며, **핵심 → 디버깅 → 응용** 순서의 예제 3종을 제공합니다.

## 폴더 구조

```
4.chaining/
├── 0.legacy(instruct)/        ← 비교용 옛 completion(instruct) 버전
├── 1.basics/                  ← prompt | llm | parser 기본 체인
├── 2.runnablelambda/          ← RunnableLambda — 함수를 체인에 끼우기
├── 3.runnablepassthrough/     ← RunnablePassthrough — 입력 유지하며 키 누적
├── 4.runnableparallel/        ← RunnableParallel — 여러 체인 동시 실행
├── 5.runnablebranch/          ← RunnableBranch — 조건 분기 (라우터)
├── 6.runnablemap/             ← RunnableMap — 입력 dict 재구성 (RunnableParallel 별칭)
├── 7.output_format/           ← OutputParser — list / JSON 변환
├── 8.execution_modes/         ← .invoke / .stream / .batch / .astream
├── 9.config_retry/            ← .with_retry() / .with_config()
├── 10.production/             ← 실전 패턴 (fallback / cache / async)
└── README.md
```

> **방침**
> - 모든 예제는 **chat 모델**(`ChatOpenAI` + `gpt-4o-mini`) 기반.
> - 각 파일은 **라이브 코딩 가능한 길이**(~30~50줄)로 핵심 한 가지에 집중.
> - 폴더 번호 = 파일 번호 prefix. (예: `5.runnablebranch/` 안의 파일은 `5.x_...py`)
> - `0.legacy(instruct)/` 만 옛 `OpenAI` + `gpt-3.5-turbo-instruct` 버전 보존.

## 학습 순서

```
1.basics              ─ 가장 단순한 체인 (prompt | llm | parser)
        ↓
2.runnablelambda      ─ 체인 중간에 함수 끼우기
        ↓
3.runnablepassthrough ─ 입력 유지하며 dict에 키 누적
        ↓
4.runnableparallel    ─ 여러 체인 동시에 실행
        ↓
5.runnablebranch      ─ 조건 분기 (라우터)
        ↓
6.runnablemap         ─ 입력 dict 를 재구성 (RunnableParallel 별칭이므로 보충 개념)
        ↓
7.output_format       ─ CSV / JSON 형식 변환
        ↓
8.execution_modes     ─ stream / batch / astream
        ↓
9.config_retry        ─ 메타데이터 + 자동 재시도
        ↓
10.production         ─ fallback / 캐시 / async
```

## 핵심 Runnable 한눈에

| Runnable | 한 줄 요약 | 폴더 |
|----------|----------|------|
| `RunnableLambda` | **임의의 파이썬 함수**를 체인 단계로 끼움 | `2.` |
| `RunnablePassthrough` | 입력 그대로 흘리며 `.assign()` 으로 키 추가 | `3.` |
| `RunnableParallel` | 같은 입력을 **여러 체인에 병렬 분배** | `4.` |
| `RunnableBranch` | **조건에 따라** 다른 체인으로 라우팅 | `5.` |
| `RunnableMap` | `RunnableParallel` 의 별칭. 입력 dict 재구성 의도일 때 사용 | `6.` |

---

## 폴더별 예제 상세

### `1.basics/` — 가장 단순한 체인

| 파일 | 핵심 내용 |
|------|------|
| `1.1_basic_chain.py` | **가장 기본** — `prompt \| llm \| StrOutputParser()` 한 줄 |
| `1.2_basic_chain_with_lambda.py` | 끝에 `RunnableLambda` 를 붙여 결과를 `{"response": ...}` dict 로 후처리 |

---

### `2.runnablelambda/` — 함수를 체인에 끼우기

| 파일 | 핵심 내용 |
|------|------|
| `2.1_runnablelambda_basic.py` | **핵심** — 회사명(str) → `{"company_name": ...}`(dict) 변환해서 다음 체인에 연결 |
| `2.2_runnablelambda_debug.py` | **디버깅** — 중간에 `print` 만 하는 `RunnableLambda` 를 끼워 값 흐름 관찰 |
| `2.3_runnablelambda_cleanup.py` | **응용** — LLM 출력의 따옴표/prefix(`"회사명: ..."`) 같은 잡음 정리 |
| `2.4_runnablelambda_pii_mask.py` | **실무** — LLM 호출 전에 이메일·전화번호 자동 마스킹 (PII 보호) |

---

### `3.runnablepassthrough/` — 상태 누적

| 파일 | 핵심 내용 |
|------|------|
| `3.1_passthrough_basic.py` | **핵심** — `.assign()` 한 번. 입력 `{"product": ...}` 유지하며 `company_name` 추가 |
| `3.2_passthrough_chain.py` | `.assign()` 을 **두 번 이어서** 누적: product → +company_name → +catch_phrase |
| `3.3_passthrough_pick.py` | **응용** — `.pick(["a","b"])` 로 누적된 dict 에서 필요한 키만 추출 (list/str 차이 포함) |
| `3.4_passthrough_api_response.py` | **실무** — QA API 응답 패턴: 질문 + 답변 + model + timestamp 한 dict 로 묶기 |

---

### `4.runnableparallel/` — 병렬 실행

| 파일 | 핵심 내용 |
|------|------|
| `4.1_parallel_basic.py` | **핵심** — 같은 입력을 KO/JA/FR 3개 번역 체인에 동시 실행 |
| `4.2_parallel_vs_sequential.py` | **시간 비교** — 순차 invoke 3회 vs `RunnableParallel` 1회. 가속비 출력 |
| `4.3_parallel_then_merge.py` | **응용 (map-reduce)** — 병렬 수집(음식/관광지/호텔) → LLM 이 다시 종합 평가 |
| `4.4_parallel_content_marketing.py` | **실무** — 상품 1개 → 광고 문구 / SEO 설명 / 해시태그 동시 생성 (콘텐츠 마케팅 자동화) |

---

### `5.runnablebranch/` — 조건 분기

| 파일 | 핵심 내용 |
|------|------|
| `5.1_branch_basic.py` | **핵심** — 키워드 매칭(`"파이썬"`, `"요리"`)으로 개발자/요리사/일반 체인 라우팅 |
| `5.2_branch_debug.py` | **디버깅** — 각 체인 앞 `RunnableLambda` 로 어느 분기를 탔는지 출력 + "된장찌개 파이썬 레시피" 같은 다중 매칭 함정 |
| `5.3_branch_with_llm_classifier.py` | **응용** — 키워드 한계 극복: **LLM 분류기**가 카테고리 판정 → 그 결과로 분기 |
| `5.4_branch_model_routing.py` | **실무** — 질문 난이도에 따라 gpt-4o-mini / gpt-4o 자동 선택 (비용 최적화) |

```python
# 5.3 핵심 구조
chain = (
    RunnablePassthrough.assign(category=classifier)
    | RunnablePassthrough.assign(answer=RunnableBranch(...))
)
```

---

### `6.runnablemap/` — 입력 dict 재구성 (보충)

> `RunnableMap` 은 `RunnableParallel` 의 별칭입니다. 실무에선 거의 `RunnableParallel` 로 부르므로 보충 개념으로 다룹니다.

| 파일 | 핵심 내용 |
|------|------|
| `6.1_runnablemap_basic.py` | **핵심** — 호출 쪽은 `{"question": ...}`, 체인은 `{"input": ...}` 기대할 때 키 매핑 |
| `6.2_runnablemap_vs_parallel.py` | `RunnableMap is RunnableParallel` — 같은 클래스의 별칭임을 확인 |
| `6.3_runnablemap_combine_fields.py` | **응용** — `last_name+first_name → name`, `current_year-birth_year → age` 처럼 필드 결합·계산 |

---

### `7.output_format/` — 결과 형식 변환

| 파일 | 핵심 내용 |
|------|------|
| `7.1_csv_parser.py` | `CommaSeparatedListOutputParser` — 쉼표 구분 응답 → `list[str]` |
| `7.2_json_parser.py` | `JsonOutputParser` — JSON 응답 → `dict` |

> 본격적인 구조화 출력 (Pydantic, `.with_structured_output()`) 은 [`../3.structured_output/`](../3.structured_output/) 참고.

---

### `8.execution_modes/` — 호출 방식

| 파일 | 핵심 내용 |
|------|------|
| `8.1_invoke_stream_batch.py` | 같은 체인을 `.invoke()` / `.stream()` / `.batch()` 세 방식으로 호출, 소요 시간 비교 |
| `8.2_streaming.py` | `.stream()` (동기) / `.astream()` (비동기) / `.astream_events()` (체인 step 추적) |

| 호출 | 용도 |
|------|------|
| `.invoke(input)` | 입력 1개 → 출력 1개 (가장 기본) |
| `.stream(input)` | 토큰 단위로 받기 (챗봇 UX) |
| `.batch([inputs])` | 여러 입력 동시 처리 (병렬) |
| `.astream(input)` | 비동기 토큰 스트림 (FastAPI 등) |
| `.astream_events(input)` | 체인 내부 step 이벤트 추적 (디버깅) |

---

### `9.config_retry/` — 메타 설정 + 자동 재시도

| 파일 | 핵심 내용 |
|------|------|
| `9.1_with_retry.py` | `.with_retry(stop_after_attempt=3, wait_exponential_jitter=True)` — 자동 재시도 |
| `9.2_with_config.py` | `.with_config({"tags": [...], "metadata": {...}, "run_name": ...})` — trace 메타데이터 + 두 메서드 조합 |

→ 수동 `try/except + time.sleep` 짤 필요 없음. LangSmith 같은 trace 도구와도 자동 연동.

---

### `10.production/` — 실전 프로덕션 패턴

| 파일 | 핵심 내용 |
|------|------|
| `10.1_production_fallback_retry.py` | async + 수동 retry + timeout + 다단계 fallback 시나리오 (가장 복잡) |
| `10.2_with_fallbacks.py` | `.with_fallbacks([backup_chain, last_resort])` — 주 체인 실패 시 백업 체인 자동 호출 |
| `10.3_llm_cache.py` | `set_llm_cache(InMemoryCache())` — 동일 입력 재호출 시 LLM 호출 자체 생략 (비용 0) |

> 단순 재시도/태깅은 `9.config_retry/` 빌트인이 더 깔끔합니다. 10번은 더 세밀한 컨트롤이 필요한 경우용.

---

### `0.legacy(instruct)/` — 옛 instruct 버전

`OpenAI` + `gpt-3.5-turbo-instruct` 기반 옛 패턴. 새 프로젝트는 chat 버전만 따라가면 됩니다.

| 파일 | 새 버전과 비교 |
|------|------|
| `1.1_prompttemplate_instruct.py` | ↔ `1.basics/1.1_basic_chain.py` |
| `1.3_template_chaining_instruct.py` | ↔ `1.basics/1.1_basic_chain.py` |
| `1.4_template_chaining_lambda_instruct.py` | ↔ `1.basics/1.2_basic_chain_with_lambda.py` |
| `1.5_template_chaining_customfunc_instruct.py` | ↔ `2.runnablelambda/2.3_runnablelambda_cleanup.py` |
| `2.1_runnablelambda_instruct.py` | ↔ `2.runnablelambda/2.1_runnablelambda_basic.py` |
| `3.1_runnablepassthrough_instruct.py` | ↔ `3.runnablepassthrough/3.1_passthrough_basic.py` |

---

## 어떤 순서로 따라가야 하나?

1. **처음 배우는 사람** → `1.basics/` → `2.runnablelambda/` → `3.runnablepassthrough/` 까지 차근차근
2. **여러 체인 조합** → `4.runnableparallel/` → `5.runnablebranch/` → `6.runnablemap/`
3. **출력 형식 / 실행 방식** → `7.output_format/` → `8.execution_modes/`
4. **실전 운영** → `9.config_retry/` → `10.production/`

각 폴더 안에서는 `x.1` (핵심) → `x.2` (디버깅/비교) → `x.3` (응용) → `x.4` (실무) 순서로 따라가세요.

## 실행

```bash
pip install langchain langchain-openai python-dotenv

python "1.basics/1.1_basic_chain.py"
python "5.runnablebranch/5.3_branch_with_llm_classifier.py"
python "10.production/10.3_llm_cache.py"
```

> 폴더 / 파일명에 괄호나 점이 있으면 shell 에서 따옴표로 감싸 실행하세요.
