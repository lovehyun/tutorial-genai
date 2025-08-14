# services/qa_service.py
# pip install pyyaml
import os, json, yaml
from typing import Dict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from services.vectorstore4 import get_vector_store


PROMPT_YAML_FILE = "services/prompts.yaml"
PROMPT_JSON_FILE = "services/prompts.json"

# 1. 프롬프트 템플릿 정의
prompt1 = ChatPromptTemplate.from_template("""
당신은 문서 기반 질문 응답 시스템입니다.
다음 문서를 참고하여 사용자의 질문에 답변해 주세요. 
모르겠다면 절대로 지어내지 말고 "모르겠습니다"라고 답하세요.

문서:
{context}

질문:
{question}

답변:
""")

prompt2 = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 문서 기반 질문 응답 시스템입니다."
     "다음 문서를 참고하여 사용자의 질문에 답변해 주세요."
     "문서에 답변할 내용이 없으면 반드시 '모르겠습니다'라고 답하세요.\n\n"
     "문서:\n{context}\n"),
    ("human", "{question}")
])

prompt = prompt1

# 2. LLM 준비 (gpt-3.5-turbo 기반)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# 3. 출력 파서
output_parser = StrOutputParser()

# 4. 체인 생성
chain = prompt | llm | output_parser

# 프롬프트 전체 로딩 함수 - YAML
def _load_prompts_from_yaml(yaml_path: str) -> Dict[str, ChatPromptTemplate]:
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
        # 아래와 동일한 list-comprehension 포멧
        return {
            name: ChatPromptTemplate.from_template(p["template"])
            for name, p in data.items()
        }

# 프롬프트 전체 로딩 함수 - JSON
def _load_prompts_from_json(json_path: str) -> Dict[str, ChatPromptTemplate]:
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"JSON 파싱 실패: {json_path} (line {e.lineno}, col {e.colno}) → {e.msg}"
            )

        result = {}
        for name, p in data.items():
            template = p["template"]
            result[name] = ChatPromptTemplate.from_template(template)

        return result


def initialize_llm():
    global prompt, llm, output_parser, chain

    # 1. 프롬프트 템플릿 정의
    prompt = _load_prompts_from_yaml(PROMPT_YAML_FILE)["default_prompt"]
    # prompts = _load_prompts_from_json(PROMPT_JSON_FILE)["default_prompt"]
    print("프롬프트 로딩:", prompt)
    
    # LLM 준비 (gpt-3.5-turbo 기반)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # 출력 파서
    output_parser = StrOutputParser()

    # 체인 생성
    chain = prompt | llm | output_parser

def answer_question(question: str) -> str:
    store = get_vector_store()
    if store is None:
        return "문서가 로드되지 않았습니다. 먼저 PDF를 업로드해주세요."

    docs = store.similarity_search(question, k=5)
    context = "\n\n".join(d.page_content for d in docs)
    
    try:
        result = chain.invoke({"context": context, "question": question})
    except Exception as e:
        return f"GPT 처리 중 오류: {e}"
    return f"질문: {question}\n응답: {result.strip()}"


def answer_question_score(question: str) -> str:
    store = get_vector_store()
    if store is None:
        return "문서가 로드되지 않았습니다. 먼저 PDF를 업로드해주세요."

    # 1. 벡터 DB에서 유사 문서 검색 (점수 포함)
    docs_with_scores = store.similarity_search_with_score(question, k=5)

    # 2. context 구성
    # context = "\n\n".join([doc.page_content for doc, _ in docs_with_scores])
    context = "\n\n".join(
        [f"[문서 {i}] (유사도 {round((1 - score) * 100, 2)}%)\n{doc.page_content}"
        for i, (doc, score) in enumerate(docs_with_scores, start=1)]
    )
    print(context)
    
    # 3. LLM 체인 실행
    try:
        result = chain.invoke({"context": context, "question": question})
    except Exception as e:
        return f"GPT 처리 중 오류: {e}"

    # 4. 출처 문서 + 유사도 정보 추출
    source_lines = []
    for doc, score in docs_with_scores:
        source = os.path.basename(doc.metadata.get("source", "unknown"))
        page = int(doc.metadata.get("page", 0)) + 1
        score_percent = round((1 - score) * 100, 2)  # 유사도는 낮을수록 가까움 → 반전
        source_lines.append(f"{source} (page {page}, 유사도 {score_percent}%)")

    # 5. 최종 출력
    return (
        f"질문: {question}\n"
        f"응답: {result.strip()}\n"
        f"참고 문서:\n" + "\n".join(f" - {line}" for line in source_lines)
    )
