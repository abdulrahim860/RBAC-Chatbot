from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

llm=OllamaLLM(model='llama3')
embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectorstore=Chroma(persist_directory="./chroma_db",embedding_function=embedding)

def get_response(query:str,role:str):
    retriever=vectorstore.as_retriever(search_kwargs={"k":4,"filter":{"role":role}})
    chain=RetrievalQA.from_chain_type(llm=llm,retriever=retriever)
    return chain.invoke({"query":query}) 