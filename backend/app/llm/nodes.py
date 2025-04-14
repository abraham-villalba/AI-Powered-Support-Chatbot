from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from app.llm.context import get_relevant_context
from app.config import Config
from app.llm.state import State, SentimentRoute, IntentRoute
from app.llm.prompts import get_question_answering_prompt, get_booking_prompt
from app.utils.logger import logger
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    trim_messages
)


# LLM Selection
if Config.LLM_WRAPPER == 'openai':
    logger.info(f"Using OpenAI LLM Wrapper with model {Config.LLM_MODEL}")
    model = ChatOpenAI(
                api_key=Config.OPENAI_API_KEY, 
                model=Config.LLM_MODEL,
                temperature=0.2,
                max_tokens=100,
                timeout=None,
                max_retries=2
            )
else:
    logger.info(f"Using Ollama LLM Wrapper with model {Config.LLM_MODEL}")
    model = ChatOllama(model=Config.LLM_MODEL, temperature=0.7, max_tokens=100)

# We will define our nodes here.
def analyze_sentiment(state: State):
    """
    Analyzes the sentiment of the user.
    """
    logger.info(f"Analyzing sentiment")
    last_message = state["messages"][-1].content
    # Use the sentiment model to analyze the sentiment of the user.
    sentiment_model = model.with_structured_output(SentimentRoute)
    decision = sentiment_model.invoke(
        [
            SystemMessage(
                content="Classify the sentiment of the user message based on the last message in the " \
                    "conversation. Only sentiments available are [positive, neutral, negative], if you are not sure, " \
                    "say neutral. Think about the state of the user, if he is just asking a question or chatting, " \
                    "the sentiment is positive. " 
            ),
            HumanMessage(content=last_message),
        ]
    )
    return {"sentiment":  "neutral" if decision.step is None else decision.step}

def sentiment_router(state: State):
    if state["sentiment"] == "negative":
        return "escalate_to_human"
    return "analyze_intent"

def escalate_to_human(state: State):
    """
    Escalates the query to a human agent.
    """
    logger.info(f"Escalating to human with state: {state}")
    return {"messages": [AIMessage(content="Your query has been escalated to a human agent. Please wait for further assistance.")], "escalated": True}

def analyze_intent(state: State):
    """
    Analyzes the intent of the user.
    """
    intent_router = model.with_structured_output(IntentRoute)
    last_message = state["messages"][-1].content
    logger.info(f"Analyzing intent")
    decision = intent_router.invoke(
        [
            SystemMessage(
                content="Classify the intent of the user based on the last messages in the conversation. " \
                "The intents available are [make_appointment, escalate_to_human, ask_question]. If you are not sure, classify as ask_question."
                "Here are the previous messages in the conversation:\n" \
                f"{get_conversation_history_context(state)}"
            ),
            HumanMessage(content=last_message),
        ]
    )

    return {"intent": "ask_question" if decision.step is None else decision.step}

def intent_router(state: State):
    if state["intent"] == "escalate_to_human":
        return "escalate_to_human"
    elif state["intent"] == "make_appointment":
        return "make_appointment"
    return "ask_question"

def make_appointment(state: State):
    """
    Makes an appointment for the user.
    """
    # Use the sentiment router to analyze the sentiment of the user.
    previus_messages = get_conversation_history_context(state)
    last_message = state["messages"][-1].content
    # Use the booking prompt to make an appointment.
    booking_prompt = get_booking_prompt()
    booking_chain = booking_prompt | model

    result = booking_chain.invoke({
        "memory": previus_messages,
        "last_message": last_message
    })
    logger.info(f"Making appointment")
    return {"messages": result}

def ask_question(state: State):
    """
    Answers the user's question.
    """
    logger.info(f"Answering question")
    user_question = state["messages"][-1].content
    # Trim the messages to avoid exceeding the token limit.
    selected_messages = trim_messages(
        state["messages"],
        token_counter=len, 
        max_tokens=7, 
        strategy="last",
        start_on="human",
        allow_partial=False,
    )
    previus_messages = ""
    for i in range(len(selected_messages) - 1):
        if isinstance(selected_messages[i], HumanMessage):
            previus_messages += f"User: {selected_messages[i].content}\n"
        elif isinstance(selected_messages[i], AIMessage):
            previus_messages += f"You: {selected_messages[i].content}\n"

    # Get the relevant context for the question.
    context = get_relevant_context(user_question)
    logger.debug(f"Context retrieved: {context}")
    # Build the prompt and chain.
    propmt = get_question_answering_prompt()
    chain = propmt | model

    result = chain.invoke({
        "context": context,
        "memory": previus_messages,
        "question": user_question
    })
    return {"messages": result}


def get_conversation_history_context(state: State):
    """
    Returns the previous messages in the conversation as a string.
    """
    previus_messages = ""
    for i in range(len(state["messages"]) - 1):
        if isinstance(state["messages"][i], HumanMessage):
            previus_messages += f"User: {state['messages'][i].content}\n"
        elif isinstance(state["messages"][i], AIMessage):
            previus_messages += f"You: {state['messages'][i].content}\n"
    return previus_messages