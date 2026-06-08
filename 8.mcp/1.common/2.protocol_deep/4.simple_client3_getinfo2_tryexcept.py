# 4.simple_client3_getinfo2_tryexcept.py — 4.simple_client3_getinfo + 예외 처리
#
# ── 연동 방식 ────────────────────────────────────────────────
#   서버가 가진 tools / resources / prompts 를 각각 list_* 로 발견하고,
#   도구 하나 호출 + 프롬프트 하나(get_prompt)까지 — 각 단계를 try/except 로 감싼다.
#   (debug_proxy 경유 → 3.simple_server2)

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command="python", args=["debug_proxy.py", "3.simple_server2.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print(f"연결 완료: {init.serverInfo.name}")

            # 1~3) tools / resources / prompts 발견
            print("\n=== 도구 ===")
            try:
                for t in (await session.list_tools()).tools:
                    print(f" - {t.name}: {t.description}")
            except Exception as e:
                print(f"조회 실패: {e}")

            print("\n=== 리소스 ===")
            try:
                for r in (await session.list_resources()).resources:
                    print(f" - {r.name}: {r.description}")
            except Exception as e:
                print(f"조회 실패: {e}")

            print("\n=== 프롬프트 ===")
            try:
                for p in (await session.list_prompts()).prompts:
                    print(f" - {p.name}: {p.description}")
            except Exception as e:
                print(f"조회 실패: {e}")

            # 4) 첫 도구 호출
            print("\n=== 도구 테스트 ===")
            try:
                t = (await session.list_tools()).tools[0]
                args = {"name": "테스트"} if "name" in str(t.inputSchema) else {}
                print(f"{t.name} → {(await session.call_tool(t.name, args)).content[0].text}")
            except Exception as e:
                print(f"도구 테스트 실패: {e}")

            # 5) 프롬프트 받아오기 — get_prompt 는 LLM 호출 없이 '지시문 텍스트'만 준다
            print("\n=== 프롬프트: translate ===")
            try:
                resp = await session.get_prompt("translate", {"text": "안녕하세요", "target_lang": "English"})
                for m in resp.messages:
                    print(f"[{m.role}] {getattr(m.content, 'text', m.content)}")
            except Exception as e:
                print(f"프롬프트 호출 실패: {e}")


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   연결 완료: SimpleServer2
#   === 도구 ===       - hello: ...
#   === 리소스 ===     - get_info: ...
#   === 프롬프트 ===   - greeting / translate
#   === 도구 테스트 === hello → Hello, 테스트!
#   === 프롬프트: translate === [user] (번역 지시문 텍스트)
