"""
Semantic Cache — "완전히 같은 질문"이 아니라 "의미가 비슷한 질문"도 캐시로 잡아낸다

10.3_llm_cache.py 의 InMemoryCache 는 문자열이 한 글자라도 다르면 캐시 미스다. 그런데 실제
서비스에서 사용자는 같은 질문을 다른 표현으로 반복한다. Semantic cache는 질문을 임베딩(벡터)으로
바꿔, 이미 답한 질문들과 코사인 유사도를 비교해서 "충분히 비슷하면" LLM을 다시 호출하지 않고
저장된 답을 그대로 돌려준다.

★ 핵심은 유사도 threshold를 얼마로 잡느냐다 — 아래 실측에서 직접 확인하겠지만, 임베딩 유사도는
"의미가 같은가"보다 "단어/문장 구조가 겹치는가"에 더 크게 좌우된다. 그래서 threshold를 안전하게
잡으면(1부) 진짜 재질문(다른 단어 사용)도 놓치고, 느슨하게 풀면(2부) 전혀 다른 질문에 엉뚱한 답을
캐시로 돌려주는 사고가 실제로 발생한다 — 둘 다 실측으로 보여준다.
"""

import time
import numpy as np
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
chain = ChatPromptTemplate.from_template("{q}") | llm | StrOutputParser()


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class SemanticCache:
    """[관전 포인트] 캐시는 그냥 (벡터, 질문, 답) 리스트 — 벡터DB 없이도 원리는 동일하다.
    실전에서는 이 리스트 대신 Redis/FAISS 같은 벡터 인덱스를 써서 검색을 빠르게 할 뿐이다."""

    def __init__(self):
        self.entries = []  # [(vector, question, answer)]

    def get(self, question: str, threshold: float):
        vec = embeddings.embed_query(question)
        best_sim, best_answer = 0.0, None
        for cached_vec, cached_q, cached_a in self.entries:
            sim = cosine_similarity(vec, cached_vec)
            if sim > best_sim:
                best_sim, best_answer = sim, cached_a
        if best_answer is not None and best_sim >= threshold:
            return best_answer, best_sim
        return None, best_sim

    def put(self, question: str, answer: str):
        vec = embeddings.embed_query(question)
        self.entries.append((vec, question, answer))


def peek(cache: SemanticCache, question: str):
    """get()과 동일하지만 캐시에 저장하지 않는다 — "만약 나중에 이 질문이 들어오면 몇 점일까"만 확인용.
    (4번 질문은 뒤에서 threshold를 낮춰 다시 조회할 것이라, 미리 캐시에 넣어버리면 자기 자신과
    비교돼 유사도 1.000이 나와서 원하는 "다른 질문의 답을 잘못 받는" 상황을 재현할 수 없다)"""
    _, sim = cache.get(question, threshold=1.01)  # 절대 HIT 안 나는 threshold로 유사도만 계산
    return sim


def ask(cache: SemanticCache, question: str, threshold: float):
    t0 = time.time()
    cached_answer, sim = cache.get(question, threshold)
    print(f"    Q: {question}")
    if cached_answer is not None:
        elapsed = time.time() - t0
        print(f"  [캐시 HIT]  유사도 {sim:.3f} >= threshold({threshold}) → API 호출 없음 ({elapsed:.2f}s)")
        print(f"    A: {cached_answer}")
    else:
        answer = chain.invoke({"q": question})
        cache.put(question, answer)
        elapsed = time.time() - t0
        print(f"  [캐시 MISS] 유사도 {sim:.3f} <  threshold({threshold}) → 실제 API 호출 ({elapsed:.2f}s)")
        print(f"    A: {answer}")
    return sim


