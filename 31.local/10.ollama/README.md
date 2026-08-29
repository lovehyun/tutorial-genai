# 31.local/10.ollama — Ollama 로 로컬 LLM 돌리기

> **처음이라면 먼저** → [`0.gguf_and_open_weights.md`](0.gguf_and_open_weights.md) — GGUF가 뭔지,
> 오픈 웨이트가 뭔지, Ollama가 내부적으로 뭘 하는지, 그리고 왜 어떤 모델(EXAONE)은 공식
> 버전이 없는지까지 기초 개념을 먼저 정리해뒀다.

Ollama 관련 예제를 한곳에 모았다. **두 종류**로 나뉜다 — 헷갈리지 않게 구분해서 본다.

## ① 호출 방법 (같은 걸 다른 방식으로)
"Ollama 를 **어떻게 부르나**" 를 비교한다. 모델은 예시로 여러 개(mistral·qwen·gemma 등)를 쓸 뿐, **핵심은 호출 방식**이다.

| 폴더 | 방식 |
|------|------|
| [`1.restapi/`](1.restapi/) | REST API 직접 호출 (`/api/chat`) |
| [`2.sdk/`](2.sdk/) | 파이썬 `ollama` SDK |
| [`3.langchain/`](3.langchain/) | LangChain(`ChatOllama`) 로 감싸기 |
| [`4.modelfile/`](4.modelfile/) | Modelfile 로 커스텀 모델 정의(시스템프롬프트·파라미터 고정) |
| [`9.openai_compat/`](9.openai_compat/) | **OpenAI 형태로 호출**(`/v1/chat/completions`) — `1.openai/` 코드가 거의 그대로 로컬에 붙는다 |

## ② 모델별 한국어 활용 (특정 모델로 실제 태스크)
"이 **모델로 무엇을 만드나**" — 한국어에 강한 모델로 실제 NLP 작업을 수행한다.

| 폴더 | 모델 | 태스크 |
|------|------|--------|
| [`5.qwen25/`](5.qwen25/) | Qwen 2.5 (Alibaba) | chat · 감성분석 · 분류 · NER · 요약 · 번역 — 생각 모드 없는 표준 모델 |
| [`6.qwen35/`](6.qwen35/) | Qwen 3.5 (Alibaba) | 생각 모드(thinking) on/off 비교 · tool calling(2.5와 신뢰도 비교) |
| [`7.exaone35/`](7.exaone35/) | EXAONE 3.5 (LG AI) | chat · 추론 · 요약 · structured JSON · 코드어시스트 · streaming · RAG |
| [`8.exaone40/`](8.exaone40/) | EXAONE 4.0 (LG AI) | 생각 모드 · tool calling(3.5엔 없던 기능) — 단, 공식 라이브러리 없어 커뮤니티 GGUF별 동작 차이 실측 |

> **한 줄 요약**: `1~4` = *어떻게 호출하나*(방법), `5~8` = *특정 모델로 무엇을 하나*(활용).
> 그래서 `1~4` 도 예시로 qwen 을 쓸 수 있지만, `5~8` 은 "모델로 한국어 태스크·생각모드·tool calling" 이라 목적이 다르다.
>
> **`5.qwen25` vs `6.qwen35`** — 같은 계열의 세대 차이: **2.5 는 생각 모드가 아예 없는 표준 모델**,
> **3.5 는 같은 모델 안에서 생각 모드를 켜고 끌 수 있는 하이브리드**다. tool calling 은 **둘 다 된다** — "생각 모드가
> 있어야 도구 호출이 된다"는 오해가 있는데 사실이 아니다(2.5도 이미 native tool calling 지원). 다만 인자를
> 헛짚는 빈도는 3.5 쪽이 더 낮다 — `6.qwen35`에서 이 차이를 직접 실측해서 비교한다.
>
> **`7.exaone35` vs `8.exaone40`** — 같은 구조의 대비다: **3.5 는 tool calling 자체를 지원 안 함**,
> **4.0 은 생각 모드 + tool calling 을 새로 지원**한다. 다만 Qwen 과 달리 EXAONE 4.0 은 **Ollama 공식
> 라이브러리에 아직 없어서** 커뮤니티 GGUF 품질에 따라 실제 동작이 갈린다(어떤 업로드는 tool calling
> 성공률이 0/3, 어떤 건 3/3) — `8.exaone40`에서 그 차이를 그대로 실측해서 보여준다.

