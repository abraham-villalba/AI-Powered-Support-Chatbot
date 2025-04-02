from langchain.prompts import ChatPromptTemplate
from langchain_core.agents import AIMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from app.config import Config

template = """
You are an assistant for question-answering tasks. The questions are related to a dentist clinic called HappyTeeth.
Use the following pieces of retrieved context to answer 
the question. If you don't know the answer, say that you
don't know. Use three sentences maximum and keep the answer concise and anwer the question in the SAME LANGUAGE as the question.
Question: {question}
Based on common queries, you have the following information that might be relevant to the customer query: {context}
Previous interactions you had with the user:{memory}
If you already said hello to the user, don't say it again.
"""
memory = []
prompt = ChatPromptTemplate.from_template(template)
index_name = 'chatbot'
embedding = OpenAIEmbeddings(model='text-embedding-3-small')
vector_store = PineconeVectorStore(index_name=index_name, embedding=embedding)

def retrieve_context(query):
    response_docs = vector_store.similarity_search(query, k=3)
    print(response_docs)
    serialized = "\n\n".join(
        (f"Content: {doc.page_content}")
        for doc in response_docs
    )
    return serialized
    

def generate_response(query):
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
        model = ChatOllama(model=Config.LLM_MODEL, temperature=0.2, max_tokens=100)
        
    context = retrieve_context(query)
    print(context)
    chain = prompt | model
    previous_messages = '\n\n'.join([f"User: {m['human']}\nYou: {m['system']}" for m in memory])
    result = chain.invoke({'question': query, 'context': context, 'memory': previous_messages})
    memory.append({'human': query, 'system': result.content})
    return result.content