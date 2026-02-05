# Multi-Agent RAG & Web Search System 🤖🔍

A powerful multi-agent framework designed to handle complex queries by combining **Retrieval-Augmented Generation (RAG)** with real-time **Web Search** capabilities. This system uses specialized agents to decide when to look at local documents and when to fetch live information from the internet.

# RAG capability

![Demo](images/covid_19.png)

# Web search capability

![Demo](images/f1.png)

## 🚀 Features

- **Multi-Agent Orchestration:** Uses a supervisor or autonomous agents to delegate tasks.
- **RAG Integration:** Efficiently retrieves context from your local knowledge base (PDFs, Text, etc.).
- **Real-time Web Search:** Integrates with tools (Tavily) to provide up-to-date answers.
- **Smart Routing:** Automatically determines whether a query requires local data or a web search.
- **Persistent Memory:** Remembers previous interactions in a conversation.

## 🛠️ Tech Stack

- **Framework:** [LangGraph, LangChain]
- **LLM:** [openai/gpt-oss-20b from Groq API]
- **Vector Database:** [ChromaDB]
- **Search Tool:** [Tavily API]
- **UI:** [Streamlit]

## 📋 Prerequisites

Before running the project, ensure you have:
- Python 3.9+
- API Keys for:
  - Groq 
  - Tavily 

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yoursrealkiran/multi_agent.git](https://github.com/yoursrealkiran/multi_agent.git)
   cd multi_agent