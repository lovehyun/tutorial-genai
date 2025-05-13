# pip install chromadb tiktoken

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


# 1. .env 파일에서 OPENAI_API_KEY 등 환경 변수 로드
load_dotenv(dotenv_path='../.env')

# 2. 문서 로드 (euc-kr로 인코딩된 텍스트 파일)
# Windows에서 cp949 디코딩 오류를 방지하려면 euc-kr로 저장해야 함
loader = TextLoader('./nvme.txt', encoding='euckr')
documents = loader.load()

# 3. 문서를 1000자 단위로 분할하고 200자 중복 유지
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# 4. 텍스트 조각을 임베딩으로 변환하기 위한 OpenAI 임베딩 모델 준비
embeddings = OpenAIEmbeddings()

# 5. Chroma 벡터 저장소 생성 및 임베딩 저장 (collection 이름 지정)
store = Chroma.from_documents(texts, embeddings, collection_name="nvme")

# 6. GPT-3.5 기반 언어 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 7. 벡터DB에서 연관 문서를 검색할 수 있는 retriever 구성
retriever = store.as_retriever()

# 8. 질문과 context를 기반으로 응답을 생성할 프롬프트 템플릿 정의
template = """다음 컨텍스트를 사용하여 질문에 답변해주세요:
{context}

질문: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# 9. 체인 구성
# - 사용자 질문은 그대로 "question"에 들어가고
# - retriever가 context를 검색하여 "context"에 전달
# - 프롬프트 → LLM → 응답
chain = (
    {"context": retriever, "question": RunnablePassthrough()} 
    | prompt 
    | llm
)

# 10. 실제 질문 실행
response = chain.invoke("NVME와 SATA의 차이점을 100글자로 요약해줘")

# 11. 응답 출력
print(response.content)
