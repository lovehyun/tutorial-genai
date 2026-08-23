# Transformer — 사전학습 모델로 의미 검색

⚠️ 폴더 이름과 달리, 이 폴더는 Transformer의 내부 구조(Q/K/V, attention 계산 등)를 직접
구현하지 않는다 — 그건 `../7.attention/`(어텐션 계산 분해)과 `../10.web_visualizations/`
(브라우저에서 forward pass부터 생성까지 직접 구현)에 있다. 여기는 **사전학습된 Transformer
모델을 라이브러리로 불러와 실전에서 쓰는 법**(문장 임베딩 → 의미 검색)에 집중한다.

## 파일

| 파일 | 내용 |
|---|---|
| `1.model_load.py` | `sentence-transformers`로 사전학습 모델(`all-MiniLM-L6-v2`) 로드, 문장 임베딩 생성 |
| `2.model_query.py` | 코퍼스 임베딩 + 쿼리 임베딩 → 코사인 유사도로 의미 검색(semantic search) |

## 설치
```bash
pip install sentence-transformers
```

## Transformer 내부 구조를 직접 보고 싶다면
- 어텐션 계산(QK^T→softmax→×V) 분해 → [`../7.attention/`](../7.attention/)
- 순서 정보가 왜 필요한지(포지셔널 인코딩) → [`../8.positional_encoding/`](../8.positional_encoding/)
- 순수 JS로 밑바닥부터 구현한 미니 Transformer → [`../10.web_visualizations/`](../10.web_visualizations/)
- 토큰화 원리 → [`../5.tokenizer/`](../5.tokenizer/)
