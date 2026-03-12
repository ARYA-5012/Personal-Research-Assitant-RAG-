import streamlit as st
import logging
import datetime

# Import refactored functions
from utils import get_pdf_text, get_text_chunks, get_vector_store, get_conversation_chain

# --- LOGGING SETUP ---
logger = logging.getLogger("ResearchOS")

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ResearchOS | Gemini RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR "PREMIUM" LOOK ---
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #0e1117; /* Dark Navy/Charcoal */
        color: #f0f2f6;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #58a6ff; /* Teal/Blue Accent */
        font-family: 'Inter', sans-serif;
    }
    
    /* Document Cards */
    .doc-card {
        background-color: #21262d;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
    
    /* Evidence/Context Box */
    .evidence-box {
        background-color: #1f242b;
        border-left: 3px solid #d29922; /* Warning Orange/Gold */
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    
    /* Chat Bubbles (Streamlit handles these mostly, but we can tweak) */
    .stChatMessage {
        border: 1px solid #30363d;
        background-color: #161b22;
    }
    
    /* Center Authentication Container */
    .auth-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 60vh;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION ---
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        if st.session_state["password"] == st.secrets["secrets"]["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        st.markdown("<h1>🔒 ResearchOS Hub</h1>", unsafe_allow_html=True)
        st.markdown("<p>Please enter the security passkey to continue.</p>", unsafe_allow_html=True)
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.markdown("</div>", unsafe_allow_html=True)
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        st.error("😕 Password incorrect")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

# --- HELPER FUNCTIONS ---
def get_chat_export_text():
    """Creates a downloadable markdown string of the chat history."""
    if "messages" not in st.session_state or not st.session_state.messages:
        return "No chat history available."
    
    export_str = "# ResearchOS Chat History\n"
    export_str += f"Date Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for msg in st.session_state.messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        export_str += f"### {role}\n{msg['content']}\n\n---\n\n"
        
    return export_str

# --- UI LAYOUT ---

def main():
    if not check_password():
        st.stop()
        
    logger.info("Main application accessed (Auth successful).")

    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    
    if "last_source_docs" not in st.session_state:
        st.session_state.last_source_docs = []
        
    if "doc_processed" not in st.session_state:
        st.session_state.doc_processed = False

    # Sidebar: Document Hub
    with st.sidebar:
        st.header("📂 Document Hub")
        pdf_docs = st.file_uploader(
            "Upload Research PDFs", accept_multiple_files=True, type=['pdf']
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚡ Process DB", use_container_width=True):
                if not pdf_docs:
                    st.error("Please upload a PDF.")
                else:
                    with st.spinner("Processing..."):
                        try:
                            # 1. Get Text
                            raw_text = get_pdf_text(pdf_docs)
                            # 2. Chunk Text
                            text_chunks = get_text_chunks(raw_text)
                            # 3. Vector Store
                            vectorstore = get_vector_store(text_chunks)
                            # 4. Chain
                            st.session_state.conversation = get_conversation_chain(vectorstore)
                            st.session_state.doc_processed = True
                            logger.info(f"Processed {len(text_chunks)} chunks from {len(pdf_docs)} docs.")
                            st.success(f"Processed {len(text_chunks)} chunks.")
                        except Exception as e:
                            logger.error(f"Error processing documents: {str(e)}")
                            st.error(f"Error: {str(e)}")
                            
        with col2:
            if st.button("🗑️ Clear DB", use_container_width=True):
                st.session_state.conversation = None
                st.session_state.doc_processed = False
                st.session_state.last_source_docs = []
                st.success("Database cleared.")
                st.rerun()
                
        st.markdown("---")
        st.header("⚙️ Session Controls")
        
        if st.button("🧼 Clear Chat History", use_container_width=True):
             st.session_state.messages = []
             st.success("Chat history cleared.")
             st.rerun()
             
        # Export button requires chat history
        chat_data = get_chat_export_text()
        st.download_button(
             label="💾 Export Chat (MD)",
             data=chat_data,
             file_name=f"researchos_export_{datetime.datetime.now().strftime('%Y%m%d%H%M')}.md",
             mime="text/markdown",
             use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("### 📊 System Stats")
        if st.session_state.doc_processed:
            st.code("Status: Ready\nBackend: FAISS\nEmbedding: MiniLM-L6\nModel: Gemini 1.5 Flash")
        else:
            st.code("Status: Idle")

    # Main Layout: 3-Pane Concept (Sidebar is 1, Center+Right is 2&3)
    col_chat, col_evidence = st.columns([0.65, 0.35], gap="large")

    # --- CENTER PANEL: CONVERSATIONAL CANVAS ---
    with col_chat:
        st.markdown("## 💬 Research Assistant")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Ask a question about your documents..."):
            if not st.session_state.conversation:
                st.error("Please process documents first!")
            else:
                # Add user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Generate Answer
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing documents..."):
                        logger.info(f"User query: {prompt[:50]}...")
                        response = st.session_state.conversation({"question": prompt})
                        answer = response['answer']
                        source_docs = response['source_documents']
                        
                        # Store sources for Evidence Panel
                        st.session_state.last_source_docs = source_docs
                        logger.info(f"Retrieved {len(source_docs)} source documents. Answer length: {len(answer)}")
                        
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.rerun() # Rerun to update Evidence Panel immediately

    # --- RIGHT PANEL: EVIDENCE INSPECTOR ---
    with col_evidence:
        st.markdown("## 🔍 Evidence Inspector")
        
        if st.session_state.last_source_docs:
            st.info(f"Retrieved {len(st.session_state.last_source_docs)} relevant fragments")
            
            for i, doc in enumerate(st.session_state.last_source_docs):
                with st.expander(f"Fragment #{i+1}", expanded=True):
                    # Render the chunk body and the page location if available
                    st.markdown(f"<div class='evidence-box'>{doc.page_content.strip()}</div>", unsafe_allow_html=True)
                    st.caption(f"Chunk Hash ID: {hash(doc.page_content)}")
        else:
            st.markdown("*Context will focus here after your first query.*")
            st.markdown("""
            <div style='opacity: 0.5; font-size: 0.9em;'>
            Waiting for query...
            <br><br>
            Top-k retrieved chunks will appear here to ground the LLM's response.
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
