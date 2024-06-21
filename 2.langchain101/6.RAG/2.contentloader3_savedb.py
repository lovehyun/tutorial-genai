# pip install chromadb tiktoken

from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

from langchain.docstore.document import Document
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

import os
import json


load_dotenv(dotenv_path='../.env')

VECTOR_DB_PATH = './vector_db.json'

def create_vector_db():
    # Load documents from a file, ensure encoding is correctly handled
    loader = TextLoader('./nvme.txt', encoding='euckr')
    documents = loader.load()

    # Add metadata to the documents if not already present
    documents = [Document(page_content=doc.page_content, metadata={"source": "nvme.txt"}) for doc in documents]

    # Split the documents into manageable chunks while retaining metadata
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # Generate embeddings for the document chunks
    embeddings = OpenAIEmbeddings()

    # Store the embeddings in Chroma, an open-source embedding database
    store = Chroma.from_documents(texts, embeddings, collection_name="nvme")

    # Save the vector store to a file
    store_data = {
        'texts': [doc.page_content for doc in texts],
        'embeddings': [embeddings.embed_query(doc.page_content) for doc in texts],
        'metadata': [doc.metadata for doc in texts]
    }
    with open(VECTOR_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(store_data, f)

    return store

def load_vector_db():
    with open(VECTOR_DB_PATH, 'r', encoding='utf-8') as f:
        store_data = json.load(f)

    documents = [Document(page_content=text, metadata=meta) for text, meta in zip(store_data['texts'], store_data['metadata'])]
    embeddings = OpenAIEmbeddings()
    store = Chroma.from_documents(documents, embeddings, collection_name="nvme")
    return store

# Check if the vector database file exists, if not create it
if os.path.exists(VECTOR_DB_PATH):
    store = load_vector_db()
else:
    store = create_vector_db()


# Initialize the language model with the correct model name and temperature
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)

# Load the QA chain that includes sources in the response
qa_chain = load_qa_with_sources_chain(llm, chain_type="map_reduce")


def answer_question(question):
    # Retrieve documents from the store
    docs = store.similarity_search(question, k=5)  # Limit to top 5 documents to reduce context length
    
    # Run the QA chain
    response = qa_chain.invoke({"input_documents": docs, "question": question})
    
    # Extract the result and source documents
    result = response['output_text'].strip()
    if "SOURCES:" in result:
        result, sources_info = result.split("SOURCES:", 1)
        result = result.strip()
        sources_info = sources_info.strip()
    else:
        sources_info = "출처 정보를 찾을 수 없습니다."
    
    # If no result or sources_info is empty, return a default message
    if not result or not sources_info or result.lower() == "i don't know.":
        return f"질문: {question}\n응답: 이 질문에 대한 답변을 제공할 수 없습니다.\n"

    # Return the result with sources info
    return f"질문: {question}\n응답: {result}\n출처:{sources_info}\n"

# Query the chain and print the result
question = "NVME와 SATA의 차이점을 100글자로 요약해줘"
print(answer_question(question))

# Query the chain and print the result
question = "PCIe는?"
print(answer_question(question))

# Example of a question outside the trained data scope
question = "우주의 크기는 얼마나 되나요?"
print(answer_question(question))
