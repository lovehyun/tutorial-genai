# pip install anthropic python-dotenv
#
# 중급 6: 프롬프트 캐싱 — 크고 고정된 컨텍스트를 캐시해 반복 호출 비용을 줄인다(최대 ~90%).
# 같은 prefix 를 다시 보내면 캐시에서 읽어온다(cache_read_input_tokens 에 잡힘).
# ★ 주의: 캐시되려면 prefix 가 충분히 커야 한다(Sonnet 4.6 최소 ~2048 토큰). 작으면 조용히 캐시 안 됨.

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 캐시 대상이 될 큰 고정 컨텍스트 (실전에선 긴 문서/규정 등). 데모용으로 길게 만든다.
big_context = "다음은 회사 제품 매뉴얼이다.\n" + ("이 제품은 방수 기능을 지원하며 보증 기간은 2년이다. " * 400)

def ask(question):
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        # system 블록에 cache_control 을 달면 그 prefix 가 캐시된다.
        system=[{"type": "text", "text": big_context, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": question}],
    )
    u = resp.usage
    print(f"  Q: {question}")
    print(f"    캐시 write: {u.cache_creation_input_tokens}, "
          f"캐시 read: {u.cache_read_input_tokens}, 일반 입력: {u.input_tokens}")

print("1번째 호출 (캐시 생성 → write 토큰이 잡힌다):")
ask("이 제품 방수 돼?")
print("2번째 호출 (캐시 적중 → read 토큰이 잡혀야 정상):")
ask("보증 기간은?")
