from langgraph.graph import MessagesState
from typing_extensions import Literal
from pydantic import BaseModel, Field

class State(MessagesState):
    """Maintains chatbot conversation state."""
    sentiment: str
    intent: str
    escalated: bool = False

class SentimentRoute(BaseModel):
    """Defines the sentiment of the user."""
    step: Literal["positive", "neutral", "negative"] = Field(
        None,
        description="The sentiment of the user. Should be one of [positive, neutral, negative]"
    )

class IntentRoute(BaseModel):
    """Defines the intent of the user."""
    step: Literal["make_appointment", "escalate_to_human", "ask_question"] = Field(
        None,
        description="The intent of the user. Should be one of [make_appointment, escalate_to_human, ask_question]"
    )