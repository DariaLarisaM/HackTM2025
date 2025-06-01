from flask import Flask, request, jsonify, render_template, redirect
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import ollama
import os
import pyodbc
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import send_from_directory

UPLOAD_FOLDER = 'data'
LLM_DOCS_FOLDER = 'docs' 
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asigură-te că directorul de upload există
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Conexiune la baza de date SQL Server - actualizată pentru GestiuneDocumente
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                      'Server=localhost\\SQLEXPRESS;'
                      'Database=GestiuneDocumente;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

# LangChain
def initialize_langchain():
    loader = DirectoryLoader(LLM_DOCS_FOLDER, glob="*.pdf")
    documents = loader.load()
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory="embeddings", embedding_function=embedding_model)
    if documents:
        vectorstore.add_documents(documents)
    return vectorstore

vectorstore = initialize_langchain()
client = ollama.Client()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('acasa.html')

@app.route('/get_documents', methods=['GET'])
def get_documents():
    """Returnează lista documentelor din baza de date"""
    try:
        cursor.execute("""
            SELECT d.id_document, d.numar_document, d.data_emitere, d.descriere, 
                   td.denumire as tip_document, p.nume, p.prenume
            FROM Documente d
            LEFT JOIN TipuriDocumente td ON d.id_tip = td.id_tip
            LEFT JOIN Persoane p ON d.id_persoana = p.id_persoana
            ORDER BY d.data_emitere DESC
        """)
        documents = cursor.fetchall()
        
        doc_list = []
        for doc in documents:
            doc_list.append({
                'id': doc.id_document,
                'filename': doc.numar_document,
                'date': doc.data_emitere.strftime('%Y-%m-%d') if doc.data_emitere else '',
                'description': doc.descriere or '',
                'type': doc.tip_document or 'Document',
                'owner': f"{doc.nume} {doc.prenume}" if doc.nume and doc.prenume else 'Necunoscut'
            })
        
        return jsonify({"documents": doc_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pdf/<int:document_id>')
def serve_pdf(document_id):
    try:
        cursor.execute("SELECT numar_document FROM Documente WHERE id_document = ?", document_id)
        result = cursor.fetchone()

        if result:
            filename = result.numar_document
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        else:
            return "Documentul nu a fost găsit", 404
    except Exception as e:
        return f"Eroare la încărcarea documentului: {str(e)}", 500


@app.route('/delete_document', methods=['POST'])
def delete_document():
    """Șterge un document din baza de date și din sistemul de fișiere"""
    try:
        data = request.json
        doc_id = data.get('id')
        
        # Obține numele fișierului înainte de ștergere
        cursor.execute("SELECT numar_document FROM Documente WHERE id_document = ?", doc_id)
        result = cursor.fetchone()
        
        if result:
            filename = result.numar_document
            
            # Șterge din baza de date
            cursor.execute("DELETE FROM Documente WHERE id_document = ?", doc_id)
            conn.commit()
            
            # Șterge fișierul fizic dacă există
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Reinițializează vectorstore
            global vectorstore
            vectorstore = initialize_langchain()
            
            return jsonify({"message": "Document șters cu succes"})
        else:
            return jsonify({"error": "Documentul nu a fost găsit"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    docs = vectorstore.similarity_search(query, k=2)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = (
        f"Context:\n{context}\n\n"
        f"Întrebare: {query}\n"
        f"Te rog să răspunzi DOAR în limba română, detaliat."
    )

    try:
        answer = query_ollama(prompt)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def query_ollama(prompt: str) -> str:
    messages = [
        {"role": "system", "content": "You must respond only in Romanian."},
        {"role": "user", "content": prompt}
    ]
    response = client.chat(model="tinyllama", messages=messages)
    return response.get('message', {}).get('content', '')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Verifică dacă fișierul există deja
        counter = 1
        original_filename = filename
        while os.path.exists(filepath):
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{counter}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1
        
        file.save(filepath)

        # Salvează în baza de date
        id_tip = 1  # Default tip document
        id_persoana = 1  # Default persoană - poți modifica logic pentru utilizatori
        numar_document = filename
        data_emitere = datetime.now().date()
        descriere = f'Document încărcat din interfață - {filename}'

        try:
            cursor.execute("""
                INSERT INTO Documente (id_tip, id_persoana, numar_document, data_emitere, descriere)
                VALUES (?, ?, ?, ?, ?)
            """, id_tip, id_persoana, numar_document, data_emitere, descriere)
            conn.commit()
            
            # Reinițializează vectorstore pentru a include noul document
            global vectorstore
            vectorstore = initialize_langchain()
            
            return jsonify({"message": f"Fișier '{filename}' încărcat și salvat în baza de date."})
        except Exception as e:
            # Șterge fișierul salvat dacă inserarea în DB a eșuat
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": f"Eroare la salvarea în baza de date: {str(e)}"}), 500
    
    return jsonify({"error": "Fișier invalid sau lipsă"}), 400

if __name__ == '__main__':
    app.run(debug=True)