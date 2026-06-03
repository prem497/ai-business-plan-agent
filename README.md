# BizGenie AI — Business Plan Agent

A full-stack AI-powered business plan generator built with **Grok API + FastAPI + Streamlit**.

## Tech Stack
- 🤖 **Grok API** (xAI) — LLM backbone
- ⚡ **FastAPI** — Backend REST API
- 🎨 **Streamlit** — Dashboard frontend
- 📊 **Plotly** — Interactive charts
- 🗄️ **SQLite + SQLAlchemy** — Plan persistence

## Quick Start

### 1. Set API Key
Edit `.env` and add your Grok API key:
```
GROK_API_KEY=your_actual_key_here
```

### 2. Install Backend
```bash
cd backend
pip install -r requirements.txt
```

### 3. Install Frontend
```bash
cd frontend
pip install -r requirements.txt
```

### 4. Run Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Run Frontend (new terminal)
```bash
cd frontend
streamlit run app.py
```

Open http://localhost:8501
