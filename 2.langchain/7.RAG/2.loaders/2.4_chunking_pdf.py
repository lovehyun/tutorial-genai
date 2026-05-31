from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# PDF 로드 (페이지별 Document)
loader = PyPDFLoader("../DATA/하계학술대회(CISC-S'24) CFP v2.pdf")
pages = loader.load()

print(f"원본 페이지 수: {len(pages)}")

# 페이지 Document들을 다시 청킹
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

chunks = splitter.split_documents(pages)

print(f"청킹 후 Document 수: {len(chunks)}\n")

# 첫 번째 청크 확인
first = chunks[0]

print("metadata:")
print(first.metadata)

print("\ncontent:")
print(first.page_content)
