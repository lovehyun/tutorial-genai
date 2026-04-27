# services/vectorstore.py
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

class VectorStore:
    def __init__(self, persist_dir=VECTOR_DB, collection=COLLECTION_NAME):
        self.persist_dir = persist_dir
        self.collection = collection
        self.store = None
        self._create_dirs()

    def _create_dirs(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(self.persist_dir, exist_ok=True)

    def initialize(self):
        if os.listdir(self.persist_dir):
            print("데이터베이스를 초기화 중입니다.")
            self.store = Chroma(
                collection_name=self.collection,
                embedding_function=OpenAIEmbeddings(),
                persist_directory=self.persist_dir
            )
            print("데이터베이스 로딩이 완료되었습니다.")

    def add_pdf(self, file_path: str):
        documents = PyPDFLoader(file_path).load()
        texts = RecursiveCharacterTextSplitter(
            separators="\n\n",chunk_size=1000, chunk_overlap=100
        ).split_documents(documents)

        embeddings = OpenAIEmbeddings()

        if self.store:
            # 기존 DB에 추가
            self.store.add_documents(texts)
        else:
            # 새로 생성
            self.store = Chroma.from_documents(
                texts, embeddings,
                collection_name=self.collection,
                persist_directory=self.persist_dir
            )

    def search(self, query: str, k: int = 5):
        if not self.store:
            return []
        return self.store.similarity_search(query, k=k)
