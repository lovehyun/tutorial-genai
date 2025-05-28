# 📁 web/app.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from flask import Flask, render_template, jsonify
import asyncio
from grading_client import ExamGradingClient
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/grade', methods=['POST'])
def grade():
    async def run():
        client = ExamGradingClient()
        await client.run_grading()
        
    asyncio.run(run())
    return jsonify({"status": "done"})

@app.route('/results')
def results():
    result_file = os.getenv("GRADING_RESULT_FILE", "answers/grading_results.json")
    if not os.path.exists(result_file):
        return jsonify({"error": "채점 결과 파일이 존재하지 않습니다."}), 404
    with open(result_file, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/render_results')
def render_results_page():
    return render_template("results.html")

if __name__ == '__main__':
    app.run(debug=True)
