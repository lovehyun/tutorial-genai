# OpenAI API 예제

OpenAI API를 활용한 다양한 애플리케이션 예제를 단계별로 학습합니다.

## 학습 순서

| 디렉토리 | 주제 | 설명 |
|----------|------|------|
| `1.intro/` | API 입문 | REST API → SDK(구버전) → SDK(신버전) → Vision |
| `2.chatbot_ui/` | 챗봇 UI | Flask 웹 챗봇 기본 구현 |
| `3.chatbot2_history/` | 대화 히스토리 | 이전 대화를 기억하는 챗봇 |
| `4.chatbot3_historysqlite/` | DB 저장 | SQLite로 대화 영구 저장 |
| `5.chatbot4_session/` | 세션 관리 | 사용자별 세션 분리 + 요약 |
| `6.twobots/` | 멀티봇 대화 | 두 봇이 자동으로 대화 |
| `7.rag/` | RAG | FAISS 벡터 검색 기반 질의응답 |
| `8.streaming/` | 스트리밍 | SSE 기반 실시간 응답 출력 |
| `9.structured_output/` | 구조화 출력 | Function Calling으로 JSON 응답 |
| `10.multimodal/` | 멀티모달 | DALL-E 이미지 생성 + Whisper 음성 인식 |

## 사전 준비

```bash
pip install openai python-dotenv flask
```

`.env` 파일에 OpenAI API 키를 설정하세요:
```
OPENAI_API_KEY=sk-...
```
