import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

def build_prompt():
    return (
        "다음 소스코드에서 보안 취약점을 분석해줘.\n"
        "각 취약점에 대해 해당 코드의 라인 번호, 코드 스니펫, 취약점 설명과 "
        "개선 방안을 마크다운 형식의 리스트로 출력해줘.\n"
        "단 '#' 으로 시작하는 주석코드는 무시해도 돼.\n\n"
        "소스코드:\n"
        "------------------------------\n"
        "{code}\n"
        "------------------------------"
    )
    
def build_prompt2():
    return (
        "다음은 Python 소스코드입니다.\n\n"
        "이 코드에서 **보안 취약점이 존재하는 부분**을 찾아주세요.\n"
        "각 취약점에 대해 다음 정보를 정리해주세요:\n"
        "- 라인 번호: 12-14\n"
        "- 코드: (간단히 요약)\n"
        "- 설명: (무엇이 문제인지)\n"
        "- 개선 방안: (간단히)\n\n"
        "※ 주석(`#`)으로 시작하는 줄은 무시해도 됩니다.\n\n"
        "소스코드:\n"
        "------------------------------\n"
        "{code}\n"
        "------------------------------"
    )

def analyze(code_with_line_numbers: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 보안 코드 분석 전문가입니다."),
        ("user", build_prompt2())
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({"code": code_with_line_numbers})
