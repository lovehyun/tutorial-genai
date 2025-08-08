# pip install langchain-chroma chromadb tiktoken
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter 
from langchain_core.documents import Document
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma

# 1. .env 파일에서 OpenAI API 키 불러오기
load_dotenv(dotenv_path='../.env')

# 2. 문서 로드
document1 = TextLoader('./nvme.txt', encoding='utf-8').load()
document2 = TextLoader('./ssd.txt', encoding='utf-8').load()

# 3. 텍스트 분할기 설정
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
# text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
#    chunk_size=1000, 
#    chunk_overlap=100,
#    encoding_name="cl100k_base"  # GPT-3.5/4 인코딩
# )

# CharacterTextSplitter (문자 기준) 사용 시:
# - 빠른 프로토타이핑
# - 정확한 토큰 수가 중요하지 않은 경우
# - 처리 속도가 중요한 경우
#
# from_tiktoken_encoder (토큰 기준) 사용 시:
# - OpenAI API 사용 시 (GPT-3.5, GPT-4 등)
# - 정확한 API 비용 계산이 필요한 경우
# - 모델의 토큰 한계를 정확히 지키고 싶은 경우

# GPT-3.5-turbo, GPT-4 계열 : encoding_name="cl100k_base"
# GPT-3 (text-davinci-003 등) : encoding_name="p50k_base"
# 구형 GPT-3 모델들 : encoding_name="r50k_base"


# 4. 문서별로 chunk화 + chunk_id 부여

# NVME 문서
texts1 = text_splitter.split_documents(document1)
for i, doc in enumerate(texts1, start=1):
    doc.metadata.update({"source": "nvme.txt", "chunk_id": i, "created_date": "2024-01-01"})

# SSD 문서
texts2 = text_splitter.split_documents(document2)
for i, doc in enumerate(texts2, start=1):
    doc.metadata.update({"source": "ssd.txt", "chunk_id": i, "created_date": "2024-01-01"})

# 청크 메타데이터 앞 5개 출력
# print("=== 분할된 문서 메타데이터 (처음 5개) ===")
# for idx, doc in enumerate(texts1[:5], start=1):
#     print(f"[{idx}] source={doc.metadata.get('source')}, chunk_id={doc.metadata.get('chunk_id')}, created_date={doc.metadata.get('created_date')}")
#     print(f"내용(앞 50자): {doc.page_content[:50]}...")
# print("=" * 50)

# 5. 모든 청크 합치기
texts = texts1 + texts2

# 6. 문서 청크에 대한 벡터 임베딩 생성
embeddings = OpenAIEmbeddings()

# 7. 벡터 저장소에 저장 (Chroma 사용)
store = Chroma.from_documents(texts, embeddings, collection_name="hdd")


# 8. GPT-3.5 모델 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 9. 답변에 문서 출처 포함하도록 프롬프트 정의
template = """다음 문서들을 참고하여 질문에 답변해주세요. 

문서내용: {context}

질문: {question}

답변을 작성하고, 마지막에 "출처: [파일명:청크번호]" 형식으로 참고한 문서 정보를 모두 명시해주세요.
예시) 출처: nvme.txt:1, ssd.txt:3
"""
prompt = ChatPromptTemplate.from_template(template)

# 10. 문서 검색 + LLM 응답 체인 구성
retriever = store.as_retriever(search_kwargs={"k": 3})  # 유사도 기준 상위 3개 문서 검색
                                                        # 이 as_retriever()는 "유사도 점수(similarity score)"를 반환하지 않습니다.

def format_docs_with_metadata(docs):
    formatted_list = []
    for d in docs:
        src = d.metadata.get("source", "unknown")
        cid = d.metadata.get("chunk_id", "?")
        created = d.metadata.get("created_date", "?")
        formatted_list.append(
            f"[출처: {src}:{cid} | 작성일: {created}]\n{d.page_content}"
        )
    return "\n\n---\n\n".join(formatted_list)

def peek_prompt(prompt_value):  # 중간 디버깅용 (프롬프트 생성 내용 확인용)
    print("=== LLM 직전 프롬프트 ===")
    print(prompt_value.to_string())
    return prompt_value  # 반드시 그대로 반환해서 체인이 계속 흘러가게 함

chain = (
    {"context": retriever | RunnableLambda(format_docs_with_metadata),
     "question": lambda x: x}
    | prompt
    | RunnableLambda(peek_prompt)  # <- 여기서 디버깅용 프린트
    | llm
    | StrOutputParser()  # 응답을 문자열로 처리 (최종 result.context 부분을 문자열로 반환)
)

# 11. 질문을 받아 응답 + 출처를 분리해서 반환하는 함수
def answer_question(question):
    try:
        result = chain.invoke(question)  # LLM 체인 실행
        
        # 답변이 잘 나왔는지 확인 (답변과 출처)
        if "출처:" in result:
            answer, sources = result.split("출처:", 1)
            answer = answer.strip()
            sources = sources.strip()
        else:
            answer = result.strip()
            sources = "출처 정보를 찾을 수 없습니다."
            
        # 최종 응답 포멧
        print(f"\n=====\n질문: {question}\n---\n응답: {answer}\n---\n출처: {sources}\n=====\n")
       
    except Exception as e:
       print(f"질문: {question}\n응답: 오류가 발생했습니다: {str(e)}\n")

# 12. 테스트 질문 실행
answer_question("NVME와 SATA의 차이점을 100글자로 요약해줘")
# answer_question("PCIe는?")
# answer_question("우주의 크기는 얼마나 되나요?")


# ---------------------------------------------------------
# 13. 디버깅용
def debug_retrieval(question):
    # 검색된 문서들 확인
    retrieved_docs = retriever.invoke(question)
    
    print(f"=== 질문: {question} ===")
    print(f"검색된 문서 개수: {len(retrieved_docs)}")
    
    for i, doc in enumerate(retrieved_docs, start=1):
        print(f"\n--- 문서 {i} ---")
        print(f"출처: {doc.metadata}")
        print(f"내용 (처음 200자): {doc.page_content[:200]}...")
    print("="*50)

def debug_retrieval_score(question):
    # 점수까지 가져오는 검색
    results = store.similarity_search_with_score(question, k=5)
    
    print(f"=== 질문: {question} ===")
    print(f"검색된 문서 개수: {len(results)}")
    
    for i, (doc, score) in enumerate(results, start=1):
        print(f"\n--- 문서 {i} ---")
        print(f"출처: {doc.metadata}")
        print(f"유사도 점수: {score:.4f}  (작을수록 유사도 높음)")
        print(f"내용 (앞 200자): {doc.page_content[:200]}...")
    print("=" * 50)

# 13-2. 디버그 테스트
# debug_retrieval("우주의 크기는 얼마나 되나요?")
# debug_retrieval("NVME와 SATA의 차이점은?")
# debug_retrieval_score("우주의 크기는 얼마나 되나요?")
# debug_retrieval_score("NVME와 SATA의 차이점은?")
