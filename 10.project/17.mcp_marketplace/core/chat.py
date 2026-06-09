"""
채팅 컨슈머 엔진 — 실제 LLM이 게이트웨이의 도구를 tool-calling 으로 사용한다.

핵심
  · 컨슈머가 구독한 도구(serverid__tool)를 LLM 에 노출(원하는 것만 on/off).
  · LLM 이 도구를 호출하면 '게이트웨이 프록시(_proxy)'로 실행 → 요청 로그·대시보드 통계에도 잡힘.
  · OpenAI / Anthropic(Claude) 둘 다 지원. LLM_PROVIDER 로 선택(미설정이면 키 있는 쪽 자동).

환경변수
  LLM_PROVIDER      'openai' | 'anthropic' (미설정 시 자동 감지)
  OPENAI_API_KEY / OPENAI_MODEL(기본 gpt-4o-mini)
  ANTHROPIC_API_KEY / ANTHROPIC_MODEL(기본 claude-haiku-4-5-20251001)
"""

import os
import json
import importlib.util

import db
import gateway


def _installed(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None

MAX_ITERS = 6   # tool-call 왕복 최대 횟수(무한루프 방지)

SYSTEM = (
    "너는 사용자를 돕는 에이전트다. 사용할 수 있는 도구는 '서버id__도구명' 형식이며 여러 외부 팀의 "
    "MCP 서버에서 마켓플레이스 게이트웨이를 통해 받은 것이다. 요청에 맞는 도구를 골라 처리하고, "
    "복합 요청은 여러 도구를 순서대로 사용하라. 도구가 없으면 솔직히 모른다고 답하라. 한국어로 답하라."
)


def _model_of(p: str) -> str:
    return (os.getenv("OPENAI_MODEL", "gpt-4o-mini") if p == "openai"
            else os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"))


def available() -> list[dict]:
    """키 설정 + SDK 설치까지 된(=실제 동작 가능한) provider 목록. GUI 선택지로 노출."""
    out = []
    if os.getenv("OPENAI_API_KEY") and _installed("openai"):
        out.append({"provider": "openai", "model": _model_of("openai")})
    if os.getenv("ANTHROPIC_API_KEY") and _installed("anthropic"):
        out.append({"provider": "anthropic", "model": _model_of("anthropic")})
    return out


def provider() -> str:
    """기본 provider. LLM_PROVIDER 우선, 없으면 키 있는 쪽."""
    p = os.getenv("LLM_PROVIDER", "").lower().strip()
    if p:
        return p
    av = available()
    return av[0]["provider"] if av else ""


def _collect_tools(consumer_id: str, enabled: list[str] | None) -> list[dict]:
    """컨슈머 구독 도구를 모아 enabled 로 필터. [{name, description, schema}]"""
    out = []
    for s in db.get_subscriptions(consumer_id):
        for t in s["tools"]:
            name = f"{s['id']}{gateway.NS}{t['name']}"
            if enabled is not None and name not in enabled:
                continue
            out.append({
                "name": name,
                "description": f"[{s['name']}] {t.get('description','')}",
                "schema": t.get("input_schema") or {"type": "object", "properties": {}},
            })
    return out


async def _exec(consumer_id: str, namespaced: str, args: dict, ip: str) -> str:
    """도구 1건을 게이트웨이 프록시로 실행하고 텍스트 결과를 돌려준다(로그에도 기록됨)."""
    if gateway.NS not in namespaced:
        return json.dumps({"error": "BAD_TOOL_NAME", "name": namespaced}, ensure_ascii=False)
    sid, tool = namespaced.split(gateway.NS, 1)
    subs = {s["id"] for s in db.get_subscriptions(consumer_id)}
    if sid not in subs:
        return json.dumps({"error": "NOT_SUBSCRIBED", "server": sid}, ensure_ascii=False)
    blocks = await gateway._proxy(sid, tool, args or {}, via=f"chat:{consumer_id}", client_ip=ip)
    return gateway._text(blocks)


# ─── OpenAI ────────────────────────────────────────────────
async def _run_openai(consumer_id, history, tools, ip) -> dict:
    from openai import OpenAI
    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    spec = [{"type": "function", "function": {
        "name": t["name"], "description": t["description"], "parameters": t["schema"]}} for t in tools]
    msgs = [{"role": "system", "content": SYSTEM}] + history
    steps = []
    for _ in range(MAX_ITERS):
        resp = client.chat.completions.create(model=model, messages=msgs, tools=spec or None)
        m = resp.choices[0].message
        if not m.tool_calls:
            return {"reply": m.content or "", "steps": steps, "provider": "openai", "model": model}
        msgs.append({"role": "assistant", "content": m.content or "", "tool_calls": [
            {"id": tc.id, "type": "function",
             "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in m.tool_calls]})
        for tc in m.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except Exception:
                args = {}
            result = await _exec(consumer_id, tc.function.name, args, ip)
            steps.append({"tool": tc.function.name, "args": args, "result": result})
            msgs.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    return {"reply": "(도구 호출이 너무 많아 중단했습니다)", "steps": steps, "provider": "openai", "model": model}


# ─── Anthropic(Claude) ─────────────────────────────────────
async def _run_anthropic(consumer_id, history, tools, ip) -> dict:
    import anthropic
    client = anthropic.Anthropic()
    model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    spec = [{"name": t["name"], "description": t["description"], "input_schema": t["schema"]} for t in tools]
    msgs = list(history)
    steps = []
    for _ in range(MAX_ITERS):
        resp = client.messages.create(model=model, max_tokens=1024, system=SYSTEM,
                                      tools=spec or None, messages=msgs)
        uses = [b for b in resp.content if b.type == "tool_use"]
        if not uses:
            text = "".join(b.text for b in resp.content if b.type == "text")
            return {"reply": text, "steps": steps, "provider": "anthropic", "model": model}
        msgs.append({"role": "assistant", "content": [b.model_dump() for b in resp.content]})
        results = []
        for u in uses:
            result = await _exec(consumer_id, u.name, u.input or {}, ip)
            steps.append({"tool": u.name, "args": u.input, "result": result})
            results.append({"type": "tool_result", "tool_use_id": u.id, "content": result})
        msgs.append({"role": "user", "content": results})
    return {"reply": "(도구 호출이 너무 많아 중단했습니다)", "steps": steps, "provider": "anthropic", "model": model}


async def run_chat(consumer_id: str, history: list[dict], enabled: list[str] | None,
                   ip: str = "-", prov: str | None = None) -> dict:
    """history: [{role:'user'|'assistant', content:str}]. 마지막이 사용자 발화.
       prov: GUI에서 고른 provider('openai'|'anthropic'). 미지정/불가 시 기본값 사용."""
    if not db.get_consumer(consumer_id):
        return {"error": "UNKNOWN_CONSUMER", "detail": f"없는 컨슈머: {consumer_id}"}
    avail = {a["provider"] for a in available()}
    p = (prov or "").lower().strip()
    if p not in avail:
        p = provider()
    if p not in ("openai", "anthropic"):
        return {"error": "NO_LLM", "detail": "서버에 OPENAI_API_KEY 또는 ANTHROPIC_API_KEY 가 없습니다."}
    tools = _collect_tools(consumer_id, enabled)
    try:
        if p == "openai":
            return await _run_openai(consumer_id, history, tools, ip)
        return await _run_anthropic(consumer_id, history, tools, ip)
    except Exception as e:
        return {"error": "LLM_ERROR", "detail": f"{type(e).__name__}: {e}"}
