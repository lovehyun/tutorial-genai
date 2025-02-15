# pip install chromadb tiktoken langchain-chroma

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
import os

load_dotenv(dotenv_path='../.env')

PERSIST_DIR = "./chroma_db"

def create_vector_db():
   # 문서 로드
   loader = TextLoader('./nvme.txt', encoding='euckr')
   documents = loader.load()

   # 메타데이터 추가
   documents = [Document(page_content=doc.page_content, metadata={"source": "nvme.txt"}) for doc in documents]

   # 문서 분할
   text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
   texts = text_splitter.split_documents(documents)

   # 임베딩 생성 및 Chroma DB에 저장 (자동 저장됨)
   embeddings = OpenAIEmbeddings()
   store = Chroma.from_documents(
       texts, 
       embeddings, 
       collection_name="nvme",
       persist_directory=PERSIST_DIR
   )
   return store

def load_vector_db():
   embeddings = OpenAIEmbeddings()
   store = Chroma(
       collection_name="nvme",
       embedding_function=embeddings,
       persist_directory=PERSIST_DIR
   )
   return store

# DB 존재 여부 확인 후 로드 또는 생성
if os.path.exists(PERSIST_DIR):
   store = load_vector_db()
else:
   store = create_vector_db()

# ChatGPT 모델 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 프롬프트 템플릿 생성
template = """다음 문서들을 참고하여 질문에 답변해주세요.
관련 정보가 없다면 "주어진 문서에서 관련 정보를 찾을 수 없습니다."라고 답변하세요.

문서들: {context}

질문: {question}

답변을 작성하고 마지막에 "SOURCES: "를 추가하고 참고한 문서의 출처를 명시해주세요.
"""

# 프롬프트 템플릿 수정
template2 = """주어진 문서들을 참고하여 질문에 답변해주세요.

문서 내용: {context}

질문: {question}

답변 작성 규칙:
1. 자연스러운 한국어로 작성하세요
2. 문서에 없는 내용은 "죄송합니다. 주어진 문서에서 해당 정보를 찾을 수 없습니다."라고 답변하세요
3. 문서의 내용을 바탕으로 명확하고 이해하기 쉽게 설명하세요
4. 기술적인 용어가 나오면 가능한 풀어서 설명해주세요

마지막에 "SOURCES: "를 추가하고 참고한 문서의 출처를 명시해주세요.
"""

prompt = ChatPromptTemplate.from_template(template2)

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
       # 체인 실행
       result = chain.invoke(question)
       
       # 응답과 출처 분리
       if "SOURCES:" in result:
           answer, sources = result.split("SOURCES:", 1)
           answer = answer.strip()
           sources = sources.strip()
       else:
           answer = result.strip()
           sources = "출처 정보를 찾을 수 없습니다."
       
       # 응답이 없거나 부적절한 경우
       if not answer or answer.lower() == "i don't know.":
           return f"질문: {question}\n응답: 이 질문에 대한 답변을 제공할 수 없습니다.\n"
           
       return f"질문: {question}\n응답: {answer}\n출처: {sources}\n"
       
   except Exception as e:
       return f"질문: {question}\n응답: 오류가 발생했습니다: {str(e)}\n"

# 테스트 질문 실행
print(answer_question("NVME와 SATA의 차이점을 100글자로 요약해줘"))
print(answer_question("PCIe는?"))
print(answer_question("우주의 크기는 얼마나 되나요?"))
