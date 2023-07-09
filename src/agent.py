import os
from dotenv import load_dotenv
from pathlib import Path

# load env vars
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
load_dotenv(os.path.join(THIS_DIR, '../bot.env'))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DOC_PATH = str(Path(".").resolve() / "docs" / "infos.txt")

import re
import langchain; langchain.debug=False
from langchain import OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.prompts import StringPromptTemplate
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from typing import List, Union

from src.config import agent_cognition as template
from src.vectortools import process_documents


# this prompt template generates the "agent_scratchpad" or the steps in the "thoughts" of the agent
    # it also formats the tools
class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        
        # loop through the thought steps and format them
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log # add the action step to the thoughts
            thoughts += f"\nObservation: {observation}\nThought: " # add the observation step to the thoughts
        
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts

        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        
        return self.template.format(**kwargs)

# create the output parser
    # can format the prompt and be used for logging
class CustomOutputParser(AgentOutputParser):
    
    # this outputs a dictionary with the action and action input
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:

        # Check if agent should finish
        if "Final Response:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Response:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise OutputParserException(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)



info_db, info_retriever, info_chain = process_documents(
    TextLoader,
    DOC_PATH, 
    'infos', 
    './db/infos'
)

def respond_to_chat(input, **kwargs):
    return input

tools = [
    Tool(
        name="Respond to chat",
        func=respond_to_chat,
        description="not a real tool. just a placeholder for the agent to respond to the chat."
    ), 
    Tool(
        name="INFO ABOUT NATALIE",
        func=info_chain.run,
        description="useful for answering questions about Natalie and her content including her website, blog, photos, and coaching sessions and other offerings as well as their costs."
    )
]

prompt = CustomPromptTemplate(
    template=template,
    tools=tools,
    input_variables=["input", "chat_history", "intermediate_steps"]
)

output_parser = CustomOutputParser()

from langchain.memory import ConversationBufferMemory
conversation_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    ai_prefix="Natalie"
)

llm = ChatOpenAI(
    temperature=0.0,
    model_name='gpt-4'
)


def initialize_agent(llm=llm, prompt=prompt, tools=tools, memory=conversation_memory):
    
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    tool_names = [tool.name for tool in tools]
    print(f'the tool names are: {tool_names}')
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names
    )
    agent_memory=memory
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=agent_memory
    )
    return agent_executor

my_agent = initialize_agent()

# print('\ninitializing agent unit testing...\n---')
# input1 = "Hi Natalie! please summarize the content in the info about you tool."
# output1 = my_agent.run(input1)

# input2 = "What kind of content do you make?"
# output2 = my_agent.run(input2)

# input3 = "How much is a subscription to your content?"
# output3 = my_agent.run(input3)

# print()
# print('test 1:')
# print(f'input: {input1}\noutput: {output1}\n')
# print('test 2:')
# print(f'input: {input2}\noutput: {output2}\n')
# print('test 3:')
# print(f'input: {input3}\noutput: {output3}\n')

# print('---\ntesting complete.')
print('---\ninitializing chat loop...')
print()
print('...begin chatting:')
i = 1
while True:
    human_input = input()
    if human_input == "\\end":
        break
    response = my_agent.run(human_input)
    print(f'iter {i}.')
    print(f'Human: {human_input}')
    print(f'Natalie: {response}')
    history = conversation_memory.load_memory_variables({})
    print('\nchat history:\n---')
    for message in history['chat_history']:
        print(f'{type(message).__name__}: {message.content}')
    print('---')

    i += 1


print()
print('chat test terminated.\n---')

# clean up and delete chroma vectorstores
vectorstores = [info_db]
for vectordb in vectorstores:
    vectordb = None