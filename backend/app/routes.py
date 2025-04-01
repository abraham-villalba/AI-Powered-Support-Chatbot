from flask import Blueprint, request
from langchain.prompts import ChatPromptTemplate
from app.utils.schemas import ChatRequestSchema, validate_chat_request
from app.utils.response_model import ResponseModel
from app.services import generate_response
from flask_cors import cross_origin

template = """
You are a support agent. You have been assigned to help a customer with a query.
The customer has asked the following question: {question}
Respond in a few sentences and be concise.
"""
prompt = ChatPromptTemplate.from_template(template)

# Create a Blueprint object to define the routes
api_bp = Blueprint('api', __name__) 

@api_bp.route('/chat', methods=['POST'])
@cross_origin()
def chat():
    """ Handles chatbot queries. """
    data, errors = validate_chat_request(request.get_json(), ChatRequestSchema())

    if errors:
        return ResponseModel(status="error", error=errors).to_json(), 400 # Bad Request

    query = data['query']
    print(data)
    result = generate_response(query)
    print(result)
    return ResponseModel(status='success', data={'response': result}).to_json(), 200
