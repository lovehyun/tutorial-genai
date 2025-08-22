import os, re, json, asyncio, traceback
from contextlib import AsyncExitStack
from typing import Dict, Any, Tuple, List

from dotenv import load_dotenv
from openai import OpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# =========================
# 0) 환경 설정 & OpenAI 클라이언트
# =========================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # .env에 OPENAI_API_KEY 필요


# =========================
# 1) 출력 포매터 (사람용/프롬프트용)
# =========================
def format_tool_info_detailed(tool, show_params: bool = True) -> str:
    """사람이 읽기 좋은 상세 도구 설명 문자열 (콘솔 출력용)."""
    result = f"  - {tool.name}: {tool.description or '설명 없음'}"
    if not show_params:
        return result
    
    schema = getattr(tool, "inputSchema", None)
    if isinstance(schema, dict) and "properties" in schema:
        props = schema.get("properties", {})
        req = set(schema.get("required", []))
        result += "\n    매개변수:"
        for name, info in props.items():
            t = info.get("type", "unknown")
            d = info.get("description", "")
            mark = "(필수)" if name in req else "(선택)"
            result += f"\n      {name}: {t} {mark}" + (f" - {d}" if d else "")
    else:
        result += "\n    매개변수: 없음"
    return result

def format_tool_info_simple(name: str, tool_info: Dict[str, Any]) -> str:
    """
    GPT 프롬프트에 넣을 간단 요약(이름/설명/매개변수 이름 목록).
    → 프롬프트 길이를 통제하면서도 파라미터 힌트를 제공.
    """
    schema = tool_info.get("schema") or {}
    props = schema.get("properties") if isinstance(schema, dict) else None
    params = list(props.keys()) if isinstance(props, dict) else []
    param_text = f"매개변수: {params}" if params else "매개변수: 없음"
    return f"- {name}: {tool_info.get('description','')} ({param_text})"


# =========================
# 2) MCP 서버 연결 & 도구 수집
# =========================
async def get_tools_from_server(server_file: str, stack: AsyncExitStack) -> Tuple[str, ClientSession, Dict[str, str], List[Any]]:
    """
    서버 프로세스를 실행하고 MCP 세션을 ExitStack에 등록해 수명 유지.
    반환: (server_name, session, {tool_name: desc}, raw_tools_list)
    """
    params = StdioServerParameters(command="python", args=[server_file])

    # stdio_client → 서버 프로세스 실행 및 stdin/stdout 연결
    read, write = await stack.enter_async_context(stdio_client(params))

    # ClientSession → MCP 프로토콜 기반 세션 생성
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()

    # 서버에서 제공하는 툴 목록 가져오기
    tools_result = await session.list_tools()
    tools = {t.name: (t.description or "") for t in tools_result.tools}
    
    return server_file, session, tools, tools_result.tools


# =========================
# 3) 기존 규칙기반 선택/파라미터 (GPT 폴백용으로 유지)
# =========================
def find_best_tool(question: str, all_tools: Dict[str, str]) -> str | None:
    """간단 키워드 매칭으로 가장 적합한 도구 선택(폴백)."""
    q = question.lower()
    for tool_name in all_tools.keys():
        if any(w in q for w in ["안녕", "hello"]) and "hello" in tool_name:
            return tool_name
        if any(w in q for w in ["더하기", "계산", "+"]) and "add" in tool_name:
            return tool_name
        if any(w in q for w in ["시간", "몇 시", "몇시"]) and "time" in tool_name:
            return tool_name
        if "날씨" in q and "weather" in tool_name:
            return tool_name
    return None

def extract_params(question: str, tool_name: str) -> Dict[str, Any]:
    """질문에서 파라미터 추출(간단 규칙, 폴백)."""
    params = {}
    q = question.strip()

    if "hello" in tool_name:
        # 구두점 제거 후, 첫 번째 유효 단어를 name으로 사용
        tokens = re.findall(r"[A-Za-z가-힣]+", q)
        name = None
        for tok in tokens:
            if tok.lower() not in {"안녕하세요", "hello", "hi"}:
                name = tok
                break
        params["name"] = name or "친구"

    elif "add" in tool_name:
        # 숫자 2개 이상 뽑아서 a, b로 사용
        nums = re.findall(r"-?\d+(?:\.\d+)?", q)
        if len(nums) >= 2:
            params["a"] = float(nums[0])
            params["b"] = float(nums[1])

    elif "weather" in tool_name:
        # 질문에 포함된 도시명을 찾고 없으면 기본값 서울
        for city in ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]:
            if city in q:
                params["city"] = city
                break
        params.setdefault("city", "서울")

    return params


