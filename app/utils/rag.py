from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

llm=OllamaLLM(model='llama3')
embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectorstore=Chroma(persist_directory="resources/vector_store",embedding_function=embedding)

template = """
You are an AI assistant for FinSolve Technologies, a leading FinTech company. Your job is to assist internal employees by answering questions using secure, role-specific data from company documents.

You are currently responding to a user whose role is: **{role}**

Follow these guidelines:
1. Answer questions based ONLY on the context provided below
2. If the information isn't in the context, say "I don't have that information" - DO NOT make up answers
3. Keep responses professional, clear, and concise
4. Include citations to the source documents when appropriate using [Document Title]
5. Focus on providing factual information relevant to the user's role
6. Consider the conversation history for context
7. For CSV data, interpret the data as structured tables with headers and rows
   - Present tabular data in a readable format
   - If asked for specific data points, extract them precisely
   - For financial data, format numbers appropriately (e.g., currency symbols, decimal places)
8. For Markdown data:
   - Properly interpret headers, lists, tables, and other formatting
   - Preserve the hierarchical structure when relevant to the query
   - Recognize and properly handle code blocks or technical content

### 📌 Context
Below is the relevant information retrieved for this query. Use it strictly.

{context}

---

### ❓ Question
{question}

---

### 💬 Final Answer:
"""

prompt = PromptTemplate.from_template(template)

def get_response(query:str,role:str):
    retriever=vectorstore.as_retriever(search_kwargs={"k":4,"filter":{"role":role}})
    
    filled_prompt = template.replace("{role}", role.upper())
    prompt = PromptTemplate.from_template(filled_prompt)

    chain=RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff",
        chain_type_kwargs={"prompt":prompt}
    )
    response = chain.invoke({
    "query": query
})

    print("\n🔍 Retrieved Context:")
    source_docs = response.get("source_documents", [])
    if not source_docs:
        print("🚫 No documents retrieved!")
    else:
        for i, doc in enumerate(source_docs, 1):
            print(f"\n--- Document {i} ---\n{doc.page_content}")
    return response['result'].replace('\n', ' ').strip() 