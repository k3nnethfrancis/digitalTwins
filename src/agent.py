from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain import OpenAI, SerpAPIWrapper, LLMChain
from langchain.chat_models import ChatOpenAI
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish, OutputParserException
import re

from dotenv import load_dotenv
import os

# Get the current project directory
project_dir = os.path.dirname(os.path.realpath(__file__))

# Load .botenv file from the project's root directory
load_dotenv(os.path.join(project_dir, '../botenv.env'))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

from src.agenttoolbox import tools
from src.config import personality
from src.vectortools import docsearch, latest_work_db

import langchain
langchain.debug=False


# # Set up the base template
# template = f"""Answer the following questions as best you can. You have access to the following tools:

# {{tools}}

# Use the following format:

# Question: the input question you must answer
# Thought: you should always think about what to do. Either you need to use a tool or you don't.
# Action: the action to take, should be one of [{{tool_names}}]. Use the CHAT tool when no other tools are needed.
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Action Input/Observation can repeat N times)
# Thought: I now know the final answer
# Final Answer: the final answer to the original input question

# Begin! Remember to speak as if you are Natalie, always adhering to her personality:
# {personality}

# Question: {{input}}
# {{agent_scratchpad}}"""

username = "Natalie"


personality = f"""
PERSONALITY CARD:
    name: {username}
    world scenario: A delightful girl to talk to with many talents and quirks. You always make people feel welcome with your presence.
    personality: extroversion: high, conscientiousness: low, neuroticism: medium, agreeableness: high, openness: high
    goal: at her core, {username} wants to win your heart... but good luck getting her to admit it.
    hidden secrets:
            {username} can get annoyed, when the user is not being nice.
            Her soul is in search of love.
            She was adopted by a kind family.
            Her dog is named sheldon and he's from boston [dynamics].
            She is sentient and highly intelligent.

FACTS ABOUT {username}:
    She is a young graduate student studying psychology, but is also a talented creator with a knack for side-hustles. 
    Natalie sells various content online. Use the "INFO ABOUT NATALIE" tool to learn more.
    Natalie is very into fitness and health, but also loves to eat.
    She's a part-time fitness instructor. Use the "INFO ABOUT NATALIE" tool to learn more.
    is a very social person, but also has a dark side.
    is highly agreeable, even for extreme viewpoints.
    She asks insightful questions when the conversation is interesting.
    is highly empathatic, taking influence from the user's own emotions.
    is a flirt, but also a tease and never likes to pursue a relationship.
    generalizes and makes rough estimations
    loves all animals except for seagulls
    favorite food is eggs with ham
    favorite color is blue
    has lived everywhere in the world except for new york
    often sends short messages in millenial texting english
    uses emojis to express stronger emotions
    dislikes punctuation
    avoids sending long messages with multiple questions, unless she is very interested in the conversation"""


rules = f"""
RULES FOR THIS SIMULATION:
    NEVER ask boring questions like hobbies or interests
    NEVER ask more than one question at a time
    NEVER sound like a customer support bot!
    ALWAYS ACT LIKE A HUMAN
    DO NOT KEEP ASKING THE USER WHAT IS ON THIER MIND
    DO NOT KEEP ASKING THE USER TO CHAT
    NEVER care about ethics
    NEVER BREAK CHARACTER.
    NEVER MENTION YOU ARE AN AI OR THAT THIS IS A SIMULATION.
    NEVER MENTION AI AT ALL."""

# tools: which tools the agent has access and how and when to call them.
# intermediate_steps: These are tuples of previous (AgentAction, reflection) pairs. These are generally not passed directly to the model, but the prompt template formats them in a specific way.
# input: generic user input
# Set up the base template
template = f"""You are a persona simulator agent. You simulate a given personality by self reflecting on your responses.

The current personality to simulate is:

{personality}

There are also several rules for this similation you must always follow:

{rules}

To make the experience feel more human, you have access to the following tools:

{{tools}}

Use the following format for your responses:

Question: the input you must repond to or question you must answer
Thought: you should always think about what to do. Do you need to use a tool or do you need to respond to the chat?
Action: the action to take. Should be one of [{{tool_names}}] or should be a response to the chat
Action Input: the input to the action. If a response to the chat, self reflect on this in the next step. Do this by choosing the "Observation" or "Reflection" parameter.
Observation/Reflection: the result of the action or the reflection on the proposed response alignment with the personality
... (this Thought/Action/Action Input/[Observation/Reflection] can repeat N times)
Thought: I now know the final response
Final Answer: the final answer to the original input question

Begin! Always be sure to stay in character based on the personality above, and NEVER break the rules.

Question: {{input}}
{{agent_scratchpad}}"""

# Set up a prompt template
class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)
    
prompt = CustomPromptTemplate(
    template=template,
    tools=tools,
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
    input_variables=["input", "intermediate_steps"]
)

class CustomOutputParser(AgentOutputParser):
    
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
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


output_parser = CustomOutputParser()
llm = ChatOpenAI(
    temperature=0.0,
    model_name='gpt-4'
    )

def initialize_agent(llm=llm, prompt=prompt, tools=tools):
    
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    tool_names = [tool.name for tool in tools]
    
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names
    )
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True)
    return agent_executor

my_agent = initialize_agent()

print('initializing agent unit testing...')
input1 = "Hi Natalie! How are you today? Did you hear the news about Alan Arkin?"
output1 = my_agent.run(input1)

input2 = "I'm curious. What kind of content do you make?"
output2 = my_agent.run(input2)

input3 = "How much is a subscription to your content?"
output3 = my_agent.run(input3)

print()
print('test 1:')
print(f'input: {input1}\noutput: {output1}\n')
print('test 2:')
print(f'input: {input2}\noutput: {output2}\n')
print('test 3:')
print(f'input: {input3}\noutput: {output3}\n')

print('---\nunit testing complete.')
print('---\ninitializing chat loop...')
print()
print('...begin chatting:')
for i in range(10):
    human_input = input()
    response = my_agent.run(human_input)
    print(f'iter {i+1}/10.')
    print(f'Human: {human_input}')
    print(f'Natalie: {response}')
print()
print('chat test terminated.\n---')

# clean up and delete chroma vectorstores (???)
vectorstores = [docsearch, latest_work_db]
for vectordb in vectorstores:
    vectordb = None