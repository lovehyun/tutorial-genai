"""
완전한 대화형 RAG — history-aware retriever + 메모리 결합.
이 예제: 여러 턴에 걸친 자연스러운 대화에서 정확한 검색 + 답변을 한다.

조립:
  RunnableWithMessageHistory
    └ history_aware_retriever 로 검색 (대화 맥락 반영)
    └ stuff documents chain 으로 답변 생성
  → 같은 session_id 안에서 multi-turn 자유롭게.
"""

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

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


# 1) 쿼리 재작성용 prompt (5.2 와 동일)
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "대화 이력과 이번 질문이 주어집니다. 이번 질문을 이력 없이도 이해될 수 있는 "
     "독립적인 검색 쿼리로 다시 써주세요. 답하지 말고 쿼리만 출력하세요."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
history_aware = create_history_aware_retriever(llm, retriever, rewrite_prompt)

# 2) 답변 생성용 prompt
qa_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 친절한 문서 기반 QA 어시스턴트입니다. 아래 문서만 참고해 답하세요. "
     "문서에 없으면 '모르겠습니다'.\n\n문서:\n{context}"),
    MessagesPlaceholder("chat_history"),
    ("user", "{input}"),
])
doc_chain = create_stuff_documents_chain(llm, qa_prompt)

# 3) 두 체인 결합 — 검색은 history-aware, 답변은 history 도 같이 봄
rag_chain = create_retrieval_chain(history_aware, doc_chain)


# 4) 세션 메모리 결합
sessions: dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in sessions:
        sessions[session_id] = InMemoryChatMessageHistory()
    return sessions[session_id]

conversational_rag = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


# 5) 멀티턴 대화 — '그거', '그건' 같은 후속 질문이 정확히 동작
def chat(question):
    print(f"\nQ: {question}")
    out = conversational_rag.invoke(
        {"input": question},
        config={"configurable": {"session_id": "demo"}},
    )
    print(f"A: {out['answer']}")


chat("NVMe 가 뭐야?")
chat("그거 PCIe 몇 세대 쓰는데?")    # ← 5.1 에서는 실패한 질문
chat("그럼 SATA SSD 와 속도 차이는?")
