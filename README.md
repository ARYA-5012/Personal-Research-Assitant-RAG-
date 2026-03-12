# 🧠 ResearchOS - Personal Research Assistant

A powerful **Retrieval-Augmented Generation (RAG)** system that transforms your PDFs into an interactive knowledge base. Ask questions, get grounded answers, and see the evidence.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.3-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **📄 PDF Ingestion** | Upload multiple research papers or documents |
| **🔍 Semantic Search** | FAISS-powered vector similarity search |
| **🤖 Grounded Answers** | Responses backed by document evidence |
| **🔬 Evidence Inspector** | See exactly which text chunks informed each answer |
| **🌙 Premium Dark UI** | Navy/charcoal theme with clean typography |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PDF Upload    │ ──► │  Text Chunking  │ ──► │   Embeddings    │
│   (PyMuPDF)     │     │ (RecursiveChar) │     │ (HuggingFace)   │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   LLM Answer    │ ◄── │  RAG Retrieval  │ ◄── │   FAISS Store   │
│ (Gemini Flash)  │     │   (LangChain)   │     │   (Vector DB)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- An [OpenRouter](https://openrouter.ai/) API key

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/research-os.git
cd research-os

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.streamlit/secrets.toml` file:

```toml
[secrets]
OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
```

> ⚠️ **Never commit your secrets.toml file!** It's already in `.gitignore`.

### Run Locally

```bash
streamlit run app.py
# Or: python -m streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## ☁️ Deploy to Streamlit Cloud

1. **Push to GitHub** (ensure `secrets.toml` is NOT committed)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New App** → Select your repo → Choose `app.py`
4. Go to **App Settings** → **Secrets** and add:
   ```toml
   [secrets]
   OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
   ```
5. Deploy! 🎉

---

## 📁 Project Structure

```
research-os/
├── .gitignore              # Git ignore rules
├── .streamlit/
│   └── secrets.toml        # API keys (DO NOT COMMIT)
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **Orchestration** | LangChain |
| **Vector Database** | FAISS (CPU) |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` |
| **LLM** | Google Gemini Flash (via OpenRouter) |
| **PDF Parsing** | PyMuPDF |

---

## 📝 Usage

1. **Upload** your PDF documents in the sidebar
2. Click **Process Documents** to build the knowledge base
3. **Ask questions** in the chat interface
4. Review the **Evidence Inspector** panel to see source chunks

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 👨‍💻 Author

<table>
<tr>
<td align="center">
<strong>Arya Yadav</strong><br>
Bennett University<br>
<a href="mailto:aryayadav5012@gmail.com">📧 Email</a> |
<a href="https://github.com/ARYA-5012">🐙 GitHub</a>
</td>
</tr>
</table>

---


## 📄 License

This project is licensed under the MIT License.

---

<p align="center">
  Built with ❤️ using Streamlit, LangChain, and Gemini
</p>

