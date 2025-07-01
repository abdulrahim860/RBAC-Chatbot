from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="deepseek/deepseek-r1-0528:free")

embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
vectorstore = Chroma(persist_directory="resources/vector_store", embedding_function=embedding)

system_template = """
You are an AI assistant for FinSolve Technologies, a leading FinTech company. Your job is to assist internal employees by answering questions using secure, role-specific data from company documents.

You are currently responding to a user whose role is: {role}

Follow these guidelines:
1. Answer questions based ONLY on the context provided below
2. If the information isn't in the retrieved context, say "I don't have that information" - DO NOT make up answers
3. Provide a clear, concise, and accurate response. Use bullet points, headers, or tables.Justify and format the content properly.Start the next point on next line and keep 2 line as space between the paragraph
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
9. If the document is technical (Markdown, CSV):  
   - Parse code blocks and tables accurately.  
   - Display data rows cleanly and clearly.

Context:
{context}
"""

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}")
])


def get_response(query: str, role: str, chat_history: list[dict] = [], use_history: bool = True):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5, "filter": {f"role_{role}": True}})
    prompt_with_role = prompt.partial(role=role)

    # Format manual chat history
    formatted_history = ""
    if use_history and chat_history:
        for turn in chat_history[-3:]:
            formatted_history += f"User: {turn['user']}\nAI: {turn['ai']}\n"

    # Combine history + question
    full_input = f"{formatted_history.strip()}\n\n{query}".strip()

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt_with_role},
        return_source_documents=True
    )

    full_input = f"{formatted_history.strip()}\n\n{query}".strip()
    response = chain.invoke({"query": full_input})


    answer = response["result"].strip()
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

    print("\n🔍 Retrieved Context:")
    for i, doc in enumerate(sources, 1):
        print(f"\n--- Document {i} ---\n{doc.page_content}")

    return {
        "answer": answer,
        "sources": sorted(set(source_names))
    }