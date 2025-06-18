from langchain.document_loaders import DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

loader=DirectoryLoader("resources/data",glob="**/*.md")
documents=loader.load()

splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
chunks=splitter.split_documents(documents)

embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db=Chroma.from_documents(documents=chunks,embedding=embedding,persist_directory="./chroma_db")

db.persist()
print("vectorstore created and persisted successfully.")