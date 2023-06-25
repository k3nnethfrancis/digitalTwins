# Import things that are needed generically
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.tools import BaseTool
from langchain.llms import OpenAI
from langchain import LLMMathChain, SerpAPIWrapper
from src.vectortools import infos, docsearch, latest_work, latest_work_db, llm

tools = [
    Tool(
        name="ABOUT KEN",
        func=infos.run,
        description="useful for answering questions about Ken and his content including his website, blog, photos, and tutorials as well as their costs. Inputs should be fully formed questions."
    ),
    Tool(
        name="KEN'S LATEST ESSAY",
        func=latest_work.run,
        description="useful for when you need to answer questions about ken's latest essay. Input should be a fully formed question.",
    ),
]

# Construct the agent. We will use the default agent type here.
# See documentation for a full list of options.
agent = initialize_agent(
    tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)

query1 = "What is your blog about and where can i read more?"
agent_response1 = agent.run(
    query1
)

query2 = "How much is a subscription to your blog?"
agent_response2 = agent.run(
    query2
)

query3 = "what do you do for a living?"
agent_response3 = agent.run(
    query3
)

query4 = "what is your latest essay about?"
agent_response4 = agent.run(
    query4
)

query5 = "i want to see ken's dog!"
agent_response5 = agent.run(
    query5
)

query6 = "how much are ken's online courses and where can I access them?"
agent_response6 = agent.run(
    query6
)


print('test a\n---')
print(f'user: {query1}\nagent: {agent_response1}')
print('---\nend test a\n')
print()
print('test b\n---')
print(f'user: {query2}\nagent: {agent_response2}')
print('---\nend test b\n')
print()
print('test c\n---')
print(f'user: {query3}\nagent: {agent_response3}')
print('---\nend test c\n')
print()
print('test d\n---')
print(f'user: {query4}\nagent: {agent_response4}')
print('---\nend test d\n')
print()
print('test e\n---')
print(f'user: {query5}\nagent: {agent_response5}')
print('---\nend test e\n')
print()
print('test f\n---')
print(f'user: {query6}\nagent: {agent_response6}')
print('---\nend test f\n')


# clean up and delete chroma vectorstores (???)
vectorstores = [docsearch, latest_work_db]
for vectordb in vectorstores:
    vectordb = None