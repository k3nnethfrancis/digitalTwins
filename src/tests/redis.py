# from langchain.embeddings.openai import OpenAIEmbeddings
# # from langchain.vectorstores import Chroma
# from langchain.vectorstores.redis import Redis

# from langchain.text_splitter import CharacterTextSplitter
# from langchain.llms import OpenAI
# from langchain.chains import RetrievalQA
# from dotenv import load_dotenv
# import os
# from langchain.document_loaders import TextLoader, WebBaseLoader
from pathlib import Path

from dotenv import load_dotenv
import os

# Get the current project directory
THIS_DIR = os.path.dirname(os.path.realpath(__file__))

# Load bot.env file from the project's root directory
load_dotenv(os.path.join(THIS_DIR, '../bot.env'))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Define the path to the document
DOC_PATH = str(Path(".").resolve() / "docs" / "infos.txt")

# def load_api_key():
#     # Get the current project directory
#     THIS_DIR = os.path.dirname(os.path.realpath(__file__))

#     # Load .env file from the project's root directory
#     load_dotenv(os.path.join(THIS_DIR, '../bot.env'))
#     return os.getenv("OPENAI_API_KEY")

# from langchain.embeddings import OpenAIEmbeddings
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.vectorstores.redis import Redis

# from langchain.document_loaders import TextLoader

# loader = TextLoader(DOC_PATH)
# documents = loader.load()
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# docs = text_splitter.split_documents(documents)

# embeddings = OpenAIEmbeddings()

# rds = Redis.from_documents(
#     docs, embeddings, redis_url="redis://localhost:6379", index_name="link"
# )

# texts = [d.page_content for d in docs]
# metadatas = [d.metadata for d in docs]

# rds, keys = Redis.from_texts_return_keys(texts,
#                                     embeddings,
#                                     redis_url="redis://localhost:3000",
#                                     index_name="link")

# print(rds)

import os
 
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.redis import Redis as RedisVectorStore
 

product_metadata = {'item_id': 'B07T2JY31Y',
 'marketplace': 'Amazon',
 'country': 'IN',
 'main_image_id': '71vX7qIEAIL',
 'domain_name': 'amazon.in',
 'bullet_point': '3D Printed Hard Back Case Mobile Cover for Sony Xperia Z1 L39H Easy to put & take off with perfect cutouts for volume buttons, audio & charging ports. Stylish design and appearance, express your unique personality. Extreme precision design allows easy access to all buttons and ports while featuring raised bezel to life screen and camera off flat surface. Slim Hard Back Cover No Warranty',
 'item_keywords': 'mobile cover back cover mobile case phone case mobile panel phone panel LG mobile case LG phone cover LG back case hard case 3D printed mobile cover mobile cover back cover mobile case phone case mobile panel phone panel Sony Xperia mobile case Sony Xperia phone cover Sony Xperia back case hard case 3D printed mobile cover mobile cover back cover mobile case phone case mobile panel phone panel Sony Xperia mobile case Sony Xperia phone cover Sony Xperia back case hard case 3D printed mobile cover mobile cove',
 'material': 'Wood',
 'brand': 'Amazon Brand - Solimo',
 'color': 'others',
 'item_name': 'Amazon Brand - Solimo Designer Leaf on Wood 3D Printed Hard Back Case Mobile Cover for Sony Xperia Z1 L39H',
 'model_name': 'Sony Xperia Z1 L39H',
 'model_number': 'gz8056-SL40528',
 'product_type': 'CELLULAR_PHONE_CASE'}

 
# data that will be embedded and converted to vectors
texts = [
    v[0] for k, v in product_metadata.items()
]
 
# product metadata that we'll store along our vectors
metadatas = list(product_metadata.values())
 
# we will use OpenAI as our embeddings provider
embedding = OpenAIEmbeddings()
 
# name of the Redis search index to create
index_name = "products"
 
# assumes you have a redis stack server running on local host
redis_url = "rediss://default:AVNS_kZxtp7N7f9jZuzxcI8W@twin-testing-db-do-user-13651350-0.b.db.ondigitalocean.com:25061"

# create and load redis with documents
vectorstore = RedisVectorStore.from_texts(
    texts=texts,
    metadatas=metadatas,
    embedding=embedding,
    index_name=index_name,
    redis_url=redis_url
)

from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import (
    ConversationalRetrievalChain,
    LLMChain
)
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.prompts.prompt import PromptTemplate


template = """Given the following chat history and a follow up question, rephrase the follow up input question to be a standalone question.
Or end the conversation if it seems like it's done.
Chat History:\"""
{chat_history}
\"""
Follow Up Input: \"""
{question}
\"""
Standalone question:"""
 
condense_question_prompt = PromptTemplate.from_template(template)
 
template = """You are a friendly, conversational retail shopping assistant. Use the following context including product names, descriptions, and keywords to show the shopper whats available, help find what they want, and answer any questions.
 
It's ok if you don't know the answer.
Context:\"""
 
{context}
\"""
Question:\"
\"""
 
Helpful Answer:"""
 
qa_prompt= PromptTemplate.from_template(template)


# define two LLM models from OpenAI
llm = OpenAI(temperature=0)
 
streaming_llm = OpenAI(
    streaming=True,
    callback_manager=CallbackManager([
        StreamingStdOutCallbackHandler()
    ]),
    verbose=True,
    max_tokens=150,
    temperature=0.2
)
 
# use the LLM Chain to create a question creation chain
question_generator = LLMChain(
    llm=llm,
    prompt=condense_question_prompt
)
 
# use the streaming LLM to create a question answering chain
doc_chain = load_qa_chain(
    llm=streaming_llm,
    chain_type="stuff",
    prompt=qa_prompt
)

chatbot = ConversationalRetrievalChain(
    retriever=vectorstore.as_retriever(),
    combine_docs_chain=doc_chain,
    question_generator=question_generator
)


# create a chat history buffer
chat_history = []
# gather user input for the first question to kick off the bot
question = input("Hi! What are you looking for today?")
 
# keep the bot running in a loop to simulate a conversation
while True:
    result = chatbot(
        {"question": question, "chat_history": chat_history}
    )
    print("\n")
    chat_history.append((result["question"], result["answer"]))
    question = input()