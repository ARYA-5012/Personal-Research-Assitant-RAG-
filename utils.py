import fitz  # PyMuPDF
import streamlit as st
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# Configure standard Python logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ResearchOS")

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
    """Split text into manageable chunks with optimized size for focus."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,   # Slightly smaller chunks for more precise retrieval
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
    """Initialize the RAG chain with a strict grounding prompt."""
    
    # Groq Config
    llm = ChatGroq(
        api_key=st.secrets["secrets"]["GROQ_API_KEY"],
        model_name="llama-3.1-8b-instant",
        temperature=0.1 # Lowered temperature for stricter grounding
    )
    
    logger.info("LLM initialized with strict grounding parameters.")

    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True,
        output_key='answer'
    )

    # Custom prompt to strictly ground the model
    prompt_template = """You are a helpful Research Assistant. Use the following pieces of context to answer the user's question. 
If you don't know the answer or the answer cannot be found in the provided context, just say: "I cannot answer this based on the provided documents. Please ask something covered by the uploaded files." Do NOT try to make up an answer.

Context: 
{context}

Question: 
{question}

Answer strictly based on the context provided above:"""

    QA_PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}), # Increased k slightly
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={'prompt': QA_PROMPT},
        verbose=True
    )
    return conversation_chain