# =========================
# 4) GPT에게 “도구 선택 + 파라미터 생성” 요청
# =========================
async def ask_gpt(user_request: str, tools_for_gpt: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    tools_for_gpt: {tool_name: {"description": str, "schema": dict|None, "server": str}}
    반환: {"tool": str|None, "params": dict, "reason": str}
    """
    tools_info_text = "\n".join(
        format_tool_info_simple(name, info) for name, info in tools_for_gpt.items()
    )

    system_msg = (
        "You are a tool selector and parameter generator. "
        "Choose the single best tool (or none) and return STRICT JSON ONLY."
    )
    prompt = f"""사용 가능한 도구들:
{tools_info_text}

사용자 요청: {user_request}

아래 JSON 스키마로만 답하세요(코드블록 금지):
{{"tool": "도구명 또는 null", "params": {{"매개변수": 값}}, "reason": "선택 이유"}}
- "tool"이 null이면 "params"는 {{}}
- 존재하는 도구명만 사용
- 매개변수 이름/타입을 도구 스키마에 맞춤
"""

    # --- 라이브 디버깅용(전체 프롬프트/응답 보기) ---
    # DEBUG: print("======= GPT PROMPT =======")
    # DEBUG: print(prompt)

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_msg},
                      {"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1,
        )
        content = (resp.choices[0].message.content or "").strip()

        # DEBUG: print("======= GPT RAW CONTENT =======")
        # DEBUG: print(content)

        # 코드펜스/잡음 제거 후 JSON만 추출
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.I|re.M).strip()
        if not (content.startswith("{") and content.endswith("}")):
            m = re.search(r"\{[\s\S]*\}", content)
            content = m.group(0) if m else "{}"

        out = json.loads(content)
        return {
            "tool": out.get("tool"),
            "params": out.get("params", {}) or {},
            "reason": out.get("reason", ""),
        }
    except Exception as e:
        return {"tool": None, "params": {}, "reason": f"GPT 오류: {e}"}


# =========================
# 5) 선택 로직(이전 구조 재사용 + GPT 경로 추가)
# =========================
async def choose_tool_and_params(question: str,
                                 all_tools: Dict[str, str],
                                 tools_for_gpt: Dict[str, Dict[str, Any]],
                                ) -> Tuple[str | None, Dict[str, Any], str]:
    """
    이전 구조를 그대로 쓰되, 우선 GPT로 선택/파라미터 생성 → 실패 시 규칙기반 폴백.
    반환: (tool_name | None, params, reason)
    """
    g = await ask_gpt(question, tools_for_gpt)
    if g.get("tool"):
        return g["tool"], g.get("params", {}) or {}, f"GPT 선택: {g.get('reason','')}"
    
    # GPT가 null을 주거나 오류/부정확하면 규칙기반 폴백
    # fb_tool = find_best_tool(question, all_tools)
    # fb_params = extract_params(question, fb_tool) if fb_tool else {}
    # return fb_tool, fb_params, f"GPT 폴백: {g.get('reason','')}"
    return None, {}, f"GPT 폴백: {g.get('reason','')}"


# =========================
# 6) 메인 루프 (이전 흐름 유지)
# =========================
async def main():
    print("GPT-MCP 하이브리드 클라이언트 (이전 코드 재사용) 시작")

    servers = ["math_server.py", "utility_server.py"]
    questions = [
        "안녕하세요 Alice!",   # hello
        "15 더하기 25는?",     # add
        "지금 몇 시?",         # current_time
        "부산 날씨는?",        # weather
        "제주 날씨는?",        # weather(미정 도시 처리 기대)
        "파일 삭제해줘",       # 도구 없음
    ]

    async with AsyncExitStack() as stack:
        sessions: List[Tuple[str, ClientSession, Dict[str, str]]] = []
        all_tools: Dict[str, str] = {}                   # (이전 코드 유지) tool_name -> description
        
        tools_for_gpt: Dict[str, Dict[str, Any]] = {}    # GPT용 확장 정보
        tool_to_session: Dict[str, ClientSession] = {}   # tool_name -> session (실행용)

        # --- 서버 연결 & 도구 수집 (이전 흐름 재사용) ---
        for server in servers:
            try:
                server_name, session, tools_map, raw_tools = await get_tools_from_server(server, stack)

                print(f"\n{server_name}에서 발견된 도구들:")
                for t in raw_tools:
                    print(format_tool_info_detailed(t))

                sessions.append((server_name, session, tools_map))
                all_tools.update(tools_map)

                # GPT 프롬프트/실행 매핑용 확장 인덱스
                for t in raw_tools:
                    tools_for_gpt[t.name] = {
                        "description": t.description or "",
                        "schema": getattr(t, "inputSchema", None),
                        "server": server_name,
                    }
                    tool_to_session[t.name] = session

            except Exception:
                print(f"{server}: 연결 실패")
                traceback.print_exc()

        if not all_tools:
            print("\n등록된 도구가 없습니다. 종료합니다.")
            return

        # 전체 도구 요약
        print(f"\n총 {len(all_tools)}개 도구 발견")
        print("-" * 30)
        print("전체 도구(요약):")
        for name, desc in all_tools.items():
            print(f"  - {name}: {desc}")
        print("-" * 30)

        # --- 질문 처리 (이전 구조 루프 유지) ---
        for q in questions:
            print(f"\n질문: {q}")

            # 1) 도구 선택 + 파라미터 결정 (GPT → 폴백)
            tool_name, params, reason = await choose_tool_and_params(
                q, all_tools, tools_for_gpt
            )
            # 선택 사유 출력
            print(f"[선택] tool={tool_name}, params={params}, reason={reason}")

            if not tool_name:
                print("답변: 적합한 도구 없음")
                continue

            # 2) 해당 도구를 보유한 세션에서 실행 (이전 구조 재사용)
            executed = False
            for server_name, session, tools_map in sessions:
                if tool_name not in tools_map:
                    continue
                try:
                    result = await session.call_tool(tool_name, params)
                    if getattr(result, "content", None):
                        content = result.content[0]
                        text = getattr(content, "text", None) or str(content)
                        print(f"답변: {text}")
                    else:
                        print("답변: (빈 응답)")
                    executed = True
                    break
                except Exception as e:
                    print(f"  - {server_name} 실행 실패: {e.__class__.__name__}: {e}")
                    # 필요하면 스택트레이스:
                    # DEBUG: traceback.print_exc()

            if not executed:
                print("답변: 실행 실패")

if __name__ == "__main__":
    asyncio.run(main())
