from langchain.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from app.config import Config

template = """
You are a support agent. You have been assigned to help a customer with a query.
The customer has asked the following question: {question}
Respond in a few sentences and be concise.
"""
prompt = ChatPromptTemplate.from_template(template)

def generate_response(query):
    print(Config.LLM_WRAPPER)
    print(Config.LLM_MODEL)
    if Config.LLM_WRAPPER == 'openai':
        print("We're using openai")
        model = ChatOpenAI(
                    api_key=Config.OPENAI_API_KEY, 
                    model=Config.LLM_MODEL,
                    temperature=0,
                    max_tokens=100,
                    timeout=None,
                    max_retries=2
                )
    else:
        model = ChatOllama(model=Config.LLM_MODEL, temperature=0, max_tokens=100)
        
    chain = prompt | model
    result = chain.invoke({'question': query})

    return result.content