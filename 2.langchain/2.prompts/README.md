# 프롬프트 작성 (Prompts)

LangChain의 **프롬프트(LLM 에 보낼 입력)를 만드는** 도구들에 집중한 폴더입니다.
출력 파싱, 체이닝, 응용 태스크, 멀티모달은 별도 폴더로 분리되었습니다 (아래 [관련 폴더](#관련-폴더) 참고).

## 폴더 구조

```
2.prompts/
├── 0.legacy(instruct)/     ← 옛 PromptTemplate / Instruct 모델 버전 (비교 학습용)
├── 1.basic/                ← ChatPromptTemplate 기본 사용
├── 2.chat_templates/       ← chat 템플릿 디테일 (system/user 역할, 메시지 객체 형식 비교)
├── 3.fewshot/              ← Few-Shot 프롬프팅 (예제 기반)
├── 4.advanced/             ← 고급 프롬프트 패턴 (MessagesPlaceholder / partial / composition)
└── README.md
```

> **방침**
> - 메인 폴더들에는 **현재 표준인 chat 모델(`ChatOpenAI` + `gpt-4o-mini`)** 기반 예제만 둡니다.
> - `0.legacy(instruct)/` 에는 옛 `OpenAI` + `gpt-3.5-turbo-instruct` 기반 예제 보존.
> - 폴더 번호 = 파일 번호 prefix 가 일치합니다. (예: `3.fewshot/` 안의 파일은 `3.x_...py`)

## 학습 흐름

```
1.basic            ─ ChatPromptTemplate 기본 (세 가지 메시지 입력 형태)
        ↓
2.chat_templates   ─ system/user 역할 분리, 메시지 객체 형식 비교
        ↓
3.fewshot          ─ 예제 기반 프롬프팅으로 출력 형식·스타일 강제
        ↓
4.advanced         ─ 실전 패턴 (대화 이력 슬롯, 부분 채우기, 합성)
```

## 핵심 개념

### PromptTemplate vs ChatPromptTemplate
- **PromptTemplate**: 단일 문자열 (legacy completion 모델용)
- **ChatPromptTemplate**: system/user/assistant 메시지 리스트 (chat 모델, 현재 표준)

### ChatPromptTemplate 메시지 입력 세 가지 형태
| 형태 | 문법 | 변수 치환 | 용도 |
|------|------|---------|------|
| (1) 튜플 단축형 | `("system", "...{var}...")` | ✅ | 권장 / 짧고 가독성 좋음 |
| (2) 메시지 템플릿 객체 | `SystemMessagePromptTemplate.from_template(...)` | ✅ | (1)의 내부 정식 형태 |
| (3) 일반 메시지 객체 | `SystemMessage(content="고정 문장")` | ❌ | 변수 없을 때만 |

→ 자세한 비교는 `1.basic/1.1_template_chat.py` 주석 참고.

## 폴더별 상세

### `1.basic/` — ChatPromptTemplate 기본
| 파일 | 설명 |
|------|------|
| `1.1_template_chat.py` | `ChatPromptTemplate` 기본 — 세 가지 메시지 입력 형태 모두 시연 |
| `1.2_template_invoke_chat.py` | `ChatOpenAI.invoke()` 호출 / `AIMessage.content` 로 결과 꺼내기 |
| `1.3_template_invoke_userinput_chat.py` | 사용자 입력 받아 chat 호출 (대화형 CLI) |
| `1.4_template_postprocess_chat.py` | `StrOutputParser`, `CommaSeparatedListOutputParser` 로 출력 가공 |

### `2.chat_templates/` — chat 템플릿 디테일
| 파일 | 설명 |
|------|------|
| `2.1_template_chat.py` | system/user 역할 분리 (gpt-4o 사용) |
| `2.2_template_chat_chaining.py` | `SystemMessagePromptTemplate.from_template` 명시적 체이닝 |

### `3.fewshot/` — Few-Shot 프롬프팅
| 파일 | 설명 |
|------|------|
| `3.1_fewshot_chat.py` | `FewShotPromptTemplate` — 예제들을 큰 문자열로 합쳐 user 메시지에 박기 |
| `3.2_fewshot_messages_chat.py` | `FewShotChatMessagePromptTemplate` — 예제를 Human/AI 메시지 쌍으로 펼치기 (**chat-native, 권장**) |

**언제 쓰나?**
- ✅ 출력 형식을 글로 설명하기 까다로울 때 (예제로 보여주는 게 빠름)
- ✅ 모호한 분류 기준(긍정/부정/중립) 을 예시로 고정하고 싶을 때
- ✅ 회사 내부 톤/스타일 강제
- ❌ 모델이 이미 잘하는 작업 (예: 한→영 번역) — 그냥 시키면 됨

### `4.advanced/` — 고급 프롬프트 패턴
| 파일 | 한 줄 요약 | 주요 용도 |
|------|-----------|---------|
| `4.1_messages_placeholder_chat.py` | 대화 이력 끼울 **슬롯** 만들기 | 멀티턴 챗봇, Memory/Agent 의 다리 |
| `4.2_partial_prompts_chat.py` | 프롬프트 변수 **미리 채우기** | 같은 템플릿으로 여러 어시스턴트, 동적 값(시각 등) 주입 |
| `4.3_prompt_composition_chat.py` | 프롬프트 조각 **`+` 로 합치기** | 페르소나/형식/입력 모듈화 |

### `0.legacy(instruct)/` — 옛 instruct 버전 (비교용)
| 파일 | 짝지 |
|------|------|
| `1.1_template_instruct.py` ~ `1.4_template_postprocess_instruct.py` | ↔ `1.basic/1.x_*_chat.py` |

> 옛날 `4.x_*_instruct.py` (tasks 짝지) 와 `2.x_*_instruct.py` (chaining 짝지) 는 chat 짝지를 따라 각각 [5.tasks/0.legacy](../5.tasks/0.legacy(instruct)/) / [4.chaining/0.legacy](../4.chaining/0.legacy(instruct)/) 로 이동했습니다.

---

## 관련 폴더 (이전 2.prompts 에서 분리된 주제들)

| 폴더 | 분리된 이유 |
|------|------------|
| [`../3.structured_output/`](../3.structured_output/) | **출력 파싱**은 입력 작성과 정반대 영역 |
| [`../4.chaining/`](../4.chaining/) | **체이닝**은 별개 주제 (2.prompts/2.chaining 의 LCEL intro 도 여기로 흡수됨) |
| [`../5.tasks/`](../5.tasks/) | **응용 태스크**(요약/번역/이메일/SQL) 는 체인 예제에 가까움 |
| [`../11.multimodal/`](../11.multimodal/) | **이미지 입력** (선택적/부록) |

## 실행

```bash
pip install langchain langchain-openai python-dotenv

python "1.basic/1.1_template_chat.py"
python "3.fewshot/3.2_fewshot_messages_chat.py"
```
