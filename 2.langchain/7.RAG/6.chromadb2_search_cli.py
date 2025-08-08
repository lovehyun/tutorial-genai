from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# Chroma DB 설정
PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "secure_coding_python"

# 임베딩 모델 준비
embeddings = OpenAIEmbeddings()

# Chroma 벡터 DB 로드
store = Chroma(collection_name=COLLECTION_NAME, embedding_function=embeddings, persist_directory=PERSIST_DIR)

def show_db_info():
    """ChromaDB의 기본 정보를 출력"""
    count = store._collection.count()
    print(f"저장된 문서 개수: {count}")
    print("-" * 50)

def show_sample_docs(limit=10):
    """저장된 문서 샘플을 출력"""
    results = store._collection.get(include=["documents", "metadatas"], limit=limit)
    ids = results["ids"]
    docs = results["documents"]
    metadatas = results["metadatas"]

    print(f"=== 저장된 문서 샘플 (최대 {limit}개) ===")
    for i, doc in enumerate(docs):
        print(f"[문서]: {i+1}")
        print(f"[UUID]: {ids[i]}")
        print(f"[내용 (앞 200자)]: {doc[:200]}...")
        print(f"[메타데이터]: {metadatas[i]}")
        print("---\n")
    print("-" * 50)

def search_documents(query, k=5, show_content_length=300):
    """질문으로 유사 문서 검색 및 결과 출력"""
    print(f"=== '{query}' 검색 결과 (상위 {k}개) ===")
    
    docs = store.similarity_search(query, k=k)
    
    if not docs:
        print("검색 결과가 없습니다.")
        return docs
    
    for i, doc in enumerate(docs):
        print(f"[문서]: {i+1}")
        # Document 객체에 id 속성이 없을 수 있으므로 안전하게 처리
        doc_id = getattr(doc, 'id', 'ID 없음')
        print(f"[문서ID]: {doc_id}")
        print(f"[내용 (앞 {show_content_length}자)]: {doc.page_content[:show_content_length]}...")
        print(f"[메타데이터]: {doc.metadata}")
        print("---\n")
    
    print("-" * 50)
    return docs

def search_with_scores(query, k=5):
    """점수와 함께 유사 문서 검색"""
    print(f"=== '{query}' 검색 결과 (점수 포함, 상위 {k}개) ===")
    
    docs_with_scores = store.similarity_search_with_score(query, k=k)
    
    if not docs_with_scores:
        print("검색 결과가 없습니다.")
        return docs_with_scores
    
    for i, (doc, score) in enumerate(docs_with_scores):
        print(f"[문서]: {i+1}")
        print(f"[유사도 점수]: {score:.4f}")
        print(f"[내용 (앞 300자)]: {doc.page_content[:300]}...")
        print(f"[메타데이터]: {doc.metadata}")
        print("---\n")
    
    print("-" * 50)
    return docs_with_scores

def interactive_search():
    """대화형 검색 모드"""
    print("=== 대화형 검색 모드 ===")
    print("검색하고 싶은 내용을 입력하세요. (종료: 'quit' 또는 'exit')")
    
    while True:
        query = input("\n검색어를 입력하세요: ").strip()
        
        if query.lower() in ['quit', 'exit', '종료']:
            print("검색을 종료합니다.")
            break
            
        if not query:
            print("검색어를 입력해주세요.")
            continue
            
        try:
            # 검색 옵션 선택
            print("\n검색 옵션:")
            print("1. 일반 검색 (기본)")
            print("2. 점수 포함 검색")
            
            option = input("옵션을 선택하세요 (1 또는 2, 기본값: 1): ").strip()
            
            if option == "2":
                search_with_scores(query)
            else:
                search_documents(query)
                
        except Exception as e:
            print(f"검색 중 오류 발생: {e}")

# 사용 예시
if __name__ == "__main__":
    # 1. DB 기본 정보 확인
    show_db_info()
    
    # 2. 저장된 문서 샘플 확인
    # show_sample_docs(5)
    
    # 3. 특정 검색어로 검색
    # search_documents("시큐어 코딩")
    # search_documents("SQL 인젝션")
    
    # 4. 점수와 함께 검색
    search_with_scores("입력 데이터 검증", k=2)
    
    # 5. 대화형 검색 (필요시 주석 해제)
    # interactive_search()
