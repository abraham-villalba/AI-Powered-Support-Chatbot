

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from app.utils.logger import logger

def get_relevant_context(query: str) -> str:
    """Retrieves relevant context from the vector store."""
    index_name = 'chatbot'
    embedding = OpenAIEmbeddings(model='text-embedding-3-small')
    vector_store = PineconeVectorStore(index_name=index_name, embedding=embedding)
    logger.debug(f"Retriving context for query: \n{query}\n Index name: {index_name}")
    
    response_docs = vector_store.similarity_search(query, k=3)
    
    logger.debug(f"Context retrieved: {response_docs}")
    
    if not response_docs:
        return "Couldn't find any relevant information."
    
    string = "\n\n".join(
        (f"Document {i + 1}: \n{doc.page_content}")
        for i, doc in enumerate(response_docs)
    )
    
    return string