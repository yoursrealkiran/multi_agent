# main.py
import streamlit as st
import os
import config
from dotenv import load_dotenv
from engine import build_graph, ingest_pdfs_into_vectordb

load_dotenv()

st.set_page_config(page_title="RAG Agent", layout="wide")

@st.cache_resource
def get_agent():
    return build_graph()

def main():
    st.title("🤖 Kiran's AI Assistant")
    st.caption(f"Powered by {config.LLM_MODEL_ID}")

    with st.sidebar:
        st.header("Admin")
        if st.button("🔄 Reload Knowledge Base"):
            with st.spinner("Ingesting..."):
                count = ingest_pdfs_into_vectordb()
                st.success(f"Indexed {count} documents.")
                st.cache_resource.clear()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if question := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            agent = get_agent()
            result = None
            for output in agent.stream({"question": question}, stream_mode="values"):
                result = output
            
            answer = result["answer"] if result else "Sorry, I encountered an error."
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()