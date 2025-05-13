from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# Chroma DB 설정
PERSIST_DIR = "./chroma_db"  # 저장된 디렉토리
COLLECTION_NAME = "secure_coding_python"  # 확인할 컬렉션 이름

# 임베딩 모델 준비
embeddings = OpenAIEmbeddings()

# Chroma 벡터 DB 로드
store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR
)

# 저장된 문서 개수 확인
count = store._collection.count()
print(f"저장된 문서 개수: {count}")

# 전체 문서 로드 (최대 10개)
results = store._collection.get(include=["documents", "metadatas"], limit=10)
ids = results["ids"]
docs = results["documents"]
metadatas = results["metadatas"]

for i, doc in enumerate(docs):
    print(f"[문서]: {i+1}")
    print(f"[UUID]: {ids[i]}")
    print(f"[내용 (앞 200자)]: {doc[:200]}...")
    print(f"[메타데이터]: {metadatas[i]}")
    print("---\n")

print("-" * 50)

# 상위 5개 문서 조회 및 내용 출력
docs = store.similarity_search("시큐어 코딩", k=5)

for i, doc in enumerate(docs):
    print(f"[문서]: {i+1}")
    print(f"[내용 (앞 300자)]: {doc.page_content[:300]}")
    print(f"[메타데이터]: {doc.metadata}")
    print("---\n")
