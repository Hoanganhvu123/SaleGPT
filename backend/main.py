import os
from dotenv import load_dotenv
from typing import Dict, Any, Type
from pydantic import BaseModel, Field

from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_groq import ChatGroq
from langchain_experimental.tools.python.tool import PythonAstREPLTool
import pandas as pd
from langchain_core.runnables import RunnablePassthrough

from langchain_core.tools import BaseTool, StructuredTool, Tool, tool, BaseToolkit
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent, create_tool_calling_agent
from langchain.callbacks.manager import CallbackManager
from langchain_core.tracers.langchain import LangChainTracer
from salegpt.prompt import ORDER_MANAGEMENT_PROMPT
from langsmith import traceable


# Load environment variables
load_dotenv()
# os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY')
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_SMITH_API_KEY")
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')



# class OrderManagementInput(BaseModel):
#     input: str = Field(description="Input commands related to managing customer orders. Please use Vietnamese input commands when using this tool.")
    
# class OrderManagementTool(StructuredTool):
#     name: str = "order_management"
#     args_schema: Type[BaseModel] = Field(description="""Input commands related to managing customer orders. 
#                                           Please use Vietnamese input commands when using this tool.""")

#     def _run(self, input: str) -> Any:
#         llm = ChatGroq(temperature=0.3, model_name="llama3-70b-8192")
#         prompt = PromptTemplate(
#             template=ORDER_MANAGEMENT_PROMPT,
#             input_variables=["input"]
#         )
#         order_data = pd.read_csv("E:\\SaleGPT\\packages\\salegpt\\data\\orders.csv")
#         python_tool = PythonAstREPLTool(globals={"df": order_data})
#         # Construct the chain
#         chain = (
#             {"input": RunnablePassthrough()} 
#             | prompt 
#             | llm
#             # | (lambda x: print("Đầu ra LLM : " + x.content))
#             # | (lambda x: print()) 
#             | (lambda x: python_tool.invoke(x.content))
#         )
#         result = chain.invoke(input)
#         print(result)
#         return result
    
class OrderManagementTool(BaseTool):
    name = "order_management"
    description = "Manage customer orders using a pandas dataframe"
    verbose = True

    def _run(self, input: str) -> str:
        llm = ChatGroq(temperature=0.3, model_name="llama3-70b-8192")
        prompt = PromptTemplate(
            template=ORDER_MANAGEMENT_PROMPT,
            input_variables=["input"]
        )
        order_data = pd.read_csv("E:\\SaleGPT\\backend\\salegpt\\data\\orders.csv")
        python_tool = PythonAstREPLTool(globals={"df": order_data})
        
        
        chain = (
            {"input": RunnablePassthrough()} 
            | prompt 
            | llm
            | (lambda x: python_tool.invoke(x.content))
        )
        result = chain.invoke(input)
        return result


if __name__ == "__main__":
    # processor = DocumentProcessor(data_path=r"E:\ShoppingGPT\packages\shoppinggpt\data\policy.txt")
    # processor.load_and_process_documents()

    # policy_tool = PolicySearchTool()
    # search_query = "Return policy"
    # results = policy_tool._run(search_query)
    # print(results)

    tools = [OrderManagementTool()]
    prompt = hub.pull("hwchase17/openai-tools-agent")
    llm = ChatGroq(temperature=0.5, model="llama3-70b-8192")
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_error = True,
        return_intermediate_steps = True
    )
    
    question = """Tao là Hoàng Anh, 12345, nhà ở ngõ 35 hưng yên, đặt cho tao sản phẩm X nhé
    và thời gian mong muốn là vào 6/8/2034
        """
    a = agent_executor.invoke({"input": question})
    print(a['output'])