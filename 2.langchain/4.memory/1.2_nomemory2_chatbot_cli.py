from dotenv import load_dotenv
import os, sys, time

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# ==============================
# [0] 환경 준비
# ==============================
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY가 설정되지 않았습니다.", file=sys.stderr)
    sys.exit(1)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMP = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))

# ==============================
# [1] 모델 & 프롬프트 (메모리 없음)
# ==============================
llm = ChatOpenAI(model=MODEL, temperature=TEMP, max_tokens=MAX_TOKENS)

# 필요시 system 프롬프트를 넣고 싶다면 아래 줄 추가:
prompt = ChatPromptTemplate.from_messages([
    # ("system", "You are a helpful assistant. 답변은 한국어로 2~4문장."),
    # ("human", "{input}")
    SystemMessagePromptTemplate.from_template("한줄로 간결하게 답변해주세요."),
    HumanMessagePromptTemplate.from_template("{input}")
])
chain = prompt | llm

# ==============================
# [2] 유틸: 간단 재시도 + 타임아웃
# ==============================
def ask_once(message: str, timeout_sec: float = 10.0) -> str:
    response = chain.invoke({"input": message}, config={"timeout": timeout_sec})
    return response.content

def ask_with_retry(message: str, retries: int = 1, timeout_sec: float = 10.0) -> str:
    last_err = None
    for attempt in range(retries + 1):
        try:
            return ask_once(message, timeout_sec=timeout_sec)
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
            else:
                raise last_err

# ==============================
# [3] (선택) 스트리밍 출력
# ==============================
def ask_stream(message: str, timeout_sec: float = 10.0) -> None:
    # chain.stream은 Prompt | LLM 조합에도 동작
    for chunk in chain.stream({"input": message}, config={"timeout": timeout_sec}):
        if hasattr(chunk, "content") and chunk.content:
            print(chunk.content, end="", flush=True)
    print()

# ==============================
# [4] CLI 루프 (메모리 없음)
# ==============================
def simple_chat(use_stream: bool = False, retries: int = 1, timeout_sec: float = 10.0):
    print("챗봇과 대화를 시작합니다. 종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n당신: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n대화를 종료합니다. 안녕히 가세요!")
            break

        if user_input.lower() in {"quit", "exit", "종료", "끝"}:
            print("대화를 종료합니다. 안녕히 가세요!")
            break
        if not user_input:
            print("메시지를 입력해주세요.")
            continue

        print("(챗봇이 응답을 생성중입니다...)")
        try:
            if use_stream:
                ask_stream(user_input, timeout_sec=timeout_sec)
            else:
                reply = ask_with_retry(user_input, retries=retries, timeout_sec=timeout_sec)
                print(f"챗봇: {reply if reply else '(빈 응답)'}")

        except Exception as e:
            print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    # 메모리 없음 / 스트리밍 끔 / 재시도 1회 / 20초 타임아웃
    simple_chat(use_stream=False, retries=1, timeout_sec=20.0)
