import langchain
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory, ConversationBufferMemory
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from src.config import username, personality, rules, init_plan, twin_instructions
from src.chains import initialize_chain, initialize_meta_chain, initialize_revise_chain, get_chat_history

from langchain.chat_models import ChatOpenAI

from dotenv import load_dotenv
import os

# Get the current project directory
project_dir = os.path.dirname(os.path.realpath(__file__))

# Load .botenv file from the project's root directory
load_dotenv(os.path.join(project_dir, '../botenv.env'))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



def main(user_input, inner_loop_iters=1, max_chat_iters=5, verbose=False, debug_mode=False):
    # init variable assignment
    langchain.debug = debug_mode # debug mode shows all langchain outputs
    twin = username # twins name
    instructions = twin_instructions # instruction prompt for twin
    twin_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, ai_prefix=twin) # initilize the conversation memory buffer. This stores chat history and returns messages when requested.
    full_history = ConversationBufferMemory(memory_key="reflect_history", return_messages=True, ai_prefix=twin)
    chain = initialize_chain(instructions) # initialize the initial conversation chain

    # print(
    #     f'''MEMORY STATE 0: {twin_memory.chat_memory}'''
    # )

    # print(f'Human: {user_input}') # print the users message

    #output = chain.predict(human_input=user_input, history=twin_memory) # assign the output to a var and include memory for the convo
    output = chain.predict(human_input=user_input) # assign the output to a var and include memory for the convo
    twin_memory.save_context({"Human": user_input}, {twin: output})    
    full_history.save_context({"Human": user_input}, {twin: output})
    if verbose:
        #print the twins output
        print(f'{twin}: {output} [END TWIN 1]') # print the first twin response
        print()
        print(
            f'''MEMORY STATE 1: {twin_memory.chat_memory}'''
        )
        print()
        print('...starting conversation loop...')
        #mem = []
        
        ## this kicks off the first query to the twin that it will self reflect about before answering
        for i in range(max_chat_iters):
            print(f'[Iter {i+1}/{max_chat_iters}]')
            
            human_input = input() # get input from the human user
            # print(f'Human: {human_input} [END HUMAN 1]') # print the users message
            twin_memory.chat_memory.add_user_message(human_input)
            print()
            # history = memory
            # history.save_context({"Human": human_input}, {twin: proposed_output})
            print(
                f'''MEMORY STATE 2: {twin_memory.chat_memory}'''
            )   
            print()
            print('...INITIALIZING INNER SELF-REFLECTION LOOP...')
            for j in range(inner_loop_iters):
                print(f'(Step {j+1}/{inner_loop_iters})')
                print()
                proposed_output = chain.predict(human_input=human_input)
                full_history.chat_memory.add_user_message(human_input)
                #full_history.save_context({"Human": human_input}, {twin: proposed_output})
                print(
                    f'''MEMORY STATE 3: {twin_memory.chat_memory}'''
                )
                
                print(f'{twin} [proposed response]: {proposed_output} [END TWIN 3]')
                print()
                print(
                    f'''HISTORY STATE 2: {full_history.chat_memory}'''
                )
                # The AI reflects on its performance using the meta chain
                meta_chain = initialize_meta_chain(personality=personality, rules=rules) # inject the twins personality and rules for the simulation
                meta_output = meta_chain.predict(chat_history=get_chat_history(chain.memory)) # assign the output to a var with memory
                print(f'{twin} [self-reflection]: {meta_output} [END REFLECTION 1]')
                print(
                    f'''MEMORY STATE 4: {twin_memory.chat_memory}'''
                ) 
                print()
                
                # initialize the revise chain
                revise_chain = initialize_revise_chain(memory=full_history)
                #revision = revise_chain.predict(chat_history=get_chat_history(chain.memory), meta_reflection=meta_output, proposed_response=proposed_output) # include history and the meta reflection output
                revision = revise_chain.predict(chat_history=get_chat_history(chain.memory), meta_reflection=meta_output, proposed_response=proposed_output) # include history and the meta reflection output
                # print(f'{twin} [revised response]: {revision} [END REVISION 1]')
                print(f'{twin}: {revision} [END REVISION 1]')
                print()
                # human_input = input()
                # print(f'Human: {human_input} [END6]')

                #save the revised exchange to memory to continue the loop
                twin_memory.chat_memory.add_ai_message(revision)
                #memory.save_context({"Human": human_input}, {twin: revision})
                print(
                    f'''MEMORY STATE 5: {twin_memory.chat_memory}'''
                ) 
                print()
                #mem.append(revision)
                print('...ENDING INNER SELF-REFLECTION LOOP..')
                print()
    else:
        #print the twins output
        print(f'{twin}: {output}') # print the first twin response
        

        ## this kicks off the first query to the twin that it will self reflect about before answering
        for i in range(max_chat_iters):
            human_input = input() # get input from the human user
            # print(f'Human: {human_input}') # print the users message
            twin_memory.chat_memory.add_user_message(human_input)
        
            for j in range(inner_loop_iters):
                proposed_output = chain.predict(human_input=human_input)
                twin_memory.chat_memory.add_user_message(human_input)
                full_history.save_context({"Human": human_input}, {twin: proposed_output})
                
                print(f'{twin} [proposed response]: {proposed_output}')

                # The AI reflects on its performance using the meta chain
                meta_chain = initialize_meta_chain(personality=personality, rules=rules) # inject the twins personality and rules for the simulation
                meta_output = meta_chain.predict(chat_history=get_chat_history(chain.memory)) # assign the output to a var with memory
                print(f'{twin} [self-reflection]: {meta_output}')

                
                # initialize the revise chain
                revise_chain = initialize_revise_chain(memory=full_history)
                #revision = revise_chain.predict(chat_history=get_chat_history(chain.memory), meta_reflection=meta_output, proposed_response=proposed_output) # include history and the meta reflection output
                revision = revise_chain.predict(chat_history=get_chat_history(chain.memory), meta_reflection=meta_output, proposed_response=proposed_output) # include history and the meta reflection output
                # print(f'{twin} [revised response]: {revision} [END REVISION 1]')
                print(f'{twin} [revision]: {revision}')

                #save the revised exchange to memory to continue the loop
                twin_memory.chat_memory.add_ai_message(revision)
            

        
        print('\n'+'#'*80+'\n')

    print(f'End of conversation! Thanks for Chatting!')


print('...send a message to start the conversation...')
# memory is not working exactly how I would like but it 'works'
init_msg = input()

main(
    user_input=init_msg,
    max_chat_iters=10,
    verbose=True,
    debug_mode=False
)