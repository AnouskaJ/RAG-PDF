from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

app = Flask(__name__)
CORS(app)

api_key = '<openai-api-key>'
df = pd.read_csv(r'C:\Users\Dell\Downloads\RAG-PDF\RAG-PDF\backend\embeddings_policy-booklet.csv')
chat_history = []

PROMPT_TEMPLATE = """
You are provided with context from a car insurance policy booklet and a chat history. 
Answer the following question based on the given context:
Context: {context}
Question: {question}
Chat History: {chat_history}

Provide a one-liner answer that is correct and complete. Follow these guidelines:
- Base your answer only on the provided context.
- Do not justify your answer.
- Do not include information not mentioned in the context.
- Avoid phrases like "according to the context" or "mentioned in the context."
"""

client_ = OpenAI(api_key=api_key)

# Get embeddings of text using openai
def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    response = client_.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

# to generate responses
def generate_response_chat(query, df, chat_history):
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    model = ChatOpenAI(openai_api_key=api_key, model='gpt-4-turbo', temperature=0.1)

    question_vector = get_embedding(query, model='text-embedding-ada-002')
    df['cosine_similarity'] = df['embedding'].apply(lambda x: cosine_similarity([question_vector], [eval(x)])[0][0])
    df = df.sort_values(by='cosine_similarity', ascending=False)
    top_10_list = df.head(10)['text_chunk'].tolist()
    prompt = prompt_template.format(context=top_10_list, question=query, chat_history=chat_history)
    messages = [{"role": "assistant", "content": prompt}]
    response = model.invoke(messages)
    
    chat_history.append(f"question: {query}\nanswer: {response.content}")
    
    return response.content, chat_history


# route to connect 
@app.route('/ask', methods=['POST'])
def ask():
    global chat_history
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({'error': 'Query is required'}), 400

    response, chat_history = generate_response_chat(query, df, chat_history)
    return jsonify({'response': response, 'chat_history': chat_history})

if __name__ == '__main__':
    app.run(debug=True)
