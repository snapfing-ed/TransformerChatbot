import streamlit as st
from src.generate import generate_answer

st.set_page_config(page_title="Collaborative Transformer Chatbot", layout="wide")

st.title("📚 Book-Grounded Collaborative Chatbot")
st.markdown("**Group ID:** G014 | **Subject:** Computer Science | **Standard RAG Pipeline**")

query = st.text_input("Ask a question based on your assigned books:", "What is an operating system?")

if st.button("Generate Answer"):
    if query.strip():
        with st.spinner("Retrieving evidence and generating grounded response..."):
            result = generate_answer(query)
            
        st.subheader("Answer")
        st.write(result["answer"])
        
        st.subheader("Traceable Citations & Sources")
        if result["insufficient_evidence"]:
            st.warning("System flagged insufficient evidence.")
        else:
            for src in result["sources"]:
                st.info(f"**Book ID:** {src['book_id']} | **Page:** {src['page']} | **Chunk ID:** {src['chunk_id']}")
    else:
                st.warning("Please enter a valid question.")