# OpenAI API 예제

OpenAI API를 활용한 다양한 애플리케이션 예제를 단계별로 학습합니다.

## 학습 순서

| 디렉토리 | 주제 | 설명 |
|----------|------|------|
| `1.intro/` | API 입문 | REST API → SDK(구버전) → SDK(신버전) → Vision |
| `2.chatbot/1.ui/` | 챗봇 UI | Flask 웹 챗봇 기본 구현 |
| `2.chatbot/2.history/` | 대화 히스토리 | 이전 대화를 기억하는 챗봇 |
| `2.chatbot/3.history_sqlite/` | DB 저장 | SQLite로 대화 영구 저장 |
| `2.chatbot/4.session/` | 세션 관리 | 사용자별 세션 분리 + 요약 |
| `5.twobots/` | 멀티봇 대화 | 두 봇이 자동으로 대화 |
| `4.rag/` | RAG | FAISS 벡터 검색 기반 질의응답 |
| `3.streaming/` | 스트리밍 | SSE 기반 실시간 응답 출력 |
| `6.structured_output_func_calling/` | 구조화 출력 & Function Calling | JSON 강제 출력 + 함수 호출 |
| `7.multimodal/` | 멀티모달 | 비전·이미지 생성·음성(STT/TTS/실시간·오디오 chat) |
| `8.moderation_content_safety/` | 안전성 검사 | Moderation API로 입력 안전성 가드 (무료) |
| `9.batch/` | 배치 처리 | 대량 작업 비동기·50% 비용 (임베딩/분류) |
| `10.finetuning/` | 파인튜닝 | 내 데이터로 학습 → `ft:` 모델 (스타일·형식 일관성) |

## 사전 준비

```bash
pip install openai python-dotenv flask
```

`.env` 파일에 OpenAI API 키를 설정하세요:
```
OPENAI_API_KEY=sk-...
```
