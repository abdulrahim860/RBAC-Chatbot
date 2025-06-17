from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

llm=Ollama(model='llama3')
embedding=HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
vectorstore=Chroma(persitant_directory="./chroma_db",embedding_function=embedding)

def get_response(query:str,role:str):
    retriever=vectorstore.as_retreiver(search_kwargs={"k":3,"filter":{"role":role}})
    chain=RetrievalQA.from_chain_type(llm=llm,retriever=retriever)
    return chain.run(query)