"""
(3) 요약 — 긴 한국어 글을 핵심 요약 + 불릿으로 (ollama SDK)
EXAONE 의 한국어 이해력으로 문서 요약.

준비: pip install ollama  +  ollama pull exaone3.5
"""
import ollama

MODEL = "exaone3.5:latest"


def chat(system, user, temperature=0.3):
    return ollama.chat(model=MODEL, options={"temperature": temperature},
                       messages=[{"role": "system", "content": system},
                                 {"role": "user", "content": user}])["message"]["content"]


document = """
인공지능(AI) 기술은 최근 몇 년간 급격히 발전하며 우리 사회 전반에 큰 영향을 미치고 있다.
특히 대규모 언어 모델(LLM)의 등장으로 기계가 사람처럼 자연스러운 문장을 생성하고 이해하는
능력이 비약적으로 향상되었다. 이러한 모델은 고객 상담, 문서 작성, 번역, 코드 생성 등 다양한
분야에서 활용되고 있다. 한편으로는 일자리 대체, 허위 정보 생성, 개인정보 보호 등 새로운
사회적 우려도 함께 제기되고 있다. 전문가들은 AI 의 혜택을 누리면서도 위험을 관리하기 위한
제도와 윤리 기준 마련이 시급하다고 입을 모은다.
"""

# [관전 포인트] 요약은 '길이/형식' 을 프롬프트로 통제 (temperature 낮게 = 사실 유지)
print("=" * 55, "\n 한 문장 요약\n", "=" * 55)
print(chat("당신은 요약 전문가입니다.", f"다음 글을 한 문장으로 요약하세요.\n\n{document}"))

print("\n" + "=" * 55, "\n 핵심 3개 불릿 요약\n", "=" * 55)
print(chat("당신은 요약 전문가입니다.",
           f"다음 글의 핵심을 불릿 3개로 요약하세요. 각 항목은 한 줄로.\n\n{document}"))

# 학습 포인트:
#   - temperature 0.3 정도로 낮춰 '없는 내용 지어내기' 를 줄인다
#   - 출력 형식(문장 수/불릿 개수)을 프롬프트로 명시하면 일관된 요약을 얻는다
