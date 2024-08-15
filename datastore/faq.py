import os
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
import time
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import WebBaseLoader
from langchain.schema import Document
import re
from dotenv import load_dotenv

load_dotenv()

os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

# Define a function to split documents into chunks

def document_split(documents, chunk_size=500, chunk_overlap=0):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    all_splits = text_splitter.split_documents(documents)
    return all_splits

def split(documents, chunk_size=1000, chunk_overlap=0):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    all_splits = text_splitter.split_documents(documents)
    return all_splits

def pinecone_vector_store(docs):
    index_name = "policy"
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)
    else:
        print(f"The index '{index_name}' already exists.")

    index = pc.Index(index_name)
    
    PineconeVectorStore.from_documents(docs, embedding=MistralAIEmbeddings(), index_name=index_name)

# def clean_text(text):
#     # Remove excessive newlines and whitespace
#     text = re.sub(r'\n\s*\n', '\n', text.strip())
    
#     # Remove large sections of repetitive and irrelevant content
#     sections_to_remove = [
#         r"Skip to main content",
#         r"\.in",
#         r"Delivering to .*",
#         r"Update location",
#         r"Upload a JPEG, PNG, WEBP, GIF, SVG, AVIF, BMP or ICO image file.",
#         r"Upload an image file size of 5 MB or less.",
#         r"Upload an image",
#         r"All Categories",
#         r"Alexa Skills",
#         r"Appliances",
#         r"Apps & Games",
#         r"Audible Audiobooks",
#         r"Baby",
#         r"Beauty",
#         r"Books",
#         r"Car & Motorbike",
#         r"Clothing & Accessories",
#         r"Collectibles",
#         r"Computers & Accessories",
#         r"Deals",
#         r"Electronics",
#         r"Furniture",
#         r"Garden & Outdoors",
#         r"Gift Cards",
#         r"Grocery & Gourmet Foods",
#         r"Health & Personal Care",
#         r"Home & Kitchen",
#         r"Industrial & Scientific",
#         r"Jewellery",
#         r"Kindle Store",
#         r"Luggage & Bags",
#         r"Luxury Beauty",
#         r"Movies & TV Shows",
#         r"MP3 Music",
#         r"Music",
#         r"Musical Instruments",
#         r"Office Products",
#         r"Pet Supplies",
#         r"Prime Video",
#         r"Shoes & Handbags",
#         r"Software",
#         r"Sports, Fitness & Outdoors",
#         r"Subscribe & Save",
#         r"Tools & Home Improvement",
#         r"Toys & Games",
#         r"Under ₹500",
#         r"Video Games",
#         r"Watches",
#         r"Search Amazon\.in",
#         r"Returns\n& Orders",
#         r"Cart",
#         r"Mobiles",
#         r"Fashion",
#         r"Electronics",
#         r"Prime",
#         r"New Releases",
#         r"Home & Kitchen",
#         r"Customer Service",
#         r"Computers",
#         r"Books",
#         r"Car & Motorbike",
#         r"Gift Ideas",
#         r"Sports, Fitness & Outdoors",
#         r"Beauty & Personal Care",
#         r"Home Improvement",
#         r"Toys & Games",
#         r"Grocery & Gourmet Foods",
#         r"Gift Cards",
#         r"Custom Products",
#         r"Baby",
#         r"Health, Household & Personal Care",
#         r"Video Games",
#         r"Pet Supplies",
#         r"Audible",
#         r"AmazonBasics",
#         r"Subscribe & Save",
#         r"Coupons",
#         r"Kindle eBooks",
#         r"Help and Customer Service",
#         r"Find more solutions",
#         r"Returns , Replacements and Refunds",
#         r"›",
#         r"About Us",
#         r"Careers",
#         r"Press Releases",
#         r"Connect with Us",
#         r"Facebook",
#         r"Twitter",
#         r"Instagram",
#         r"Make Money with Us",
#         r"Protect and Build Your Brand",
#         r"Become an Affiliate",
#         r"Fulfilment by Amazon",
#         r"Advertise Your Products",
#         r"Let Us Help You",
#         r"COVID-19 and Amazon",
#         r"Your Account",
#         r"Returns Centre",
#         r"100% Purchase Protection",
#         r"Help",
#         r"English",
#         r"India",
#         r"AbeBooksBooks, art& collectibles",
#         r"AudibleDownloadAudio Books",
#         r"IMDbMovies, TV& Celebrities",
#         r"ShopbopDesignerFashion Brands",
#         r"Prime Now 2-Hour Deliveryon Everyday Items",
#         r"Conditions of Use & Sale",
#         r"Privacy Notice",
#         r"Interest-Based Ads",
#         r"© 1996-2024, Amazon.com, Inc. or its affiliates",
#         r"Back to top",
#         r"Get to Know Us",
#         r"Amazon Science",
#         r"Sell on Amazon",
#         r"Sell under Amazon Accelerator",
#         r"Amazon Global Selling",
#         r"Amazon Pay on Merchants",
#         r"Amazon App Download",
#         r"Abe, art& collectibles",
#         r"Amazon BusinessEverything ForYour Business",
#         r"ShopbopDesigner Brands",
#         r"DownloadAudio ",
#         r"Amazon Web ServicesScalable CloudComputing Services",
#         r"Now 2-Hour Deliveryon Everyday Items",
#         r"Amazon  100 million songs, ad-freeOver 15 million podcast episodes © 1996-2024, Amazon.com, Inc. or its affiliates"
#     ]

