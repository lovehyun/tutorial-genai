# pip install flask python-dotenv openai
import os
import logging
from dotenv import load_dotenv

from flask import Flask, request, jsonify, send_from_directory

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

logging.basicConfig(level=logging.INFO)

load_dotenv()

# static_url_path=''는 정적 파일의 URL 경로 접두사를 설정합니다.
#  - static_url_path='': /styles.css로 접근 가능
#  - 설정 없을 때: /static/styles.css로 접근해야 함
app = Flask(__name__, static_folder='public', static_url_path='')

# LangChain 모델 초기화
llm = ChatOpenAI(
    model='gpt-3.5-turbo',
    temperature=0.7,
    api_key=os.getenv('OPENAI_API_KEY')
)

# 1단계: 요약 프롬프트
summary_prompt = PromptTemplate.from_template(
    """다음 리뷰 목록을 기반으로 간결한 요약을 한국어로 작성하시오.

리뷰내역:
{reviews_text}
"""
)

# 2단계: 번역 프롬프트
translate_prompt = PromptTemplate.from_template(
    """다음 한국어 문장을 {target_lang_name}로 번역해줘:

{summary_ko}
"""
)

###########################################################
# 체인 구성
###########################################################
# 방법1. -->
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# 요약 → 번역 파이프라인
summary_then_translate = (
    {
        # 이런 "딕셔너리 매퍼"를 쓰면, 다음 단계(= 번역 프롬프트) 에 들어갈 입력 딕셔너리를 만들게 됩니다.
        # "summary_ko" 키는 왼쪽 서브체인의 결과값으로 채워지고,
        # "target_lang_name" 키는 원래 입력에서 가져온 값으로 채워집니다. (이때 그대로 전달하려고 RunnablePassthrough()를 씁니다)

        # 1단계: 요약 결과를 summary_ko 로 매핑
        "summary_ko": summary_prompt | llm | RunnableLambda(lambda m: m.content),
        # 2단계: 호출 시 넣은 target_lang_name 그대로 통과
        "target_lang_name": RunnablePassthrough()
    }
    # 2단계 프롬프트 및 LLM
    | translate_prompt
    | llm
    | RunnableLambda(lambda m: m.content)
)
# 방법1. <--


# 방법2. -->
from langchain_core.runnables import RunnableLambda

# 요약 → 번역 파이프라인 (원본 입력에서 필요한 키를 Lambda로 뽑아 주입)
summary_then_translate = (
    {
        "summary_ko": summary_prompt | llm | RunnableLambda(lambda m: m.content),
        "target_lang_name": RunnableLambda(lambda x: x["target_lang_name"])
    }
    | translate_prompt
    | llm
    | RunnableLambda(lambda m: m.content)
)
# 방법2. <--


# 방법3. -->
from langchain_core.runnables import RunnableBranch, RunnableLambda

# 1) 요약만 하는 Runnable (content 텍스트로 변환)
summarize_only = summary_prompt | llm | RunnableLambda(lambda m: m.content)

# 2) 요약 → 번역 체인 (최종 문자열 반환)
summarize_then_translate = (
    {
        "summary_ko": summarize_only,
        "target_lang_name": RunnableLambda(lambda x: x["target_lang_name"]),
    }
    | translate_prompt
    | llm
    | RunnableLambda(lambda m: m.content)
)

# 분기:
# - branches (조건 True(ko)면 요약만 반환)
# - 그 외(default)면 요약→번역 수행
#
# RunnableBranch(branches: Sequence[Tuple[condition_callable, runnable]], default: Optional[runnable] = None)
summary_or_translate = RunnableBranch(
    (lambda x: x.get("target_lang") == "ko", summarize_only),
    summarize_then_translate
)
# 방법3. <--


# In-memory storage for reviews
reviews = []

@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.get_json()
    rating = data.get('rating')
    opinion = data.get('opinion')

    if not rating or not opinion:
        return jsonify({'error': 'Rating and opinion are required'}), 400

    reviews.append({'rating': rating, 'opinion': opinion})
    return jsonify({'message': 'Review added successfully'}), 201

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    return jsonify({'reviews': reviews})

@app.route('/api/ai-summary', methods=['GET'])
def get_ai_summary():
    target_lang = request.args.get('lang', 'ko')
    lang_name_map = {
        'ko': '한국어',
        'en': '영어',
        'ja': '일본어',
        'zh': '중국어',
        'fr': '프랑스어',
        'it': '이탈리아어'
    }
    target_lang_name = lang_name_map.get(target_lang, '한국어')

    if not reviews:
        return jsonify({'summary': '리뷰가 없습니다.', 'averageRating': 0})

    average_rating = sum(review['rating'] for review in reviews) / len(reviews)
    reviews_text = '\n'.join([f"별점: {review['rating']}, 내용: {review['opinion']}" for review in reviews])

    try:
        # 방법 1. 2. -->
        # 항상 번역까지: summary_then_translate
        # result_msg = summary_then_translate.invoke({
        #     "reviews_text": reviews_text,
        #     "target_lang_name": target_lang_name
        # })
        # 방법 1. 2. <--

        # 방법 3. -->        
        # ko면 번역 스킵: summary_or_translate
        result_msg = summary_or_translate.invoke({
            "reviews_text": reviews_text,
            "target_lang": target_lang,
            "target_lang_name": target_lang_name
        })
        # 방법 3. <--
        
        print('[최종 번역 결과]:', result_msg)
        return jsonify({'summary': result_msg, 'averageRating': average_rating})
    
    except Exception as e:
        app.logger.error(f'Error generating AI summary: {str(e)}')
        return jsonify({'error': 'Failed to generate AI summary'}), 500

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index2.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
