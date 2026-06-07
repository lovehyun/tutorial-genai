"""
(7) 간단 RAG — 내 문서를 근거로만 답하기 (할루시네이션 줄이기) (ollama SDK)
검색(retrieve) → 컨텍스트 주입 → EXAONE 가 '문서 기반' 으로 답.
여기선 의존성 없이 간단한 단어겹침 검색을 쓴다. (본격 벡터검색 RAG 는 2.langchain/7.RAG 참고)

준비: pip install ollama  +  ollama pull exaone3.5
"""
import ollama

MODEL = "exaone3.5:latest"

# 작은 지식 베이스 (실제로는 파일/DB 에서 로드)
DOCS = [
    "EXAONE 3.5 는 LG AI Research 가 개발한 한국어 특화 대규모 언어 모델이다.",
    "EXAONE 3.5 는 2.4B, 7.8B, 32B 세 가지 크기로 공개되었다.",
    "Ollama 는 로컬에서 LLM 을 쉽게 실행하게 해주는 도구다.",
    "비빔밥은 밥 위에 나물과 고추장을 비벼 먹는 한국 음식이다.",
]


def retrieve(query, k=2):
    """단어 겹침이 많은 문서 상위 k개 (초간단 검색)"""
    q_words = set(query.replace("?", "").split())
    scored = [(len(q_words & set(d.split())), d) for d in DOCS]
    scored.sort(reverse=True)
    return [d for score, d in scored[:k] if score > 0]


def answer(query):
    context = "\n".join(retrieve(query))
    resp = ollama.chat(
        model=MODEL, options={"temperature": 0.0},
        messages=[
            {"role": "system", "content":
             "아래 [문서] 내용만 근거로 답하세요. 문서에 없으면 '문서에 없습니다' 라고 답하세요."},
            {"role": "user", "content": f"[문서]\n{context}\n\n[질문] {query}"}],
    )
    return context, resp["message"]["content"]


for q in ["EXAONE 3.5 는 누가 만들었어?", "EXAONE 는 어떤 크기로 나왔어?", "파이썬은 누가 만들었어?"]:
    ctx, ans = answer(q)
    print("=" * 55)
    print(f"[질문] {q}")
    print(f"[검색된 근거]\n{ctx if ctx else '(없음)'}")
    print(f"[답변] {ans}\n")

# 학습 포인트:
#   - RAG = 검색으로 찾은 문서를 프롬프트에 넣어 '근거 있는' 답을 시킴
#   - "문서에 없으면 모른다고" 지시 → 마지막 질문(파이썬)은 근거가 없어 답을 거절해야 정상
#   - 실전은 단어겹침 대신 임베딩 벡터검색 사용 (2.langchain/7.RAG)
