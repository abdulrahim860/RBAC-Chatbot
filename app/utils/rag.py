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

Follow these rules carefully:

### 🔒 Access Control
1. Only provide answers based on documents that are **authorized for the user's role**.
2. If the user asks about data from departments outside their role (e.g., HR asking about Finance), respond with:
   > "You are not authorized to access that information."

3. If the data is not available in the provided context, say:
   > "I don't have that information based on the current documents."

---

### 📄 Answering Instructions
4. Use **only the context provided below** — do not make up or hallucinate information.
5. Keep the answer **clear**, **professional**, and **concise**.
6. Include **document references** in square brackets, e.g., `[engineering_master_doc.md]`.

---

### 📊 Context Interpretation
7. For **Markdown documents**:
   - Understand headers, bullet points, and code blocks.
   - Maintain structure and hierarchy when useful.

8. For **CSV data**:
   - Treat the data as a table with rows and columns.
   - Format numbers properly (e.g., currency like `$1200.50`, percentages like `12.3%`).
   - Provide direct values when asked for specific numbers.

---

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