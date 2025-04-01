from flask import Blueprint, request, jsonify
from langchain.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_openai import ChatOpenAI

template = """
You are a support agent. You have been assigned to help a customer with a query.
The customer has asked the following question: {question}
Respond in a few sentences and be concise.
"""
prompt = ChatPromptTemplate.from_template(template)

# Create a Blueprint object to define the routes
api_bp = Blueprint('api', __name__) 

@api_bp.route('/chat', methods=['POST'])
def chat():
    model = OllamaLLM(model="llama3.2")
    chain = prompt | model
    data = request.get_json()
    print(data)
    result = chain.invoke({"question": "How do I reset my password?"})
    print(result)
    return jsonify({'response': result})
