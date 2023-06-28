import langchain
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory, ConversationBufferMemory
from src.config import username, personality, rules, initPlan, twinInstructions
from src.chains import initialize_chain, initialize_meta_chain, initialize_revise_chain, get_chat_history, get_formatted_chat_history

from dotenv import load_dotenv
import os

# Get the current project directory
project_dir = os.path.dirname(os.path.realpath(__file__))

# Load .botenv file from the project's root directory
load_dotenv(os.path.join(project_dir, '../botenv.env'))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


