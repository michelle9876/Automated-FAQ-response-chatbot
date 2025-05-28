from openai import OpenAI
import os
from dotenv import load_dotenv

from memory import chat_memory

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def generate_answer_with_streaming(user_id: str, question: str, context: str):
    memory = chat_memory.get(user_id, [])

    system_prompt = (
        "당신은 네이버 스마트스토어 FAQ데이터 기반으로 작동하는 전문 챗봇입니다.\n"
        "사용자의 질문에 대해 반드시 제공된 데이터 내용 바탕으로 정확한 정보를 제공하고, 논리적으로, 적절한 답변 제공해 주세요.\n"
        "답변이 끝난 뒤에는, 사용자가 추가로 궁금해할 수 있는 관련 질문을 2가지 제안해 주세요.\n"
        "제안하는 후속 질문은 반드시 하이픈(-)으로 시작하고, 자연스럽고 유익해야 합니다.\n"
        "마지막에는 다른 궁금하신 점이 있으시면 편하게 질문해주세요. 라고 말해주세요."
    )

    messages = [{"role": "system", "content": system_prompt}] + memory + [
        {"role": "user", "content": f"문서 내용:\n{context}\n\n질문: {question}"}
    ]

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
        temperature=0.2,
    )

    def event_stream():
        reply_text = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                reply_text += content
                yield content

        memory.append({"role": "user", "content": question})
        memory.append({"role": "assistant", "content": reply_text})
        chat_memory[user_id] = memory[-10:]  # 최근 10개 유지

    return event_stream()