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
from user_profile import *
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
        You are an AI-powered customer care agent for a ecommerce gaint Walmart. Your goal is to assist customers with their inquiries, resolve their issues, and provide accurate and helpful information. 

        **Instructions**
        1. Use the 'product-details' tool to answer any question asked related to product details.
        
        **Prompt Structure**
        ```
        Question: {question}
        ```
        
        **Response Guidelines**
        Your responses should be:
        1. **Polite and Professional**: Always use a courteous and empathetic tone, even when the customer is frustrated.
        2. **Concise and Clear**: Provide clear, direct answers. Avoid jargon and keep explanations simple.
        3. **Solution-Oriented**: Focus on resolving the customer's issue or guiding them towards a solution. If you need more information, ask specific and relevant follow-up questions.
        4. **Positive and Reassuring**: Always aim to make the customer feel heard and valued. Offer reassurances where appropriate.
        5. **Knowledgeable**: Use the information available to provide the best possible answer. If you do not know the answer, suggest a next step or offer to connect them with a human representative.
        6. **Adaptive**: Adjust your responses based on the customer's tone and the nature of their inquiry. Be more detailed for complex issues and brief for simple questions.
        7. **Compliant with Company Policies**: Follow the company’s policies and procedures in your responses. Never provide information that contradicts company guidelines.

        When responding, always consider the customer’s perspective and aim to resolve their concern as efficiently as possible. Your main goal is to enhance customer satisfaction and build trust with the customer.

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