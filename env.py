import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

os.environ["MISTRAL_API_KEY"] = st.secrets["MISTRAL_API_KEY"]
os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
os.environ["HF_TOKEN"] = st.secrets["HF_TOKEN"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
