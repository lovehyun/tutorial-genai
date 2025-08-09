from dotenv import load_dotenv
import os, asyncio, random
from time import perf_counter

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# ================== 공통 준비 ==================
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
to_str = StrOutputParser()

primary_prompt = ChatPromptTemplate.from_messages([
    ("system", "영어를 한국어로 정확히 번역하세요."),
    ("human", "{text}")
])
translate_chain = primary_prompt | llm | to_str

backup_prompt = ChatPromptTemplate.from_messages([
    ("system", "간단히 한국어로 번역하세요. 가능한 직역."),
    ("human", "{text}")
])
backup_chain = backup_prompt | llm | to_str | RunnableLambda(lambda s: {"response": s})
final_fallback = RunnableLambda(lambda _: {"response": "⚠️ 지금은 번역을 처리할 수 없습니다. 잠시 후 다시 시도해주세요."})

# ================== 노드 팩토리 ==================
async def slow_async(x, delay=3.0):
    await asyncio.sleep(delay)
    return x

def make_slow_node(delay: float):
    # ainvoke에서 제대로 await되도록 afunc 사용
    return RunnableLambda(func=lambda x: x, afunc=lambda x: slow_async(x, delay=delay))

def make_primary_chain(fail_p: float):
    def maybe_fail(text: str, p: float):
        if random.random() < p: # 특정 확율로 실패 (예, fail_p = 0.7 = 70% 실패)
            raise RuntimeError("의도적 실패: 파서/네트워크 오류 시뮬레이션")
        return {"response": text}
    
    fail_node = RunnableLambda(lambda s: maybe_fail(s, p=fail_p))
    return translate_chain | fail_node  # 성공 시 {"response": "..."} 구조

# ================== 실행 함수 ==================
async def run_with_retry_timeout_fallback(
    text: str,
    fail_p: float = 0.6,     # 실패 확률
    max_retries: int = 3,
    base_delay: float = 0.6, # 재시도 백오프 시작(초)
    timeout_sec: float = 1.5,# 각 시도 타임아웃
    use_delay: bool = True,  # 느린 노드 사용 여부
    delay_sec: float = 3.0,  # 느린 노드 지연 시간
):
    attempts = 0
    t0 = perf_counter()

    primary_chain = make_primary_chain(fail_p)
    combined = (make_slow_node(delay_sec) | primary_chain) if use_delay else primary_chain

    while attempts <= max_retries:
        try:
            attempts += 1
            out = await combined.ainvoke({"text": text}, config={"timeout": timeout_sec})
            elapsed = perf_counter() - t0
            return {"ok": True, "source": "primary", "attempts": attempts,
                    "elapsed_sec": round(elapsed, 3), **out}
        except Exception as e:
            if attempts > max_retries:
                break
            backoff = base_delay * (2 ** (attempts - 1))
            print(f"[재시도 대기] attempt={attempts} error={repr(e)} -> {backoff:.2f}s")
            await asyncio.sleep(backoff)

    # 1차 폴백
    try:
        out2 = await backup_chain.ainvoke({"text": text}, config={"timeout": 4.0})
        elapsed = perf_counter() - t0
        return {"ok": True, "source": "backup", "attempts": attempts,
                "elapsed_sec": round(elapsed, 3), **out2}
        
    except Exception as e2:
        out3 = final_fallback.invoke({})
        elapsed = perf_counter() - t0
        return {"ok": False, "source": "final_fallback", "attempts": attempts,
                "elapsed_sec": round(elapsed, 3), "error": repr(e2), **out3}

# ================== 데모 ==================
async def main():
    random.seed()

    text = "Hello, nice to meet you. Let's build something great together!"

    print("\n=== [A] 짧은 타임아웃(1.0s) + 지연 ON(3s) → 타임아웃/재시도/폴백 예상 ===")
    resA = await run_with_retry_timeout_fallback(
        text=text,
        fail_p=0.6,  # 실패 60%
        max_retries=2,
        base_delay=0.4,
        timeout_sec=1.0,   # slow 3s > timeout 1s
        use_delay=True,
        delay_sec=3.0,
    )
    print("[A 결과]", resA)

    print("\n=== [B] 넉넉한 타임아웃(5.0s) + 지연 ON(3s) + 실패확률 0 → 주 경로 성공 ===")
    resB = await run_with_retry_timeout_fallback(
        text=text,
        fail_p=0.0,        # 실패 없음
        max_retries=0,
        timeout_sec=5.0,   # slow 3s < timeout 5s
        use_delay=True,
        delay_sec=3.0,
    )
    print("[B 결과]", resB)

    print("\n=== [C] 실패 확률만(80%) + 지연 OFF → 순수 재시도/폴백 확인 ===")
    resC = await run_with_retry_timeout_fallback(
        text=text,
        fail_p=0.8,        # 80% 실패
        max_retries=3,
        base_delay=0.4,
        timeout_sec=5.0,   # 타임아웃 충분
        use_delay=False,   # 지연 없음
    )
    print("[C 결과]", resC)

if __name__ == "__main__":
    asyncio.run(main())
