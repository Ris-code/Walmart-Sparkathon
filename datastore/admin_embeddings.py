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

def document_split(adminSalesData):
    documents = []

    for _, row in adminSalesData.iterrows():
        content = (
            f"Date: {row['date_']}\n"
            f"City Name: {row['city_name']}\n"
            f"Order ID: {row['order_id']}\n"
            f"Cart ID: {row['cart_id']}\n"
            f"Customer Key: {row['dim_customer_key']}\n"
            f"Procured Quantity: {row['procured_quantity']}\n"
            f"Unit Selling Price: {row['unit_selling_price']}\n"
            f"Total Discount Amount: {row['total_discount_amount']}\n"
            f"Product ID: {row['product_id']}\n"
            f"Total Weighted Landing Price: {row['total_weighted_landing_price']}\n"
            f"Product Name: {row['product_name']}\n"
            f"Unit: {row['unit']}\n"
            f"Product Type: {row['product_type']}\n"
            f"Brand Name: {row['brand_name']}\n"
            f"Manufacturer Name: {row['manufacturer_name']}\n"
            f"Category L0: {row['l0_category']}\n"
            f"Category L1: {row['l1_category']}\n"
            f"Category L2: {row['l2_category']}\n"
            f"Category L0 ID: {row['l0_category_id']}\n"
            f"Category L1 ID: {row['l1_category_id']}\n"
            f"Category L2 ID: {row['l2_category_id']}"
        )

        documents.append(Document(page_content=content))

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)

    all_splits = text_splitter.split_documents(documents)

    return all_splits

def pinecone_vector_store(adminSalesData):
    index_name = "adminsales"  
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
    docs = document_split(adminSalesData)
    # print(docs)
    # Vectorize and store the documents in Pinecone
    PineconeVectorStore.from_documents(docs, embedding=MistralAIEmbeddings(), index_name=index_name)

if __name__ == "__main__":
    # Load product data from CSV
    adminSalesData = pd.read_csv("merged_sales_products.csv")

    chunk_size = 10
    print(len(adminSalesData))
    for start in range(1560, len(adminSalesData), chunk_size):
        end = start + chunk_size
        print(start)
        chunk = adminSalesData[:][start:end]
        pinecone_vector_store(chunk)
