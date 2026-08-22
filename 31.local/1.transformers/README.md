# 1.transformers — 트랜스포머 모델의 기본 기능

HuggingFace `transformers` 로 **트랜스포머 모델이 안에서 무슨 일을 하는지** 를
기초부터 한 단계씩 쌓아 배웁니다. (특정 LLM 활용/서빙은 뒤쪽 폴더에서)

## 학습 순서

```
[1] 토큰화         글자 → 토큰 → ID            1.1 토크나이저 · 1.2 특수토큰/mask
       ↓
[2] 토큰 → 출력    ID → 벡터 → 다음토큰 확률    2.1 hidden state · 2.2 logits
       ↓
[3] 두 모델 유형   인코더(이해) vs 디코더(생성)  3.1 빈칸채우기 · 3.2 생성
       ↓
[4] 디코딩 전략    다음 토큰을 어떻게 고르나       4.1 greedy/beam/top-k/top-p
       ↓
[5] 어텐션         '왜' 되는가 — 내부 메커니즘     5.1 어텐션 · 5.2 헤드별 분석
```

| 파일 | 배우는 것 |
|---|---|
| `1.1_tokenizer_basics.py` | 모델의 토크나이저로 단어를 subword 로 쪼개기 (GPT-2 BPE vs BERT WordPiece) |
| `1.2_special_tokens.py` | 특수 토큰([CLS]/[SEP]), `attention_mask`, 배치 패딩 |
| `2.1_embeddings_hidden_states.py` | forward → 토큰별 벡터(`last_hidden_state`) = 특징 추출 |
| `2.2_logits_next_token.py` | LM 헤드 → `logits` → softmax → 다음 토큰 확률 (생성의 원리) |
| `3.1_encoder_fillmask.py` | 인코더(BERT) — `[MASK]` 빈칸 채우기 = '이해' |
| `3.2_decoder_generate.py` | 디코더(GPT-2) — 텍스트 생성 = '생성' |
| `4.1_decoding_strategies.py` | greedy / beam / sampling / top-k / top-p 비교 |
| `5.1_attention.py` | 토큰이 어디를 주목하는지 attention 가중치 시각화 |
| `5.2_headwise_attention.py` | 헤드별 entropy / top-k 주목 토큰 (심화) |

### 부록 — 응용(통합 · 서빙)

트랜스포머 '기본 기능' 은 아니지만, 같은 GPT-2 를 응용하는 예시로 남겨둡니다.
(본격적인 로컬 LLM 서빙은 `4.mistral` / `6.ollama*` 등 참고)

| 파일 | 내용 |
|---|---|
| `6.1_langchain_integration.py` | GPT-2 를 LangChain(`HuggingFacePipeline`) 체인에 끼우기 |
| `6.2_flask_serving.py` | GPT-2 생성을 Flask REST API 로 서빙 |

## 설치 & 실행

```bash
pip install transformers torch
# 부록: pip install langchain langchain-core langchain-huggingface flask

cd "3.local/1.transformers"
python 1.1_tokenizer_basics.py
```

> 처음 실행 시 모델이 `~/.cache/huggingface` 에 다운로드됩니다 (gpt2 ~0.5GB, bert-base ~0.4GB).
> 모두 CPU 로 동작하며 GPU 가 있으면 더 빠릅니다.
