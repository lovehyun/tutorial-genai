# pip install anthropic python-dotenv
#
# 중급 7: 에러 처리 — SDK 의 타입별 예외로 상황을 구분한다.
# 문자열 매칭("429" in str(e)) 대신 예외 "클래스"로 잡는 게 정석.
# 참고: SDK 는 429(한도)·5xx(서버오류)를 자동 재시도한다(max_retries 로 조절, 기본 2).

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def safe_call(model):
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=100,
            messages=[{"role": "user", "content": "안녕"}],
        )
        print("  성공:", resp.content[0].text)
    except anthropic.NotFoundError:
        print("  모델/엔드포인트를 찾을 수 없음 (모델 ID 오타?)")
    except anthropic.AuthenticationError:
        print("  API 키가 잘못됨")
    except anthropic.RateLimitError:
        print("  요청 한도 초과 — 잠시 후 재시도")
    except anthropic.APIStatusError as e:
        print(f"  API 오류 {e.status_code}: {e.message}")

print("정상 모델:")
safe_call("claude-haiku-4-5")

print("잘못된 모델 ID:")
safe_call("claude-does-not-exist")   # NotFoundError 발생
