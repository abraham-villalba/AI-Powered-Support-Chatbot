from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from app.config import Config
from app.llm.state import State, SentimentRoute, IntentRoute
from app.llm.prompts import get_question_answering_prompt
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    trim_messages
)


# LLM Selection
if Config.LLM_WRAPPER == 'openai':
    model = ChatOpenAI(
                api_key=Config.OPENAI_API_KEY, 
                model=Config.LLM_MODEL,
                temperature=0.2,
                max_tokens=100,
                timeout=None,
                max_retries=2
            )
else:
    model = ChatOllama(model=Config.LLM_MODEL, temperature=0.7, max_tokens=100)

# We will define our nodes here.
def analyze_sentiment(state: State):
    """
    Analyzes the sentiment of the user.
    """
    # Use the sentiment router to analyze the sentiment of the user.
    print(f"Analyzing sentiment")
    last_message = state["messages"][-1].content
    print(last_message)
    sentiment_model = model.with_structured_output(SentimentRoute)
    decision = sentiment_model.invoke(
        [
            SystemMessage(
                content="Classify the sentiment of the user message based on the last message in the " \
                    "conversation. Only sentiments available are [frustrated, neutral], if you are not sure, " \
                    "say neutral. Think about the state of the user, if he is just asking a question or chatting, " \
                    "the sentiment is neutral. If the user is frustrated, the sentiment is frustrated. " 
            ),
            HumanMessage(content=last_message),
        ]
    )
    return {"sentiment": decision.step}

def sentiment_router(state: State):
    if state["sentiment"] == "frustrated":
        return "escalate_to_human"
    return "analyze_intent"

def escalate_to_human(state: State):
    """
    Escalates the query to a human agent.
    """
    # Use the sentiment router to analyze the sentiment of the user.
    print(f"Escalating to human with state: {state}")
    return {"messages": [AIMessage(content="Escalating to human agent.")]}

def analyze_intent(state: State):
    """
    Analyzes the intent of the user.
    """
    intent_router = model.with_structured_output(IntentRoute)
    # Use the sentiment router to analyze the sentiment of the user.
    last_message = state["messages"][-1].content
    print(f"Analyzing intent")
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
    return {"intent": decision.step}

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
    print(f"Making appointment")
    return {"messages": [AIMessage(content="Making appointment.")]}

def ask_question(state: State):
    """
    Answers the user's question.
    """
    print(f"Answering question")
    # Use the sentiment router to analyze the sentiment of the user.
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
    
    context = "No additional context found."
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