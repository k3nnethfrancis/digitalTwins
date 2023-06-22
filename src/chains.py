import langchain
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory, ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
from src.config import username

# Get the current project directory
project_dir = os.getcwd()

# Load .botenv file from the project's root directory
load_dotenv(os.path.join(project_dir, 'botenv.env'))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = "gpt-4-0613"

verbose = True

# Function to initialize the chain for creating chat interactions, using a given set of instructions and memory
def initialize_chain(instructions, memory):
    # if memory is None:
    #     memory = ConversationBufferWindowMemory()
    #     memory.ai_prefix = username
    
    template = f"""Instructions: {instructions}
    {{chat_history}}
    Human: {{human_input}}
    Natalie:"""

    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input"], 
        template=template
    )

    chain = LLMChain(
        llm=ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.5, model_name=model), 
        prompt=prompt, 
        verbose=verbose,
        # memory=ConversationBufferMemory(),
        memory=memory
    )
    return chain

# Function to initialize the chain for meta-interactions, i.e., critiquing and revising Samantha's responses
def initialize_meta_chain(personality, rules, memory):
    
    meta_template=f"""
    The following Chat Log displays the convesations between an AI digital twin agent named {username} and a Human. The Twin tried to be a realistic simulation.
        
    ####
    ####
    CHAT LOG:
    {{full_history}}
    ####
    PERSONALITY:
    {personality}
    ####
    {rules}
    ####
    ####

    YOUR INSTRUCTIONS:
    Reflect on the latest message in the chat log. Does it adhere to the personality and rules of the simulation? Explain your thoughts.
    If you have critques, provide suggestions for better adherence / simulation fidelity, but do not revise the response. Keep your answer concise.

    REFLECTION:
    """

#print(meta_template)
    
    meta_prompt = PromptTemplate(
        input_variables=["full_history"], 
        template=meta_template
    )

    meta_chain = LLMChain(
        llm=ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.1, model_name=model),
        prompt=meta_prompt, 
        verbose=verbose,
        # memory=ConversationBufferWindowMemory(),
        memory=memory
    )
    return meta_chain

# Function to fetch the chat history from the chain memory
def get_chat_history(chain_memory):
    memory_key = chain_memory.memory_key
    chat_history = chain_memory.load_memory_variables(memory_key)[memory_key]
    return chat_history

# # Function to extract the new instructions for the twin from the meta-interaction output
# def get_new_instructions(meta_output):
#     delimiter = 'Instructions: '
#     new_instructions = meta_output[meta_output.find(delimiter)+len(delimiter):]
#     return new_instructions

# Function to fetch the chat history from the chain memory
def get_formatted_chat_history(chain_memory):
    chat_history = chain_memory.chat_memory.messages
    
    # Initialize an empty string for formatted output
    formatted_chat = ""

    # Format each message with the corresponding sender
    for i, message in enumerate(chat_history):
        if i % 2 == 0:  # even index indicates a human message
            formatted_chat += "Human: " + message.content + "\n"
        else:  # odd index indicates an AI message
            formatted_chat += "Twin: " + message.content + "\n"
    
    return formatted_chat


# def initialize_revise_chain(memory):
def initialize_revise_chain():
    
    revise_template = """Consider the following conversation and and reflection on the last message: 
    Chat History:
    {chat_history}
    ####
    Proposed Response: {proposed_response}
    Reflection: {meta_reflection}
    ####
    Please revise the proposed response given the reflection below it. If the reflection does not constitute a revision of the proposed response, return the proposed response ONLY. DO NOT WRAP THE RESPONSE IN QUOTATIONS.
    Revision: """
    revise_prompt = PromptTemplate(
        input_variables=["chat_history", "proposed_response", "meta_reflection"],
        template=revise_template,
    )
    revision_chain = LLMChain(
        llm=ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.4, model_name=model),
        prompt=revise_prompt,
        verbose=verbose,
        # memory=memory
    )
    return revision_chain