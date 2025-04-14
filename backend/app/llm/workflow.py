from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from app.llm.state import State
from app.utils.logger import logger
from langchain_core.messages import HumanMessage
from app.llm.nodes import (
    analyze_sentiment,
    analyze_intent,
    escalate_to_human,
    make_appointment,
    ask_question,
    sentiment_router,
    intent_router,
)

"""This file contains the workflow for the chatbot. It defines the nodes and edges of the graph, and compiles it into a workflow."""

# Create our graph.
graph = StateGraph(State)

# Memory
memory = MemorySaver()

# Add our nodes to the graph.
graph.add_node(analyze_sentiment, "analyze_sentiment")
graph.add_node(analyze_intent, "analyze_intent")
graph.add_node(escalate_to_human, "escalate_to_human")
graph.add_node(make_appointment, "make_appointment")
graph.add_node(ask_question, "ask_question")

# Add our edges to the graph.
graph.add_edge(START, "analyze_sentiment")
graph.add_conditional_edges(
    "analyze_sentiment",
    sentiment_router,
    {  # Name returned by route_decision : Name of next node to visit
        "analyze_intent": "analyze_intent",
        "escalate_to_human": "escalate_to_human",
    },
)
graph.add_conditional_edges(
    "analyze_intent",
    intent_router,
    {  # Name returned by route_decision : Name of next node to visit
        "escalate_to_human": "escalate_to_human",
        "make_appointment": "make_appointment",
        "ask_question": "ask_question"

    },
)
graph.add_edge("escalate_to_human", END)
graph.add_edge("make_appointment", END)
graph.add_edge("ask_question", END)

workflow = graph.compile(checkpointer=memory)

logger.info(workflow.get_graph().draw_ascii())

def generate_response(query, session_id):
    """Generates a response to the user's query.
    Args:
        query (str): The user's query.
        session_id (str): The session ID of the user.
    Returns:
        str: The response to the user's query.
    """
    config = {"configurable": {"thread_id": session_id}}
    input_message = HumanMessage(content=query)
    response = workflow.invoke({"messages": [input_message]}, config)
    logger.debug(f"Response to query: {query} is \n RESPONSE: {response['messages'][-1].content}")
    return response.get("messages")[-1].content