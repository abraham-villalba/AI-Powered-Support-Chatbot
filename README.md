# AI-Powered-Support-Chatbot
Chatbot that provides instant support for customer queries and automates common tasks, integrating an LLM for natural language understanding and response generation.
This project was developed using the following stack:
- **Backend:** Python with Flask, Langchain, Langgraph and Pinecone for the Embeddings Store.
- **Frontend:** Python with Streamlit

## Features
1. **Core Chat Functionality**.- Use an LLM to respond to user queries.
2. **FAQ Integration**.- Use RAG (Retrieval-Augmented Generation) using a specific FAQ dataset to answer domain-specific questions accuretly.
3. **Task Automationn**.- Mocked tasks suchs as escalations and booking appointments.
4. **Conversation Memory**.- Context handling to maintain the flow in multi-turn conversations.
5. **Sentiment Analysis**.- Sentiment Analysis to detect frustrated users and trigger escalations.

## Setup
To set up this project on your local machine follow this instructions after cloning the repository.

> Note: To run this project on your local machine you need to have **[Docker](https://www.docker.com/)** installed as well as a valid **[OpenAI API Key](https://openai.com/index/openai-api//)**. You also need to have valid **[Pinecone API Key](https://docs.pinecone.io/guides/get-started/quickstart)**.

1. In order to run this project, you need to create a **.env** file in file inside the **backend/** directory at the same level as its corresponding **Dockerfile** including the following structure and information.
    ```text
    OPENAI_API_KEY=YOUR_OPENAI_API_KEY
    LLM_WRAPPER=openai
    LLM_MODEL=gpt-4o-mini or model of your choice
    PINECONE_API_KEY=YOUR_PINECONE_API_KEY
    ```
2. In order to use RAG, you need to set up an embeddings store with Pinecone, to achieve this, you must create an index called *chatbot*. You can do this directly on the Pinecone web page or follow their instructions [here](https://docs.pinecone.io/guides/indexes/create-an-index). Make sure to choose the template for the **text-embedding-3-small** OpenAI's embeddings model.
3. Once your index has been created, execute the script stored in **backend/scripts** to generate the required embeddings and store them in the vector store.
    ```bash
    python backend/scripts/vectorize_document.py
    ```
4. Once you have your **.env** file in place and your vector store set up correctly, make sure you're on the root directory of the directory and execute the following docker command to build the required images and start both the client and the server service.
    > Make sure you have docker running before executing this command
    ```docker
    docker-compose up --build 
    ```
3. To access the web page, open your browser and go to [http://0.0.0.0:8501/](http://0.0.0.0:8501/).

4. To shutdown the services, use the following command.
    ```docker
    docker-compose down
    ```