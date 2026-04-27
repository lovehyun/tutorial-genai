import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

VECTOR_DB = './chroma_db'
COLLECTION_NAME = 'my-data'
DATA_DIR = './DATA'
store = None

def get_vector_store():
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
    loader = PyPDFLoader(file_path) # 기본 metadata["source"] 및 metadata["page"] 가 추가됨
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
