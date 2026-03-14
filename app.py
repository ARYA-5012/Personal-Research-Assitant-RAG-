import streamlit as st
import logging
import datetime

# Import refactored functions
from utils import get_pdf_text, get_text_chunks, get_vector_store, get_conversation_chain

# --- LOGGING SETUP ---
logger = logging.getLogger("ResearchOS")

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ResearchOS | RAG Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════
#  DESIGN SYSTEM — Observatory Gold Aesthetic
#  Typography : Cormorant Garamond · JetBrains Mono · Source Sans 3
#  Palette    : Deep navy bg, gold accent, cyan highlight
# ════════════════════════════════════════════════════════════
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;0,700;1,300;1,400&family=JetBrains+Mono:wght@400;500;700&family=Source+Sans+3:wght@300;400;600&display=swap" rel="stylesheet">

<style>
    /* ══════════════════════════════════════
       CSS VARIABLES — Design Tokens
    ══════════════════════════════════════ */
    :root {
        --bg:       #070910;
        --bg-2:     #0d1220;
        --bg-3:     #131926;
        --bg-4:     #1a2233;
        --accent:   #d4a843;
        --accent-d: rgba(212,168,67,0.14);
        --accent-g: rgba(212,168,67,0.30);
        --cyan:     #00c4d8;
        --cyan-d:   rgba(0,196,216,0.12);
        --text:     #ede8da;
        --text-2:   #8a9ab5;
        --text-3:   #3e4a5e;
        --border:   rgba(255,255,255,0.055);
        --border-2: rgba(255,255,255,0.11);
        --fd: 'Cormorant Garamond', Georgia, serif;
        --fm: 'JetBrains Mono', 'Courier New', monospace;
        --fb: 'Source Sans 3', system-ui, sans-serif;
    }

    /* ══════════════════════════════════════
       GLOBAL — Body & App Container
    ══════════════════════════════════════ */
    html, body, .stApp {
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: var(--fb) !important;
        font-weight: 300;
    }

    /* Dot-grid background */
    .stApp::before {
        content: '';
        position: fixed; inset: 0;
        background-image: radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
        background-size: 28px 28px;
        pointer-events: none;
        z-index: 0;
    }

    /* Vignette overlay */
    .stApp::after {
        content: '';
        position: fixed; inset: 0;
        background: radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.50) 100%);
        pointer-events: none;
        z-index: 0;
    }

    /* Reset Streamlit's default top padding */
    .block-container {
        padding-top: 2rem !important;
        position: relative;
        z-index: 1;
    }

    /* ══════════════════════════════════════
       TYPOGRAPHY
    ══════════════════════════════════════ */
    h1 {
        font-family: var(--fd) !important;
        font-weight: 300 !important;
        color: var(--text) !important;
        letter-spacing: -0.02em;
        line-height: 1.05 !important;
    }

    h2 {
        font-family: var(--fd) !important;
        font-weight: 300 !important;
        color: var(--text) !important;
        letter-spacing: -0.01em;
        font-size: 1.6rem !important;
        border-bottom: 1px solid var(--border) !important;
        padding-bottom: 0.6rem !important;
    }

    h3 {
        font-family: var(--fm) !important;
        font-weight: 500 !important;
        color: var(--accent) !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    p, li, span, div {
        font-family: var(--fb) !important;
        color: var(--text-2);
    }

    a { color: var(--accent) !important; }

    /* ══════════════════════════════════════
       SIDEBAR
    ══════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background-color: var(--bg-2) !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2 {
        font-family: var(--fm) !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        color: var(--accent) !important;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        border-bottom: none !important;
        padding-bottom: 0 !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: var(--border) !important;
        margin: 1rem 0 !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: var(--text-2) !important;
        font-family: var(--fb) !important;
    }

    /* Sidebar file uploader styling */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        border: 1px dashed var(--border-2) !important;
        border-radius: 4px;
        padding: 0.5rem;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
        border-color: var(--accent) !important;
    }

    /* ══════════════════════════════════════
       BUTTONS
    ══════════════════════════════════════ */
    .stButton > button {
        font-family: var(--fm) !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--bg) !important;
        background: var(--accent) !important;
        border: none !important;
        border-radius: 2px !important;
        padding: 0.55rem 1rem !important;
        transition: opacity 0.2s, transform 0.15s !important;
    }
    .stButton > button:hover {
        opacity: 0.85 !important;
        color: var(--bg) !important;
        border: none !important;
        transform: translateY(-1px);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* Download button */
    .stDownloadButton > button {
        font-family: var(--fm) !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--text-2) !important;
        background: transparent !important;
        border: 1px solid var(--border-2) !important;
        border-radius: 2px !important;
        padding: 0.55rem 1rem !important;
        transition: border-color 0.2s, color 0.2s !important;
    }
    .stDownloadButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }

    /* ══════════════════════════════════════
       CHAT MESSAGES
    ══════════════════════════════════════ */
    [data-testid="stChatMessage"] {
        background-color: var(--bg-2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 4px !important;
        padding: 1rem 1.2rem !important;
        margin-bottom: 0.6rem !important;
        transition: border-color 0.3s;
    }
    [data-testid="stChatMessage"]:hover {
        border-color: var(--border-2) !important;
    }

    /* User message accent bar */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        border-left: 2px solid var(--accent) !important;
    }

    /* Assistant message cyan bar */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 2px solid var(--cyan) !important;
    }

    [data-testid="stChatMessage"] p {
        color: var(--text) !important;
        font-family: var(--fb) !important;
        font-size: 0.92rem !important;
        line-height: 1.75 !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        border-color: var(--border-2) !important;
    }
    [data-testid="stChatInput"] textarea {
        font-family: var(--fb) !important;
        color: var(--text) !important;
        background-color: var(--bg-3) !important;
    }

    /* ══════════════════════════════════════
       EVIDENCE PANEL
    ══════════════════════════════════════ */
    .evidence-box {
        background-color: var(--bg-3) !important;
        border-left: 3px solid var(--accent) !important;
        padding: 1.1rem 1.3rem !important;
        margin-bottom: 0.8rem !important;
        border-radius: 0 3px 3px 0 !important;
        font-family: var(--fb) !important;
        font-size: 0.85rem !important;
        line-height: 1.8 !important;
        color: var(--text-2) !important;
        transition: border-color 0.3s, background-color 0.3s;
    }
    .evidence-box:hover {
        border-left-color: var(--cyan) !important;
        background-color: var(--bg-4) !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: 3px !important;
        background-color: var(--bg-2) !important;
        transition: border-color 0.3s;
    }
    [data-testid="stExpander"]:hover {
        border-color: rgba(212,168,67,0.3) !important;
    }
    [data-testid="stExpander"] summary span {
        font-family: var(--fm) !important;
        font-size: 0.72rem !important;
        color: var(--text-2) !important;
        letter-spacing: 0.04em;
    }

    /* ══════════════════════════════════════
       CODE BLOCKS (System Stats)
    ══════════════════════════════════════ */
    [data-testid="stCode"],
    pre, code {
        font-family: var(--fm) !important;
        font-size: 0.72rem !important;
        background-color: var(--bg-3) !important;
        color: var(--cyan) !important;
        border: 1px solid var(--border) !important;
        border-radius: 3px !important;
        line-height: 1.9 !important;
    }

    /* ══════════════════════════════════════
       ALERTS, INFO, SUCCESS, ERROR
    ══════════════════════════════════════ */
    [data-testid="stAlert"] {
        font-family: var(--fm) !important;
        font-size: 0.75rem !important;
        border-radius: 2px !important;
    }

    /* ══════════════════════════════════════
       SPINNER
    ══════════════════════════════════════ */
    .stSpinner > div {
        border-top-color: var(--accent) !important;
    }

    /* ══════════════════════════════════════
       AUTH SCREEN
    ══════════════════════════════════════ */
    .auth-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 70vh;
        text-align: center;
        position: relative;
        z-index: 1;
    }

    .auth-logo {
        font-family: var(--fm);
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--accent);
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
        opacity: 0;
        animation: authFadeUp 0.6s 0.1s ease forwards;
    }
    .auth-logo span { color: var(--text-3); }

    .auth-heading {
        font-family: var(--fd) !important;
        font-size: clamp(2.8rem, 5vw, 4.5rem) !important;
        font-weight: 300 !important;
        color: var(--text) !important;
        line-height: 1.05 !important;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem !important;
        opacity: 0;
        animation: authFadeUp 0.7s 0.25s ease forwards;
    }
    .auth-heading em {
        font-style: italic;
        color: var(--accent);
    }

    .auth-subtitle {
        font-family: var(--fd) !important;
        font-size: 1.1rem !important;
        font-weight: 300 !important;
        font-style: italic;
        color: var(--text-2) !important;
        margin-bottom: 2.5rem !important;
        opacity: 0;
        animation: authFadeUp 0.7s 0.4s ease forwards;
    }

    .auth-input-wrap {
        opacity: 0;
        animation: authFadeUp 0.7s 0.55s ease forwards;
        max-width: 340px;
        width: 100%;
    }

    /* Scanline on auth */
    .auth-scan {
        position: fixed; left: 0; right: 0; top: 0;
        height: 1.5px;
        background: linear-gradient(90deg, transparent 0%, var(--accent) 40%, var(--cyan) 60%, transparent 100%);
        animation: authScan 5s ease-in-out infinite;
        opacity: 0;
        z-index: 10;
    }
    @keyframes authScan {
        0%   { top: 0%; opacity: 0; }
        8%   { opacity: 0.45; }
        92%  { opacity: 0.45; }
        100% { top: 100%; opacity: 0; }
    }

    @keyframes authFadeUp {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ══════════════════════════════════════
       MAIN PANEL HEADERS
    ══════════════════════════════════════ */
    .panel-header {
        font-family: var(--fd) !important;
        font-size: 1.5rem !important;
        font-weight: 300 !important;
        color: var(--text) !important;
        padding-bottom: 0.55rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: baseline;
        gap: 0.8rem;
    }
    .panel-header .panel-num {
        font-family: var(--fm);
        font-size: 0.6rem;
        color: var(--accent);
        opacity: 0.55;
    }

    /* ══════════════════════════════════════
       EVIDENCE EMPTY STATE
    ══════════════════════════════════════ */
    .evidence-empty {
        padding: 2rem 1.2rem;
        text-align: center;
        border: 1px dashed var(--border-2);
        border-radius: 4px;
        background: var(--bg-2);
    }
    .evidence-empty p {
        font-family: var(--fm) !important;
        font-size: 0.7rem !important;
        color: var(--text-3) !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        line-height: 2 !important;
    }

    /* ══════════════════════════════════════
       SYSTEM STATS TERMINAL
    ══════════════════════════════════════ */
    .sys-terminal {
        background: var(--bg-3);
        border: 1px solid var(--border);
        border-radius: 4px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    .sys-terminal-bar {
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 6px 10px;
        background: var(--bg-4);
        border-bottom: 1px solid var(--border);
    }
    .sys-dot {
        width: 8px; height: 8px; border-radius: 50%;
    }
    .sys-dot.r { background: #e5534b; }
    .sys-dot.y { background: #e3a53a; }
    .sys-dot.g { background: #3fb950; }
    .sys-terminal-title {
        font-family: var(--fm);
        font-size: 0.55rem;
        color: var(--text-3);
        margin-left: auto;
        letter-spacing: 0.04em;
    }
    .sys-terminal-body {
        padding: 0.8rem 1rem;
        font-family: var(--fm);
        font-size: 0.68rem;
        line-height: 1.9;
        color: var(--text-2);
    }
    .sys-terminal-body .sys-key {
        color: var(--accent);
    }
    .sys-terminal-body .sys-val {
        color: var(--cyan);
    }

    /* ══════════════════════════════════════
       CAPTION / FOOTNOTE
    ══════════════════════════════════════ */
    [data-testid="stCaptionContainer"] {
        font-family: var(--fm) !important;
        font-size: 0.6rem !important;
        color: var(--text-3) !important;
        letter-spacing: 0.04em;
    }

    /* ══════════════════════════════════════
       SCROLLBAR
    ══════════════════════════════════════ */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--bg-4);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(212,168,67,0.4);
    }

    /* ══════════════════════════════════════
       TEXT INPUT FIELDS
    ══════════════════════════════════════ */
    [data-testid="stTextInput"] input {
        font-family: var(--fm) !important;
        font-size: 0.85rem !important;
        background-color: var(--bg-3) !important;
        color: var(--text) !important;
        border: 1px solid var(--border-2) !important;
        border-radius: 2px !important;
        transition: border-color 0.3s !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent-d) !important;
    }

    /* ══════════════════════════════════════
       HIDE STREAMLIT BRANDING
    ══════════════════════════════════════ */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  AUTHENTICATION — Cinematic Splash Screen
# ════════════════════════════════════════════════════════════
def check_password():
    """Returns `True` if the user entered the correct password."""

    def password_entered():
        if st.session_state["password"] == st.secrets["secrets"]["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown('<div class="auth-scan"></div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="auth-logo">RESEARCH<span> // </span>OS</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="auth-heading">Welcome to Research<em>OS</em></h1>', unsafe_allow_html=True)
        st.markdown('<p class="auth-subtitle">Enter your security passkey to access the intelligence hub.</p>', unsafe_allow_html=True)
        st.markdown('<div class="auth-input-wrap">', unsafe_allow_html=True)
        st.text_input("Passkey", type="password", on_change=password_entered, key="password", label_visibility="collapsed")
        st.markdown('</div></div>', unsafe_allow_html=True)
        return False
    elif not st.session_state["password_correct"]:
        st.markdown('<div class="auth-scan"></div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="auth-logo">RESEARCH<span> // </span>OS</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="auth-heading">Welcome to Research<em>OS</em></h1>', unsafe_allow_html=True)
        st.error("Incorrect passkey. Try again.")
        st.markdown('<div class="auth-input-wrap">', unsafe_allow_html=True)
        st.text_input("Passkey", type="password", on_change=password_entered, key="password", label_visibility="collapsed")
        st.markdown('</div></div>', unsafe_allow_html=True)
        return False
    return True

# ════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════
def get_chat_export_text():
    """Creates a downloadable markdown string of the chat history."""
    if "messages" not in st.session_state or not st.session_state.messages:
        return "No chat history available."
    
    export_str = "# ResearchOS — Chat Export\n"
    export_str += f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n"
    
    for msg in st.session_state.messages:
        role = "**User**" if msg["role"] == "user" else "**ResearchOS**"
        export_str += f"### {role}\n{msg['content']}\n\n---\n\n"
        
    return export_str

# ════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ════════════════════════════════════════════════════════════
def main():
    if not check_password():
        st.stop()
        
    logger.info("Main application accessed (Auth successful).")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "last_source_docs" not in st.session_state:
        st.session_state.last_source_docs = []
    if "doc_processed" not in st.session_state:
        st.session_state.doc_processed = False

    # ──────────────────────────────────
    # SIDEBAR
    # ──────────────────────────────────
    with st.sidebar:
        st.header("📂 DOCUMENT HUB")
        pdf_docs = st.file_uploader(
            "Upload Research PDFs", accept_multiple_files=True, type=['pdf'],
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚡ PROCESS", use_container_width=True):
                if not pdf_docs:
                    st.error("Upload a PDF first.")
                else:
                    with st.spinner("Ingesting…"):
                        try:
                            raw_text = get_pdf_text(pdf_docs)
                            text_chunks = get_text_chunks(raw_text)
                            vectorstore = get_vector_store(text_chunks)
                            st.session_state.conversation = get_conversation_chain(vectorstore)
                            st.session_state.doc_processed = True
                            logger.info(f"Processed {len(text_chunks)} chunks from {len(pdf_docs)} docs.")
                            st.success(f"✓ {len(text_chunks)} chunks indexed.")
                        except Exception as e:
                            logger.error(f"Error processing documents: {str(e)}")
                            st.error(f"Error: {str(e)}")
                            
        with col2:
            if st.button("🗑️ CLEAR", use_container_width=True):
                st.session_state.conversation = None
                st.session_state.doc_processed = False
                st.session_state.last_source_docs = []
                st.rerun()
                
        st.markdown("---")
        st.header("⚙️ SESSION")
        
        if st.button("🧹 CLEAR CHAT", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
             
        chat_data = get_chat_export_text()
        st.download_button(
            label="💾 EXPORT CHAT",
            data=chat_data,
            file_name=f"researchos_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True
        )
        
        st.markdown("---")

        # System Stats — Mini Terminal
        if st.session_state.doc_processed:
            st.markdown("""
            <div class="sys-terminal">
                <div class="sys-terminal-bar">
                    <div class="sys-dot r"></div>
                    <div class="sys-dot y"></div>
                    <div class="sys-dot g"></div>
                    <div class="sys-terminal-title">system — live</div>
                </div>
                <div class="sys-terminal-body">
                    <span class="sys-key">status</span>&nbsp;&nbsp;<span class="sys-val">● online</span><br>
                    <span class="sys-key">engine</span>&nbsp;&nbsp;<span class="sys-val">FAISS (cpu)</span><br>
                    <span class="sys-key">embed </span>&nbsp;&nbsp;<span class="sys-val">MiniLM-L6-v2</span><br>
                    <span class="sys-key">model </span>&nbsp;&nbsp;<span class="sys-val">llama-3.1-8b</span><br>
                    <span class="sys-key">provider</span>&nbsp;<span class="sys-val">Groq LPU</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="sys-terminal">
                <div class="sys-terminal-bar">
                    <div class="sys-dot r"></div>
                    <div class="sys-dot y"></div>
                    <div class="sys-dot g"></div>
                    <div class="sys-terminal-title">system — idle</div>
                </div>
                <div class="sys-terminal-body">
                    <span class="sys-key">status</span>&nbsp;&nbsp;<span style="color: var(--text-3);">○ waiting for documents</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ──────────────────────────────────
    # MAIN PANELS
    # ──────────────────────────────────
    col_chat, col_evidence = st.columns([0.65, 0.35], gap="large")

    # ─── CENTER: Conversational Canvas ───
    with col_chat:
        st.markdown("""
        <div class="panel-header">
            <span class="panel-num">01 —</span> Research Assistant
        </div>
        """, unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a question about your documents…"):
            if not st.session_state.conversation:
                st.error("Process documents first.")
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Retrieving & synthesizing…"):
                        logger.info(f"Query: {prompt[:50]}…")
                        response = st.session_state.conversation({"question": prompt})
                        answer = response['answer']
                        source_docs = response['source_documents']
                        st.session_state.last_source_docs = source_docs
                        logger.info(f"Retrieved {len(source_docs)} fragments.")
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.rerun()

    # ─── RIGHT: Evidence Inspector ───
    with col_evidence:
        st.markdown("""
        <div class="panel-header">
            <span class="panel-num">02 —</span> Evidence Inspector
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.last_source_docs:
            num_docs = len(st.session_state.last_source_docs)
            st.markdown(f"""
            <div style="font-family: var(--fm); font-size: 0.68rem; color: var(--cyan); 
                        letter-spacing: 0.06em; margin-bottom: 1rem; text-transform: uppercase;">
                ✓ {num_docs} fragment{'s' if num_docs != 1 else ''} retrieved
            </div>
            """, unsafe_allow_html=True)
            
            for i, doc in enumerate(st.session_state.last_source_docs):
                with st.expander(f"// Fragment #{i+1}", expanded=(i == 0)):
                    st.markdown(
                        f"<div class='evidence-box'>{doc.page_content.strip()}</div>",
                        unsafe_allow_html=True
                    )
                    st.caption(f"hash: {hash(doc.page_content)}")
        else:
            st.markdown("""
            <div class="evidence-empty">
                <p>Awaiting query…</p>
                <p>Top-k retrieved chunks will<br>appear here to ground the response.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
