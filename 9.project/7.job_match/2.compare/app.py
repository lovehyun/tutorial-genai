# pip install flask requests beautifulsoup4 lxml pymupdf
from flask import Flask
from routes import routes
from compare import compare_routes
from gpt_compare import gpt_routes
import os

import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 폴더가 없으면 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 블루프린트 등록
app.register_blueprint(routes)
app.register_blueprint(compare_routes)
app.register_blueprint(gpt_routes)

if __name__ == '__main__':
    app.run(debug=True)
