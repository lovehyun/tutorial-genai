# pip install pypdf langchain-chroma
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# 1. .env 파일에서 OpenAI API 키 로드
load_dotenv(dotenv_path='../.env')

# 2. PDF 파일 및 Chroma 저장 경로 설정
PDF_FILENAME = './DATA/Python_시큐어코딩_가이드(2023년_개정본).pdf'
PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "secure_coding_python"

# 3. Chroma DB를 새로 생성하는 함수
def create_vector_db(file_path):
    try:
        # PDF 문서 로딩
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"총 {len(documents)} 페이지의 문서가 로드되었습니다.")

        # 각 페이지에 메타데이터 추가: 파일명, 페이지번호 (pypdf 가 이미 해줌)
        # 단, ./DATA/ 라는 패스 제거하고 다시 파일명만으로 설정.
        for doc in documents:
            doc.metadata["source"] = os.path.basename(file_path)
            if "page" not in doc.metadata:
                doc.metadata["page"] = doc.metadata.get("page", 0) + 1

    except Exception as e:
        print(f"PDF 파일을 로드하는 동안 오류가 발생했습니다: {e}")
        return None

    # 첫 번째 내용 있는 페이지 출력
    for doc in documents:
        if doc.page_content.strip():
            print(f"\n---\n내용이 있는 첫 번째 페이지 번호: {doc.metadata['page']}")
            print(f"내용 샘플: {doc.page_content[:100]}...\n---\n")
            break

    # 문서 분할 (tiktoken 기준, 중복 500자)
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        separator="\n\n",
        chunk_size=2000,
        chunk_overlap=500,
    )
    texts = text_splitter.split_documents(documents)

    # OpenAI 임베딩 생성 및 Chroma에 저장
    embeddings = OpenAIEmbeddings()
    store = Chroma.from_documents(texts, embeddings, collection_name=COLLECTION_NAME, persist_directory=PERSIST_DIR)
    return store

# 4. 기존 Chroma DB 로드
def load_vector_db():
    embeddings = OpenAIEmbeddings()
    store = Chroma(collection_name=COLLECTION_NAME, embedding_function=embeddings, persist_directory=PERSIST_DIR)
    return store

# 5-1. DB내에 문서 존재 여부 확인 (파일만 체크하면 한계...)
# import os
# if os.path.exists(PERSIST_DIR):
#     print("기존 데이터베이스를 로딩합니다.")
#     store = load_vector_db()
# else:
#     print("새로운 데이터베이스를 생성합니다.")
#     store = create_vector_db()

# 5-2. 파일/컬렉션 확인
def check_collection_exists(persist_dir, collection_name):
    try:
        embeddings = OpenAIEmbeddings()
        store = Chroma(collection_name=collection_name, embedding_function=embeddings, persist_directory=persist_dir)
        # 임의 호출: 문서 일부 조회 (아무거나 달라고 요청, 문서가 많으면 1개만 달라고 요청)
        # results = store.get()
        results = store.get(limit=1)
        
        # 빈 컬렉션이라면 (len(results["ids"]) == 0)
        return bool(results["ids"])
    
    except Exception as e:
        print(f"컬렉션 존재 여부 확인 중 오류: {e}")
        return False

if check_collection_exists(PERSIST_DIR, COLLECTION_NAME):
    print(f"기존 데이터베이스를 로딩합니다. 컬랙션명: {COLLECTION_NAME}")
    store = load_vector_db()
else:
    print(f"새로운 데이터베이스를 생성합니다.")
    store = create_vector_db(PDF_FILENAME)
    if store is None:
        raise Exception("벡터 DB 생성에 실패했습니다.")


# 6. ChatGPT LLM 초기화 (정확한 응답을 위한 temperature 0에 가깝게 설정)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# 7. 질문 프롬프트 정의 (출처 포함, 구조화된 규칙 포함)
template = """주어진 문서 내용을 바탕으로 질문에 답변해주세요.

문서 내용: 
{context}

질문: {question}

답변 작성 규칙:
1. 명확하고 구조적으로 답변을 작성하세요
2. 시큐어 코딩 관련 내용은 실제 코드 예시나 구체적인 대응방안을 포함하세요
3. 리스트 형태로 요청된 경우, 번호를 매겨 구분하여 작성하세요
4. 보안 취약점과 그에 대한 대응방안을 함께 설명하세요
5. 답변에 사용한 출처를 포함해주세요
"""

