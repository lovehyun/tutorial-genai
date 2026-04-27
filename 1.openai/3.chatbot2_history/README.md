# 챗봇 2 - 대화 히스토리

이전 대화 내용을 기억하는 챗봇 구현입니다.

## 핵심 개념

- 대화 히스토리를 `messages` 리스트로 관리
- 이전 대화 맥락을 유지하여 자연스러운 연속 대화
- 토큰 절약을 위한 히스토리 제한 (최근 N개만 유지)

## 예제 목록

| 파일 | 설명 |
|------|------|
| `app_restapi.py` | REST API로 히스토리 관리 |
| `app2_openailib.py` | OpenAI SDK로 히스토리 관리 |
| `app3_history.py` | 메모리 기반 대화 히스토리 |
| `app4_historylimit.py` | 히스토리 개수 제한 (토큰 절약) |

## 실행

```bash
python app3_history.py
```
