from langchain_community.document_loaders import DirectoryLoader,CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings  
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
from access_control import assign_roles

md_loader = DirectoryLoader("resources/data", glob="**/*.md")
md_documents = md_loader.load()

csv_documents = []
csv_dir = Path("resources/data")
for csv_file in csv_dir.rglob("*.csv"):
    loader = CSVLoader(file_path=str(csv_file))
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = str(csv_file)  
    csv_documents.extend(docs)

# Combine all documents
documents = md_documents + csv_documents

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n### ", "\n## ", "\n# ", "\n\n", "\n", " ", ""]

)
chunks = splitter.split_documents(documents)

for chunk in chunks:
    file_path = chunk.metadata.get('source', '')
    role_flags = assign_roles(file_path)
    chunk.metadata.update(role_flags)

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

db = Chroma.from_documents(
    chunks,
    embedding,
    persist_directory="resources/vector_store"
)

print("✅ Vectorstore created successfully!")
