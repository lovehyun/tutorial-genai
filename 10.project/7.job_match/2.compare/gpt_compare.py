from flask import Blueprint, request, Response, jsonify
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

gpt_routes = Blueprint('gpt_routes', __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@gpt_routes.route('/gpt_compare', methods=['POST'])
def gpt_compare():
    data = request.get_json()
    left = data.get('left', '').strip()
    right = data.get('right', '').strip()

    if not left or not right:
        return jsonify({'error': '텍스트가 비어 있습니다.'}), 400

    def generate():
        try:
            system_prompt = (
                "당신은 채용 도우미입니다. "
                "아래는 왼쪽에 사용자의 이력서 내용이고, 오른쪽은 구인 사이트에 등록된 채용 공고입니다. "
                "두 텍스트를 비교하여 직무 적합성을 평가하고, 구직자가 이 공고에 적합한지 상세하게 설명해주세요. "
                "유사한 항목, 부족한 항목, 강점 등을 조목조목 정리해주세요. 마지막에는 간단한 요약과 적합도 점수(0~100)를 주세요."
            )

            user_prompt = f"""[사용자 이력서]
{left}

[채용 공고]
{right}
"""

            print("[GPT 요청 프롬프트]")
            print("[SYSTEM]:", system_prompt)
            print("[USER]:", user_prompt)

            yield "GPT 분석 요청 중...\n"

            stream = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                stream=True,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices[0].delta else ''
                if delta:
                    yield delta

        except Exception as e:
            print("[GPT 오류]:", e)
            yield f"\n분석 중 오류 발생: {e}"

    return Response(generate(), mimetype='text/plain')
