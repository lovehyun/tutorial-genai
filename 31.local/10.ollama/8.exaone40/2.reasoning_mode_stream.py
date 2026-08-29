"""
(2) 생각 모드를 스트리밍으로 — EXAONE 4.0은 thinking이 안 갈라지니 직접 지켜보고 잘라낸다.

Qwen 3.5(../6.qwen35/2.thinking_mode_stream.py)와 이름은 같지만 사정이 다르다. 그쪽은
스트림 안에서도 message["thinking"]과 message["content"]가 처음부터 깔끔히 나뉘어 온다.
EXAONE 4.0(이 커뮤니티 GGUF)은 1.reasoning_mode.py 에서 확인했듯 그 분리 자체가 안 되고,
사고 과정과 최종 답변이 전부 content 필드 하나로 흘러나오며 그 사이에 </think> 태그만 섞여
있다. 그래서 여기서는 (1) 원본 스트림을 있는 그대로 보여주고 (2) 다 받은 뒤에 </think> 를
기준으로 직접 잘라 정리한 버전을 나란히 보여준다.

준비: pip install ollama  +  ollama pull sam860/exaone-4.0:1.2b
"""
import ollama

MODEL = "sam860/exaone-4.0:1.2b"
QUESTION = "인공지능을 한 문장으로 설명해줘."

stream = ollama.chat(
    model=MODEL,
    messages=[{"role": "user", "content": QUESTION}],
    think=True,
    stream=True,
)

buffer = ""
marked = False
final_chunk = None

print("[원본 스트림 — 있는 그대로] ", end="", flush=True)
for chunk in stream:
    piece = chunk["message"].content or ""
    buffer += piece
    print(piece, end="", flush=True)
    if not marked and "</think>" in buffer:
        # ⚠️ 정확히 이 지점에서 "여기부터 진짜 답변"이라고 표시해준다 — 모델/API 가
        # 알려주는 게 아니라 우리가 </think> 문자열을 직접 찾아서 표시하는 것이다.
        print("\n   ^^^ 방금 </think> 가 나왔다 — 여기부터가 진짜 답변이다 ^^^\n", end="", flush=True)
        marked = True
    final_chunk = chunk

# ── 다 받은 뒤, 사고/답변을 실제로 나눠서 정리된 버전도 보여준다 ──
print("\n\n" + "=" * 50)
print("[정리된 버전] (</think> 기준으로 직접 자른 것)")
head, sep, rest = buffer.partition("</think>")
if sep:
    print("사고 과정:", head.strip()[:200], "...")
    print("최종 답변:", rest.strip())
else:
    print("(이번엔 </think> 가 안 나왔다 — 사고를 끝맺지 못하고 스트림이 끝난 것)")
    print("받은 전체 내용:", buffer.strip())

print(f"\ndone_reason={final_chunk.get('done_reason')}")


# 정리:
#   - Qwen 3.5 는 stream=True 여도 사고/답변이 이미 분리된 채로 오니 그대로 쓰면 된다.
#   - EXAONE 4.0(이 GGUF)은 그렇지 않다 — "원본 스트림"을 그대로 보면 사고 과정과 답변이
#     한 덩어리로 실시간으로 섞여 나오는 걸 직접 확인할 수 있다. 실전에서 이런 모델을
#     쓴다면 이 파일처럼 </think> 등장 여부를 직접 감지하는 코드를 스트리밍 소비 쪽에
#     넣어야 한다 — 라이브러리가 대신 해주길 기대하면 안 된다.
#   - "실패 케이스"(사고를 못 끝맺고 스트림이 끝나는 경우)도 실측된 적이 있다
#     (1.reasoning_mode.py 의 GPU 실측 참고) — 그래서 위 코드는 </think> 가 아예 없을
#     경우도 분기 처리해뒀다.


# ─── 실행 결과 (실측, sam860/exaone-4.0:1.2b, CPU) ───────────────
# [원본 스트림 — 있는 그대로] 음... 사용자가 인공지능에 대해 간단히 한 문장으로
# 요약해달라고 요청했네. pretty straightforward query.
#
# 사용자는 아마도 복잡한 개념보다는 핵심 기능만 grasp할 수 있는 간결한 설명을
# 원하는 것 같아. ... (사고 과정이 계속 흘러나온다)
#    ^^^ 방금 </think> 가 나왔다 — 여기부터가 진짜 답변이다 ^^^
#
# 인공지능(AI)은 인간처럼 학습하고 문제 해결 능력을 모방하는 소프트웨어 시스템입니다.
#
# ==================================================
# [정리된 버전] (</think> 기준으로 직접 자른 것)
# 사고 과정: 음... 사용자가 인공지능에 대해 간단히 한 문장으로 요약해달라고
# 요청했네. pretty straightforward query. ...
# 최종 답변: 인공지능(AI)은 인간처럼 학습하고 문제 해결 능력을 모방하는
# 소프트웨어 시스템입니다.
#
# done_reason=stop
