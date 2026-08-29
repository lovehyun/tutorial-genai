"""
(1) 생각 모드(reasoning) on/off — EXAONE 3.5 에는 없던 기능.
EXAONE 4.0 은 Qwen 3.5 처럼 같은 모델 안에서 생각 모드를 켜고 끌 수 있다(think=True/False).

준비: pip install ollama  +  ollama pull sam860/exaone-4.0:1.2b

⚠️ EXAONE 4.0 은 Ollama 공식 라이브러리에 아직 없다 — 커뮤니티가 올린 GGUF
(sam860/exaone-4.0)를 쓴다. 이 파일 아래 실측에서 보듯, 공식 라이브러리 모델(Qwen 3.5)과
달리 생각 과정이 message["thinking"] 으로 깔끔하게 분리되지 않는 경우가 있다 — 커뮤니티
변환본의 한계를 그대로 보여주는 것도 이 파일의 목적이다.
"""
import ollama

MODEL = "sam860/exaone-4.0:1.2b"
QUESTION = "인공지능을 한 문장으로 설명해줘."


def ask(think: bool):
    return ollama.chat(model=MODEL, messages=[{"role": "user", "content": QUESTION}], think=think)


print("[생각 모드 OFF]")
r_off = ask(think=False)
print(r_off["message"].content)

print("\n[생각 모드 ON]")
r_on = ask(think=True)
thinking = r_on["message"].thinking or ""
content = r_on["message"].content or ""
print(f"message['thinking'] 길이: {len(thinking)}자  ← Qwen 3.5(../6.qwen35)라면 여기 채워져야 정상")

if not thinking and "</think>" in content:
    # ⚠️ 여기서 실제로 확인된 것: thinking 필드는 비어 있는데, </think> 원본 태그가
    # content 안에 그대로 새어 나온다. Ollama 가 이 GGUF 의 템플릿에서 생각 부분을 제대로
    # 분리 못 한다는 뜻이다 — Qwen 3.5 는 공식 라이브러리라 이 분리가 정확히 되지만,
    # EXAONE 4.0 커뮤니티 변환본은 그렇지 않을 수 있다.
    #   참고: 여는 태그 <think> 는 실행마다 있을 때도 없을 때도 있다(챗 템플릿이 미리
    #   깔아주는 경우가 많아, 모델이 실제로 "생성"하는 건 대개 닫는 태그부터다) — 그래서
    #   판별은 </think> 유무만으로 한다.
    print("→ thinking 필드가 비어 있고, 대신 content 안에 </think> 태그가 그대로 섞여 있다!")
    head, _, rest = content.partition("</think>")
    manual_thinking = head.replace("<think>", "").strip()
    final_answer = rest.strip()
    print(f"\n[직접 잘라낸 사고 과정] ({len(manual_thinking)}자)")
    print(manual_thinking)
    print("\n[직접 잘라낸 최종 답변]")
    print(final_answer)
else:
    print(thinking)
    print("\n[최종 답변]")
    print(content)


# 정리:
#   - EXAONE 4.0 도 think=True/False 옵션 자체는 받아준다 — 옵션이 없다고 에러가 나거나
#     무시되지는 않는다.
#   - 하지만 Ollama 공식 라이브러리 모델(Qwen 3.5)과 다르게, **이 커뮤니티 GGUF 에서는
#     message["thinking"] 이 채워지지 않고 원본 <think>...</think> 태그가 content 에
#     그대로 섞여 나온다.** ollama.show() 로 보면 이 모델도 "thinking" capability 가
#     선언돼 있는데도 실측으론 이렇다 — **"capability 가 선언돼 있다"와 "API가 정확히
#     동작한다"는 다른 문제**라는 걸 보여주는 실제 사례다.
#   - 실전 교훈: message["thinking"] 을 무조건 믿지 말고, 비어 있으면 content 안에
#     <think> 태그가 섞여 있는지 직접 확인하는 방어 코드가 필요하다(위 코드가 그 예시다).
#   - 원인은 모델 자체가 아니라 **Ollama 로 패키징한 커뮤니티 업로더의 템플릿 설정** 쪽일
#     가능성이 높다 — 공식 라이브러리에 없는 모델을 쓸 때 감수해야 하는 리스크다.


# ─── 실행 결과 (실측, sam860/exaone-4.0:1.2b, CPU) ───────────────
# [생각 모드 OFF]
# "인공지능은 인간의 능력을 모방하는 컴퓨터 프로그램으로 데이터를 학습하고 예측 및
# 문제 해결 능력을 부여합니다."
#
# [생각 모드 ON]
# message['thinking'] 길이: 0자  ← Qwen 3.5(../6.qwen35)라면 여기 채워져야 정상
# → thinking 필드가 비어 있고, 대신 content 안에 </think> 태그가 그대로 섞여 있다!
#
# [직접 잘라낸 사고 과정] (399자)
# Okay, 사용자가 인공지능을 한 문장으로 요약해달라고 했네. pretty straightforward
# request이야.
# 사용자는 아마 복잡한 개념을 간결하게 이해하고 싶은 모양이야. 기술 용어보다는 핵심만
# catching them might be better.
# 내가 생각할 때 중요한 건...
# 1) 정의적 측면(기계의 지능 학습/예측 능력 강조)
# 2) 현대 기술 적용 범위(데이터 처리부터 의료까지 다양함)
# 3) 미래 전망(지속 발전하는 시스템이라는 점)
# 을 포함시켜야겠어. 한 문장엔 150자 내외로 압축하는 게 좋겠다. ...
#
# [직접 잘라낸 최종 답변]
# 인공지능은 데이터를 학습하고 패턴을 인식하여 인간이 이해하기 어려운 문제를 스스로
# 해결하거나 자동화된 서비스를 제공하는 컴퓨터 기반 intelligent 시스템입니다.


# ─── 참고: 같은 실험을 GPU 서버(RTX 4070 Laptop)에서 실측 ────────────────
# OFF  2.3초  done_reason=stop
# ON   2.0초  done_reason=stop  thinking_field_len=0
#   content: "음, 사용자가 인공지능을 하나의 문장으로 압축해서 알려달라고 요청했네.
#   ... 사용자가 " (여기서 그대로 끊김 — </think> 태그도, 최종 답변도 없이 끝났다!)
#
# → CPU에서는 사고 후 </think> + 최종 답변까지 도달했는데, GPU에서는 같은 코드로도
#   사고 도중에 문장이 그냥 끊겨버렸다(Qwen 3.5의 "예산 부족" 현상과 다른 형태지만
#   본질은 같다 — 생각 모드는 "언제 끝날지" 자체가 실행마다 달라지는 불안정한 과정이다).
#   속도도 OFF(2.3초)와 ON(2.0초)이 거의 차이 없다 — 1.2B라는 작은 모델 크기 때문에
#   생각을 하든 안 하든 그 자체로 빠르지만, 그만큼 "생각을 제대로 끝맺을 여유"도 없다는
#   뜻일 수 있다.
