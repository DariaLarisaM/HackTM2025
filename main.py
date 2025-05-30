import os

# Importuri corecte conform noilor pachete recomandate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import PyPDFLoader

folder_path = os.path.join(os.path.dirname(__file__), "data")

if not os.path.exists(folder_path):
    raise Exception(f"Folderul '{folder_path}' nu există. Creează-l și pune acolo PDF-uri.")

documents = []
for filename in os.listdir(folder_path):
    if filename.endswith(".pdf"):
        loader = PyPDFLoader(os.path.join(folder_path, filename))
        documents.extend(loader.load())

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="embeddings", embedding_function=embedding_model)
vectorstore.add_documents(documents)

llm = OllamaLLM(model="mistral")

from langchain.chains import RetrievalQA
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())

print("Întreabă chatbot-ul (scrie 'exit' pentru a ieși):")
while True:
    query = input("Întrebare: ")
    if query.lower() == "exit":
        break
    response = qa.invoke({"query": query})
    print("Răspuns:", response["result"])