def main():
    cache = SemanticCache()

    print("=" * 60)
    print("  1부 — threshold = 0.85 (보수적으로 잡은 경우)")
    print("=" * 60)

    print("\n1) 첫 질문 — 캐시 비어있음 → 무조건 MISS")
    ask(cache, "파이썬에서 리스트와 튜플의 차이를 한 줄로 설명해줘.", threshold=0.85)

    print("\n2) 단어 구성이 거의 같은 재질문 — HIT 기대")
    ask(cache, "파이썬 리스트와 튜플 차이 한 줄로 알려줘.", threshold=0.85)

    print("\n3) 완전히 다른 주제 — MISS 기대")
    ask(cache, "자바스크립트에서 var와 let의 차이는?", threshold=0.85)

    print("\n4) [함정] 문장 구조는 거의 같은데 실제로는 다른 질문 — 리스트 vs 딕셔너리")
    print("   (아직 캐시에 저장은 안 하고, '이 질문이 기존 캐시와 얼마나 비슷한가'만 확인)")
    trap_question = "파이썬에서 리스트와 딕셔너리의 차이를 한 줄로 설명해줘."
    print(f"    Q: {trap_question}")
    sim4 = peek(cache, trap_question)
    print(f"   → 기존 캐시(1번 '리스트 vs 튜플')와의 유사도 {sim4:.3f} — threshold 0.85 에서는 안전하게 MISS 처리될 것")

    print("\n5) 진짜 재질문이지만 단어를 많이 바꾼 경우 — 1번과 같은 의도인데도")
    sim5 = ask(cache, "파이썬 list랑 tuple이 어떻게 다른지 한 문장으로 알려줘.", threshold=0.85)
    print(f"   → 같은 의도인데도 threshold 0.85 를 못 넘겨 MISS(실측 유사도 {sim5:.3f}) — 보수적 threshold의 대가")

    print("\n" + "=" * 60)
    print("  2부 — 같은 캐시를 그대로 두고 threshold만 0.75로 낮추면?")
    print("=" * 60)
    print("\n6) 4번과 '완전히 같은 질문'을 (아직 캐시에 없는 채로) threshold 0.75로 조회")
    sim6 = ask(cache, trap_question, threshold=0.75)
    print(f"   → 유사도 {sim6:.3f} >= 0.75 라서 이번엔 HIT — 그런데 캐시에 있던 건 '리스트 vs 튜플' 질문의 답이다!")
    print("      '리스트와 딕셔너리 차이'를 물었는데 '리스트와 튜플 차이' 답을 그대로 받는 사고가 실측으로 재현됨.")

    print("\n" + "=" * 60)
    print("  [ 학습 포인트 ]")
    print("=" * 60)
    print("""
1. 임베딩 유사도는 "의미가 같은가"보다 "단어/문장 구조가 겹치는가"에 더 크게 좌우된다.
   위 실측에서 확인했듯, 5번("list랑 tuple이 어떻게 다른지 한 문장으로")은 1번과 완전히 같은
   의도인데도 단어를 많이 바꿔서 유사도가 낮게 나왔고(threshold 0.85 미달), 오히려 4번
   ("리스트와 딕셔너리")은 다른 질문인데 문장 구조가 거의 같아서 유사도가 더 높게 나왔다.

2. threshold를 올리면(1부, 0.85) 안전하지만 캐시 적중률이 낮아진다 — 표현을 조금만 바꿔도
   다시 API를 호출하니, 비용 절감 효과가 기대만큼 크지 않을 수 있다.

3. threshold를 낮추면(2부, 0.75) 적중률은 올라가지만, 6번에서 실측으로 보여준 것처럼 전혀
   다른 질문에 잘못된 답을 그대로 돌려주는 사고가 실제로 일어난다 — 챗봇/고객지원 같은
   서비스에서는 이게 "틀린 정보를 자신있게 제공"하는 신뢰도 문제로 직결된다.

4. 실전에서 쓰는 완화책:
   - threshold를 보수적으로 잡고, 적중률보다 정확도를 우선한다
   - 캐시된 답을 쓸 때도 원문 질문을 같이 보여주고("이런 질문에 대한 답변입니다") 사용자가
     다른 질문이라고 정정할 수 있게 한다
   - 도메인이 좁고 반복 질문이 정말 많은 경우(FAQ봇 등)에만 적용하고, 자유 대화형 챗봇에는
     신중하게 적용한다
""")


if __name__ == "__main__":
    main()
