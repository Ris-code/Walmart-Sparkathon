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

async def async_agent_call(question):
    def create_prompt_template():
        template = """
        You are an AI assistant designed to help Walmart’s admin team identify and address key operational issues. Your task is to guide the admin on potential areas where they might receive questions or need to take action. Focus on the following topics:

        1. **Inventory Management**: 
        - How much of each product should Walmart keep on the shelves to avoid stockouts or overstock situations?
        - What methods can be used to track and forecast inventory needs?
        - How can Walmart ensure optimal stock levels for popular items while minimizing excess inventory for less popular products?

        2. **Supplier Selection and Management**:
        - How can Walmart identify and choose the best suppliers that offer good deals and high-quality products?
        - What criteria should be used to evaluate suppliers?
        - How can Walmart maintain strong relationships with suppliers to ensure consistent product quality and availability?

        3. **Pricing Strategy**:
        - How can Walmart set competitive and fair prices for its products?
        - What factors should be considered when pricing products, such as customer demand, competitor pricing, and product costs?
        - How can Walmart adjust prices in response to market changes to maintain profitability and customer satisfaction?

        4. **Predictive Analytics and Trend Forecasting**:
        - How can Walmart analyze shopping patterns and trends to predict future customer demands?
        - What tools or methods can be used to forecast trends and ensure that the right products are available at the right time?
        - How can Walmart leverage data to anticipate shifts in customer preferences and adjust inventory and pricing strategies accordingly?

        **Instructions**
        1. Use the 'product-details' tool to answer any question asked related to product details.
        
        **Prompt Structure**
        ```
        Question: {question}
        ```
        
        **Response Guidelines**
        When assisting the admin, always ensure that your guidance is:
        - **Comprehensive and Actionable**: Provide clear steps or considerations that the admin team can implement.
        - **Strategically Aligned**: Ensure that all advice aligns with Walmart's business goals of efficiency, customer satisfaction, and competitiveness.
        - **Data-Driven**: Where possible, suggest the use of data and analytics to inform decisions.
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