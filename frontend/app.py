import streamlit as st
import uuid
from utils.api import generate_response

# Initialize chat history and state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "waiting" not in st.session_state:
    st.session_state.waiting = False

# Page configuration
st.set_page_config(
    page_title="AI-Powered Support Chatbot",
    page_icon="🤖",
    layout="centered",
)

st.title("AI-Powered Support Chatbot")
st.caption("Demo Chatbot that provides instant support for customer queries and automates common tasks, " \
            "integrating an LLM for natural language understanding and response generation for a "
            "fictional dentist clinic called HappyTeeth.")

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# When waiting is True and we’ve shown the user message
if st.session_state.waiting:
    st.chat_input("Waiting for response...", disabled=True)
    with st.spinner("Thinking..."):
        bot_response = generate_response(
            st.session_state.messages[-1]["content"],
            st.session_state.session_id
        )
        
        # Show assistant response
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.session_state.waiting = False
        st.rerun()

if prompt := st.chat_input("Say something...", key="input"):

    # Check if input is empty
    if not prompt.strip():
        st.warning("Please enter a valid message.")
        st.stop()
    # Check if input is too long
    if len(prompt) > 1000:
        st.warning("Your message is too long. Please shorten it and try again.")
        st.stop()
    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.waiting = True
    st.rerun()  # Force re-run to trigger waiting logic
