import requests

def generate_response(query : str, session_id : str) -> str:
    """Generate a response from the chatbot API.
    Args:
        query (str): The user's query.
        session_id (str): The session ID for the conversation.
    Returns:
        str: The chatbot's response.
    """
    # Check if the query is empty
    if not query.strip():
        return "Please enter a valid message before sending."
    # Check if the session ID is empty
    if not session_id.strip():
        return "Session ID is required for the conversation."
    # Check if the query is too long
    if len(query) > 1000:
        return "Your message is too long. Please shorten it and try again."
    bot_response = ""
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/chat",
            headers={"Content-Type": "application/json"},
            json={
                "query": query,
                "session_id": session_id,
            },
            timeout=50  # Optional: avoid hanging forever
        )
        if response.status_code == 200:
            bot_response = response.json()["data"]["response"]
        else:
            bot_response = "Oops, something went wrong. Please try again."
    except requests.exceptions.RequestException as e:
            bot_response = f"Error: I'm unable to connect to the server. Please check your connection or try again later."
    
    return bot_response