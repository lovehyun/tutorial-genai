# 1.basic — Anthropic Claude API 기초

Claude API 의 기본 기능을 **한 파일에 하나씩, 쉬운 것부터** 차근차근 익힌다.
모델은 haiku / sonnet / opus 를 용도와 규격에 맞게 골라 썼다.

## 준비
```bash
pip install anthropic python-dotenv
```
`.env` 에 `ANTHROPIC_API_KEY=sk-ant-...` 를 넣는다.

## 순서
| 파일 | 배우는 것 | 모델 |
|------|-----------|------|
| `0.apikey.py` | API 키 로드 확인 | - |
| `1.hello.py` | 가장 단순한 호출 한 번 | Haiku |
| `2.system.py` | system 프롬프트(역할/말투) — top-level 파라미터 | Sonnet |
| `3.multiturn.py` | 멀티턴 대화 (stateless, 기록 직접 관리) | Haiku |
| `4.streaming.py` | 스트리밍 출력 | Sonnet |
| `5.params.py` | max_tokens / temperature + 모델별 주의 | Haiku |
| `6.models.py` | haiku/sonnet/opus 비교 + 기능표 | 셋 다 |
| `7.thinking.py` | 생각하기 (adaptive vs budget_tokens) | Opus/Haiku |
| `7.thinking_stream.py` | 생각 과정을 스트리밍으로 실시간 보기 | Opus |
| `8.response.py` | 응답 객체(블록/stop_reason/usage) + 토큰 세기 | Sonnet |

## 모델별 규격 차이 (꼭 기억)
| 기능 | Haiku 4.5 | Sonnet 4.6 | Opus 4.8 |
|------|:--------:|:----------:|:--------:|
| temperature / top_p | O | O | **X (400)** |
| adaptive thinking | X | O | O |
| extended thinking (budget_tokens) | O | O | X |
| effort 파라미터 | X | O | O |

- Opus 4.8 에 `temperature`/`top_p` 를 보내면 **400 에러** → 동작은 프롬프트로 조절한다.
- `temperature` 와 `top_p` 를 동시에 보내면 Claude 4 계열 전부 400 → 둘 중 하나만.
- Anthropic 의 `system` 은 messages 의 role 이 아니라 **top-level 파라미터**다.
- thinking 을 켜면 응답 `content` 의 첫 블록이 `thinking` 일 수 있으니 `block.type` 으로 걸러서 텍스트를 뽑는다.
