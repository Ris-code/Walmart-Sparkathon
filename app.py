import streamlit as st
import sys
import os
from streamlit_option_menu import option_menu
import base64
import env
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
            options=["Home", "Dashboard", "About", "Service Bot"],
            icons=["house", "file-bar-graph", "info-circle", "robot"],
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
        st.write("Hello")

    elif main_choice == "Dashboard":
        st.write("Dash")

    elif main_choice == "About":
        st.write("About")

    elif main_choice == "PayBot":
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