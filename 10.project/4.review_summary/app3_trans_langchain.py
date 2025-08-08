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

# 체인 구성
summary_chain = summary_prompt | llm
translate_chain = translate_prompt | llm

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
        # 1단계: 요약
        summary_ko = summary_chain.invoke({"reviews_text": reviews_text}).content
        print('[1차 요약 결과]:', summary_ko)

        # 2단계: 번역 (ko가 아닌 경우만)
        if target_lang != 'ko':
            translated = translate_chain.invoke({
                "summary_ko": summary_ko,
                "target_lang_name": target_lang_name
            }).content
        else:
            translated = summary_ko

        print('[최종 번역 결과]:', translated)
        return jsonify({'summary': translated, 'averageRating': average_rating})
    
    except Exception as e:
        app.logger.error(f'Error generating AI summary: {str(e)}')
        return jsonify({'error': 'Failed to generate AI summary'}), 500

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index2.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
