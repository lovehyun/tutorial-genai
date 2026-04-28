# 로컬 LLM 빠르게 시작하기

## 과정 정보
- **기간**: 1일 (총 8시간)
- **난이도**: 입문
- **대상**: 클라우드 API 의존 없이 로컬 환경에서 LLM을 실행하고 싶은 개발자
- **선수 과목**: 입문 1. 생성형 AI API 첫걸음

## 학습 목표
1. HuggingFace Transformers로 로컬 모델(GPT-2 등)을 로드하고 추론할 수 있다
2. Ollama와 GPT4All로 로컬 LLM 서버를 구성할 수 있다
3. 한국어 NLP 파이프라인(형태소 분석, 감성분석, 번역 등)을 이해할 수 있다

## 커리큘럼

### Day 1: Transformers · Ollama · GPT4All · 한국어 NLP

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | 로컬 LLM의 장단점, 환경 설정 |
| 09:30-10:00 | GPT-2 로컬 실행 | `3.local/1.transformers/1.1_local_gpt2.py` | HuggingFace에서 GPT-2 로드 및 텍스트 생성 |
| 10:00-10:30 | LangChain 연동 & Flask 서빙 | `3.local/1.transformers/1.2_local2_gpt2_langchain.py`, `3.local/1.transformers/1.3_local3_gpt2_flask.py` | 로컬 모델을 LangChain/Flask로 서빙 |
| 10:45-11:15 | Ollama 기초 | `3.local/6.ollama/1.intro.py`, `3.local/6.ollama/1.intro2_restapi.py` | Ollama 설치, 기본 호출, REST API |
| 11:15-12:00 | Ollama 스트리밍 서버 | `3.local/6.ollama/2.serve_nostream.py`, `3.local/6.ollama/3.serve_stream.py` | 스트리밍/논스트리밍 서버 구성 |
| 13:00-13:30 | GPT4All 기초 | `3.local/7.gpt4all/1.intro.py`, `3.local/7.gpt4all/2.basic_qa.py` | GPT4All 설치와 기본 QA |
| 13:30-14:00 | GPT4All 대화 & 시스템 프롬프트 | `3.local/7.gpt4all/3.conversation.py`, `3.local/7.gpt4all/4.system_prompt.py` | 대화 모드, 시스템 프롬프트 설정 |
| 14:00-14:30 | GPT4All 파일 처리 | `3.local/7.gpt4all/6.fileprocessing.py`, `3.local/7.gpt4all/8.local_docs.py` | 로컬 문서 처리 및 QA |
| 14:45-15:15 | HuggingFace 파이프라인 | `3.local/3.huggingface/1.intro_distilbert_sa.py`, `3.local/3.huggingface/1.intro2_distilbert_qa.py` | 감성분석, QA 파이프라인 |
| 15:15-15:45 | 한국어 NLP (감성분석/분류) | `3.local/8.korean_llm/1.chat.py`, `3.local/8.korean_llm/2.sentiment.py`, `3.local/8.korean_llm/3.classification.py` | 한국어 챗, 감성분석, 텍스트 분류 |
| 15:45-16:15 | 한국어 NLP (NER/요약/번역) | `3.local/8.korean_llm/4.ner.py`, `3.local/8.korean_llm/5.summarization.py`, `3.local/8.korean_llm/6.translation.py` | 개체명 인식, 요약, 번역 |
| 16:15-17:00 | 종합 비교 & Q&A | — | Ollama vs GPT4All vs HuggingFace 비교 정리, 종합 Q&A |

## 환경 설정

```bash
pip install transformers torch flask gradio gpt4all
# Ollama: https://ollama.ai 에서 별도 설치
```

## 참고 자료
- `3.local/1.transformers/` — HuggingFace Transformers 기초
- `3.local/3.huggingface/` — HuggingFace 파이프라인
- `3.local/6.ollama/` — Ollama 로컬 서버
- `3.local/7.gpt4all/` — GPT4All
- `3.local/8.korean_llm/` — 한국어 NLP
