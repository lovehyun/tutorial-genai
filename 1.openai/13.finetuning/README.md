# 13.finetuning — OpenAI 모델 파인튜닝 (Fine-tuning API)

내 데이터로 `gpt-4o-mini` 같은 모델을 학습시켜 **`ft:...` 전용 모델**을 만든다.

## ⚠️ 가장 먼저 — 파인튜닝은 '지식 주입'이 아니다
| 목적 | 써야 할 것 |
|------|-----------|
| 최신/사내 **정보**를 알게 하기 | **RAG** (`7.rag`) — 파인튜닝 ❌ |
| 빠른 동작 변경·실험 | **프롬프트/Few-shot** |
| **스타일·형식·톤·행동을 일관되게** 굳히기, **긴 프롬프트 줄이기**, 엣지케이스 굳히기 | **파인튜닝** ✅ |

> "모델이 우리 회사 규정을 모른다" → 파인튜닝으로 규정을 외우게 하는 건 비추천(RAG가 맞음).
> "매번 똑같은 톤/형식으로 답하게 하고 싶다, 프롬프트가 너무 길다" → 파인튜닝이 적합.

## 실전 use-case (파인튜닝이 값어치를 하는 곳)

핵심은 '지식'이 아니라 **행동·형식·분류를 대량으로 일관·저비용·저지연**으로 만드는 것:

| use-case | 무엇 | 왜 파인튜닝 |
|----------|------|-------------|
| **분류** (가장 흔함) | 인텐트/티켓 라우팅, 감정·주제 태깅, 커스텀 모더레이션 | 작은 ft 모델이 큰 모델 프롬프팅보다 **싸고 빠르고 정확**(대량일수록 이득) |
| **구조화 출력** | 지저분한 텍스트 → 고정 JSON 추출(인보이스/이력서/계약서) | 복잡한 포맷일수록 프롬프트보다 안정적 |
| **톤·페르소나** | 고객지원 표준 톤, 브랜드 보이스, 캐릭터 챗봇 | 매번 길게 지시 안 해도 일관 재현 |
| **프롬프트 압축** | 거대 system+few-shot 동작을 모델에 구워 넣기 | 프롬프트가 짧아져 **토큰·지연 절감**(스케일) |
| **디스틸레이션** | gpt-4o 출력/사람 라벨로 mini 학습 | **mini 비용에 4o급 품질**(좁은 작업) |
| **도메인 컨벤션** | 사내 스키마 SQL, 특정 코딩 스타일, 법률/의료 표현 형식 | 새 지식이 아니라 '표현 방식'을 굳힘 |
| **도구 호출·엣지케이스** | 고정 툴셋 함수·인자 정확도, 일관된 거부/안전 행동 | 들쭉날쭉한 행동을 고정 |

> 구체 예: 고객센터 자동응답 · 티켓 자동 라우팅 · 문서 구조화 추출 파이프라인 ·
> 사내 SQL/코드 어시스턴트 · 커스텀 모더레이션 분류기 · 대량 데이터 라벨링 자동화.

### 대표 use-case 예제 (코드, 데이터→학습→사용 자체 완결)
| 폴더 | use-case | 데이터 형태 |
|------|----------|-------------|
| [`usecase_classify/`](usecase_classify/) | **분류**(티켓 라우팅/인텐트) | assistant = 라벨 한 단어 |
| [`usecase_extract/`](usecase_extract/) | **구조화 추출**(텍스트→JSON) | assistant = 고정 키 JSON |

**안티패턴**: 최신/사내 정보 → RAG · 자주 바뀌는 규칙 → 프롬프트 · 데이터 적거나 비일관 → 효과 미미.

**현실적 순서**: 프롬프트 → RAG → (그래도 부족하면) 파인튜닝. 모델·구조화출력·RAG가 좋아져
파인튜닝은 보통 **스케일에서 비용·일관성을 최적화하는 마지막 수**다.

## 흐름
```
① 학습 데이터(JSONL) 작성  — chat 형식, 최소 10개·권장 50~100+
② files.create(purpose='fine-tune') 로 업로드
③ fine_tuning.jobs.create(training_file, model='gpt-4o-mini-2024-07-18')
④ jobs.retrieve 로 상태 폴링 (running → succeeded)  ← 수 분~수십 분, 과금됨
⑤ 결과 'ft:gpt-4o-mini-...' 모델을 chat.completions 에서 그대로 사용
```

## 파일 (기본 → 고도화 → 실용)
| 파일 | 내용 |
|------|------|
| `1.prepare_data.py` | **학습 데이터(train.jsonl) 만들기** — 형식/요건 (가장 중요) |
| `2.create_job.py` | 업로드 → 잡 생성 → 폴링 → `ft:...` 모델 ID |
| `3.use_finetuned.py` | **실용** — ft 모델 사용 + 베이스 모델과 톤 비교 |

## 실행
```bash
cd 1.openai/13.finetuning
pip install openai python-dotenv
# 1.openai/.env 에 OPENAI_API_KEY

python 1.prepare_data.py                       # train.jsonl 생성
python 2.create_job.py                         # ⚠️ 과금·시간 소요 → ft 모델 ID 출력
FT_MODEL=ft:gpt-4o-mini-...:... python 3.use_finetuned.py   # 결과 사용/비교
# PowerShell: $env:FT_MODEL="ft:..."; python 3.use_finetuned.py
```

## 데이터 가이드
- 형식: 한 줄 = `{"messages":[{"role":"system",...},{"role":"user",...},{"role":"assistant",...}]}`
- `assistant` 응답 = **모델이 따라 할 정답 스타일**. 일관될수록 결과가 좋다.
- 최소 10개, 보통 50~100+ 부터 효과. 검증셋(`validation_file`)·에폭 등은 선택 하이퍼파라미터.

## 비용·주의
- 학습 토큰만큼 과금, 완료까지 수 분 이상. 데모도 실제로 돈/시간이 든다.
- 베이스 모델은 **파인튜닝 가능 스냅샷**이어야 한다(예: `gpt-4o-mini-2024-07-18`).

## 다른 종류의 파인튜닝 (참고)
이 폴더는 **OpenAI API(클라우드)** 파인튜닝이다. **로컬/오픈소스** 파인튜닝은:
- `12.study/2.bert/` — BERT 분류 파인튜닝 (HuggingFace Trainer)
- `3.local/2.mymodel/`, `3.local/3.huggingface/` — 로컬 모델 학습
- `0.docs/05_genai_advanced/14_finetuning_lora.md` — LoRA 등 개념
