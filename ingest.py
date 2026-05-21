import os
import glob
from tqdm import tqdm
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader # Added Word Loader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# 1. Load Environment Variables
load_dotenv()

# --- CONFIGURATION ---
DATA_PATH = "./ice_library"
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

def run_ingestion():
    # Initialize Pinecone and Embeddings
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP
    )

    # 2. Get list of all PDFs AND Word Documents
    # This looks for .pdf, .docx, and .doc
    files = []
    for ext in ("*.pdf", "*.docx", "*.doc"):
        files.extend(glob.glob(os.path.join(DATA_PATH, ext)))
    
    if not files:
        print(f"❌ No supported documents found in {DATA_PATH}.")
        return

    print(f"🚀 Found {len(files)} documents. Starting batch ingestion...")

    # 3. Process documents
    for file_path in tqdm(files, desc="Ingesting Library"):
        try:
            # --- LOADER SELECTION LOGIC ---
            if file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith(".docx") or file_path.endswith(".doc"):
                loader = Docx2txtLoader(file_path)
            else:
                continue # Skip unsupported types

            raw_docs = loader.load()
            
            # Split and Upload
            chunks = text_splitter.split_documents(raw_docs)
            
            PineconeVectorStore.from_documents(
                chunks,
                embeddings,
                index_name=INDEX_NAME
            )
            
        except Exception as e:
            print(f"⚠️ Error processing {os.path.basename(file_path)}: {e}")
            continue

    print("\n✅ Ingestion Complete! Your Vault now includes Word and PDF files.")

if __name__ == "__main__":
    run_ingestion()