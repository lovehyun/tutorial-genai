"""
출처 인용 (Citations) — 답변에 "어느 문서/페이지에서 왔는지" 자동 부착.
이 예제: 검색된 청크의 메타데이터를 답변 끝에 자동 부착합니다.

  답변: ...
  참고 문서:
    - nvme.txt
    - ssd.txt

운영 환경에서 신뢰도 확보의 핵심 — "왜 이렇게 답했는지" 추적 가능.
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
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "다음 문서들을 참고해서 답해주세요. 문서에 없으면 '모르겠습니다'.\n\n"
     "문서:\n{context}"),
    ("user", "{question}"),
])


def format_docs_with_index(docs):
    """청크에 [1], [2] 번호를 붙여서 인용 가능하게"""
    return "\n\n".join(f"[{i}] {d.page_content}" for i, d in enumerate(docs, 1))


def extract_sources(docs):
    """검색된 청크의 출처를 중복 제거해서 리스트로"""
    seen, sources = set(), []
    for d in docs:
        src = d.metadata.get("source", "unknown")
        if src not in seen:
            seen.add(src)
            sources.append(src)
    return sources


# 검색 결과를 두 곳에 동시에 사용 — context(문자열), sources(리스트)
# 그래서 retriever 를 한 번만 호출하고 둘 다에 활용
def retrieve_and_split(inputs):
    docs = retriever.invoke(inputs["question"])
    return {
        "question": inputs["question"],
        "context":  format_docs_with_index(docs),
        "sources":  extract_sources(docs),
    }


# answer 생성 후 sources 와 합쳐서 최종 텍스트 만들기
def append_sources(d):
    src_lines = "\n".join(f"  - {s}" for s in d["sources"])
    return f"{d['answer']}\n\n📚 참고 문서:\n{src_lines}"

def debug_prompt(prompt_value):
    print("\n\n========== LLM 입력 Prompt ==========")
    for msg in prompt_value.messages:
        print(f"\n[{msg.type.upper()}]")
        print(msg.content)
    print("====================================\n\n")
    return prompt_value

chain = (
    RunnableLambda(retrieve_and_split)
    | RunnablePassthrough.assign(
        answer=(prompt 
                | RunnableLambda(debug_prompt)    # <-- 중간 결과 출력
                | llm 
                | StrOutputParser()
        )
    )
    | RunnableLambda(append_sources)
)

print(chain.invoke({"question": "NVMe 의 인터페이스가 뭐고 어떤 장점이 있어?"}))


# retrieve_and_split
#         ↓
# prompt ← 여기서 {context}, {question}이 실제 값으로 채워짐
#         ↓
# debug_prompt ← 여기서 완성된 prompt 출력
#         ↓
# llm
#         ↓
# StrOutputParser
