"""
Script to generate embeddings of our dataset and store it in a Vector Store
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
from uuid import uuid4
import os

load_dotenv(override=True)

def generate_chunks(file_path):
    """ Generate chunks of text from a file """
    # Load data into memory
    with open(file_path) as f:
        data = f.read()

    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=400,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False
    )

    chunks = text_splitter.create_documents([data])
    return chunks

def upload_embeddings_to_store(index_name, chunks):
    """ Upload embeddings to Pinecone Vector Store """
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    if not PINECONE_API_KEY:
        raise ValueError('PINECONE_API_KEY environment variable is not set.')
    if not OPENAI_API_KEY:
        raise ValueError('OPENAI_API_KEY environment variable is not set.')

    # Create embedding model
    embedding = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model='text-embedding-3-small',
    )

    # Generate IDs for each chunk
    uuids = [str(uuid4()) for _ in range(len(chunks))]
    # Create Vector Store
    store = PineconeVectorStore(embedding=embedding, index_name=index_name)
    # Store embeddings
    store.add_documents(documents=chunks, ids=uuids)

if __name__ == '__main__':
    file_path = '../faq_data.txt'
    index_name = 'chatbot'
    try:
        chunks = generate_chunks(file_path)
        upload_embeddings_to_store(index_name, chunks)
        print("Embeddings uploaded successfully!")
    except Exception as e:
        print("Failed to upload embeddings.")
        print(e)
