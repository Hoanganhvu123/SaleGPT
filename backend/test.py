from langchain.chains.qa_generation.base import QAGenerationChain
from langchain.chains.router.embedding_router import EmbeddingRouterChain
from langchain.chains.router.multi_prompt import MultiPromptChain

from langchain_groq import ChatGroq
from langchain.text_splitter import CharacterTextSplitter
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_SMITH_API_KEY")
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

# Tạo một language model (ví dụ sử dụng ChatGroq)
llm = ChatGroq(temperature=0.5, model="llama3-70b-8192")

# Tạo một text splitter để chia văn bản thành các đoạn nhỏ
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

# Tạo một QAGenerationChain
# qa_chain = QAGenerationChain(llm = llm, k=2)

chain = QAGenerationChain.from_llm(llm)  

# Cung cấp văn bản đầu vào
text = "Langchain là một framework mạnh mẽ để phát triển các ứng dụng dựa trên mô hình ngôn ngữ. Nó cung cấp một tập hợp các thư viện và công cụ giúp nhà phát triển xây dựng các ứng dụng có khả năng xử lý ngữ cảnh và lập luận."

# Sử dụng QAGenerationChain để tạo câu hỏi và trả lời
result = chain.invoke(text, )
# In kết quả
print(result)