# 30.study — 생성형 AI 기초 원리

벤더 API를 호출하는 게 아니라, **그 뒤에서 실제로 무슨 일이 일어나는지**를 코드로 직접 뜯어본다.
토큰화 → 임베딩 → 어텐션 → 포지셔널 인코딩 → (BERT/GPT의) 학습 목적함수 → 디코딩 전략까지,
Transformer가 텍스트를 이해하고 생성하는 전 과정을 순서대로 쌓는다.

## 디렉토리

| 폴더 | 주제 | 설명 |
|---|---|---|
| [`5.tokenizer/`](5.tokenizer/) | 토크나이저 | BPE, WordPiece, SentencePiece 비교 |
| [`6.embedding/`](6.embedding/) | 임베딩 | 워드/문장 임베딩을 벡터공간으로 시각화 |
| [`7.attention/`](7.attention/) | 어텐션 | Self-Attention 계산(QK^T→softmax→×V) 분해 |
| [`8.positional_encoding/`](8.positional_encoding/) | 포지셔널 인코딩 | 어텐션은 왜 순서를 모르는가, sin/cos로 어떻게 주입하는가 |
| [`9.decoding_strategies/`](9.decoding_strategies/) | 디코딩/샘플링 | temperature·top-k·top-p가 확률 분포를 어떻게 바꾸는가 |
| [`11.training_objectives/`](11.training_objectives/) | 학습 목적함수 | Causal LM(GPT) vs Masked LM(BERT) — loss가 어디서 계산되는가 |
| [`12.kv_cache/`](12.kv_cache/) | KV 캐시 | 매 스텝 처음부터 재계산 안 하는 이유 — 속도 실측 + 결과 동일성 증명 |
| [`13.rnn_vs_transformer/`](13.rnn_vs_transformer/) | RNN vs Transformer | 기울기 소실·병렬화를 직접 측정해 Transformer가 RNN을 대체한 이유를 확인 |
| [`14.instruction_tuning/`](14.instruction_tuning/) | Instruction Tuning | base 모델 vs instruction-tuned 모델 — 같은 질문에 대한 응답 비교 |
| [`1.transformer/`](1.transformer/) | 사전학습 모델 활용 | `sentence-transformers`로 의미 검색 |
| [`2.bert/`](2.bert/) | BERT 파인튜닝 | 감성분류·토픽분류 직접 학습 |
| [`4.korean_nlp/`](4.korean_nlp/) | 한국어 NLP | 형태소 분석, 전처리 |
| [`10.web_visualizations/`](10.web_visualizations/) | 브라우저 종합 데모 | 설치 없이 슬라이더로 만져보는 인터랙티브 버전 |
| `3.langchain_curriculum/` | (별도 성격) | LangChain 실전 커리큘럼 — "원리" 학습이 아니라 실습 커리큘럼에 가까워 이 폴더 성격과는 다르다 |

## 추천 학습 순서

```
5.tokenizer → 6.embedding → 7.attention → 8.positional_encoding
   (텍스트를 토큰으로, 토큰을 벡터로, 벡터 간 관계를 attention으로, 순서 정보를 추가로)
        ▼
13.rnn_vs_transformer                (왜 하필 attention 구조인가 — RNN 대비 기울기 소실/병렬화 실측)
        ▼
11.training_objectives              ("그래서 이걸로 뭘 배우나" — GPT vs BERT가 다른 문제를 품)
        ▼
9.decoding_strategies                (학습된 모델이 다음 토큰을 실제로 어떻게 고르는가)
        ▼
12.kv_cache                          (생성할 때 매 스텝 처음부터 다시 계산하지 않는 이유)
        ▼
14.instruction_tuning                (사전학습만 된 모델과 instruction-tuned 모델은 뭐가 다른가)
        ▼
1.transformer, 2.bert, 4.korean_nlp  (사전학습 모델을 실전에서 쓰기 — 의미 검색, 파인튜닝, 한국어)
        ▼
10.web_visualizations                (지금까지 배운 걸 브라우저에서 종합/시각화로 다시 확인)
```

> 폴더 번호는 "주제 분류"고, 위 순서가 "학습 순서"다 — `5.mcp`와 같은 원칙.

## 이 저장소의 다른 폴더와의 관계
- **로컬에서 실제로 모델을 실행/파인튜닝/서빙**하려면 → [`../31.local/`](../31.local/) (여기가 "원리"라면 그쪽은 "실전")
- 특히 디코딩 전략의 **실제 생성 문장 비교**는 [`../31.local/1.transformers/4.1_decoding_strategies.py`](../31.local/1.transformers/4.1_decoding_strategies.py) 참고 — 여기(`9.decoding_strategies`)는 확률 분포 자체를 시각화하고, 그쪽은 결과 문장을 비교한다(서로 보완).

## 공통 설치
```bash
pip install transformers torch matplotlib numpy seaborn sentence-transformers
```
한글이 그래프에서 깨지면 Windows는 `Malgun Gothic`, macOS/Linux는 `NanumGothic`이 필요하다 —
이미 각 스크립트에 폴백 폰트 목록으로 처리돼 있다.
