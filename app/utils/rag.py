from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

llm=OllamaLLM(model='llama3')
embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectorstore=Chroma(persist_directory="./chroma_db",embedding_function=embedding)

prompt=PromptTemplate(
    input_variables=["context","question"],
    template=(
        "use ONLY the following context to answer the question."
        "Do not use prior knowledge or make up answers.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )
)
def get_response(query:str,role:str):
    retriever=vectorstore.as_retriever(search_kwargs={"k":4,"filter":{"role":role}})
    chain=RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt":prompt}
    )
    response = chain.invoke({"query": query})
    return response['result'].replace('\n', ' ').strip() 