# 🔷 dentsu_smart_buddy

An enterprise-grade **AI-powered research assistant** built with **Streamlit, LangChain, and Azure OpenAI**.
It enables intelligent conversations, real-time web research, document analysis, image understanding, and productivity support in a single platform.

---

## ✨ Overview

**dentsu_smart_buddy** is designed to:

* Provide accurate, structured answers using AI
* Perform real-time web research
* Analyze uploaded documents and images
* Maintain conversation history with memory
* Deliver a premium, modern user experience
* Support dentsu teams with faster research, smarter insights, and improved productivity

---

## 🚀 Features

### 💬 Conversational AI

* Chat-based interface using Streamlit
* Multi-turn conversations with context
* Clean markdown-formatted responses

### 🌐 Web Search Integration

* Uses Tavily API for real-time data
* Automatically detects when fresh information is needed
* Displays sources separately

### 📄 Document Analysis

Supports:

* PDF
* DOCX
* TXT

Extracts and injects document context into responses

### 🖼️ Image Analysis

* Upload images such as PNG, JPG, and JPEG
* AI analyzes and describes visual content
* Supports multimodal queries

### 🌦️ Weather Tool

* Real-time weather lookup via API

### 🧠 Memory & History

* SQLite-based chat history
* Persistent conversations
* Session-based memory

### 👤 Authentication

* User login/signup
* Secure password hashing
* Role support for admin and user accounts

### 🎨 UI/UX

* Custom dark theme
* dentsu-inspired design
* Clean chat and source display
* Modern sidebar for history and uploads

---

## 🏗️ Architecture

```text
Frontend (Streamlit)
        ↓
Application Logic (Python)
        ↓
LangChain Agent
        ↓
Azure OpenAI (LLM)
        ↓
Tools:
  - Web Search (Tavily)
  - Weather API
  - Document Context
  - Image Analysis
        ↓
SQLite Database
```

---

## 📂 Project Structure

```text
.
├── app.py                  # Main application
├── dentsu_smart_buddy.db   # App database
├── agent_memory.db         # Agent memory
├── .env                    # Environment variables
├── requirements.txt        # Dependencies
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/your-username/dentsu-smart-buddy.git
cd dentsu-smart-buddy
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
MODEL_ENDPOINT=your_azure_endpoint
CHAT_MODEL_NAME=your_model_name
AZURE_OPENAI_API_KEY=your_api_key
api_version=2024-08-01-preview

TAVILY_API_KEY=your_tavily_api_key
WEATHER_API_KEY=your_weather_api_key
```

### 5. Run the App

```bash
streamlit run app.py
```

---

## 🧩 Key Components

### Database

* SQLite storage
* Tables: users, conversations, messages, documents

### Agent System

* LangChain tool-calling agent
* Tools:

  * Web search
  * Weather
  * Document context
  * Image analysis

### File Processing

* PDF → PyMuPDF
* DOCX → python-docx
* TXT → native parsing
* Images → Base64 encoding

### UI

* Sidebar for history and uploads
* Chat interface
* Source chips
* dentsu-branded visual styling

---

## 🔒 Security

* Password hashing using SHA-256
* No plaintext credentials
* Environment-based API keys
* Local SQLite storage for user and conversation data

---

## 📈 Future Improvements

* Vector database integration with FAISS or Pinecone
* Semantic document search
* Advanced role-based access control
* Cloud deployment on Azure or AWS
* Streaming responses
* Enterprise analytics dashboard
* Team-based workspaces

---

## 🤝 Contributing

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Submit a pull request

---

## 👨‍💻 Author

Built as an **AI-powered research assistant system** for dentsu-inspired enterprise productivity and research workflows.

---

## ⭐ Support

If you like this project, please ⭐ the repository!
