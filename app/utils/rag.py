from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="deepseek/deepseek-r1-0528:free")

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectorstore = Chroma(persist_directory="resources/vector_store", embedding_function=embedding)

system_template = """
You are an AI assistant for FinSolve Technologies, a leading FinTech company. Your job is to assist internal employees by answering questions using secure, role-specific data from company documents.

You are currently responding to a user whose role is: {role}

Follow these guidelines:
1. Answer questions based ONLY on the context provided below
2. If the information isn't in the retrieved context, say "I don't have that information" - DO NOT make up answers
3. Keep responses professional, clear, and concise
4. Dont expand you answer,unless asked by user
5. Focus on providing factual information relevant to the user's role
6. Consider the conversation history for context
7. For CSV data, interpret the data as structured tables with headers and rows
   - Present tabular data in a readable format
   - If asked for specific data points, extract them precisely
   - If a specific employee is requested, show **only that row** in a clean readable table.
   - For financial data, format numbers appropriately (e.g., currency symbols(₹), decimal places)
8. For Markdown data:
   - Properly interpret headers, lists, tables, and other formatting
   - Preserve the hierarchical structure when relevant to the query
   - Recognize and properly handle code blocks or technical content

Context:
{context}
"""

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}")
])

def get_response(query: str, role: str):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5, "filter": {f"role_{role}": True}})

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff",
        chain_type_kwargs={
            "prompt": prompt.partial(role=role)  
        }
    )

    response = chain.invoke({"query": query})

    answer = response["result"].replace("\n", " ").strip()
    sources = response.get("source_documents", [])

    source_names = []
    for doc in sources:
       source_path = doc.metadata.get("source", None)
       if source_path:
          path_obj = Path(source_path)
          if len(path_obj.parts) >= 2:
               folder = path_obj.parts[-2]
               filename = path_obj.name
               source_names.append(f"{folder}/{filename}")
          else:
              source_names.append(path_obj.name)


    if source_names:
       answer += "\n\n📄 **Sources:** " + ", ".join(set(source_names))

    print("\n🔍 Retrieved Context:")
    for i, doc in enumerate(response.get("source_documents", []), 1):
        print(f"\n--- Document {i} ---\n{doc.page_content}")
    return answer
