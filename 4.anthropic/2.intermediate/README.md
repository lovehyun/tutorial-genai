# 2.intermediate — Claude API 중급

`1.basic` 위에서, 네이티브 Anthropic API 의 자주 쓰는 중급 기능들. 한 파일 = 한 기능.

## 준비
```bash
pip install anthropic python-dotenv pydantic
```
`.env` 에 `ANTHROPIC_API_KEY=sk-ant-...`

## 순서
| 파일 | 기능 | 모델 |
|------|------|------|
| `1.vision.py` | 이미지 입력(비전) — URL / base64 | Sonnet |
| `2.pdf.py` | PDF·문서 입력 (document 블록) | Sonnet |
| `3.tool_use.py` | 도구 호출 기본 — 수동 루프 | Sonnet |
| `4.tool_runner.py` | tool runner(beta) — 자동 루프 (`@beta_tool`) | Sonnet |
| `5.structured_output.py` | 구조화 출력 — `messages.parse()` + Pydantic | Sonnet |
| `6.prompt_caching.py` | 프롬프트 캐싱 — `cache_control` 로 비용 절감 | Sonnet |
| `7.error_handling.py` | 타입별 예외 처리 + 자동 재시도 | Haiku |

## 메모
- `2.pdf.py` 는 같은 폴더에 `doc.pdf` 가 필요하다.
- `6.prompt_caching.py` 는 prefix 가 충분히 커야 캐시된다(Sonnet 4.6 최소 ~2048 토큰).
- 도구·구조화 출력은 비전/캐싱과 함께 조합해 쓸 수 있다.