#     for section in sections_to_remove:
#         text = re.sub(section, '', text, flags=re.MULTILINE)

#     # Further clean up to remove any extra lines left
#     text = re.sub(r'\n\s*\n', '\n', text.strip())

#     # Remove any leading or trailing whitespace from lines
#     text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())

#     return text

policy = [
    # "https://www.walmart.com/help/article/track-your-order/143cf6e1d8cb48e6a1ed840409881235",
    # "https://www.walmart.com/help/article/edit-or-cancel-an-order/2c7e3d99812044f8aaa65aee0eae3d1c",
    # "https://www.walmart.com/help/article/substitutions-for-store-pickup-and-delivery-items/c8dd3973509b42488da66a362af4666d",
    # "https://www.walmart.com/help/article/canceled-orders/8f8dc075d900475a990d4dede6215f0f",
    # "https://www.walmart.com/help/article/delayed-orders/1a0e2c333442429ea5b85ccf3c5e408e",
    # "https://www.walmart.com/help/article/missing-items/c161a53cd3b7437eb2397d7f0699e0cd",
    # "https://www.walmart.com/help/article/order-not-received/af24f9d61b5143d9973f95c9d5bc3140",
    # "https://www.walmart.com/help/article/reorder/8c2a6854a3e9428faa93836347c46dd2",
    # "https://www.walmart.com/help/article/alcohol-orders/4ce95076037f4098b616783db3a18716",
    # "https://www.walmart.com/help/article/driver-feedback-and-tips/6dbcf806f22e4fc2952790c9dbc5eae5",
    # "https://www.walmart.com/help/article/pickup-and-delivery/d0d02a5f54e54592930f110aaf6a2f50",
    # "https://www.walmart.com/help/article/pickup-and-delivery-changes-and-exceptions/97461ebd27b04ab78cfa1ca3de480a83",
    # "https://www.walmart.com/help/article/guided-delivery-instructions/6fcd3e697ef740bdac25769f0f2e8c3c",
    # "https://www.walmart.com/help/article/drone-delivery/4870314a62634f368fe23cdf94ea28e2",
    # "https://www.walmart.com/help/article/how-to-update-your-address-rooftop-pin/ce440398878b4afd8e02385d68b69008",
    # "https://www.walmart.com/help/article/undeliverable-order-options/0a286bd65f9842579af9cc596f090151",
    # "https://www.walmart.com/help/article/chat-with-your-shopper/28fedaf51c20425fa6b0ce86cb972f2d",
    # "https://www.walmart.com/help/article/passkeys/79bc4a57374146c497ebe3bf8d4f9b10",
    # "https://www.walmart.com/help/article/temporary-holds-and-charges/e5dcfc1ca83e49d4999fb510c7fe13af",
    # "https://www.walmart.com/help/article/payment-methods/af059a7587894f2f831a6159cd92d933",
    # "https://www.walmart.com/help/article/account-security-and-unrecognized-charges-or-orders/0cd87e9619854081ba9ea99672112165",
    # "https://www.walmart.com/help/article/view-store-purchases-and-find-receipts/f56a1afbf3b5428bb69f0124daa49108",
    # "https://www.walmart.com/help/article/walmart-cash/77662758469249c29aed82885d5e554f",
    # "https://www.walmart.com/help/article/manage-password/35d7915384d44826ab2ccb7d7a69493c",
    # "https://www.walmart.com/help/article/tax-exempt/8901af969603497b97a844cf4a6bd958",
    # "https://www.walmart.com/help/article/the-walmart-site-and-app-experience/27f2678cb25a40a7b57a359fec3ca67f",
    # "https://www.walmart.com/help/article/find-purchase-and-send-a-gift/d1791e3c65e64e56999e3d98e6766e74",
    # "https://www.walmart.com/help/article/out-of-stock-items/8c40895090384f2cbe1389537b24e3c1",
    # "https://www.walmart.com/help/article/quantity-limits-and-bulk-purchases/825450266d4245b29e242d06a01bd91d",
    # "https://www.walmart.com/help/article/price-and-other-listing-errors/4c06730885e143fe8b4a0719da70bd79",
    # "https://www.walmart.com/help/article/extra-savings/205b65e070f247d7a98687b7ff2d5cc9",
    # "https://www.walmart.com/help/article/store-or-associate-feedback/41fd0647ccd74db2bf2b8dd7cebc0c04",
    # "https://www.walmart.com/help/article/food-safety/d64ebfc2e07c448fbe3385c32bea1832",
    # "https://www.walmart.com/help/article/gaming-console-restock-ps5-and-xbox-series-x-s/8e83d0d8222d4a089da2f7940f2afd37",
    # "https://www.walmart.com/help/article/online-vision-center-orders/3ec500a26aed4d93886e38abd4e7a684",
    # "https://www.walmart.com/help/article/apple-services-offer/f3b882cb458e42be8ad2d7e8693d35f5",
    # "https://www.walmart.com/help/article/walmart-policies-and-guidelines/ad54d80077af478ea18a55c5ee13b2ee",
    # "https://www.walmart.com/help/article/walmart-price-match-policy/6295d9e1a501489b9aa40a60c899b288",
    # "https://www.walmart.com/help/article/single-use-bag-policy/6538739d9dba47e5a0aa302ec9e92963",
    # "https://www.walmart.com/help/article/responsible-disclosure-and-accessibility-policies/0f173dab8bd942da84b1cd7ab5ffc3cb",
    # "https://www.walmart.com/help/article/walmart-inc-wellness-services-app-privacy-policy-and-notice-of-privacy-practices/3de1231f867841c7a629da1cfbcf0ee2",
    # "https://www.walmart.com/help/article/claims-of-intellectual-property-infringement/6171b9ac00384f3f920aa14a9c08bdac",
    # "https://www.walmart.com/help/article/third-party-software-and-licensing-notices/a5b3802e3c424fc9ac6872ea93e1c4c5",
    # "https://www.walmart.com/help/article/walmart-cash-faqs/3260c30df45443de80b4ac720717af28",
    # "https://www.walmart.com/help/article/walmart-pet-services-privacy-notice/4df3c2b6d6724886beb8645b6d16fee6",
    # "https://www.walmart.com/help/article/walmart-promotions-disclosure/98e3b17b03ef4676a208fb22477e3c5d",
    # "https://www.walmart.com/help/article/refunds/a86a0400e237444cb9a5f3c3ce500d1b",
    # "https://www.walmart.com/help/article/walmart-standard-return-policy/adc0dfb692954e67a4de206fb8d9e03a",
    # "https://www.walmart.com/help/article/walmart-marketplace-return-policy/63c3566a9d3546858582acae2fbfdb7e",
    # "https://www.walmart.com/help/article/walmart-membership/534c4edc29204a6bb15145a61146bf51",
    # "https://www.walmart.com/help/article/walmart-core-benefits/db8260cb77f74523a040b14d2c047ac6",
    # "https://www.walmart.com/help/article/walmart-core-benefits-automotive/9b7deb0aa485427fa605fbcd05bd2e62",
    # "https://www.walmart.com/help/article/walmart-benefits-free-delivery-from-your-store-and-early-access-deals/d1738a201207485c99fd53ccdbc49699",
    # "https://www.walmart.com/help/article/walmart-partnerships-and-limited-time-offers/19e111f997d440fcb70e3b0c702f4a52",
    # "https://www.walmart.com/help/article/manage-walmart-membership/126c9a990a944c3abd8531de52a87440",
    # "https://www.walmart.com/help/article/walmart-billing-and-payments/6d81a1f3cfe843e8b9cbeebe926e7cdf",
    # "https://www.walmart.com/help/article/paramount-benefit/35624ec8e133496ab647a398a90cf779",
    # "https://www.walmart.com/help/article/walmart-travel/0f75ff42ece74f9ca0bcae0c1e73e86d",
    # "https://www.walmart.com/help/article/inhome-plus-up/19da7530eeec4c8eb1f84271c28e0c38",
    "https://www.walmart.com/help/article/inhome-billing-and-payments/611a8baf1ecf4ef88c8be2a3e95ffd8a",
    "https://www.walmart.com/help/article/inhome-ordering/e37847e4b61d4335b39eef3382ef2f31",
    "https://www.walmart.com/help/article/inhome-returns-pick-up/d4ec06a89e124517a016be09901a782b",
    "https://www.walmart.com/help/article/myq-smart-garage-control-and-level-smart-locks/6854fe4336e340fb81317ae26528d974",
    "https://www.walmart.com/help/article/home-and-garage-keypads/b733712d0b0f42e49342606ea15abe81",
    "https://www.walmart.com/help/article/other-inhome-delivery-options/07f4d4271348426ab9e096490526366f"
]

# Loop through each policy URL
for link in policy:
    loader = WebBaseLoader(link)
    data = loader.load()

    # Extract text from the loaded document(s) and clean it
    cleaned_documents = []
    for doc in data:
        cleaned_content = doc.page_content
        cleaned_doc = Document(page_content=cleaned_content, metadata=doc.metadata)
        cleaned_documents.append(cleaned_doc)

    # Now cleaned_documents contain the cleaned content in document form
    print("link:",link)
    # Split cleaned documents into smaller chunks
    split_documents = split(cleaned_documents)
    # print(split_documents)
    # break
    for i in split_documents:
    # Process and store each chunk in Pinecone
        pinecone_vector_store([i])