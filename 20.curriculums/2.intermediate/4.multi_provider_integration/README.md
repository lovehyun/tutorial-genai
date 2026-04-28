# 멀티 프로바이더 통합

## 과정 정보
- **기간**: 2일 (총 16시간)
- **난이도**: 중급
- **대상**: OpenAI 외에 Claude, Gemini 등 다양한 LLM을 통합 활용하고 싶은 개발자
- **선수 과목**: 입문 3. LangChain 핵심 마스터

## 학습 목표
1. Anthropic Claude API의 기본/고급 기능(스트리밍, 대화, 파라미터)을 사용할 수 있다
2. Google Gemini API의 멀티모달(Vision, 이미지 생성) 기능을 활용할 수 있다
3. LangChain을 통해 여러 프로바이더를 통합하고 코드리뷰 앱을 구축할 수 있다

## 커리큘럼

### Day 1: Claude와 Gemini API 심화

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | 멀티 프로바이더 전략, 각 프로바이더 특성 비교 |
| 09:30-10:00 | Claude API 기초 | `4.anthropic/1.basic/1.intro.py`, `4.anthropic/1.basic/0.apikey.py` | Anthropic API 키 설정, 기본 호출 |
| 10:00-10:30 | Claude 파라미터 & 모델 | `4.anthropic/1.basic/3.params.py`, `4.anthropic/1.basic/4.models.py` | 온도, 모델 선택, 파라미터 최적화 |
| 10:45-11:15 | Claude 스트리밍 & 대화 | `4.anthropic/1.basic/5.stream.py`, `4.anthropic/1.basic/6.conversation.py` | 스트리밍 응답, 멀티턴 대화 |
| 11:15-12:00 | Claude + LangChain | `4.anthropic/2.langchain/1.intro.py`, `4.anthropic/2.langchain/2.prompttemplate.py` | LangChain에서 Claude 사용 |
| 13:00-13:30 | Claude 체이닝 & 대화 | `4.anthropic/2.langchain/3.chaining.py`, `4.anthropic/2.langchain/4.conversation.py` | LCEL 체이닝, 대화 메모리 |
| 13:30-14:00 | Claude 텍스트/벡터 | `4.anthropic/2.langchain/5.textloader.py`, `4.anthropic/2.langchain/6.vectorstore.py` | 텍스트 로더, 벡터스토어 연동 |
| 14:00-14:30 | Claude 복합 체인 | `4.anthropic/2.langchain/9.complex.py` | 복합 체인 예제 |
| 14:45-15:15 | Gemini 기초 & 채팅 | `7.google/1.basic/1.intro.py`, `7.google/1.basic/2.chat.py`, `7.google/1.basic/3.params.py` | Gemini API 기초 |
| 15:15-15:45 | Gemini 멀티모달 | `7.google/2.multimodal/1.vision.py`, `7.google/2.multimodal/2.image_gen.py` | Gemini Vision, 이미지 생성 |
| 15:45-16:15 | Gemini + LangChain | `7.google/3.langchain/1.intro.py`, `7.google/3.langchain/2.chain.py` | LangChain에서 Gemini 사용 |
| 16:15-17:00 | Gemini Structured Output | `7.google/3.langchain/3.structured_output.py`, `7.google/1.basic/5.structured_output.py` | Gemini Structured Output, 종합 비교 |

### Day 2: 코드리뷰 앱 — 멀티 프로바이더 실전

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 | — | Claude/Gemini 핵심 복습 |
| 09:30-10:00 | 코드리뷰 앱 (OpenAI) | `10.project/6.code_review_app/1.openai/app1_textarea.py` | textarea 기반 코드리뷰 기본 |
| 10:00-10:30 | 코드리뷰 + LangChain | `10.project/6.code_review_app/1.openai/app1_textarea_langchain.py` | LangChain 기반 코드리뷰 |
| 10:45-11:15 | GitHub URL 연동 | `10.project/6.code_review_app/1.openai/app2_githuburl.py`, `10.project/6.code_review_app/1.openai/app3_improvedisplay.py` | GitHub URL에서 코드 가져오기, UI 개선 |
| 11:15-12:00 | 프롬프트 선택 | `10.project/6.code_review_app/1.openai/app4_promptselection.py` | 리뷰 관점 선택 기능 |
| 13:00-13:30 | Anthropic 코드리뷰 | `10.project/6.code_review_app/2.anthropic/app1_textarea_anthropic.py` | Claude 기반 코드리뷰 |
| 13:30-14:00 | Anthropic GitHub 연동 | `10.project/6.code_review_app/2.anthropic/app2_githuburl_anthropic.py` | Claude + GitHub URL 코드리뷰 |
| 14:00-14:30 | 통합 분석기 (OpenAI) | `10.project/6.code_review_app/3.common/analyzers/openai_analyzer.py`, `10.project/6.code_review_app/3.common/analyzers/openai_analyzer2_lc.py` | OpenAI 분석기 모듈 |
| 14:45-15:15 | 통합 분석기 (Anthropic) | `10.project/6.code_review_app/3.common/analyzers/anthropic_analyzer.py`, `10.project/6.code_review_app/3.common/analyzers/anthropic_analyzer2_lc.py` | Anthropic 분석기 모듈 |
| 15:15-15:45 | 통합 앱 완성 | `10.project/6.code_review_app/3.common/app3_improvedisplay_common.py`, `10.project/6.code_review_app/3.common/app4_fileseparate.py` | 프로바이더 선택 가능한 통합 앱 |
| 15:45-17:00 | 종합 프로젝트 & 발표 | — | 멀티 프로바이더 앱 커스터마이징, 결과 공유 |

## 환경 설정

```bash
pip install langchain langchain-openai langchain-anthropic langchain-google-genai anthropic google-generativeai flask
```

## 참고 자료
- `4.anthropic/1.basic/` — Claude API 기초
- `4.anthropic/2.langchain/` — Claude + LangChain
- `7.google/` — Gemini API 전체
- `10.project/6.code_review_app/` — 코드리뷰 앱 프로젝트
