# engine.py
import os
import config
from typing import List
from typing_extensions import TypedDict

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_tavily import TavilySearch
from langchain_core.documents import Document
from langgraph.graph import START, END, StateGraph

class GraphState(TypedDict):
    question: str
    documents: List[Document]
    sender: str
    answer: str

def ingest_pdfs_into_vectordb():
    documents = []
    if not os.path.exists(config.KNOWLEDGE_BASE_DIR):
        return 0
    
    for file_name in os.listdir(config.KNOWLEDGE_BASE_DIR):
        if file_name.lower().endswith(".pdf"):
            file_path = os.path.join(config.KNOWLEDGE_BASE_DIR, file_name)
            try:
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            except Exception: continue
    
    if not documents: return 0
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE, 
        chunk_overlap=config.CHUNK_OVERLAP
    )
    texts = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
    vectorstore = Chroma.from_documents(
        texts, embeddings, persist_directory=config.PERSIST_DIRECTORY
    )
    vectorstore.persist()
    return len(documents)

def create_retriever():
    if not os.path.exists(config.PERSIST_DIRECTORY): return None
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
    vectorstore = Chroma(persist_directory=config.PERSIST_DIRECTORY, embedding_function=embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 1})

def router_node(state: GraphState) -> str:
    llm = ChatGroq(temperature=0, model_name=config.LLM_MODEL_ID)
    prompt = f"Route the question: '{state['question']}'. Categories: 'vectorstore' or 'web_search'. Respond with one word."
    response = llm.invoke(prompt)
    return "web_search" if "web_search" in response.content.lower() else "vectorstore"

def retrieve_node(state: GraphState) -> GraphState:
    retriever = create_retriever()
    docs = retriever.invoke(state["question"]) if retriever else []
    return {"documents": docs, "sender": "retrieve_node"}

def web_search_node(state: GraphState) -> GraphState:
    tavily = TavilySearch(max_results=config.MAX_SEARCH_RESULTS, include_domains=config.SEARCH_DOMAINS)
    results = tavily.invoke(state["question"])
    scraped = []
    urls = [r.get("url") for r in results.get("results", []) if r.get("url")]
    for url in urls:
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            for d in docs: d.metadata["source"] = url
            scraped.extend(docs)
        except: continue
    return {"documents": scraped, "sender": "web_search_node"}

def generate_node(state: GraphState) -> GraphState:
    context = "\n\n".join(doc.page_content for doc in state["documents"])
    prompt = f"Context: {context}\n\nQuestion: {state['question']}\n\nAnswer:"
    llm = ChatGroq(temperature=0, model_name=config.LLM_MODEL_ID)
    return {"answer": llm.invoke(prompt).content, "sender": "generate_node"}

def build_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate", generate_node)
    workflow.add_conditional_edges(START, router_node, {"vectorstore": "retrieve", "web_search": "web_search"})
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()