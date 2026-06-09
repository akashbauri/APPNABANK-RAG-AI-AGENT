import os
from pypdf import PdfReader
from app.rag.chromadb_client import chroma_manager
from app.rag.embedder import embedder

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def build_and_seed_vector_database():
    print("--- STARTING DOCUMENT INGESTION WORKFLOW ---")
    pdf_sources = [
        {"file": "banking_kb.pdf", "collection": "banking_knowledge"},
        {"file": "stock_market_en.pdf", "collection": "stock_market_english"},
        {"file": "stock_market_hi.pdf", "collection": "stock_market_hindi"}
    ]

    base_pdf_dir = "./pdfs"
    os.makedirs(base_pdf_dir, exist_ok=True)

    for source in pdf_sources:
        path = os.path.join(base_pdf_dir, source["file"])
        coll = chroma_manager.get_or_create_collection(source["collection"])
        
        if not os.path.exists(path):
            # Create dummy structural placeholder text files to maintain a production execution baseline
            print(f"Warning: File {source['file']} not found. Provisioning automated structural placeholder records.")
            dummy_content = f"Placeholder knowledge text content for file: {source['file']}. Appna Bank AI core banking metrics standard data layer operational metadata framework documentation."
            chunks = [dummy_content]
        else:
            reader = PdfReader(path)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            chunks = chunk_text(full_text)

        # Vectorize and upsert segments
        embeddings = embedder.embed_documents(chunks)
        ids = [f"{source['file']}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": source["file"]} for _ in chunks]

        coll.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        print(f"Successfully processed and stored {len(chunks)} text chunks into collection: [{source['collection']}]")

if __name__ == "__main__":
    build_and_seed_vector_database()
