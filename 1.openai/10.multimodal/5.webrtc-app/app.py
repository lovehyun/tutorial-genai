# pip install flask flask-socketio python-dotenv torch simple-peer
# pip install faster-whisper

from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from whisper_utils import transcribe_audio
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
socketio = SocketIO(app, cors_allowed_origins="*")

meeting_log = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    print("요청 수신됨: ", request.files)
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['audio']
    print("업로드 파일명:", file.filename)
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    transcript = transcribe_audio(filepath)
    os.remove(filepath)

    user = request.form.get("user", "사용자")
    message = f"[{user}] {transcript}"
    meeting_log.append(message)

    socketio.emit("caption", {"message": message})
    return jsonify({'message': message})

@app.route('/summary', methods=['POST'])
def summary():
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    transcript = "\n".join(meeting_log)
    messages = [
        {"role": "system", "content": "다음 회의록을 요약해 주세요."},
        {"role": "user", "content": transcript}
    ]
    print(transcript)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return jsonify({"summary": response.choices[0].message.content.strip()})

if __name__ == '__main__':
    socketio.run(app, debug=True)