## 🔧 모델 바꾸기 (저사양·재현용)
각 파일 상단의 **`MODEL = "..."` 한 줄만 바꾸면** 다른 모델로 돌아간다. 저사양 PC 에서도 재현되게 **가벼운 것 위주** 권장:

| 모델 | 크기(대략) | 특징 | pull |
|------|-----------|------|------|
| **qwen2.5:0.5b** | ~0.4GB | 초경량, 한국어 OK | `ollama pull qwen2.5:0.5b` |
| **qwen2.5:1.5b** ⭐기본 | ~1.0GB | 가볍고 한국어 무난 | `ollama pull qwen2.5:1.5b` |
| **llama3.2:1b** | ~1.3GB | 다국어, 아주 가벼움 | `ollama pull llama3.2:1b` |
| **gemma2:2b** | ~1.6GB | 구글, 균형 | `ollama pull gemma2:2b` |
| **llama3.2:3b** | ~2.0GB | 조금 더 똑똑 | `ollama pull llama3.2:3b` |
| **phi3:mini** | ~2.2GB | 영어 강함 | `ollama pull phi3:mini` |
| mistral(7b) | ~4.1GB | 중간급(3.langchain 기본) | `ollama pull mistral` |

- **8GB RAM 이하**면 `qwen2.5:0.5b`~`llama3.2:1b` 부터. 한국어 태스크는 `qwen2.5` 계열이 무난.
- 이 레포 예제는 **전부 `qwen2.5:1.5b` 로 통일**(저사양 재현). 각 파일 `MODEL`/`model=` 옆 주석에 교체 후보를 적어뒀다.

### 📥 다운로드는 어디서? (HuggingFace 아님 — Ollama 레지스트리)
`ollama pull` 은 **Ollama 공식 레지스트리**에서 받는다. HuggingFace 가 아니다.

| 무엇 | 어디 / 방법 |
|------|-------------|
| 모델 검색·둘러보기 | **<https://ollama.com/library>** (인기/최신 정렬, vision·tools·thinking 필터) |
| 특정 모델의 **정확한 태그·용량** | `https://ollama.com/library/<모델>/tags` (예: [qwen2.5/tags](https://ollama.com/library/qwen2.5/tags), [gemma2/tags](https://ollama.com/library/gemma2/tags)) |
| 받기 | `ollama pull <모델>:<태그>` (예: `ollama pull qwen2.5:1.5b`) |
| 로컬에 받은 것 확인 | `ollama list` · 정보: `ollama show <모델>` |
| **HuggingFace 에서 직접** | `ollama pull hf.co/<사용자>/<저장소>` (GGUF). 원본 가중치는 대개 HF 에 먼저 올라오고 Ollama 가 패키징 |

> ※ 태그는 시점 따라 바뀐다. **2026-07 현재** qwen 은 `qwen2.5`·`qwen3`·`qwen3.5`, gemma 는 `gemma2`·`gemma4` 세대까지 있다.
> 예제 기본은 가장 가벼운 축인 `qwen2.5:1.5b`(~1GB). 최신·정확한 크기는 위 tags 페이지에서 확인.

## 사전 준비
```bash
# Ollama 설치 후 모델 pull (기본)
ollama pull qwen2.5:1.5b
# 저사양이면:  ollama pull qwen2.5:0.5b  또는  ollama pull llama3.2:1b
pip install ollama langchain-ollama       # 2.sdk / 3.langchain 용
```
- 다른 로컬 런타임: `../6.gpt4all/` · `../1.transformers/` · `../3.huggingface/`
