# pip install chromadb tiktoken

from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

load_dotenv()

# 파일 포멧 인코딩 변경해서 euckr 로 저장해둘것. UTF-8일 경우 cp949로딩 오류 발생.
loader = TextLoader('./nvme.txt')

documents = loader.load()
# print(documents)

# 파라그래프, 라인, 단어, 형태로 구분해서 잘라서 저장
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# print(texts[0])
# print(texts[1])

embeddings = OpenAIEmbeddings()

# 오픈소스 임베딩DB 인 Chroma 사용해서 데이터 저장
store = Chroma.from_documents(texts, embeddings, collection_name="nvme")

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
chain = RetrievalQA.from_chain_type(llm, retriever=store.as_retriever())

print(chain.invoke("NVME와 SATA의 차이점을 100글자로 요약해줘"))
