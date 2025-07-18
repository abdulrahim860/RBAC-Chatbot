from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from chromadb.config import Settings as ClientSettings
from pathlib import Path

# Module-level variable to cache the vectorstore instance
_vectorstore = None

# Function to load (and cache) the vectorstore from disk
def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        base_dir = Path(__file__).resolve().parent.parent
        vectorstore_dir = base_dir / "resources" / "vector_store"
        _vectorstore = Chroma(
            persist_directory=str(vectorstore_dir),
            embedding_function=embedding,
            collection_name="default",  
            client_settings=ClientSettings(anonymized_telemetry=False)
        )
        collection = _vectorstore._client.get_collection("default")
        print("🔍 Total documents in vectorstore:", collection.count())
    return _vectorstore