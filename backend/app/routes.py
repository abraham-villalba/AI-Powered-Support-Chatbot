from flask import Blueprint, request
from app.utils.schemas import ChatRequestSchema, validate_chat_request
from app.utils.response_model import ResponseModel
from app.llm.workflow import generate_response
from flask_cors import cross_origin
from app.utils.logger import logger


# Create a Blueprint object to define the routes
api_bp = Blueprint('api', __name__) 

@api_bp.route('/chat', methods=['POST'])
@cross_origin()
def chat():
    """ Handles chatbot queries. """
    data, errors = validate_chat_request(request.get_json(), ChatRequestSchema())

    if errors:
        logger.error(f"Chat endpoint validation errors: {errors}")
        return ResponseModel(status="error", error=errors).to_json(), 400 # Bad Request

    query = data['query']
    logger.info(f"Chat endpoint called by {data['session_id']}")
    result = generate_response(query, data['session_id'])
    return ResponseModel(status='success', data={'response': result}).to_json(), 200
