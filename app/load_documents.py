from langchain_community.document_loaders import DirectoryLoader
from langchain_huggingface import HuggingFaceEmbeddings  
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

loader = DirectoryLoader("resources/data", glob="**/*.md")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n### ", "\n## ", "\n# ", "\n\n", "\n", " ", ""]

)
chunks = splitter.split_documents(documents)

for chunk in chunks:
    file_path = chunk.metadata.get('source', '').lower()
    if "engineering" in file_path:
        role = "engineering"
    elif "hr" in file_path:
        role = "hr"
    elif "marketing" in file_path:
        role = "marketing"
    elif "finance" in file_path:
        role = "finance"
    else:
        role = "general"
    chunk.metadata["role"] = role

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

db = Chroma.from_documents(
    chunks,
    embedding,
    persist_directory="./chroma_db"
)

print("✅ Vectorstore created successfully!")
