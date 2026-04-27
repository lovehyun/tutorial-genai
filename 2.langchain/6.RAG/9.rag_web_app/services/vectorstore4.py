import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

VECTOR_DB = './chroma_db'
DATA_DIR = './DATA'
COLLECTION_NAME = 'my-data'
store = None

# 저장된 store 가져오기
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
    
    # metadata["source"]를 basename(파일명)으로 덮어쓰기
    for doc in documents:
        doc.metadata["source"] = os.path.basename(file_path)

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
        
        store.add_documents(texts) # 내용 추가
    else: # 없으면 새로 생성
        store = Chroma.from_documents(
            texts,
            embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=VECTOR_DB
        )

    return store

def preview_file_entries(file_name: str):
    """특정 source 메타데이터를 가진 벡터 문서들을 미리 조회하고 출력"""
    global store
    if store is None:
        print("벡터 스토어가 초기화되지 않았습니다.")
        return

    # 내부 컬렉션에서 조건에 맞는 벡터 가져오기
    result = store._collection.get(where={"source": file_name})

    ids = result.get("ids", [])
    documents = result.get("documents", [])
    metadatas = result.get("metadatas", [])

    print(f"파일명 '{file_name}'에 해당하는 벡터 {len(documents)}개가 존재합니다.")
    for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
        print(f"\n문서 {i}")
        print(f"내용: {doc[:50]}...")  # 앞 50자만 표시
        print(f"메타데이터: {meta}")
        
def delete_file(file_name: str):
    """지정한 파일명(source)과 매칭되는 벡터를 삭제하고, 실제 PDF/Text 파일도 지움."""
    # 1. 컬렉션 내에서 metadata.source == file_name 인 벡터 삭제
    # 내부 collection 객체를 직접 삭제
    # preview_file_entries(file_name)
    store._collection.delete(where={"source": file_name})
    
    # persist 옵션 사용중이면 persist() 호출
    if hasattr(store, "persist"):
        store.persist()
    
    # 2. DATA 디렉토리의 원본 파일 삭제
    path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(path):
        os.remove(path)

def list_files():
    """DATA_DIR에 남아있는 파일 목록 리턴"""
    files = [f for f in os.listdir(DATA_DIR)
            if os.path.isfile(os.path.join(DATA_DIR, f))]
    return files
