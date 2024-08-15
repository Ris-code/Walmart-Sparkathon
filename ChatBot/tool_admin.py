import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain.schema import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from pinecone import Pinecone as pc
from langchain_pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from tqdm.autonotebook import tqdm
from langchain_core.tools import tool
from langchain.tools.retriever import create_retriever_tool
from langchain_core.messages import HumanMessage
from langchain import hub
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain import PromptTemplate
from env import *
import pandas as pd
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import create_sql_agent

def retrieve_tool(index, topic, description, pinecone_key=os.environ.get("PINECONE_API_KEY")):
    # Initialize Pinecone client
    pc_client = pc(api_key=pinecone_key)
    Index = pc_client.Index(index)

    # Initialize vector store
    vectorstore = Pinecone(Index, embedding=MistralAIEmbeddings())
    retriever = vectorstore.as_retriever(k=1)

    # Create and return the retriever tool
    retriever_tool = create_retriever_tool(
        retriever,
        topic,
        description
    )

    return retriever_tool

## Tool 1
retrieve_tool_1 = retrieve_tool("query-category-new", 
                                topic="payment_query_search", 
                                description="Search for information related to payment queries. For any questions about Payment and payment methods, you must use this tool!",
                                )

tool = [retrieve_tool_1]