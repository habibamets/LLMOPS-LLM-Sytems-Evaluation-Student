import os
import requests
import pypdf
import sys

def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Erreur : Le fichier {pdf_path} n'existe pas.")
        sys.exit(1)
        
    text = ""
    with pypdf.PdfReader(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    
    return text.strip()

def chunk_text(text, chunk_size=1000, overlap=100):
    """Découpe un texte long en chunks simples pour Meilisearch/TEI."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def ingest_to_rag(file_path):
    print(f"Extraction du texte de {file_path}...")
    full_text = extract_text_from_pdf(file_path)
    
    if not full_text:
        print("Erreur : Impossible d'extraire le texte du PDF.")
        sys.exit(1)
        
    # On découpe le texte pour éviter d'envoyer un document géant à l'API d'ingestion
    chunks = chunk_text(full_text)[:32]  # On limite à 32 chunks pour l'évaluation
    print(f"{len(chunks)} fragments générés. Envoi au backend...")
    
    documents = []
    base_name = os.path.basename(file_path)
    for i, chunk in enumerate(chunks):
        documents.append({
            "id": f"{base_name.replace('.pdf', '')}_chunk_{i}",
            "text": chunk,
            "metadata": {"source": base_name, "chunk": i}
        })
    
    # Appel de l'API RAGOPS tournant dans le réseau Docker
    url = "http://backend:8000/ingest"
    try:
        response = requests.post(url, json=documents, timeout=60)
        if response.status_code == 200:
            print(f"Succès ! {len(documents)} documents ingérés dans le RAG.")
        else:
            print(f"Erreur lors de l'ingestion ({response.status_code}): {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Erreur de connexion RAGOPS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Le chemin correspond au montage fait dans docker-compose.yml
    DATA_FILE = "/app/data/linear_algebra.pdf"
    print("="*50)
    print("PREPARATION DU RAG POUR L'EVALUATION")
    print("="*50)
    ingest_to_rag(DATA_FILE)
