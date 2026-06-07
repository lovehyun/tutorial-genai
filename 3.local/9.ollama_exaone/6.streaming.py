"""
(6) 스트리밍 출력 — 생성되는 토큰을 실시간으로 받아 출력 (ollama SDK)
긴 답변에서 '다 기다렸다 한 번에' 대신 타이핑되듯 보여준다 (챗봇 UX 의 기본).

준비: pip install ollama  +  ollama pull exaone3.5
"""
import ollama

MODEL = "exaone3.5:latest"


def chat_stream(prompt):
    """stream=True → 청크를 for 루프로 받아 이어붙인다 (REST 의 NDJSON 파싱이 불필요)"""
    for chunk in ollama.chat(model=MODEL, stream=True,
                             messages=[{"role": "user", "content": prompt}]):
        print(chunk["message"]["content"], end="", flush=True)
    print()


print("=" * 55)
print(" 스트리밍 생성 (토큰이 도착하는 대로 출력)")
print("=" * 55)
chat_stream("인공지능의 장점 3가지를 한국어로 설명해줘.")

# 학습 포인트:
#   - SDK 는 stream=True 면 그냥 for 루프 — chunk["message"]["content"] 를 이어붙이면 끝
#   - REST 버전(6.ollama1_restapi/2.streaming.py)은 iter_lines()+json.loads 가 필요했다