prompt = ChatPromptTemplate.from_template(template)

# 8. 검색기 구성 (문서 중 관련성 높은 5개 청크 검색)
retriever = store.as_retriever(search_kwargs={"k": 5})

# 8-2. 문서와 메타데이터를 통한 출처를 함께 처리하는 함수 정의
def format_docs_with_sources(docs):
    """각 문서 내용 하단에 해당 출처 정보를 직접 연결"""
    formatted_docs = []
    sources = [] # 파일명과 페이지 정보 함께 저장
    
    for doc in docs:
        # 문서 내용
        content = doc.page_content
        
        # 해당 문서의 출처 정보
        page_num = doc.metadata.get('page', '알 수 없음')
        source_file = doc.metadata.get('source', '알 수 없음').split('/')[-1]  # 파일명만 추출
        
        # 파일명과 페이지 함께
        source_info = f"[출처: {source_file} - 페이지 {page_num + 1}]"
        sources.append(source_info)
        
        # 문서 내용 + 출처 정보를 함께 포맷팅
        formatted_chunk = f"{content}\n{source_info}"
        formatted_docs.append(formatted_chunk)
    
    return {
        'context': '\n\n---\n\n'.join(formatted_docs),  # 청크 간 구분자 추가
        'sources': list(set(sources))  # 중복 제거된 출처 목록 (필요시 추가 활용)
    }
    
# 8-3. 전체 체인 구성: 문서검색 → 프롬프트 생성 → GPT 응답 → 문자열로 출력
chain_rawdata = (
    {"context": retriever, "question": RunnablePassthrough()}  # "question": lambda x: x}
    | prompt
    | llm
    | StrOutputParser()
)

chain2_strdata = (
    {"context": retriever | (lambda docs: format_docs_with_sources(docs)['context']), 
     "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 11. 질문을 받아 답변 + 출처를 포맷에 맞게 반환하는 함수 (11-1, 11-2는 생략가능. 바로 11-3부터 실행 가능.)
def answer_question(question):
    try:
        # 분석용 -->
        # 11-1. 관련 문서 직접 검색 (Document() 객체를 전체 반환. LangChain 에는 이 중 page_content만 들어감.)
        docs = retriever.invoke(question)

        # 11-2. context 구성: 문서 내용 + 출처 함께 표시
        context = ""
        sources = []
        for i, doc in enumerate(docs, start=1):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "N/A")
            sources.append(f"{source} (page {page})")
            context += f"[출처: {source}, 페이지: {page}]\n{doc.page_content.strip()}\n\n"
        
        print(f"\n--- GPT가 참고한문서---\n{context}\n-----\n")
        # 분석용 <--
        
        # 11-3. 체인 실행
        result = chain2_strdata.invoke(question) # 체인을 통해서 context 수행 (7-1이 자동으로 추출)
        answer = result.strip()

        # 11-5. 최종 출력
        print(f"\n---\nQ. 질문: {question}\n\nA. 답변:\n{answer}")
        # for i, doc in enumerate(docs, start=1):
        #     source = doc.metadata.get("source", "unknown")
        #     page = doc.metadata.get("page", "N/A")
        #     sources.append(f"- {source} (page {page})")  # 참고문서 앞에 " - " 추가
        #     context += f"[출처: {source}, 페이지: {page}]\n{doc.page_content.strip()}\n\n"

    except Exception as e:
        return f"질문: {question}\n오류 발생: {str(e)}\n"


# 12. 테스트 질문 실행
answer_question("시큐어코딩의 주요 기법들에 대해서 리스트 형태로 요약해서 설명해줘")
# answer_question("입력데이터 검증 및 오류 기법에 대해서 상세히 설명해줘")
