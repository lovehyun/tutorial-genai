# pip install chromadb tiktoken

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


load_dotenv(dotenv_path='../.env')

# 파일 포멧 인코딩 변경해서 euckr 로 저장해둘것. UTF-8일 경우 cp949로딩 오류 발생.
loader = TextLoader('./nvme.txt', encoding='euckr')

documents = loader.load()
# print(documents)

# 문서 단위를 1000자로 나누고, 중복 200자 유지하여 분할
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# print(texts[0])
# print(texts[1])

# OpenAI Embeddings 사용
embeddings = OpenAIEmbeddings()

# Chroma 벡터DB 저장
store = Chroma.from_documents(texts, embeddings, collection_name="nvme")

# GPT 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 검색기 설정
retriever = store.as_retriever()

# 프롬프트 템플릿 설정
template = """다음 컨텍스트를 사용하여 질문에 답변해주세요:
{context}

질문: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# 체인 구성
chain = (
    {"context": retriever, "question": RunnablePassthrough()} 
    | prompt 
    | llm
)

# 질문 실행
response = chain.invoke("NVME와 SATA의 차이점을 100글자로 요약해줘")

# 응답 출력
print(response.content)
