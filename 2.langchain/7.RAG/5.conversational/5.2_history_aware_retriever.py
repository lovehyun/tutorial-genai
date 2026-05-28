"""
History-aware Retriever — 대화 맥락을 보고 검색 쿼리를 다시 만든다.
이 예제: "그거 PCIe 몇 세대?" 같은 후속 질문이 정확히 검색되도록 합니다.

핵심 아이디어:
  검색 직전에 LLM 이 "이전 대화 + 이번 질문 → 독립적인 검색 쿼리" 로 재작성.
  예) history=[NVMe 설명], question="그거 PCIe 몇 세대?"
      → 재작성: "NVMe 의 PCIe 버전"
"""

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import create_history_aware_retriever

load_dotenv()

# (벡터 스토어 준비 — 5.1 과 동일)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(
    collection_name="conv_rag",
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

# 1) 쿼리 재작성용 prompt — history + 이번 질문 → 독립 쿼리
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "대화 이력과 이번 질문이 주어집니다. 이번 질문을 이력 없이도 이해될 수 있는 "
     "독립적인 검색 쿼리로 다시 써주세요. 답하지 말고 쿼리만 출력하세요."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# 2) history-aware retriever — 내부적으로 rewrite_prompt → llm → retriever 흐름
history_aware = create_history_aware_retriever(llm, retriever, rewrite_prompt)


# 3) 직접 동작 확인
chat_history = [
    HumanMessage(content="NVMe 가 뭐야?"),
    AIMessage(content="NVMe 는 PCIe 를 사용하는 SSD 인터페이스 규격입니다."),
]

followup = "그거 PCIe 몇 세대를 쓰는데?"
print(f"이전 대화: NVMe 설명")
print(f"이번 질문: {followup}\n")

docs = history_aware.invoke({"chat_history": chat_history, "input": followup})
print(f"history-aware 가 검색한 문서들 ({len(docs)} 개):")
for d in docs:
    print(f"  → {d.page_content[:80]}...")
print("\n→ '그거' 가 NVMe 를 가리키는 것을 LLM 이 파악해서 적절한 쿼리로 변환했음.")
