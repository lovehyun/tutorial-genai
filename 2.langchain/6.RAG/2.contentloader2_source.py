# pip install chromadb tiktoken

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

load_dotenv(dotenv_path='../.env')

# 파일 로드 (euckr 인코딩 사용)
loader = TextLoader('./nvme.txt', encoding='euckr')
documents = loader.load()

# 문서에 메타데이터 추가
documents = [Document(page_content=doc.page_content, metadata={"source": "nvme.txt"}) for doc in documents]

# 문서를 관리 가능한 크기로 분할 (메타데이터 유지)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
texts = text_splitter.split_documents(documents)

# 문서 청크에 대한 임베딩 생성
embeddings = OpenAIEmbeddings()

# Chroma 벡터 DB에 임베딩 저장
store = Chroma.from_documents(texts, embeddings, collection_name="nvme")

# ChatGPT 모델 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 프롬프트 템플릿 생성
template = """다음 문서들을 참고하여 질문에 답변해주세요. 
출처도 반드시 포함해주세요.

문서들: {context}

질문: {question}

답변을 작성하고 마지막에 "출처: " 다음에 참고한 문서의 출처를 명시해주세요.
"""

prompt = ChatPromptTemplate.from_template(template)

# 검색 및 응답 체인 구성
retriever = store.as_retriever(search_kwargs={"k": 5})  # 상위 5개 문서만 검색
chain = (
   {"context": retriever, "question": lambda x: x}
   | prompt
   | llm
   | StrOutputParser()
)

def answer_question(question):
   try:
       # 체인 실행 및 응답 받기
       result = chain.invoke(question)
       
       # 응답과 출처 분리
       if "출처:" in result:
           answer, sources = result.split("출처:", 1)
           answer = answer.strip()
           sources = sources.strip()
       else:
           answer = result.strip()
           sources = "출처 정보를 찾을 수 없습니다."
       
       # 응답이 비어있거나 무의미한 경우 기본 메시지 반환
       if not answer or answer.lower() == "i don't know.":
           return f"질문: {question}\n응답: 이 질문에 대한 답변을 제공할 수 없습니다.\n"
           
       return f"질문: {question}\n응답: {answer}\n출처: {sources}\n"
       
   except Exception as e:
       return f"질문: {question}\n응답: 오류가 발생했습니다: {str(e)}\n"

# 테스트 질문들 실행
print(answer_question("NVME와 SATA의 차이점을 100글자로 요약해줘"))
print(answer_question("PCIe는?"))
print(answer_question("우주의 크기는 얼마나 되나요?"))
