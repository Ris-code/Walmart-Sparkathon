import os
import time
import pandas as pd
from langchain_mistralai import ChatMistralAI
from langchain.schema import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
# print(os.getenv("PINECONE_API_KEY"))

def document_split(product_data):
    # Initialize an empty list to store Document objects
    documents = []

    # Iterate over each row in the product data
    for _, row in product_data.iterrows():
        # Combine relevant product information into a single content string
        content = f"Product Name: {row['product_name']}\n Category: {row['category']}\n Discounted Price: {row['discounted_price']}\nActual Price: {row['actual_price']}\nDiscount Percentage: {row['discount_percentage']}\nRating: {row['rating']}\nRating Count: {row['rating_count']}\nReview Title: {row['review_title']}\nReview Content: {row['review_content']}\nAbout Product: {row['about_product']}"

        # Append the Document object to the list
        documents.append(Document(page_content=content))

    # Initialize the text splitter
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)

    # Split documents into chunks
    all_splits = text_splitter.split_documents(documents)
    print(1)

    return all_splits

def pinecone_vector_store(product_data):
    index_name = "product-index"  # Unique index name for storing product vectors
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    # Create the index if it doesn't already exist
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        # Wait until the index is ready
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)
    else:
        print("The index already exists.")

    index = pc.Index(index_name)
    # print(index)

    # Split the product data into chunks
    docs = document_split(product_data)
    # print(docs)
    # Vectorize and store the documents in Pinecone
    PineconeVectorStore.from_documents(docs, embedding=MistralAIEmbeddings(), index_name=index_name)

if __name__ == "__main__":
    # Load product data from CSV
    product_data = pd.read_csv("product.csv")

    chunk_size = 2
    for start in range(0, len(product_data), chunk_size):
        end = start + chunk_size
        print(start)
        chunk = product_data[:][start:end]
        # print(chunk)
    # Vectorize and store product data in Pinecone
        pinecone_vector_store(chunk)
