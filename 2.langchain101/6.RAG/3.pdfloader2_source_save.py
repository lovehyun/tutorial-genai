# pip install pypdf

from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

import os
import json

# 환경 변수 로드
load_dotenv(dotenv_path='../.env')

# 파일 경로 설정
PDF_FILENAME = './DATA/Python_시큐어코딩_가이드(2023년_개정본).pdf'
VECTOR_DB_PATH = './DATA/vector_db_secure_coding.json'
store = None

def create_vector_db(file_path):
    # PDF 로드
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"총 {len(documents)} 페이지의 문서가 로드되었습니다.")
    except Exception as e:
        print(f"PDF 파일을 로드하는 동안 오류가 발생했습니다: {e}")
        documents = []

    # 문서 내용 확인 (첫 번째 내용이 있는 페이지 출력)
    first_content_page = None
    for i, doc in enumerate(documents):
        if doc.page_content.strip():  # 내용이 있는지 확인
            first_content_page = (i + 1, doc.page_content)
            break
    
    if first_content_page:
        page_num, first_page_content = first_content_page
        print(f"내용이 있는 첫 번째 페이지 번호: {page_num}")
        print(f"내용이 있는 첫 번째 페이지 내용: {first_page_content[:500]}...")  # 500자까지 출력
    else:
        print("문서에서 내용이 있는 페이지를 찾을 수 없습니다.")

    # 텍스트 분할 설정
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n\n",
        chunk_size=2000,
        chunk_overlap=500,
    )

    # 텍스트 분할 실행
    texts = text_splitter.split_documents(documents)

    # 중복 제거
    unique_texts = list({text.page_content: text for text in texts}.values())

    # 임베딩 생성
    embeddings = OpenAIEmbeddings()

    # 벡터 DB 생성
    store = Chroma.from_documents(unique_texts, embeddings, collection_name="secure_coding_python")

    # 벡터 스토어 데이터를 파일에 저장
    store_data = {
        'texts': [doc.page_content for doc in unique_texts],
        'embeddings': [embeddings.embed_query(doc.page_content) for doc in unique_texts],
        'metadata': [doc.metadata for doc in unique_texts]
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
    store = Chroma.from_documents(documents, embeddings, collection_name="secure_coding_python")
    return store

# 벡터 데이터베이스 파일이 존재하는지 확인하고, 존재하지 않으면 생성
if os.path.exists(VECTOR_DB_PATH):
    store = load_vector_db()
else:
    store = create_vector_db(PDF_FILENAME)

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

# 질문 및 응답
try:
    result = answer_question("시큐어코딩의 주요 기법들에 대해서 리스트 형태로 요약해서 설명해줘")
    print(result)
    
    result = answer_question("입력데이터 검증 및 오류 기법에 대해서 상세히 설명해줘")
    print(result)
except Exception as e:
    print(f"질문을 처리하는 동안 오류가 발생했습니다: {e}")
