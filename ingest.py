from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

import os

docs = []
data_path = os.path.join(os.path.dirname(__file__), "data")
for filename in os.listdir(data_path):
    if filename.endswith(".pdf"):
        loader = PyPDFLoader(os.path.join(data_path, filename))
        docs.extend(loader.load())
    elif filename.endswith(".docx"):
        loader = Docx2txtLoader(os.path.join(data_path, filename))
        docs.extend(loader.load())

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")

db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory="embeddings"
)
db.persist()
print("✅ Vector store creat local.")
