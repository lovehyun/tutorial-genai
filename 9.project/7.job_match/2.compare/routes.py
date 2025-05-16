from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import requests
import os
import fitz  # PyMuPDF
import lxml.html
import re

# Flask Blueprint 생성
routes = Blueprint('routes', __name__)

# PDF 텍스트 추출 함수
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() for page in doc)
        return text.strip()
    except Exception as e:
        return f"PDF 파싱 오류: {e}"

def clean_text(text):
    # 앞뒤 공백 제거
    text = text.strip()
    # 여러 줄바꿈을 하나로
    text = re.sub(r'\n\s*\n+', '\n', text)
    # 각 줄 양 끝 공백 제거
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines)

# URL에서 XPath 또는 CSS Selector 기반 텍스트 추출 함수
def extract_text_from_url(url, selector):
    print("[요청 시작] URL:", url)
    print("[선택자 입력] XPath 또는 CSS Selector:", selector)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        print("[요청 성공] 상태 코드:", response.status_code)
        print("[응답 길이]:", len(response.content), "bytes")

        # lxml을 사용한 XPath 시도
        try:
            doc = lxml.html.fromstring(response.content)
            print("[DOM 파싱 완료] lxml.html.fromstring() 성공")

            elements = doc.xpath(selector)
            print("[XPath 매칭 요소 수]:", len(elements))

            if elements:
                texts = "\n".join(el.text_content().strip() for el in elements)
                texts = clean_text(texts)
                print("[XPath 텍스트 추출 성공]")
                return texts
            else:
                print("[XPath로 요소를 찾지 못함]")
        except Exception as xpath_err:
            print("[XPath 처리 오류]:", xpath_err)

        # fallback: BeautifulSoup + CSS Selector
        print("[Fallback] BeautifulSoup로 CSS Selector 시도")
        soup = BeautifulSoup(response.content, 'html.parser')
        selected = soup.select(selector)
        print("[CSS Selector 매칭 요소 수]:", len(selected))

        if selected:
            texts = "\n".join(el.get_text(strip=True) for el in selected)
            texts = clean_text(texts)
            print("[CSS Selector 텍스트 추출 성공]")
            return texts
        else:
            print("[CSS Selector로 요소를 찾지 못함]")

        return "선택자에 해당하는 요소를 찾을 수 없습니다."

    except Exception as e:
        print("[요청 또는 파싱 중 오류]:", e)
        return f"URL 처리 오류: {e}"

# PDF 업로드 및 텍스트 추출
@routes.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'PDF 파일이 없습니다.'}), 400
    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': '파일명이 없습니다.'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    text = extract_text_from_pdf(filepath)
    return jsonify({'text': text})

# URL 요청 및 선택자 기반 텍스트 추출
@routes.route('/fetch_url', methods=['POST'])
def fetch_url():
    data = request.get_json()
    url = data.get('url', '').strip()
    selector = data.get('xpath', '').strip()

    # 유효성 검사
    if not url or not selector:
        return jsonify({'error': 'URL과 선택자를 모두 입력해주세요.'}), 400
    if not isinstance(selector, str) or not isinstance(url, str):
        return jsonify({'error': '입력값은 문자열이어야 합니다.'}), 400

    try:
        text = extract_text_from_url(url, selector)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': f'텍스트 추출 실패: {e}'}), 500

