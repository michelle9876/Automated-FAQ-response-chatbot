from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding

def is_smartstore_question(question: str) -> bool:
    system_prompt = "다음 질문이 네이버 스마트스토어 관련인지 판단하세요. 관련 있으면 'Yes', 없으면 'No'."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0
    )
    result = response.choices[0].message.content.strip().lower()
    return "yes" in result
