import os
import json
from dotenv import load_dotenv

from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

load_dotenv(dotenv_path='../.env')

VECTOR_DB_PATH = './vector_db.json'
store = None

def create_vector_db(file_path):
    # 파일에서 문서를 로드하고 인코딩이 올바르게 처리되었는지 확인
    loader = TextLoader(file_path, encoding='euckr')
    documents = loader.load()

    # (옵셔널) 문서에 메타데이터가 없으면 추가
    documents = [Document(page_content=doc.page_content, metadata={"source": file_path}) for doc in documents]

    # 문서를 관리 가능한 크기로 나누면서 메타데이터 유지
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # 문서 청크에 대한 임베딩 생성
    embeddings = OpenAIEmbeddings()

    # Chroma라는 오픈 소스 임베딩 데이터베이스에 임베딩 저장
    store = Chroma.from_documents(texts, embeddings, collection_name="nvme")

    # 벡터 스토어를 파일에 저장
    store_data = {
        'texts': [doc.page_content for doc in texts],
        'embeddings': [embeddings.embed_query(doc.page_content) for doc in texts],
        'metadata': [doc.metadata for doc in texts]
    }
    with open(VECTOR_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(store_data, f)

    return store

def load_vector_db():
    global store
    with open(VECTOR_DB_PATH, 'r', encoding='utf-8') as f:
        store_data = json.load(f)

    documents = [Document(page_content=text, metadata=meta) for text, meta in zip(store_data['texts'], store_data['metadata'])]
    embeddings = OpenAIEmbeddings()
    store = Chroma.from_documents(documents, embeddings, collection_name="nvme")
    return store

# 벡터 데이터베이스 파일이 존재하는지 확인하고, 존재하지 않으면 생성
if os.path.exists(VECTOR_DB_PATH):
    store = load_vector_db()
else:
    store = None

# 올바른 모델 이름과 온도로 언어 모델 초기화
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)

# 응답에 출처를 포함하는 QA 체인 로드
qa_chain = load_qa_with_sources_chain(llm, chain_type="map_reduce")

def answer_question(question):
    # 스토어에서 문서 검색
    docs = store.similarity_search(question, k=5)  # 컨텍스트 길이를 줄이기 위해 상위 5개 문서로 제한
    
    # QA 체인 실행
    response = qa_chain.invoke({"input_documents": docs, "question": question})
    
    # 응답과 출처 문서 추출
    result = response['output_text'].strip()
    if "SOURCES:" in result:
        result, sources_info = result.split("SOURCES:", 1)
        result = result.strip()
        sources_info = sources_info.strip()
    else:
        sources_info = "출처 정보를 찾을 수 없습니다."
    
    # 결과나 출처 정보가 없으면 기본 메시지 반환
    if not result or not sources_info or result.lower() == "i don't know.":
        return f"질문: {question}\n응답: 이 질문에 대한 답변을 제공할 수 없습니다.\n"

    # 결과와 출처 정보를 반환
    return f"질문: {question}\n응답: {result}\n출처:{sources_info}\n"
