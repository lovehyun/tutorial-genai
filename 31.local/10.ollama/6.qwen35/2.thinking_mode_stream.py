"""
(2) 생각 모드를 스트리밍으로 — "아직 살아있나?"를 실시간으로 확인한다.

1.thinking_mode.py 에서 본 것처럼 생각 모드는 수십 초씩 걸릴 수 있고, 심지어 예산을
다 써버리고 빈 답으로 끝날 수도 있다. stream=True 로 바꾸면 사고 과정이 토큰 단위로
그 자리에서 흘러나와서, 멈춰있는 게 아니라 실제로 "생각하고 있다"는 걸 눈으로 확인할 수 있고,
이상하게 새는 것 같으면 중간에 끊을 수도 있다(이 파일은 끝까지 받지만, 실전에서는
break 로 끊고 재시도하는 로직을 붙이기 좋다).

준비: pip install ollama  +  ollama pull qwen3.5:2b
"""
import ollama

MODEL = "qwen3.5:2b"
QUESTION = "인공지능을 한 문장으로 설명해줘."

stream = ollama.chat(
    model=MODEL,
    messages=[{"role": "user", "content": QUESTION}],
    think=True,
    stream=True,   # ← 이 한 줄만 다르다 — 나머지는 1.thinking_mode.py 와 동일
)

phase = None
final_chunk = None
for chunk in stream:
    m = chunk["message"]
    if m.thinking:
        if phase != "thinking":
            print("\n[사고 중] ", end="", flush=True)
            phase = "thinking"
        print(m.thinking, end="", flush=True)   # 토큰이 도착하는 즉시 바로 출력
    if m.content:
        if phase != "content":
            print("\n\n[답변] ", end="", flush=True)
            phase = "content"
        print(m.content, end="", flush=True)
    final_chunk = chunk

print(f"\n\ndone_reason={final_chunk.get('done_reason')}  eval_count={final_chunk.get('eval_count')}")


# 정리:
#   - stream=True 하나만 바꾸면 된다 — think=True/False 와 완전히 독립적인 옵션이다.
#   - 스트리밍이 아니면(1.thinking_mode.py) 사고+답변이 다 끝날 때까지 아무 것도 안 보이다가
#     한 번에 통째로 나온다 — 그 사이 사용자는 "멈춘 건가?"를 알 방법이 없다.
#   - 스트리밍하면 사고 과정이 토큰 단위로 실시간으로 보인다. 아래 실측 발췌처럼, 모델이
#     후보 문장을 여러 개 만들었다가("Draft 1", "Draft 2"...) 스스로 다시 고치는 과정을
#     그대로 지켜볼 수 있다 — 1.thinking_mode.py 의 "왜 예산을 다 쓰는가"에 대한 답이
#     실시간으로 눈앞에서 펼쳐지는 셈이다.
#   - 실전 활용: 사고 과정이 일정 길이/시간을 넘으면 중간에 스트림을 끊고(break) "예산을 늘려
#     재시도" 하는 로직을 붙이면, 1.thinking_mode.py 의 "빈 답변으로 끝남" 문제를 사용자를
#     오래 기다리게 하지 않고 더 빨리 감지·대응할 수 있다.


# ─── 실행 결과 (실측, qwen3.5:2b, CPU) — 사고 과정 발췌 ─────────────────
# [사고 중] Thinking Process:
#
# 1.  **Analyze the Request:**
#     *   Topic: Artificial Intelligence (AI).
#     *   Constraint: One sentence explanation in Korean ("한 문장").
#
# 2.  **Identify Key Concepts of AI:** ...
#
# 3.  **Drafting Initial Sentences:**
#     *   인공지능은 인간과 유사한 지능을 가진 컴퓨터가 문제를 해결하는 기술을 말하는
#         것입니다. - Accurate but maybe too literal.
#     *   인공지능은 인간의 똑똑함과 같은 능력을 갖춘 자동화된 시스템입니다. - Good, but
#         "smarts" might be better translated as "지능".
#     *   인공지능은 데이터를 분석하여 패턴을 찾고 예측하는 알고리즘과 시스템을
#         의미합니다. - Very technical definition.
#
# 4.  **Selecting the Best Option:**
#     *   Draft A: 인공지능은 컴퓨터가 학습하고 판단하여 인간의 지능과 유사한 작업을
#         수행하는 시스템을 뜻합니다.
#     *   Draft B: 인공지능은 데이터를 분석하고 예측이나 결정에 필요한 논리나 패턴을
#         찾아내는 알고리즘 및 시스템의 총칭입니다.
#
# 5.  **Refining for Conciseness and Clarity:** ...
#     Actually, the standard definition often says: '인공지능(AI)이란 머신러닝과 같은
#     기술을 활용해서...'
#
# 6.  **Final Polish (Checking One-Sentence Constraint):**
#     "인공지능은计算机를 대상으로 하는 프로그램이며..." -> Too wordy.
#     Let's try: "..." (Too long).
#
# (이런 식으로 Draft/Option 을 열 번 넘게 다시 쓰며 "Let's go with this simpler
#  definition", "Actually, the most standard one-sentence explanation..."을 반복하다가
#  맨 마지막에야 하나를 확정한다 — 실시간으로 보면 왜 사고 과정이 그렇게 길어지는지
#  훨씬 체감된다.)
#
# [답변] 인공지능은 데이터와 논리를 기반으로 스스로 학습하고 판단하여 인간이 해야 할
# 일을 대신하거나 복잡한 문제를 해결하는 기능을 갖는 시스템입니다.
#
# done_reason=stop  eval_count=2775
