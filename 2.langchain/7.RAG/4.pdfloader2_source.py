# pip install pypdf langchain-chroma

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# 1. .env에서 OpenAI API 키 로드
load_dotenv(dotenv_path='../.env')

# 2. PDF 파일 로드 (LangChain의 PyPDFLoader 사용)
pdf_filename = './DATA/Python_시큐어코딩_가이드(2023년_개정본).pdf'
loader = PyPDFLoader(pdf_filename)
pages = loader.load()  # 페이지별로 문서 객체 반환

# 3. 로드된 페이지 수 및 첫 페이지 일부 확인
# print(f"총 페이지 수: {len(pages)}")
# print(f"2페이지 내용 샘플:\n{pages[1].page_content}")
# print(f"2페이지 메타데이터:\n{pages[1].metadata}")

# 4. 문서 분할 (청크 단위: 2000토큰, 중복: 500토큰, 두 문단 단위로 나눔)
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    # separators=["\n\n", "\n", " ", ""],  # 문단→줄→공백→문자 순서로 시도
    separator="\n\n",        # 문단 단위 기준
    chunk_size=2000,         # 최대 2000자
    chunk_overlap=500        # 중복 500자 포함
)
texts = text_splitter.split_documents(pages)

# 5. OpenAI Embedding 모델로 청크 벡터 생성
embeddings = OpenAIEmbeddings()

# 6. ChromaDB에 문서 벡터 저장 (로컬 디렉토리에 저장됨)
store = Chroma.from_documents(
    texts, 
    embeddings, 
    collection_name="secure_coding_python",
    persist_directory="./chroma_db"  # 저장 위치
)


# 7. OpenAI ChatGPT 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# 8. 문서 기반 질문응답을 위한 프롬프트 템플릿 정의
template = """주어진 문서 내용을 바탕으로 질문에 답변해주세요.

문서 내용: 
{context}

질문: {question}

답변 작성 규칙:
1. 명확하고 구조적으로 답변을 작성하세요
2. 기술적 내용은 실제 예시를 포함하여 설명하세요
3. 보안 관련 내용은 위험성과 대응방안을 함께 설명하세요
4. 리스트 형태로 요청된 경우 번호를 매겨 구분하여 작성하세요
5. 답변에 사용한 출처를 포함해주세요
"""

prompt = ChatPromptTemplate.from_template(template)

# 9. 검색기 설정 (문서 5개 검색 후 사용)
retriever = store.as_retriever(search_kwargs={"k": 5})

# 10. 문서와 메타데이터를 통한 출처를 함께 처리하는 함수 정의
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

# 11. 전체 체인 구성: 문서검색 → 프롬프트 생성 → GPT 응답 → 문자열로 출력
chain = (
    {"context": retriever | (lambda docs: format_docs_with_sources(docs)['context']), 
     "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 12. 질문을 입력하면 답변을 출력하는 함수 정의 (12-2. 만 필수, 나머지 두개는 선택사항)
def answer_question(question):
    try:
        # 12-1. 관련 문서들 검색
        retrieved_docs = retriever.invoke(question)
        docs_info = format_docs_with_sources(retrieved_docs)

        # 12-2. GPT 응답 생성
        response = chain.invoke(question)
        print(f"\n질문: {question}\n")
        print(f"답변: \n{response}\n")
        
        # 12-3. 각 문서의 상세 출처 정보 표시
        print(f"참고한 문서 전체 출처:")
        for i, source in enumerate(docs_info['sources'], 1):
            print(f"  {i}. {source}")
            
        print("-" * 50)
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")


# 13. 예시 질문 실행 (시큐어코딩 가이드 문서 기반)
answer_question("시큐어코딩의 주요 기법들에 대해서 리스트 형태로 요약해서 설명해줘")
answer_question("입력데이터 검증 및 오류 기법에 대해서 상세히 설명해줘")
