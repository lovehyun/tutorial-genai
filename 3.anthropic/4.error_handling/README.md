# 4.error_handling — 에러 처리

SDK가 제공하는 타입별 예외로 상황을 구분합니다. 문자열 매칭(`"429" in str(e)`) 대신
예외 **클래스**로 잡는 게 정석입니다.

## 파일

| 파일 | 내용 |
|------|------|
| `1.error_handling.py` | 타입별 예외 처리 + 자동 재시도 |

## 참고

SDK는 `429`(rate limit)·`5xx`(서버 오류)를 자동으로 재시도합니다(`max_retries`로 조절, 기본 2회) —
직접 재시도 로직을 짜기 전에 이미 되고 있는지 먼저 확인하세요.

## 설치

```bash
pip install anthropic python-dotenv
```

API 키는 `3.anthropic/.env`에 설정합니다: `ANTHROPIC_API_KEY=sk-ant-...`
