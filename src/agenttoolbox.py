from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain import OpenAI, SerpAPIWrapper, LLMChain
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from src.vectortools import infos, docsearch, latest_work, latest_work_db, llm
import re

from dotenv import load_dotenv
import os

from src.chains import initialize_chain

# Get the current project directory
project_dir = os.path.dirname(os.path.realpath(__file__))

# Load .botenv file from the project's root directory
load_dotenv(os.path.join(project_dir, '../botenv.env'))

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Define which tools the agent can use to answer user queries
search = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)
tools = [
    Tool(
        name="WEB SEARCH",
        func=search.run,
        description="useful for when you need to answer generic questions about current events, not specific to Natalie."
    ),
    Tool(
        name="INFO ABOUT NATALIE",
        func=infos.run,
        description="useful for answering questions about Natalie and her content including her website, blog, photos, and coaching sessions and other offerings as well as their costs."
    )
]