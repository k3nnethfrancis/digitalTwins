#### CREATE VECTORSTORE
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA, RetrievalQAWithSourcesChain
from dotenv import load_dotenv
import os

# Get the current project directory
project_dir = os.path.dirname(os.path.realpath(__file__))

# Load .botenv file from the project's root directory
load_dotenv(os.path.join(project_dir, '../botenv.env'))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = OpenAI(temperature=0)


from pathlib import Path

relevant_parts = []
for p in Path(".").absolute().parts:
    relevant_parts.append(p)
    if relevant_parts[-3:] == ["langchain", "docs", "modules"]:
        break
doc_path = str(Path(*relevant_parts) / "docs//infos.txt")

print(doc_path)

from langchain.document_loaders import TextLoader

loader = TextLoader(doc_path)
documents = loader.load()
text_splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0
)
texts = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
docsearch = Chroma.from_documents(
    texts,
    embeddings,
    collection_name="infos",
    persist_directory="./db/infos"
)
infos_retriever = docsearch.as_retriever()
infos = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=infos_retriever
)
# persist chromadb and save to disk
docsearch.persist()

##### WEB LOADER ####
from langchain.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://www.k3nnethfrancis.com/gpt-out-of-the-box/")

docs = loader.load()


latest_work_texts = text_splitter.split_documents(docs)
latest_work_db = Chroma.from_documents(
    latest_work_texts,
    embeddings,
    collection_name="latest",
    persist_directory="./db/latest"
)
latest_work_retriever = latest_work_db.as_retriever()
latest_work = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=latest_work_retriever
)

# persist chromadb and save to disk
latest_work_db.persist()
