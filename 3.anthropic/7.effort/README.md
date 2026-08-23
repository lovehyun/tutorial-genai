# 7.effort — effort 파라미터

생각 깊이/토큰 소비를 조절하는 Anthropic 전용 파라미터입니다.
`output_config={"effort": "low"|"medium"|"high"|"max"}` (기본값 `high`).

## 파일

| 파일 | 내용 |
|------|------|
| `1.effort.py` | effort 값을 바꿔가며 품질/비용 트레이드오프 확인 |

## 주의

- **Opus / Sonnet 4.6만 지원.** Haiku 4.5 / Sonnet 4.5에 보내면 에러납니다.
- `"max"`는 **Opus 전용**입니다.
- `1.basic/7a.thinking.py`의 "생각하기(thinking)"와는 다른 개념입니다 — thinking은 추론
  과정을 노출할지의 여부, effort는 그 추론에 얼마나 공을 들일지의 정도입니다.

## 설치

```bash
pip install anthropic python-dotenv
```

API 키는 `3.anthropic/.env`에 설정합니다: `ANTHROPIC_API_KEY=sk-ant-...`
