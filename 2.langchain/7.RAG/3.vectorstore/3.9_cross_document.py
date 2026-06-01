"""
교차 문서 종합 — 정답의 절반은 A 문서, 절반은 B 문서에 있을 때도 검색이 되나?
이 예제: 같은 컬렉션에 넣고 k 를 넉넉히 주면, 한 번의 검색이 A·B 양쪽 청크를
모두 끌어와 LLM 이 합쳐서 답합니다. (3.8 의 '통합' 이 실제로 동작하는 모습)

  핵심: 두 조각이 '각각' 질문과 닮아 있으면 한 번의 유사도 검색으로 둘 다 top-k 에
        들어온다 → LLM 이 종합. (A 를 알아야 B 를 찾는 '다단계 추론' 은 6.agentic 참고)
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 정답이 두 문서에 '쪼개져' 있는 구조 — 속도는 A 에, 수명은 B 에만 있음
docs = [
    Document(page_content="제품 ZX1 의 시퀀셜 읽기 속도는 약 7GB/s 다.",          metadata={"source": "A_spec.txt"}),
    Document(page_content="제품 ZX1 의 보장 수명은 600 TBW 다.",                  metadata={"source": "B_warranty.txt"}),
    # 방해용(distractor) 문서들 — 질문과 덜 관련
    Document(page_content="구형 HDD 는 회전 디스크 기반이라 IO 가 느리다.",        metadata={"source": "C_misc.txt"}),
    Document(page_content="데이터센터는 항온항습 환경을 유지한다.",                metadata={"source": "C_misc.txt"}),
]

store = Chroma.from_documents(docs, embeddings, collection_name="cross_doc_demo")

prompt = ChatPromptTemplate.from_template(
    "아래 자료만 보고 답하세요. 자료에 없으면 모른다고 하세요.\n\n자료:\n{context}\n\n질문: {question}"
)
chain = prompt | llm | StrOutputParser()


def answer_question(question: str):
    """검색(k=3) → 가져온 출처 확인 → 컨텍스트 합쳐 LLM 종합"""
    print("\n" + "#" * 60)
    print(f"[질문] {question}")
    print("#" * 60)

    # 1) 검색 — k 를 넉넉히. A·B 청크가 모두 후보로 들어오는지 확인
    results = store.similarity_search(question, k=3)
    found = {d.metadata["source"] for d in results}
    for d in results:
        print(f"  [{d.metadata['source']}] {d.page_content}")
    print(f"→ 가져온 출처: {found}  (A_spec + B_warranty 가 둘 다 있어야 종합 가능)")

    # 2) 종합 — 가져온 청크 전부를 컨텍스트로 LLM 에게
    context = "\n".join(d.page_content for d in results)
    print(f"[종합 답변] {chain.invoke({'context': context, 'question': question})}")


# 두 질문 모두 'A 절반(속도) + B 절반(수명)' 을 합쳐야만 답이 되는 구조
answer_question("ZX1 의 읽기 속도와 보장 수명을 둘 다 알려줘")     # 속도(A) + 수명(B) 나열
answer_question("ZX1 은 빠르면서도 오래 쓸 수 있는 제품이야?")     # 속도(A) + 수명(B) 로 '판단'


# 정리:
#   - A 절반 + B 절반 → 같은 컬렉션 + 넉넉한 k 면 한 번에 둘 다 끌려와 종합됨 (지금 케이스)
#   - k 를 1~2 로 줄이면 한쪽만 들어와 반쪽 답이 날 수 있음 (k 값 직접 바꿔 확인해보기)
#   - "A 를 알아야 B 에서 뭘 찾을지 아는" 다단계 질문은 한 번의 검색으로 부족 → 6.agentic

store.delete_collection()



# ─────────────────────────────────────────────────────────────────────
# 실제 실행 결과  (py312_gpt / gpt-4o-mini, temperature=0)
#
#   [질문] ZX1 의 읽기 속도와 보장 수명을 둘 다 알려줘
#     가져온 출처: {A_spec.txt, B_warranty.txt, C_misc.txt}
#     [종합 답변] ZX1의 시퀀셜 읽기 속도는 약 7GB/s이며, 보장 수명은 600 TBW입니다.
#
#   [질문] ZX1 은 빠르면서도 오래 쓸 수 있는 제품이야?
#     가져온 출처: {A_spec.txt, B_warranty.txt, C_misc.txt}
#     [종합 답변] 네, ZX1은 시퀀셜 읽기 속도가 약 7GB/s로 빠르며,
#                보장 수명이 600 TBW로 오래 쓸 수 있는 제품입니다.
#
#   ▷ 관전 포인트: 두 질문 모두 속도(A) + 수명(B) 이 한 번의 검색에 둘 다 들어와 종합됨.
#     - 1번은 '나열', 2번은 두 사실을 합친 '판단' → 교차 문서 종합의 두 형태.
#     - k=1 로 줄이면 한쪽만 들어와 반쪽 답이 된다 (set 출력 순서는 실행마다 다름).
# ─────────────────────────────────────────────────────────────────────
