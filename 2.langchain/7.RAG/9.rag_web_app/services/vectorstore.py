import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

VECTOR_DB = './chroma_db'
COLLECTION_NAME = 'my-data'
DATA_DIR = './DATA'
store = None

# 초기 로딩 함수
def initialize_vector_db():
    global store
    if os.path.exists(VECTOR_DB) and os.listdir(VECTOR_DB):
        # 기존 DB파일이 있으면, 로딩
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
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # 2. 문서 분할
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # 3. 임베딩 모델
    embeddings = OpenAIEmbeddings()

    # 4. 기존 DB가 있으면 불러와서 추가
    # if os.path.isdir(VECTOR_DB) and os.listdir(VECTOR_DB):
    if store:
        store.add_documents(texts)
    else: # 없으면 새로 생성
        store = Chroma.from_documents(
            texts,
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=VECTOR_DB
        )

    return store


# 1. 프롬프트 템플릿 정의
# prompt = ChatPromptTemplate.from_template("""
# 당신은 문서 기반 질문 응답 시스템입니다.
# 다음 문서를 참고하여 사용자의 질문에 답변해 주세요. 
# 모르겠다면 절대로 지어내지 말고 "모르겠습니다"라고 답하세요.
#
# 문서:
# {context}
#
# 질문:
# {question}
#
# 답변:
# """)

prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "당신은 문서 기반 질문 응답 시스템입니다. "
     "아래 '문서' 내용을 참고하여 질문에 답변하세요. "
     "\n문서:\n{context}\n\n"
     "만약 문서에 정보가 없다면 절대로 지어내지 말고 '모르겠습니다'라고 답하세요."
    ),
    ("human", "{question}")
])

# 2. LLM 준비 (gpt-3.5-turbo 기반)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 3. 출력 파서
output_parser = StrOutputParser()

# 4. 체인 구성: [프롬프트] → [LLM] → [파서]
chain = prompt | llm | output_parser


def answer_question(question: str) -> str:
    if store is None:
        return "문서가 로드되지 않았습니다. 먼저 PDF를 업로드해주세요."

    # 1. 벡터 DB에서 유사 문서 검색
    docs = store.similarity_search(question, k=5)
    context = "\n\n---\n\n".join([doc.page_content for doc in docs])
    
    # 1-2. 백터 DB에서 유사 문서 검색 및 점수 출력
    # docs = store.similarity_search_with_score(question, k=5)
    # print("\n[DEBUG] 검색 결과:")
    # THRESHOLD = 0.5
    # for i, (doc, score) in enumerate(docs, start=1):
    #     print(f"문서 #{i}. Score: {score:.4f}")
    #     if score < THRESHOLD: # 0.5 이하만 관련성 있는 문서로 판단
    #         print(f" >> 문서 발췌: {doc.page_content[:100]}...")
    #     else:
    #         print(f" >> 점수가 낮아 컨텍스트로 사용하기 부적합할 수 있음: {doc.page_content[:100]}...")      
    # filtered = [(doc, score) for doc, score in docs if score < THRESHOLD]
    # context = "\n\n---\n\n".join([doc.page_content for doc, _ in filtered])

    # 2. 실행
    try:
        result = chain.invoke({"context": context, "question": question})
    except Exception as e:
        return f"GPT 처리 중 오류: {e}"

    return f"질문: {question}\n응답: {result}"
