import streamlit as st
from agent_user import *
import asyncio
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import time


def chat():
    print(1)
    st.markdown("<h1 style='text-align: center; color: white; margin-top: -20px'>Ask Walmart Bot</h1>", unsafe_allow_html=True)

    button_dic = {"pay_query": "Payment queries", 
                "refund_return": "Refund and Returns", 
                "product_query": "Any product query",
                "walmart": "Walmart services"
                }
    

    with st.chat_message("assistant"):
        st.markdown(f"Hello Rishav, I'm here to assist you. Please feel free to ask any questions.")

        st.markdown("""
            <style>
            .stButton>button {
                background-color: white;
                color: black;
                border-radius: 20px;
                font-weight: 200;
                font-size: 12px;
                text-align: center;
                cursor: pointer;
            }
            .stButton>button :hover{
                border-radius: 20px;
                padding: 2px;
                color: black;    
            }
            .stTextInput{
                background-color: black;        
            }
            </style>
        """, unsafe_allow_html=True)

        pay_query = st.button("Payment queries")
        refund_return = st.button("Refund and Returns")
        product_query = st.button("Any product query")
        walmart = st.button("Walmart services")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    def output(prompt):
        # st.chat_message("user").markdown(prompt)

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        progress_bar = st.progress(0)
        progress_text = st.empty()
        progress_text.text("Connecting...")
        start_time = time.time()

        async def run_agent():
            # Get response and updated scratchpad
            response = await agent(prompt)
            
            return response
        
        response = asyncio.run(run_agent())

        elapsed_time = time.time() - start_time

        for i in range(101):
            if i < 25:
                progress_text.text("Processing your request...")
            elif i < 50:
                progress_text.text("Fetching relevant information...")
            elif i < 75:
                progress_text.text("Formulating a response...")
            else:
                progress_text.text("Finalizing response...")

            progress_bar.progress(i)
            time.sleep(elapsed_time / 100)


        print("this is: ", response)
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
    # React to user input
    if prompt := st.chat_input("How can I help You"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        output(prompt)
        
    if pay_query:
        prompts = f"Have queries regarding {button_dic['pay_query']} of Walmart"
        st.chat_message("user").markdown(prompts)
        output(prompts)

    if refund_return:
        prompts = f"Have queries regarding {button_dic['refund_return']} of Walmart"
        st.chat_message("user").markdown(prompts)
        output(prompts)

    if product_query:
        prompts = f"Have queries regarding {button_dic['product_query']} of Walmart"
        st.chat_message("user").markdown(prompts)
        output(prompts)

    if walmart:
        prompts = f"Have queries regarding {button_dic['walmart']} of Walmart"
        st.chat_message("user").markdown(prompts)
        output(prompts)