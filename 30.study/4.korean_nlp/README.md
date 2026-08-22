# 한국어 자연어 처리 기초

한국어 텍스트의 형태소 분석, 전처리, 품사 태깅 등 NLP 기초 과정을 학습합니다.

## 한국어 NLP의 특수성

| 특성 | 영어 | 한국어 |
|------|------|--------|
| 어순 | SVO (주어-동사-목적어) | SOV (주어-목적어-동사) |
| 형태 | 고립어 (단어 형태 변화 적음) | 교착어 (조사/어미가 결합) |
| 띄어쓰기 | 단어 = 공백 기준 | 어절 = 공백 기준 (1어절에 여러 형태소) |
| 토큰화 | 공백 분리로 충분 | 형태소 분석 필요 |

```
영어: "I eat an apple"     → ["I", "eat", "an", "apple"]        (공백 분리)
한국어: "나는 사과를 먹었다" → ["나/NP", "는/JX", "사과/NNG", "를/JKO", "먹/VV", "었/EP", "다/EF"]
                              (형태소 분석 필요)
```

## 예제

| 파일 | 설명 |
|------|------|
| `1.morpheme.py` | 한국어 형태소 분석 — Okt, Kkma, Komoran 비교 |
| `2.preprocessing.py` | 한국어 텍스트 전처리 파이프라인 |

## 설치

```bash
pip install konlpy
# Java 런타임 필요 (KoNLPy 의존)
# Ubuntu: sudo apt-get install default-jdk
# Mac: brew install java
```
