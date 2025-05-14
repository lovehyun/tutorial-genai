# pip install pypdf langchain-chroma

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma

# 1. .env에서 OpenAI API 키 로드
load_dotenv(dotenv_path='../.env')

# 2. PDF 파일 로드 (LangChain의 PyPDFLoader 사용)
pdf_filename = './DATA/Python_시큐어코딩_가이드(2023년_개정본).pdf'
loader = PyPDFLoader(pdf_filename)
pages = loader.load()  # 페이지별로 문서 객체 반환

# 3. 로드된 페이지 수 및 첫 페이지 일부 확인
print(f"총 페이지 수: {len(pages)}")
print(f"1페이지 내용 샘플:\n{pages[1].page_content}")

# 4. 문서 분할 (청크 단위: 2000자, 중복: 500자, 두 문단 단위로 나눔)
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
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
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 8. 문서 기반 질문응답을 위한 프롬프트 템플릿 정의
template = """주어진 문서 내용을 바탕으로 질문에 답변해주세요.

문서 내용: {context}

질문: {question}

답변 작성 규칙:
1. 명확하고 구조적으로 답변을 작성하세요
2. 기술적 내용은 실제 예시를 포함하여 설명하세요
3. 보안 관련 내용은 위험성과 대응방안을 함께 설명하세요
4. 리스트 형태로 요청된 경우 번호를 매겨 구분하여 작성하세요
"""

prompt = ChatPromptTemplate.from_template(template)

# 9. 검색기 설정 (문서 5개 검색 후 사용)
retriever = store.as_retriever(search_kwargs={"k": 5})

# 10. 전체 체인 구성: 문서검색 → 프롬프트 생성 → GPT 응답 → 문자열로 출력
chain = (
    {"context": retriever, "question": lambda x: x}
    | prompt
    | llm
    | StrOutputParser()
)

# 11. 질문을 입력하면 답변을 출력하는 함수 정의
def ask_question(question):
    try:
        response = chain.invoke(question)
        print(f"\n질문: {question}")
        print(f"답변: {response}\n")
    except Exception as e:
        print(f"오류 발생: {str(e)}")

# 12. 예시 질문 실행 (시큐어코딩 가이드 문서 기반)
ask_question("시큐어코딩의 주요 기법들에 대해서 리스트 형태로 요약해서 설명해줘")
ask_question("입력데이터 검증 및 오류 기법에 대해서 상세히 설명해줘")
