import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_chroma import Chroma

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

VECTOR_DB = './chroma_db'
COLLECTION_NAME = 'my-data'
DATA_DIR = './DATA'
store = None
    
def get_store():
    return store

# 초기 로딩 함수
def initialize_vector_db():
    global store
    if os.path.exists(VECTOR_DB) and os.listdir(VECTOR_DB):
        store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=OpenAIEmbeddings(),
            persist_directory=VECTOR_DB
        )

    # DATA 디렉토리가 존재하지 않으면 생성
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def create_vector_db(file_path):
    global store
    
    # 1. PDF 문서 로딩
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # 2. 문서 분할
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # 3. 임베딩 모델
    embeddings = OpenAIEmbeddings()

    # 4. 저장 폴더 없으면 생성
    if not os.path.exists(VECTOR_DB):
        os.makedirs(VECTOR_DB)

    # 5. 기존 DB가 있으면 불러와서 추가
    if os.path.isdir(VECTOR_DB) and os.listdir(VECTOR_DB):
        store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=VECTOR_DB
        )
        store.add_documents(texts)
    else: # 없으면 새로 생성
        store = Chroma.from_documents(
            texts,
            embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=VECTOR_DB
        )

    return store


# LLM 준비 (gpt-3.5-turbo 기반)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 출력 파서
output_parser = StrOutputParser()

# 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_template("""
당신은 문서 기반 질문 응답 시스템입니다.
다음 문서를 참고하여 사용자의 질문에 답변해 주세요. 
모르겠다면 절대로 지어내지 말고 "모르겠습니다"라고 답하세요.

문서:
{context}

질문:
{question}

답변:
""")

def answer_question(question: str) -> str:
    global store
    if store is None:
        return "문서가 로드되지 않았습니다. 먼저 PDF를 업로드해주세요."

    # 1. 벡터 DB에서 유사 문서 검색
    docs = store.similarity_search(question, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])

    # 2. 체인 구성: [프롬프트] → [LLM] → [파서]
    chain = prompt | llm | output_parser

    # 3. 실행
    try:
        result = chain.invoke({
            "context": context,
            "question": question
        })
    except Exception as e:
        return f"GPT 처리 중 오류: {e}"

    return f"질문: {question}\n응답: {result.strip()}"
