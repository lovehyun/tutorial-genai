# app.py
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import traceback
import logging
from datetime import datetime
from functools import wraps
from config.problems import PROBLEMS
from services.ai_service import AIService

# 환경 변수 로드
load_dotenv()

# Flask 앱 설정
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# AI 서비스 초기화
try:
    ai_service = AIService()
    logger.info("AI 서비스가 성공적으로 초기화되었습니다.")
except Exception as e:
    logger.error(f"AI 서비스 초기화 실패: {e}")
    ai_service = None

def require_ai_service(f):
    """AI 서비스가 필요한 엔드포인트를 위한 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not ai_service or not ai_service.is_initialized:
            return jsonify({
                "error": "AI 서비스가 사용할 수 없습니다.",
                "error_type": "service_unavailable"
            }), 503
        return f(*args, **kwargs)
    return decorated_function

def validate_json_data(required_fields=None):
    """JSON 데이터 검증을 위한 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({
                    "error": "요청 데이터가 없습니다.",
                    "error_type": "invalid_request"
                }), 400
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        "error": f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}",
                        "error_type": "missing_parameter"
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def handle_api_errors(f):
    """API 에러 처리를 위한 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API 오류: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                "error": f"요청 처리 중 오류가 발생했습니다: {str(e)}",
                "error_type": "internal_error"
            }), 500
    return decorated_function

def get_problem_by_id(problem_id):
    """문제 ID로 문제를 찾는 헬퍼 함수"""
    return next((p for p in PROBLEMS if p['id'] == problem_id), None)

def get_service_status():
    """서비스 상태 정보를 반환하는 헬퍼 함수"""
    return {
        'is_available': ai_service is not None and ai_service.is_initialized,
        'error_message': None if ai_service else "AI 서비스를 초기화할 수 없습니다.",
        'usage_stats': ai_service.get_usage_stats() if ai_service else {}
    }

@app.route('/')
def index():
    """메인 페이지 - 문제 목록 표시"""
    return render_template('index.html', 
                         problems=PROBLEMS, 
                         service_status=get_service_status())

@app.route('/problem/<int:problem_id>')
def problem_detail(problem_id):
    """문제 상세 페이지"""
    problem = get_problem_by_id(problem_id)
    if not problem:
        return render_template('error.html', 
                             error="요청하신 문제를 찾을 수 없습니다."), 404
    
    return render_template('problem.html', 
                         problem=problem, 
                         service_status=get_service_status())

@app.route('/api/solution', methods=['POST'])
@require_ai_service
@validate_json_data(['problem_id'])
@handle_api_errors
def get_solution():
    """AI 풀이 생성 API"""
    data = request.get_json()
    problem_id = data['problem_id']
    
    logger.info(f"풀이 요청: 문제 {problem_id}")
    
    problem = get_problem_by_id(problem_id)
    if not problem:
        return jsonify({
            "error": "문제를 찾을 수 없습니다.",
            "error_type": "problem_not_found"
        }), 404
    
    # AI 풀이 생성
    solution = ai_service.generate_solution(problem)
    
    return jsonify({
        "success": True,
        "solution": solution,
        "problem": problem,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/check-answer', methods=['POST'])
@require_ai_service
@validate_json_data(['problem_id', 'user_answer'])
@handle_api_errors
def check_answer():
    """학생 답안 채점 API"""
    data = request.get_json()
    problem_id = data['problem_id']
    user_answer = data['user_answer']
    
    logger.info(f"답안 채점 요청: 문제 {problem_id}")
    
    problem = get_problem_by_id(problem_id)
    if not problem:
        return jsonify({
            "error": "문제를 찾을 수 없습니다.",
            "error_type": "problem_not_found"
        }), 404
    
    # AI 답안 채점
    feedback, score = ai_service.check_answer(problem, user_answer)
    
    return jsonify({
        "success": True,
        "feedback": feedback,
        "score": score,
        "problem": problem,
        "user_answer": user_answer,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/hint', methods=['POST'])
@require_ai_service
@validate_json_data(['problem_id'])
@handle_api_errors
def get_hint():
    """추가 힌트 제공 API"""
    data = request.get_json()
    problem_id = data['problem_id']
    
    logger.info(f"힌트 요청: 문제 {problem_id}")
    
    problem = get_problem_by_id(problem_id)
    if not problem:
        return jsonify({
            "error": "문제를 찾을 수 없습니다.",
            "error_type": "problem_not_found"
        }), 404
    
    # AI 힌트 생성
    hint = ai_service.generate_hint(problem)
    
    return jsonify({
        "success": True,
        "hint": hint,
        "problem": problem,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/status')
def get_service_status_api():
    """AI 서비스 상태 조회 API"""
    try:
        if not ai_service:
            return jsonify({
                "status": "unavailable",
                "message": "AI 서비스가 초기화되지 않았습니다.",
                "details": {}
            })
        
        usage_stats = ai_service.get_usage_stats()
        current_settings = ai_service.get_current_settings()
        
        return jsonify({
            "status": "available" if ai_service.is_initialized else "error",
            "message": "AI 서비스가 정상 작동 중입니다." if ai_service.is_initialized else "AI 서비스에 문제가 있습니다.",
            "usage_stats": usage_stats,
            "current_settings": current_settings,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"상태 조회 중 오류: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"상태 조회 중 오류가 발생했습니다: {str(e)}",
            "details": {}
        }), 500

@app.route('/api/reset-memory', methods=['POST'])
@require_ai_service
@handle_api_errors
def reset_memory():
    """AI 대화 메모리 초기화 API"""
    ai_service.reset_memory()
    logger.info("AI 메모리가 초기화되었습니다.")
    
    return jsonify({
        "success": True,
        "message": "대화 메모리가 초기화되었습니다.",
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return render_template('error.html', 
                         error="요청하신 페이지를 찾을 수 없습니다."), 404

@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    logger.error(f"내부 서버 오류: {error}")
    return render_template('error.html', 
                         error="서버 내부 오류가 발생했습니다."), 500

@app.errorhandler(503)
def service_unavailable(error):
    """503 에러 핸들러"""
    return render_template('error.html', 
                         error="AI 서비스를 사용할 수 없습니다."), 503

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    
    logger.info(f"Flask 서버 시작: {host}:{port}, Debug: {debug_mode}")
    app.run(debug=debug_mode, port=port, host=host)
