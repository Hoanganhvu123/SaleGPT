import os
from typing import Dict, Any
import pandas as pd
from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.agents.openai_functions_agent.base import (
    OpenAIFunctionsAgent,
    create_openai_functions_agent,
)
from langchain.agents import AgentExecutor  
from langchain import hub

from langchain.memory import ConversationBufferWindowMemory, ConversationBufferMemory
from langchain.memory.combined import CombinedMemory
from langchain.memory.entity import (
    ConversationEntityMemory,
    InMemoryEntityStore,
    RedisEntityStore,
    SQLiteEntityStore,
    UpstashRedisEntityStore,
)
from langchain.memory.vectorstore import VectorStoreRetrieverMemory

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.agents.react.agent import create_react_agent

from salegpt.tool.product_search import ProductSearchTool
from salegpt.tool.policy_search import PolicySearchTool
from salegpt.agent.prompt import shopping_assistant_prompt
 
 
 
# Load environment variables
load_dotenv()
os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY')
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_SMITH_API_KEY")
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')


class ShoppingGPT:
    def __init__(self, llm, verbose=False, **kwargs):
        self.llm = llm
        self.verbose = verbose

        self.memory = ConversationBufferWindowMemory()
        self.human_chat_memory = []
        self.human_input = ""
        

    def human_step(self) -> str:
        self.human_input = input("User: ")
        self.memory.chat_memory.add_user_message(self.human_input)
 
 
    def agent_step(self):
        tools = [ProductSearchTool(), PolicySearchTool()]
        inputs = {
            "chat_history": self.memory.chat_memory.messages,
            "input": self.human_input,
        }
        prompt = hub.pull("hwchase17/openai-tools-agent")
        agent = create_tool_calling_agent(self.llm, tools ,prompt)
        
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools , 
            verbose = True,
            handle_parsing_errors=True,
        )
        
        ai_message = agent_executor.invoke(inputs)
        agent_output = ai_message['output']
        self.memory.chat_memory.add_ai_message(agent_output)  
        print("AI : " + agent_output)