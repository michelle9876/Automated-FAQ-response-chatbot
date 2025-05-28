import pickle
from openai import OpenAI
import tiktoken
import numpy as np
import os
from dotenv import load_dotenv

# .env 파일 로딩
load_dotenv()

# 환경변수에서 키 불러오기
api_key = os.getenv("OPENAI_API_KEY")
# print(api_key)

client = OpenAI(api_key=api_key)
with open("embedding_model.pkl", "rb") as f:
    loaded_data = pickle.load(f)

print(loaded_data)