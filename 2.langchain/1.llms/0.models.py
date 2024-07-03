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
