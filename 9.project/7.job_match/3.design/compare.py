# pip install scikit-learn numpy pandas
 
from flask import Blueprint, request, Response, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

compare_routes = Blueprint('compare_routes', __name__)

# 텍스트 유사도 분석 함수
def compare_texts(text1, text2):
    try:
        vectorizer = TfidfVectorizer().fit_transform([text1, text2])
        vectors = vectorizer.toarray()
        sim_score = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
        return round(sim_score * 100, 2)
    except Exception as e:
        return f"유사도 계산 오류: {e}"

# /compare 라우트
@compare_routes.route('/compare', methods=['POST'])
def compare():
    data = request.get_json()
    text1 = data.get('left', '').strip()
    text2 = data.get('right', '').strip()

    if not text1 or not text2:
        return jsonify({'error': '비교할 텍스트가 충분하지 않습니다.'}), 400

    def generate():
        yield "분석을 시작합니다...\n"
        yield "텍스트 벡터화를 수행 중...\n"
        score = compare_texts(text1, text2)
        yield f"분석 완료: 두 문서의 유사도는 {score}% 입니다.\n"

    return Response(generate(), mimetype='text/plain')
