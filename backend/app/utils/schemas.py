"""
Includes request schemas for the API endpoints.
"""
from marshmallow import Schema, fields, ValidationError

class ChatRequestSchema(Schema):
    """ Schema for the chat request data. """
    query = fields.String(required=True, error_messages={"required": "Query field is required to generate a response."})
    session_id = fields.String(required=False, error_messages={"required": "Session ID field is required to maintain the conversation state."})

def validate_chat_request(data, schema):
    """ Validates the chat request data. """
    try:
        return schema.load(data), None
    except ValidationError as e:
        return False, e.messages