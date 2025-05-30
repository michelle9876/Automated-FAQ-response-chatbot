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
print(api_key)
client = OpenAI(api_key=api_key)


with open("final_result.pkl", "rb") as f:
    data = pickle.load(f)

if hasattr(data, "to_string"):
    text = data.to_string()
else:
    text = str(data)

# print(text)    


# 1. 텍스트 분할 (chunking)
def split_text(text, max_tokens=200, overlap=20):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    
    chunks = []
    for i in range(0, len(tokens), max_tokens - overlap):
        chunk = tokens[i:i + max_tokens]
        chunk_text = tokenizer.decode(chunk)
        print("===chunk=====")
        print(chunk_text)
        chunks.append(chunk_text)
    return chunks

chunks = split_text(text)

# 2. 각 chunk에 대해 임베딩 생성
def get_embedding(text):
    print(f"임베딩 생성 중: {text[:50]}...")  # 현재 처리 중인 텍스트 출력
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


#코사인 유사도
def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))



print("\n=== 임베딩 생성 시작 ===")
embeddings = []
for i, chunk in enumerate(chunks):
    print(f"\n[처리 중 {i+1}/{len(chunks)}]")
    embedding = get_embedding(chunk)
    embeddings.append(embedding)
    print(f"완료: 임베딩 차원 = {len(embedding)}")

print("\n=== 임베딩 생성 완료 ===")

# 출력 확인
for i, (chunk, embed) in enumerate(zip(chunks, embeddings)):
    print(f"[Chunk {i+1}] {chunk[:30]}... -> 임베딩 벡터 길이: {len(embed)}")



#질문에 대한 답변 함수
def ask_model(question, context):
    system_prompt = "다음 문서를 참고하여 질문에 답변하세요."
    user_prompt = f"""문서 내용:
{context}

질문: {question}
답변:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content


# 무한 반복으로 질문 받기 부분 전에 모델 저장
print("\n=== 임베딩 데이터 저장 중 ===")
model_data = {
    'chunks': chunks,
    'embeddings': embeddings,
    'original_text': text
}

with open('embedding_model.pkl', 'wb') as f:
    pickle.dump(model_data, f)
print("임베딩 데이터가 'embedding_model.pkl'에 저장되었습니다.")

# 무한 반복으로 질문 받기
print("\n=== 대화를 시작합니다 (종료하려면 'q' 또는 'quit' 입력) ===")
while True:
    question = input("\n질문을 입력하세요: ")
    
    if question.lower() in ['q', 'quit']:
        print("대화를 종료합니다.")
        break
        
    # 질문에 대한 임베딩 생성
    question_embedding = get_embedding(question)
    
    # 유사도 계산
    similarities = []
    for i, emb in enumerate(embeddings):
        similarity = cosine_similarity(question_embedding, emb)
        similarities.append(similarity)
    
    # 가장 유사한 chunk 찾기
    top_idx = int(np.argmax(similarities))
    relevant_chunk = chunks[top_idx]
    
    print("\n=== 응답 생성 중 ===")
    answer = ask_model(question, relevant_chunk)
    print("\n=== 응답 완료 ===")
    print("\n 모델의 답변:")
    print(answer)
