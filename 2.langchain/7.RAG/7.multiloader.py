from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain.schema import Document
from langchain_chroma import Chroma

load_dotenv()

# 1. 기본 설정
PERSIST_DIR = "./chroma_db"
COLLECTION_NAMES = ["secure_coding_python", "nvme"]

# 2. 컬렉션 로딩
embeddings = OpenAIEmbeddings()
collections = {
    name: Chroma(
        collection_name=name,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR
    )
    for name in COLLECTION_NAMES
}

# 3. GPT 체인 구성
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
prompt = ChatPromptTemplate.from_template("""
다음 문서들을 참고하여 질문에 답변해주세요:

문서들:
{context}

질문:
{question}
""")

chain = (
    prompt
    | llm
    | StrOutputParser()
)

# 4. 문서 검색 함수 (타겟 있으면 해당 컬렉션만, 없으면 전체)
def search_documents(question: str, k=3, target=None) -> list[Document]:
    if target:
        print(f"'{target}' 컬렉션에서 검색합니다.")
        return collections[target].similarity_search(question, k=k)
    else:
        print("모든 컬렉션에서 통합 검색합니다.")
        docs = []
        for store in collections.values():
            docs.extend(store.similarity_search(question, k=2))
        return docs

# 5. 질문 실행 함수
def ask(question: str, target_collection: str = None):
    docs = search_documents(question, target=target_collection)

    context = "\n\n".join([doc.page_content for doc in docs])
    response = chain.invoke({"context": context, "question": question})

    print(f"\n질문: {question}")
    if target_collection:
        print(f"대상 컬렉션: {target_collection}")
    print(f"참고 문서 수: {len(docs)}")
    print(f"GPT 응답:\n{response}\n")

# 6. 테스트
ask("NVMe의 특징은?", target_collection="nvme")     # 단일 컬렉션 검색
ask("보안 로그 분석이란?", target_collection=None)   # 전체 컬렉션 검색
