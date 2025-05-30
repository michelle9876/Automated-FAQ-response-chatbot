from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import os
from dotenv import load_dotenv


from chat import generate_answer_with_streaming
from memory import chat_memory
from vector_store import get_relevant_chunk
from utils import get_embedding, is_smartstore_question


# .env 파일 로딩
load_dotenv()
app = FastAPI()

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.get("/")
def read_root():
    return {"message": "SmartStore FAQ Chatbot API is running"}


@app.get("/chat")
async def chat_stream(question: str, user_id: str = "default_user"):
    # 스마트스토어 질문 필터링 
    if not is_smartstore_question(question):
        def fake_stream():
            yield "저는 스마트 스토어 FAQ를 위한 챗봇입니다. 스마트 스토어에 대한 질문을 부탁드립니다.\n"
        return StreamingResponse(fake_stream(), media_type="text/plain")

     # 유사한 chunk 검색 
    question_embedding = get_embedding(question)

    context = get_relevant_chunk(question_embedding)

    # 스트리밍 응답 생성
    return StreamingResponse(
        generate_answer_with_streaming(user_id=user_id, question=question, context=context),
        media_type="text/plain"
    )

@app.get("/memory/{user_id}")
def get_user_memory(user_id: str):
    memory = chat_memory.get(user_id)
    if not memory:
        return {"message": f"user_id='{user_id}'에 대한 대화 기록이 없습니다."}
    return {
        "user_id": user_id,
        "history": memory
    }
