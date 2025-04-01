from flask import Blueprint, request, jsonify
from langchain.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_openai import ChatOpenAI
from app.utils.schemas import ChatRequestSchema, validate_chat_request
from app.utils.response_model import ResponseModel

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
    """ Handles chatbot queries. """
    data, errors = validate_chat_request(request.get_json(), ChatRequestSchema())

    if errors:
        return ResponseModel(status="error", error=errors).to_json(), 400 # Bad Request

    model = OllamaLLM(model='llama3.2')
    chain = prompt | model
    query = data['query'] #"Hello, my name is Abraham"
    print(data)
    print(query)
    result = chain.invoke({'question': query})
    print(result)
    return ResponseModel(status='success', data={'response': result}).to_json(), 200
