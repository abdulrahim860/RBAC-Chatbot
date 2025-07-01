# load_vectorstore.py

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        _vectorstore = Chroma(
            persist_directory="resources/vector_store",
            embedding_function=embedding
        )
    return _vectorstore
