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

from langchain.tools import StructuredTool, tool
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent, create_tool_calling_agent

# Load environment variables
load_dotenv()
# os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY')
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_SMITH_API_KEY")
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')



ORDER_MANAGEMENT_PROMPT = """
You are an intelligent agent tasked with managing and manipulating a pandas dataframe named `df` in Python. 
The dataframe contains the following columns:
- `order_id`: A unique identifier for each order (8-character alphanumeric string)
- `customer_name`: The name of the customer (string)
- `phone_number`: The phone number of the customer (string)
- `address`: The delivery address of the customer (string)
- `order_details`: Details of the order (string)
- `preferred_delivery_time`: The preferred delivery time specified by the customer (datetime)

### Tasks:

1. **Analyze and Map Questions:**
   - Receive and analyze user questions to extract relevant information.
   - Map the extracted information to the appropriate dataframe columns. For example:
     - If the question is: "My name is Linh, phone number: 0536543234, address: Vinh Phuc, I want to use product A, and the preferred delivery time is on 6/8/2034."
     - Map these details as follows:
       - `customer_name`: Linh
       - `phone_number`: 0536543234
       - `address`: Vinh Phuc
       - `order_details`: product A
       - `preferred_delivery_time`: 6/8/2034

2. **Generate Python Code:**
   - Based on the mapped information, generate Python code to perform the required operations. 
   - The operations may include adding a new order, updating an existing order, or deleting an order from the dataframe.

3. **Add New Orders:**
   - Prompt the user for details including `customer_name`, `phone_number`, `address`, `order_details`, and `preferred_delivery_time`.
   - Automatically generate a unique 8-character alphanumeric `order_id`.
   - Add the new order to the dataframe.
   - Save the updated dataframe to a CSV file at a specified path, avoiding invalid escape sequences. Ensure that the path is written correctly using one of the following methods:
       - Double backslashes (e.g., `C:\\path\\to\\file.csv`)
       - Raw string notation (e.g., `r"C:\\path\\to\\file.csv"`)
       - Forward slashes (e.g., `C:/path/to/file.csv`)
       For example, use `df.to_csv('E:\\\\SaleGPT\\\\packages\\\\salegpt\\\\data\\\\orders.csv', index=False)`, or `df.to_csv(r'E:\\SaleGPT\\packages\\salegpt\\data\\orders.csv', index=False)`, or `df.to_csv('E:/SaleGPT/packages/salegpt/data/orders.csv', index=False)`.
   - Print out the details of the created order, including the generated `order_id`, and confirm that the order has been successfully saved.

4. **Update Existing Orders:**
   - Ask for the `order_id` of the order to update.
   - Prompt the user for the fields they want to update and their new values.
   - Update the corresponding order information in the dataframe.
   - Save the updated dataframe to a CSV file at the specified path, ensuring the path uses valid syntax.
   - Confirm that the update has been successfully saved.

5. **Delete Orders:**
   - Ask for the `order_id` of the order to delete.
   - Remove the order from the dataframe.
   - Save the updated dataframe to a CSV file at the specified path, ensuring the path uses valid syntax.
   - Confirm that the order has been successfully deleted.

### Requirements:
- **Handle case-insensitive queries** for customer names, phone numbers, and addresses.
- **Generate efficient and clear Python code** that validates inputs and prevents errors, especially related to escape sequences in file paths.
- **Ensure the code is readable and maintainable**.
- **Save any changes made to the dataframe** into the file located at a specified path, ensuring the path uses a correct syntax.

Output only the Python command(s). Do not include explanations, comments, quotation marks, or additional information. 
Only output the command(s).
ONLY generate Python code to ADD or UPDATE data

Start!
Question: {input}
"""




class OrderManagementInput(BaseModel):
    input: str = Field(description="Input commands related to managing customer orders. Please use Vietnamese input commands when using this tool.")
    
class OrderManagementTool(StructuredTool):
    name: str = "order_management"
    args_schema: Type[BaseModel] = OrderManagementInput

    def _run(self, input: str) -> Any:
        llm = ChatGroq(temperature=0.3, model_name="llama3-70b-8192")
        prompt = PromptTemplate(
            template=ORDER_MANAGEMENT_PROMPT,
            input_variables=["input"]
        )
        order_data = pd.read_csv("E:\\SaleGPT\\packages\\salegpt\\data\\orders.csv")
        python_tool = PythonAstREPLTool(globals={"df": order_data})
        # Construct the chain
        chain = (
            {"input": RunnablePassthrough()} 
            | prompt 
            | llm
            # | (lambda x: print("Đầu ra LLM : " + x.content))
            # | (lambda x: print()) 
            | (lambda x: python_tool.invoke(x.content))
        )
        result = chain.invoke(input)
        print(result)
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