"""
검색 → 답변 — 이 폴더의 마무리. 찾은 청크를 LLM 에 넣어 '진짜 정답' 을 받습니다.
이 예제: 3.1~3.11 은 산출물이 '청크 목록' 이었지만, 여기서 한 칸을 더 붙입니다.

    질문 ──► [검색] ──► 청크 3개 ──► [프롬프트에 끼워넣기] ──► [LLM] ──► 문장 답변
             ↑ 3.1~3.11 이 여기까지                              ↑ 이번에 추가되는 부분

핵심:
  - LLM 은 벡터 DB 를 모릅니다. 검색된 청크를 **텍스트로 프롬프트에 붙여줘야** 답합니다.
  - 그래서 RAG 품질의 상한은 검색이 정합니다 — 못 찾은 내용은 LLM 도 못 답합니다(3-b 참고).
  - 여기선 일부러 체인(`|`) 없이 한 줄씩 손으로 호출합니다. LCEL 표준형은 ../4.rag_chain/ 에서.

  ※ pip install langchain-chroma chromadb langchain-openai
"""

import os
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

PERSIST_DIR     = "./chroma_db"
COLLECTION_NAME = "answer_demo"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# ── 1) 벡터 스토어 준비 (3.6 통합 컬렉션 패턴 — nvme + ssd 를 한 곳에)
store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)

if store._collection.count() == 0:                      # 비어있을 때만 임베딩 (재실행 시 비용 0)
    docs = TextLoader("../DATA/nvme.txt", encoding="utf-8").load() \
         + TextLoader("../DATA/ssd.txt",  encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)
    for c in chunks:                                    # 출처를 파일명만 남게 정리 (인용 표시용)
        c.metadata["source"] = os.path.basename(c.metadata.get("source", "?"))
    store.add_documents(chunks)
    print(f"새 DB 생성 — {len(chunks)} 청크 저장\n")
else:
    print(f"기존 DB 로드 — {store._collection.count()} 청크 있음\n")


# ── 2) LLM + 프롬프트
#      "문서에 없으면 모른다고 하라" 가 핵심 — 이게 없으면 LLM 이 제 지식으로 지어냅니다(환각).
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 문서 기반 QA 시스템입니다. 아래 [문서] 내용만 근거로 답하세요.\n"
     "문서에 없는 내용은 추측하지 말고 '문서에 없습니다' 라고 답하세요.\n\n"
     "[문서]\n{context}"),
    ("user", "{question}"),
])


def answer(question: str, k: int = 3) -> str:
    """검색 → 컨텍스트 조립 → LLM 호출 까지 한 번에 (RAG 의 최소 단위)"""

    # (a) 검색 — 여기까지가 3.1~3.11 에서 하던 일. 점수도 같이 받아 근거를 눈으로 확인
    hits = store.similarity_search_with_score(question, k=k)

    print(f"Q. {question}   (k={k})")
    print("  ── 검색된 근거 " + "─" * 40)
    for d, score in hits:
        src = d.metadata.get("source", "?")
        print(f"   [{src}] dist={score:.3f} | {d.page_content[:50]}...")

    # (b) 컨텍스트 조립 — Document 객체는 LLM 이 못 읽으니 '문자열' 로 펴줘야 함.
    #     출처를 함께 적어두면 LLM 이 답변에 인용을 달 수 있음 (본격 인용은 4.2/4.3)
    context = "\n\n".join(
        f"({d.metadata.get('source', '?')}) {d.page_content}" for d, _ in hits
    )

    # (c) LLM 호출 — 체인을 안 쓰면 실제론 이 두 줄이 전부
    messages = prompt.format_messages(context=context, question=question)
    result   = llm.invoke(messages).content

    print("  ── LLM 답변 " + "─" * 43)
    print(f"   {result}\n")
    return result


# ── 3-a) 한 문서 안에서 풀리는 질문
answer("NVMe SSD 의 인터페이스와 대략적인 속도는?")

# ── 3-b) 두 문서를 합쳐야 풀리는 질문 — k 를 바꿔가며 같은 질문을 던져봅니다.
#         3.9 에서 본 그 함정: 검색이 반쪽만 가져오면 LLM 도 반쪽만 답합니다.
QUESTION = "NVMe 와 SATA SSD 중 뭐가 얼마나 더 빠른가?"
answer(QUESTION, k=1)   # 근거 부족 → 비교를 못 하거나 한쪽만 언급
answer(QUESTION, k=4)   # 양쪽 청크가 다 들어와야 비로소 '비교' 가 됨


# 정리:
#   - RAG = 검색(3장) + 생성(이 파일). LLM 에 넘어가는 건 결국 **문자열 하나(context)** 뿐.
#   - 그래서 튜닝 포인트는 대부분 LLM 이 아니라 검색 쪽에 있음 — k / 청킹 / 컬렉션 배치.
#   - 프롬프트의 "문서에 없으면 모른다고 하라" 한 줄이 환각을 크게 줄임.
#
# 다음 단계:
#   - ../4.rag_chain/4.1_standard_chain.py  : 위 (a)(b)(c) 를 LCEL 체인 한 줄로
#   - ../4.rag_chain/4.2_with_citations.py  : 답변에 출처 붙이기
#   - ../5.conversational/                  : 이전 대화를 기억하는 RAG
