# pip install pypdf langchain-chroma

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
import os

load_dotenv(dotenv_path='../.env')

PDF_FILENAME = './DATA/Python_시큐어코딩_가이드(2023년_개정본).pdf'
PERSIST_DIR = "./DATA/chroma_db_secure"

def create_vector_db(file_path):
    try:
        # PDF 로드
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"총 {len(documents)} 페이지의 문서가 로드되었습니다.")

        # 각 문서의 메타데이터에 파일명과 페이지 번호 추가
        for doc in documents:
            doc.metadata["source"] = os.path.basename(file_path)
            # PyPDFLoader에서 이미 page 메타데이터를 추가하지만, 
            # 명시적으로 다시 한번 확인
            if "page" not in doc.metadata:
                doc.metadata["page"] = doc.metadata.get("page", 0) + 1

    except Exception as e:
        print(f"PDF 파일을 로드하는 동안 오류가 발생했습니다: {e}")
        return None

    # 문서 내용 확인
    for i, doc in enumerate(documents):
        if doc.page_content.strip():
            print(f"내용이 있는 첫 번째 페이지 번호: {doc.metadata['page']}")
            print(f"내용 샘플: {doc.page_content[:500]}...")
            break

    # 텍스트 분할
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n\n",
        chunk_size=2000,
        chunk_overlap=500,
    )
    
    texts = text_splitter.split_documents(documents)
    
    # 중복 제거 (메타데이터 유지하면서)
    seen = {}
    unique_texts = []
    for text in texts:
        if text.page_content not in seen:
            seen[text.page_content] = True
            unique_texts.append(text)

    # 임베딩 생성 및 Chroma DB 저장
    embeddings = OpenAIEmbeddings()
    store = Chroma.from_documents(
        unique_texts,
        embeddings,
        collection_name="secure_coding_python",
        persist_directory=PERSIST_DIR
    )
    
    return store

def load_vector_db():
    embeddings = OpenAIEmbeddings()
    store = Chroma(
        collection_name="secure_coding_python",
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR
    )
    return store

# DB 존재 여부 확인 후 로드 또는 생성
if os.path.exists(PERSIST_DIR):
    store = load_vector_db()
else:
    store = create_vector_db(PDF_FILENAME)
    if store is None:
        raise Exception("벡터 DB 생성에 실패했습니다.")

# ChatGPT 모델 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 프롬프트 템플릿 생성
template = """주어진 문서 내용을 바탕으로 질문에 답변해주세요.

문서 내용: {context}

질문: {question}

답변 작성 규칙:
1. 명확하고 구조적으로 답변을 작성하세요
2. 시큐어 코딩 관련 내용은 실제 코드 예시나 구체적인 대응방안을 포함하세요
3. 리스트 형태로 요청된 경우, 번호를 매겨 구분하여 작성하세요
4. 보안 취약점과 그에 대한 대응방안을 함께 설명하세요

마지막에 "SOURCES: "를 추가하고 문서의 출처와 페이지 번호를 모두 명시해주세요.
"""

prompt = ChatPromptTemplate.from_template(template)

# 검색 및 응답 체인 구성
retriever = store.as_retriever(search_kwargs={"k": 5})
chain = (
    {"context": retriever, "question": lambda x: x}
    | prompt
    | llm
    | StrOutputParser()
)

def answer_question(question):
    try:
        result = chain.invoke(question)
        
        # 응답과 출처 분리
        if "SOURCES:" in result:
            answer, sources = result.split("SOURCES:", 1)
            answer = answer.strip()
            # 출처 정보 가공
            sources = sources.strip()
            # 페이지 정보가 없는 경우를 위한 기본 처리
            if not any(c.isdigit() for c in sources):
                sources = f"{sources} (페이지 정보 없음)"
        else:
            answer = result.strip()
            sources = "출처 정보를 찾을 수 없습니다."
        
        # 응답이 없거나 부적절한 경우
        if not answer or answer.lower() == "i don't know.":
            return f"질문: {question}\n응답: 죄송합니다. 해당 질문에 대한 적절한 답변을 찾을 수 없습니다.\n"
            
        return f"질문: {question}\n답변: {answer}\n참고: {sources}\n"
        
    except Exception as e:
        return f"질문: {question}\n오류 발생: {str(e)}\n"

# 질문 테스트
try:
    print(answer_question("시큐어코딩의 주요 기법들에 대해서 리스트 형태로 요약해서 설명해줘"))
    print(answer_question("입력데이터 검증 및 오류 기법에 대해서 상세히 설명해줘"))
except Exception as e:
    print(f"질문 처리 중 오류가 발생했습니다: {e}")
