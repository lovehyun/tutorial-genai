# 5.prompt_caching — 프롬프트 캐싱

크고 고정된 컨텍스트(긴 시스템 프롬프트, 문서 등)를 캐시해 반복 호출 비용을 최대 ~90%까지 줄입니다.
같은 prefix를 다시 보내면 캐시에서 읽어옵니다(`cache_read_input_tokens`에 잡힘).

## 파일

| 파일 | 내용 |
|------|------|
| `1.prompt_caching.py` | `cache_control`로 프롬프트 캐싱 적용 |

## 주의

- 캐시되려면 prefix가 충분히 커야 합니다(Sonnet 4.6 기준 최소 ~2048 토큰). 작으면 **조용히 캐시가
  안 됩니다**(에러 없이 그냥 매번 새로 계산) — 비용이 안 줄었다면 이 임계값부터 의심할 것.

## 설치

```bash
pip install anthropic python-dotenv
```

API 키는 `3.anthropic/.env`에 설정합니다: `ANTHROPIC_API_KEY=sk-ant-...`
