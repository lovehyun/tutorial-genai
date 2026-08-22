# 3.advanced — Claude API 고급

서버 사이드 도구, 대량 처리, 파일 등 한 단계 더 들어간 기능.

## 준비
```bash
pip install anthropic python-dotenv
```
`.env` 에 `ANTHROPIC_API_KEY=sk-ant-...`

## 순서
| 파일 | 기능 | 모델 |
|------|------|------|
| `1.effort.py` | effort 파라미터 — 품질/비용 조절 | Opus |
| `2.web_search.py` | 서버 도구 — 웹 검색 | Sonnet |
| `3.code_execution.py` | 서버 도구 — 코드 실행(샌드박스) | Sonnet |
| `4.batches.py` | Batches API — 대량 비동기, 50% 할인 | Haiku |
| `5.files_api.py` | Files API(beta) — 업로드 후 `file_id` 재사용 | Sonnet |

## 주의
- `effort` 는 Opus / Sonnet 4.6 전용 (Haiku 4.5 는 미지원 → 에러). `max` 는 Opus 전용.
- 서버 도구(웹검색·코드실행)와 배치는 **과금 정책이 다르다**. 문서를 확인할 것.
- `4.batches.py` 는 완료까지 시간이 걸린다(보통 1시간 내, 최대 24시간).
- `5.files_api.py` 는 같은 폴더에 `doc.pdf` 가 필요하다.
