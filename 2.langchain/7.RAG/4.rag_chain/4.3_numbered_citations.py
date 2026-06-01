"""
번호형 인용 (Numbered Citations) — 답변 문장마다 [1], [2] 로 근거를 표기.
이 예제: 4.2 를 확장 — 답변 안에 [n] 인라인 인용을 넣고, 출처도 번호별로 나열합니다.

4.2 와의 차이:
  - 4.2 : 답변 끝에 출처를 'unique' 하게 한 번씩 (- nvme.txt / - ssd.txt)
  - 4.3 : 답변에 [1][2] 인라인 표기 + 출처를 '청크 번호별' 로 (중복 허용)
            [1] nvme.txt
            [2] nvme.txt   ← 같은 파일이어도 청크가 다르면 번호도 다름
            [3] ssd.txt
  → 논문/리포트처럼 "이 문장의 근거가 몇 번 문서" 인지 정확히 추적.
"""

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(
    collection_name="rag_chain_demo",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)

if store._collection.count() == 0:
    docs = TextLoader("../DATA/nvme.txt", encoding="utf-8").load() \
         + TextLoader("../DATA/ssd.txt",  encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)
    for c in chunks:
        c.metadata["source"] = os.path.basename(c.metadata.get("source", "?"))
    store.add_documents(chunks)

retriever = store.as_retriever(search_kwargs={"k": 3})

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ★ 프롬프트가 '인라인 인용' 을 명시적으로 지시 — 이게 4.2 와의 핵심 차이
prompt = ChatPromptTemplate.from_messages([
    ("system",
        "다음 번호가 매겨진 문서들만 참고해 한국어로 답하세요.\n"
        "각 문장 끝에, 근거가 된 문서 번호를 [1], [2] 처럼 표기하세요.\n"
        "한 문장이 여러 문서를 근거로 하면 [1][2] 처럼 모두 표기합니다.\n"
        "문서에 없으면 '모르겠습니다'.\n\n"
        "문서:\n{context}"),
    ("user", "{question}"),
])


def format_docs_with_index(docs):
    """청크에 [1], [2] 번호를 붙여 프롬프트에 (인용 대상)"""
    return "\n\n".join(f"[{i}] {d.page_content}" for i, d in enumerate(docs, 1))


def numbered_sources(docs):
    """청크 번호별 출처 — 중복 제거 안 함 (인라인 [n] 과 1:1 대응)"""
    return [f"[{i}] {d.metadata.get('source', 'unknown')}" for i, d in enumerate(docs, 1)]


# retriever 를 한 번만 호출해 context(번호 문자열) 와 sources(번호별 목록) 둘 다 만들기
def retrieve_and_split(inputs):
    docs = retriever.invoke(inputs["question"])
    return {
        "question": inputs["question"],
        "context":  format_docs_with_index(docs),
        "sources":  numbered_sources(docs),
    }


def append_sources(d):
    src_lines = "\n".join(f"  {s}" for s in d["sources"])   # s = "[1] nvme.txt"
    return f"{d['answer']}\n\n📚 출처:\n{src_lines}"


chain = (
    RunnableLambda(retrieve_and_split)
    | RunnablePassthrough.assign(answer=(prompt | llm | StrOutputParser()))
    | RunnableLambda(append_sources)
)

print(chain.invoke({"question": "NVMe 의 인터페이스가 뭐고 어떤 장점이 있어?"}))
