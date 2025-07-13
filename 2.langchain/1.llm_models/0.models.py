# https://platform.openai.com/docs/api-reference/models
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path='../.env')
client = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY'),  # this is also the default, it can be omitted
)

model_list = client.models.list()
for m in model_list:
    print(m.id)

# | 모델 이름                   | Chat Model  | Completion (Instruct) Model   | 비고                                   |
# | -------------------------- | ----------- | ----------------------------- | -------------------------------------- |
# | **text-davinci-003**       | ❌          | ✅                           | Legacy Completion 모델 (2024년 초 비권장됨) |
# | **gpt-3.5-turbo**          | ✅          | ❌                           | 대표적인 Chat Model                     |
# | **gpt-3.5-turbo-instruct** | ❌          | ✅                           | Completion용 (구 text-davinci 대체)     |
# | **gpt-4**                  | ✅          | ❌                           | Chat Model                             |
# | **gpt-4o**                 | ✅          | ❌                           | 최신 멀티모달 Chat Model                |
# | **gpt-4o-mini**            | ❌          | ✅                           | 현재 기준으로 **Instruct 전용**         |

