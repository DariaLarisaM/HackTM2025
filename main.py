import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import RetrievalQA

folder_path = "D:\\HackTm2025\\data"
if not os.path.exists(folder_path):
    raise Exception(f"Folderul '{folder_path}' nu există. Creează-l și pune acolo PDF-uri.")

documents = []
for filename in os.listdir(folder_path):
    if filename.endswith(".pdf"):
        loader = PyPDFLoader(os.path.join(folder_path, filename))
        documents.extend(loader.load())

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = Chroma(
    persist_directory="embeddings",
    embedding_function=embedding_model
)
vectorstore.add_documents(documents)

llm = OllamaLLM(model="mistral")

prompt_template = ChatPromptTemplate.from_template("""
Folosește doar informațiile din contextul de mai jos pentru a răspunde la întrebare în limba română. Nu inventa răspunsuri.

Context:
{context}

Întrebare:
{question}

Răspuns:
""")

qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    chain_type_kwargs={"prompt": prompt_template},
    return_source_documents=False
)

print("✅ Chatbot-ul juridic e gata. Scrie o întrebare sau 'exit' pentru a ieși.")
while True:
    query = input("\nÎntrebare: ")
    if query.lower() in ["exit", "quit"]:
        break
    result = qa.invoke({"query": query})
    print("📘 Răspuns:", result["result"])
