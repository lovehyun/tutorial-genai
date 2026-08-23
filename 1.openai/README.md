# OpenAI API 예제

OpenAI API를 활용한 다양한 애플리케이션 예제를 단계별로 학습합니다.

## 학습 순서

번호는 **필요한 인프라의 무게** 기준으로 묶여 있습니다. 1~7번은 Chat/Responses API 호출 방식만
바꿔가며 익히는 가벼운 단계이고, 8~9번부터 벡터스토어·이미지/음성 API 같은 별도 셋업이 필요한
무거운 단계, 10~12번은 프로덕션 운영 관심사입니다.

| 디렉토리 | 주제 | 설명 |
|----------|------|------|
| `1.restapi/` | REST API 입문 | `requests`로 직접 호출 — Chat Completions → Responses |
| `2.sdk/` | SDK | 구버전 → 신버전 → 멀티턴 → Vision 맛보기 → Responses(멀티턴·스트리밍·web_search) |
| `3.chatbot/` | 챗봇 | UI → 히스토리 → SQLite 저장 → 세션 관리(+요약) |
| `4.streaming/` | 스트리밍 | SSE 기반 실시간 응답 출력 |
| `5.twobots/` | 멀티봇 대화 | 두 봇이 자동으로 대화 |
| `6.structured_output/` | 구조화 출력 | JSON 강제 출력 (프롬프트 → json_mode → json_schema → pydantic) |
| `7.function_calling/` | Function Calling | 모델이 함수 호출을 판단·실행 |
| `8.rag/` | RAG | FAISS 벡터 검색 기반 질의응답 |
| `9.multimodal/` | 멀티모달 | 비전 · 이미지 생성 · STT · TTS · 실시간 음성 (5개 그룹) |
| `10.moderation_content_safety/` | 안전성 검사 | Moderation API로 입력 안전성 가드 (무료) |
| `11.batch/` | 배치 처리 | 대량 작업 비동기·50% 비용 (임베딩/분류) |
| `12.finetuning/` | 파인튜닝 | 내 데이터로 학습 → `ft:` 모델 (스타일·형식 일관성) |

## 사전 준비

```bash
pip install openai python-dotenv flask
```

`.env` 파일에 OpenAI API 키를 설정하세요:
```
OPENAI_API_KEY=sk-...
```
