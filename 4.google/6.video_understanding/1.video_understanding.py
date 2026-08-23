# pip install google-genai python-dotenv
#
# 비디오 이해 — Gemini만의 강점 중 하나. 이미지 몇 장을 프레임 샘플링해서 보는 게 아니라,
# 영상을 '영상 그대로' 이해한다(시간 흐름·장면 전환·오디오까지 함께 처리).
# OpenAI/Anthropic 예제 폴더에는 이 기능이 없다 — 텍스트/이미지/PDF 입력까지만 다룬다.
#
# 로컬 파일 없이도 유튜브 URL을 그대로 넣을 수 있어 실습이 간단하다(별도 업로드 불필요).
# 로컬 영상 파일을 쓰려면 File.io 대신 아래 주석의 업로드 방식을 참고할 것.

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# [관전 포인트 1] file_data + file_uri에 유튜브 URL을 그대로 넣는다 — 다운로드/업로드 불필요.
#   (역사상 최초로 업로드된 유튜브 영상 — "Me at the zoo", 2005)
video_part = types.Part(file_data=types.FileData(file_uri="https://www.youtube.com/watch?v=jNQXAC9IVRw"))
question_part = types.Part(text="이 영상은 무슨 내용이야? 한 문장으로 설명해줘.")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=types.Content(parts=[video_part, question_part]),
)

print(response.text)

# 참고: 로컬 영상 파일을 쓰려면 먼저 업로드해서 file_id를 받아야 한다.
#   uploaded = client.files.upload(file="my_video.mp4")
#   video_part = types.Part(file_data=types.FileData(file_uri=uploaded.uri))
# (긴 영상일수록 업로드/처리 시간이 걸린다 — Files API는 3.anthropic/9.files_api와 같은 개념)
