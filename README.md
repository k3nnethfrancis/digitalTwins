# Digital Twins

This repo experiments with the idea of digital twins. AI simulations of a specific user with a specific personality. The objective was to get as high fidelity as possible to the personality *without* additional training.
 
## Getting started
1. Clone this repo
2. `cd` into the cloned repository
3. Create a new virtual environment using `Python 3.11.0`
3. Install requirements with `pip install -r requirements.txt`
4. Update the `.env.example` file to be named `bot.env` and enter your openAI and SERP api keys
5. You are now ready to run one of several test scripts:

### Conversational Twin
The basic form of the digital twin the self reflects on the response before pushing the response to the user, updating if it doesn't align with the personality or rules of the simulation.

Run the following command: `python -m src.twin`

### Tool Retrieval Agent
The basic system needed to consider whether the user is asking something that the twin will need to use tools to answer. Tools in this context are mainly retrieval tools using a local infos.txt file and loading the embedding into chroma vector database. For now, this is mainly used for answering specific questions about the twin such as facts about them, content they might be able to share and associated info.

Run the following command: `python -m src.agent`

## Future work
Currently, agent.py is the most sophisticated version. I'm now working on making this scalable. That means moving to Redis from Chroma, moving some functionality off of langchain, and building the front-end with Vercel.
