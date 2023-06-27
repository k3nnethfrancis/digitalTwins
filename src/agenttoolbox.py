from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain import OpenAI, SerpAPIWrapper, LLMChain
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from src.vectortools import infos, docsearch, latest_work, latest_work_db, llm
import re

from dotenv import load_dotenv
import os

# Get the current project directory
project_dir = os.path.dirname(os.path.realpath(__file__))

# Load .botenv file from the project's root directory
load_dotenv(os.path.join(project_dir, '../botenv.env'))

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")



# Define which tools the agent can use to answer user queries
search = SerpAPIWrapper()
tools = [
    Tool(
        name = "WEB SEARCH",
        func=search.run,
        description="useful for when you need to answer generic questions about current events, not specific to Natalie."
    ),
    Tool(
        name="INFO ABOUT NATALIE",
        func=infos.run,
        description="useful for answering questions about Natalie and her content including her website, blog, photos, and tutorials as well as their costs. Inputs should be fully formed questions."
    ),
    Tool(
        name="NATALIE'S LATEST CONTENT",
        func=latest_work.run,
        description="useful for when you need to answer specific questions about Natalies's latest peice of content. Input should be a fully formed question.",
    ),
]