# 9.embeddings — 임베딩

텍스트를 의미를 담은 숫자 벡터로 바꿉니다. RAG(검색 증강 생성)의 첫 단계입니다.

## 순서

| 파일 | 내용 |
|------|------|
| `1.embeddings.py` | `gemini-embedding-001`로 문장 임베딩 + 코사인 유사도 비교 |
| `2.semantic_search.py` | 그 벡터로 실제로 검색해본다 — 질문을 임베딩해서 문서 여러 개 중 가장 가까운 걸 찾기 |

## 참고

- OpenAI(`text-embedding-*`)에는 임베딩 API가 있고, **Anthropic에는 없습니다**(Voyage AI 등
  외부 제공자를 권장). Gemini는 자체 임베딩 모델을 제공합니다.
- `2.semantic_search.py`는 FAISS 같은 벡터 인덱스 없이 numpy로 직접 구현한 최소 버전입니다 —
  "임베딩이 검색에 어떻게 쓰이는지" 원리만 보여줍니다. 청크 분할·인덱싱까지 포함한 실전 RAG
  파이프라인은 [`../../1.openai/8.rag/`](../../1.openai/8.rag/) 참고.

## 설치

```bash
pip install google-genai python-dotenv numpy
```

API 키는 `4.google/.env`에 설정합니다: `GOOGLE_API_KEY=...`
