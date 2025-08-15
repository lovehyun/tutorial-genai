from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain.schema import SystemMessage

from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool

import tkinter as tk
from tkinter import simpledialog, messagebox
import sys

# "빌트인 HumanInputRun" 대신 직접 만든 Human 툴을 써서 프롬프트/입력 UX를 100% 내 마음대로 제어
# 뭐가 다른가?
# - 이전(빌트인 HumanInputRun): prompt_func/input_func로 커스터마이즈는 가능하지만, 내부 동작/표시는 제한적.
# - 지금(직접 Tool 정의): print 형식, 다국어 안내, 검증 로직, 로깅, 마스킹, 추가 질문 흐름 등 모든 UX를 직접 설계 가능.


# 0. 환경 변수 로드
load_dotenv()

# 1. OpenAI 모델 초기화
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. Tkinter GUI 기반 Human 도구
@tool
def ask_user_gui(prompt: str) -> str:
    """
    Tkinter로 팝업을 띄워 사람에게 입력을 받습니다.
    - 정상 입력: 입력 문자열 반환
    - 취소/닫기: '사용자가 입력을 취소했습니다.' 반환
    - GUI 실패(예: 헤드리스 환경): 콘솔 입력으로 폴백
    """
    try:
        # Tk는 메인 스레드에서 실행되어야 합니다.
        root = tk.Tk()
        root.withdraw()  # 루트 창 숨김

        # 정보 알림 (선택)
        # messagebox.showinfo("질문", "에이전트가 사용자에게 질문합니다.")

        # 문자열 입력 받기 (모달)
        ans = simpledialog.askstring("에이전트 질문", prompt, parent=root)

        # 리소스 정리
        root.destroy()

        if ans is None:
            return "사용자가 입력을 취소했습니다."
        return ans.strip()
    except Exception as e:
        # 예: headless 서버 등에서 TclError → 콘솔로 폴백
        print(f"[GUI 사용 불가, 콘솔로 폴백] {e}")
        try:
            return input(f"\n[콘솔 입력 모드]\n{prompt}\n> ").strip()
        except Exception:
            return "입력을 받을 수 없습니다."

# 헤드리스 환경 폴백: X 서버 없는 서버/컨테이너 등에서 TclError가 날 수 있음. 그 경우 콘솔 입력으로 자동 폴백합니다.

tools = [ask_user_gui]


# 3. 에이전트 초기화
agent_chain = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# rules = SystemMessage(content=
#     "모르는 개인 정보는 Human Input 도구로 '단 한 번' 짧게 물어봐라. "
#     "답을 받으면 한국어로 간단히 최종 답을 말하라. 추측/지어내기 금지."
# )

# agent = initialize_agent(
#     tools=[human_tool],
#     llm=llm,
#     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
#     agent_kwargs={"system_message": rules},
#     handle_parsing_errors=True,
#     max_iterations=3,
#     early_stopping_method="force",
#     verbose=True
# )


# 4. 모델 실행
# result = agent_chain.invoke({"input": "What's my nickname?"})
result = agent_chain.invoke({"input": "내 이름은 뭐야?"})
print("\n최종 결과:", result["output"])
