from flask import Flask, request, jsonify, render_template
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import ollama

app = Flask(__name__)

# Încarcă documente PDF din folderul docs
loader = DirectoryLoader('docs', glob="*.pdf")
documents = loader.load()

# Modelul de embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Vectorstore-ul pentru căutare similaritate
vectorstore = Chroma(persist_directory="embeddings", embedding_function=embedding_model)
vectorstore.add_documents(documents)

# Client Ollama pentru chat
client = ollama.Client()

def query_ollama(prompt: str) -> str:
    response = client.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    # Încearcă să returnezi direct conținutul mesajului
    if 'message' in response and 'content' in response['message']:
        return response['message']['content']
    elif 'content' in response:
        return response['content']
    else:
        # fallback: returnează string întreg pentru debug
        return str(response)


@app.route('/')
def home():
    return render_template('indexAI.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Caută cele mai relevante 2 documente
    docs = vectorstore.similarity_search(query, k=2)
    context = "\n\n".join([doc.page_content for doc in docs])

    # Creează prompt pentru model
    prompt = f"Context:\n{context}\n\nÎntrebare: {query}\nRăspuns detaliat:"

    try:
        answer = query_ollama(prompt)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
