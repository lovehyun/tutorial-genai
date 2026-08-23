# 8.batches — Batches API

급하지 않은 대량 요청을 비동기로 처리해 **가격 50% 할인**을 받습니다.
요청들을 모아 제출 → 완료까지 폴링 → 결과 수집하는 흐름입니다.

## 파일

| 파일 | 내용 |
|------|------|
| `1.batches.py` | 배치 제출 → 폴링 → 결과 수집 |

## 주의

- 완료까지 보통 1시간 내(최대 24시간) 걸립니다 — 데모라도 실제로 시간이 듭니다.
- 실시간 응답이 필요한 챗봇/UI에는 맞지 않습니다. 대량 분류·요약·오프라인 처리에 적합합니다.
- 비교: [`../../1.openai/11.batch/`](../../1.openai/11.batch/) — OpenAI의 Batch API도 같은 개념(50% 할인)입니다.

## 설치

```bash
pip install anthropic python-dotenv
```

API 키는 `3.anthropic/.env`에 설정합니다: `ANTHROPIC_API_KEY=sk-ant-...`
