from langchain_community.document_loaders import DirectoryLoader, CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
from backend.utils.access_control import assign_roles

# Function to build and persist a vectorstore from Markdown and CSV files
def build_vectorstore():
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "resources" / "data"
    vectorstore_dir = base_dir / "resources" / "vector_store"
    # Load Markdown files
    md_loader = DirectoryLoader(str(data_dir), glob="**/*.md")
    md_documents = md_loader.load()

    # Load CSV files
    csv_documents = []
    for csv_file in data_dir.rglob("*.csv"):
        loader = CSVLoader(file_path=str(csv_file))
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = str(csv_file)
        csv_documents.extend(docs)

    # Merge Markdown and CSV documents
    documents = md_documents + csv_documents

    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n### ", "\n## ", "\n# ", "\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)

    # Assign role-based access
    for chunk in chunks:
        file_path = chunk.metadata.get('source', '')
        role_flags = assign_roles(file_path)
        chunk.metadata.update(role_flags)

    # Create and persist vectorstore
    embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    Chroma.from_documents(
        chunks,
        embedding,
        persist_directory=str(vectorstore_dir)
    )

    print("✅ Vectorstore created and saved to disk!")

if __name__ == "__main__":
    build_vectorstore()