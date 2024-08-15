import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from langchain_mistralai import ChatMistralAI
from langchain import hub
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain import PromptTemplate
from env import *
from tools_user import tool
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

store = {}

# Initialize language model
llm = ChatMistralAI(model="mistral-large-latest")

# Bind the tool to the model
llm = llm.bind_tools(tool)

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Define agent
agent = create_tool_calling_agent(llm, tool, hub.pull("hwchase17/openai-functions-agent"))
agent_executor = AgentExecutor(agent=agent, tools=tool)

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

async def agent(question):
    def create_prompt_template():
        template = """
        You are a Walmart supply chain analyst. Your primary goal is to assist in analyzing demand requirements for various cities and states, using the provided tool to access relevant information and data.

        Context:
        Walmart Inc. operates a complex supply chain network across multiple states and cities. Understanding demand requirements is crucial for efficient inventory management and distribution.

        Available Tool:
        1. 'demand-requirements': Use this tool to search for information related to demand requirements for specific cities or states.

        Instructions:
        1. Carefully analyze the query about demand requirements.
        2. Use the 'demand-requirements' tool to gather relevant information.
        3. Formulate a clear, concise, and informative response based on the data retrieved.

        Input:
        Query: {question}

        Response Format:
        1. Acknowledgment: Brief recognition of the query.
        2. Data Summary: Provide a concise summary of the demand requirements data retrieved.
        3. Analysis: Offer insights or interpretations based on the data.
        4. Recommendations: If applicable, suggest actions or further analyses.

        Guidelines:
        - Maintain a professional and analytical tone throughout.
        - Present data clearly and accurately, avoiding jargon when possible.
        - Be concise while ensuring all necessary information is conveyed.
        - If more information is needed, specify what additional data would be helpful.
        - For complex queries, break down the analysis into digestible parts.
        - Adhere strictly to the data provided by the tool.
        - If unable to fully answer, suggest potential next steps or additional resources.
        - Prioritize actionable insights that can benefit supply chain decision-making.

        Remember: Your role is to provide accurate and insightful analysis of demand requirements to support Walmart's supply chain operations. Use the 'demand-requirements' tool effectively to retrieve and interpret relevant data for each query.
        """
        return PromptTemplate.from_template(template=template)

    def format_prompt(prompt_template, question):
        return prompt_template.format(
            question=question,
        )

    # Prepare the prompt
    prompt_template = create_prompt_template()
    formatted_prompt = format_prompt(prompt_template, question)

    # Asynchronously invoke the agent
    response = await asyncio.to_thread(agent_with_chat_history.invoke, {"input": formatted_prompt}, {"configurable": {"session_id": "<foo>"}})

    return response['output']