import streamlit as st

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import fitz  # PyMuPDF
import os

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
</style>
""", unsafe_allow_html=True)

# --- BACKEND FUNCTIONS ---

@st.cache_resource
def get_embeddings_model():
    """Load HuggingFace embeddings (cached)."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_pdf_text(pdf_docs):
    """Extract text from PDF documents using PyMuPDF (fitz) for better quality."""
    text = ""
    for pdf in pdf_docs:
        doc = fitz.open(stream=pdf.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
    return text

def get_text_chunks(text):
    """Split text into manageable chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    """Create FAISS vector store."""
    embeddings = get_embeddings_model()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    """Initialize the RAG chain with Gemini via OpenRouter."""
    
    # OpenRouter Config
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.secrets["secrets"]["OPENROUTER_API_KEY"],
        model="google/gemini-3-flash-preview",
        temperature=0.3
    )

    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True,
        output_key='answer' # Critical for ConversationalRetrievalChain
    )

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        memory=memory,
        return_source_documents=True, # We need this for the "Evidence Panel"
        verbose=True
    )
    return conversation_chain

# --- UI LAYOUT ---

def main():
    # Sidebar: Document Hub
    with st.sidebar:
        st.header("📂 Document Hub")
        pdf_docs = st.file_uploader(
            "Upload Research PDFs", accept_multiple_files=True, type=['pdf']
        )
        
        if st.button("⚡ Process Documents"):
            if not pdf_docs:
                st.error("Please upload at least one PDF.")
            else:
                with st.spinner("Processing... (Ingest -> Chunk -> Embed)"):
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
                        st.success(f"Processed {len(text_chunks)} chunks from {len(pdf_docs)} documents.")
                    except Exception as e:
                        st.error(f"Error processing documents: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 📊 System Stats")
        if "doc_processed" in st.session_state and st.session_state.doc_processed:
            st.code("Status: Ready\nBackend: FAISS (CPU)\nModel: Gemini 1.5 Flash")
        else:
            st.code("Status: Idle")

    # Main Layout: 3-Pane Concept (Sidebar is 1, Center+Right is 2&3)
    # We use columns for Chat vs Evidence
    
    col_chat, col_evidence = st.columns([0.65, 0.35], gap="large")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    
    if "last_source_docs" not in st.session_state:
        st.session_state.last_source_docs = []

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
                        response = st.session_state.conversation({"question": prompt})
                        answer = response['answer']
                        source_docs = response['source_documents']
                        
                        # Store sources for Evidence Panel
                        st.session_state.last_source_docs = source_docs
                        
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.rerun() # Rerun to update Evidence Panel immediately

    # --- RIGHT PANEL: EVIDENCE INSPECTOR ---
    with col_evidence:
        st.markdown("## 🔍 Evidence Inspector")
        
        if st.session_state.last_source_docs:
            st.info(f"Retrieved {len(st.session_state.last_source_docs)} relevant fragments")
            
            for i, doc in enumerate(st.session_state.last_source_docs):
                with st.expander(f"Fragment #{i+1} (Similarity Req.)", expanded=True):
                    # We don't have true similarity scores from standard retrieved docs in this chain unless customized, 
                    # but we show the content.
                    st.markdown(f"<div class='evidence-box'>{doc.page_content[:400]}...</div>", unsafe_allow_html=True)
                    st.caption(f"Source: Chunk ID {hash(doc.page_content)}")
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
