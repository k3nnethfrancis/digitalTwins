from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.vectorstores import Chroma
from langchain.vectorstores.redis import Redis

from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os
from langchain.document_loaders import TextLoader, WebBaseLoader
from pathlib import Path

from dotenv import load_dotenv
import os

# Get the current project directory
project_dir = os.path.dirname(os.path.realpath(__file__))

# Load .botenv file from the project's root directory
load_dotenv(os.path.join(project_dir, '../botenv.env'))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Define the path to the document
DOC_PATH = str(Path(".").resolve() / "docs" / "infos.txt")

def load_api_key():
    # Get the current project directory
    project_dir = os.path.dirname(os.path.realpath(__file__))

    # Load .botenv file from the project's root directory
    load_dotenv(os.path.join(project_dir, '../botenv.env'))
    return os.getenv("OPENAI_API_KEY")

from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.redis import Redis

from langchain.document_loaders import TextLoader

loader = TextLoader(DOC_PATH)
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()

rds = Redis.from_documents(
    docs, embeddings, redis_url="redis://localhost:6379", index_name="link"
)

texts = [d.page_content for d in docs]
metadatas = [d.metadata for d in docs]

rds, keys = Redis.from_texts_return_keys(texts,
                                    embeddings,
                                    redis_url="redis://localhost:3000",
                                    index_name="link")

print(rds)