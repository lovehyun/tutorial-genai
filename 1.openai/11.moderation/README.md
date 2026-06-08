# 11.moderation — 콘텐츠 안전성 검사 (Moderation API)

입력이 OpenAI 정책(폭력·혐오·자해·성적 등)에 걸리는지 검사하는 **무료** API.
실전에서는 사용자 입력을 LLM 에 보내기 **전에** 걸러내는 안전장치로 쓴다.

## 핵심
- `client.moderations.create(model='omni-moderation-latest', input=...)`
- 결과: `results[0].flagged`(차단여부) · `.categories`(카테고리별 True/False) · `.category_scores`(0~1 점수)
- `omni-moderation-latest` 는 **멀티모달** → 텍스트뿐 아니라 이미지도 검사
- 무료라서 모든 사용자 입력에 부담 없이 적용 가능

## 파일 (기본 → 고도화 → 커스터마이즈 → 실용)
| 파일 | 내용 |
|------|------|
| `1.moderate_text.py` | 텍스트 검사 — `flagged` + 걸린 카테고리 |
| `2.moderate_image_scores.py` | **이미지+텍스트** 검사 + 카테고리 **점수** 상위 보기 |
| `3.guarded_chatbot.py` | **실용** — 입력 검사 후 통과한 것만 챗봇에 전달(가드) |
| `4.custom_policy.py` | **내 정책** — `category_scores`에 **내 임계값**·카테고리별 허용/차단(강화·완화) |
| `5.llm_moderation.py` | **완전 커스텀 규칙(분리 게이트, 2-call)** — 판정만; 통과 시 별도 호출로 답변 |
| `6.policy_in_prompt.py` | **정책을 답변 프롬프트에 내장(1-call)** — 한 호출로 거절/답변 (싸지만 소프트) |

## 커스터마이즈는 어디까지?
- **카테고리는 고정**(폭력·혐오·성적·자해 등) — 새 카테고리 추가/재학습 불가
- 하지만 **정책은 내가 정함**: `category_scores`(0~1)에 **내 임계값**을 적용해 더 엄격/관대하게, 특정 카테고리는 무시(허용) → `4.custom_policy.py`
- **"우리만의 규칙"**(의료 조언 금지, 경쟁사 언급 금지, 주제 이탈 금지 등)은 Moderation API로 표현 불가 → **LLM 분류기** → `5.llm_moderation.py`
- 모델 자체 안전장치와는 **별개의 명시적 레이어**다. 입력 검사(Moderation/LLM) → 모델 → 출력 검사로 **방어 심층화**.
- 실전: 보편 위반은 **Moderation(무료·빠름)**으로 먼저 거르고, 통과분만 **LLM 정책**으로 추가 심사 = 2단 방어.

### LLM 정책: 분리(2-call) vs 내장(1-call)
| | 분리 게이트 `5` | 프롬프트 내장 `6` |
|---|---|---|
| 흐름 | 판정 → (통과 시) 별도 호출로 답변 | 한 호출로 거절/답변 |
| 비용·지연 | 2배 | 절반 |
| 거절 신뢰성 | **견고**(답변 모델과 분리, 우회 어려움) | 소프트(가끔 답해버림·탈옥에 약함) |
| 구조화 신호 | `allow/규칙/사유` → 로깅·분기 | 없음(자연어 거절만) |
| 적합 | **반드시 막아야 하는 규칙** | 가벼운 **주제 유도** |
> 실무는 둘 다: 시스템 프롬프트로 1차 유도(싸게) + 꼭 막을 건 분리 게이트/Moderation으로 입력 차단(심층 방어).

## 실행
```bash
cd 1.openai/11.moderation
pip install openai python-dotenv
# 1.openai/.env 에 OPENAI_API_KEY

python 1.moderate_text.py
python 2.moderate_image_scores.py
python 3.guarded_chatbot.py      # 대화 루프 (exit 종료)
python 4.custom_policy.py        # 내 임계값/카테고리 정책
python 5.llm_moderation.py       # LLM 커스텀 규칙 심사 (분리 게이트, 2-call)
python 6.policy_in_prompt.py     # 정책을 답변 프롬프트에 내장 (1-call)
```

## 참고
- 입력 가드 + 출력 가드(생성된 답변도 검사)로 양방향 적용하면 더 안전합니다.
- 더 정교한 안전/권한 제어는 에이전트 도구 제한([`2.langchain/8.agents` 또는 `8.mcp/4.langchain/4.tools_safety`])과 함께 쓰세요.
