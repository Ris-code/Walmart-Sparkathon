import streamlit as st
import sys
import os
from streamlit_option_menu import option_menu
import base64
import env
import json
import pandas as pd
from streamlit_folium import st_folium
import numpy as np
# # Add directories to sys.path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ChatBot')))
image = os.path.join(os.path.dirname(__file__), 'Images')


def img_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def set_custom_css():
    custom_css = """
    <style>
        .sidebar .sidebar-content {
            padding-top: 0px;
        }
        .custom-sidebar-img {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 80%;  
            height: auto;  
            margin-top: -50px;  
        }
        .nav-link-selected {
            background-color: rgba(255, 255, 255, 0.3);  
            color: #141920;  
        }
        .custom-container {
            background-color: white;  
            padding: 10px;
            border-radius: 10px;
            min-height: 320px;  
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
        }
        .custom-button {
            background-color: orange;  
            color: black;
            width: 100%;
            border: none;
            padding: 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        .custom-button:hover {
            background-color: #e67e22;  
        }
        .custom-image {
            width: 100%;  
            height: 100%;
            max-height: 300px;  
            object-fit: cover;
            margin-bottom: 10px;
        }
        .price {
            font-size: 17px;
            font-weight: bold;
            background-color: orange;
            color: black;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            width: 100%;
            height: 100%;
            flex: 1;
            padding: 5px;
        }
        .item-name {
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            background-color: #f0f0f0;  
            padding: 5px;
            color: black;
            border: 1px solid #ddd;  
            border-radius: 5px;
        }
        .custom-buy-now {
            background-color: orange;
            color: black;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            display: inline-block;
            cursor: pointer;
            width: 100%;
        }
        .custom-buy-now:hover {
            background-color: #e67e22;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def display_home():
    # Specify the path to your JSON file
    json_file_path = 'productDict.json'

    # Open and load the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Now `data` is a Python dictionary
    # print(data)

    df = pd.read_csv("recommendations1.csv")
    df_cust = pd.read_csv("customerRecommendationData.csv")

    product = {}
    index = 0
    for _, row in df.head(6).iterrows():
        prod_id = data[str(int(row["productID"]))]
        df_new = df_cust[df_cust["product_id"]==prod_id]
        df_new.reset_index(inplace=True)
        product[index] = {
            "name": df_new["product_name"][0],
            "price": df_new["actual_price"][0],
            "rating": df_new["rating"][0],
            "image": df_new["img_link"][0],
            "category": df_new["category"][0],
        }
        index+=1
    
    # print(product)
    len_items = len(product)

    st.markdown(f"<h1 style='text-align: left; color: white; margin-top: -20px'>Top Recommended</h1>", unsafe_allow_html=True)
    
    # Calculate the number of rows needed
    rows = [st.columns(3) for _ in range(len_items // 3)]
    if len_items % 3:
        rows.append(st.columns(len_items % 3))

    # Display items in the calculated rows
    item_index = 0
    for row in rows:
        for col in row:
            if item_index < len_items:
                item = product[item_index]
                print(item)
                with col:
                    with st.container():
                        st.markdown(f'<img src="{item["image"]}" class="custom-image">', unsafe_allow_html=True)
                        st.markdown(f'<div class="item-name">{item["name"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="price">{item["price"]}</div>', unsafe_allow_html=True)
                        if st.button("Buy Now", key=f"buy_now_{item_index}", use_container_width=True):
                            # if 'item' not in st.session_state:
                            st.session_state.item = item
                            st.session_state.current_page = "Recommendation"
                item_index += 1   

@st.cache_data
def generate_data(products):
    # Generate random Indian city locations (latitude, longitude)
    locations = [
        {"city": "Mumbai", "lat": 19.0760, "lon": 72.8777},
        {"city": "Delhi", "lat": 28.7041, "lon": 77.1025},
        {"city": "Bengaluru", "lat": 12.9716, "lon": 77.5946},
        {"city": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
        {"city": "Chennai", "lat": 13.0827, "lon": 80.2707},
        {"city": "Kolkata", "lat": 22.5726, "lon": 88.3639},
        {"city": "Pune", "lat": 18.5204, "lon": 73.8567},
        {"city": "Ahmedabad", "lat": 23.0225, "lon": 72.5714},
        {"city": "Jaipur", "lat": 26.9124, "lon": 75.7873},
        {"city": "Lucknow", "lat": 26.8467, "lon": 80.9462},
    ]

    # Generate random demand values and trends for each product at each location
    data_with_trend = []
    for location in locations:
        for product in products:
            demand = np.random.randint(50, 200)  # Random demand between 50 and 200 units
            trend = np.random.choice(['increase', 'decrease'])  # Randomly choose if demand will increase or decrease
            percentage_change = np.random.choice([5, 10, 15, 20, 25, 30])  # Random percentage change
            if trend == 'decrease':
                percentage_change = -percentage_change  # Make the change negative if it's a decrease
            data_with_trend.append({
                "city": location["city"],
                "lat": location["lat"],
                "lon": location["lon"],
                "product": product,
                "demand": demand,
                "percentage_change": percentage_change
            })

    # Create a DataFrame
    df_trend = pd.DataFrame(data_with_trend)
    return df_trend

def app():
    set_custom_css()
    
    img_path = os.path.join(image, 'walmart.png')
    img_base64 = img_to_base64(img_path)

    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="custom-sidebar-img" alt="Amazon Logo">',
        unsafe_allow_html=True
    )

    with st.sidebar:
        main_choice = option_menu(
            menu_title="",
            options=["Home", "Dashboard", "Service Bot", "Product Trend Analysis"],
            icons=["house", "file-bar-graph", "robot", "geo-alt"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"background-color": "#004f9a", "margin-top": "10px"},
                "icon": {"color": "#ffffff", "font-size": "25px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "5px",
                    "padding": "10px",
                    "color": "white"
                },
                "nav-link-selected": {"background-color": "#002d58", "color": "#ffffff"},
            }
        )
    

    if main_choice == "Home":
        display_home()

    elif main_choice == "Dashboard":
        st.write("Dash")
    
    elif main_choice == "Product Trend Analysis":
        import map_test
        df = pd.read_csv("city.csv")
        # Generate random product names
        products = df["product_name"].unique().tolist()

        # Streamlit app
        st.title("Product Demand and Trend Analysis")

        # Create a dropdown for product selection
        selected_product = st.selectbox('Select a product:', products)
        df_trend = generate_data(products)
                # Generate and display the map
        map_display = map_test.create_map(selected_product, df_trend)
        st_folium(map_display, width=1080, height=800)

    elif main_choice == "Service Bot":
        option = st.sidebar.selectbox( 
            "Select a user type",           
            ("Customer", "Admin"),
        )

        if(option=="Customer"):
            # st.write("Cus-Chat")
            from bot_user import chat
            chat()

        if(option=="Admin"):
            # st.write("Admin")
            from bot_admin import chat_admin
            chat_admin()

def main():
    st.set_page_config(
        page_title="Walmart",
        page_icon=os.path.join(image, 'logo.png'),
        initial_sidebar_state="expanded",
        layout="wide",
    )

    app()
    


if __name__ == "__main__":
    main()