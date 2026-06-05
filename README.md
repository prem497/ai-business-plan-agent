project title:AI — Business Plan agent

Problem :startup fails   without proper analysis 
Solution this agent will give all detail plan enter your idea 


📌 Overview
 AI agent helps entrepreneurs and businesses generate detailed, structured business plans in seconds using the power of xAI's Grok LLM. Simply describe your business idea and let the agent do the rest — from market analysis to financial projections.

🔄 System Workflow
User
 │
 │  enters business idea (name, industry, goals, budget)
 ▼
┌─────────────────────────────────┐
│        Streamlit UI             │  ← localhost:8501
│  Renders input form             │
└────────────┬────────────────────┘
             │  HTTP POST /generate
             ▼
┌─────────────────────────────────┐
│        FastAPI Backend          │  ← localhost:8000
│  Validates & routes request     │
└──────┬──────────────┬───────────┘
       │              │
       │ prompt       │ save/retrieve
       ▼              ▼
┌─────────────┐  ┌──────────────┐
│  Grok API   │  │  SQLite DB   │
│  (xAI LLM)  │  │  SQLAlchemy  │
│ grok-3-mini │  │  persists    │
└──────┬──────┘  │  plans       │
       │         └──────────────┘
       │  plan text + JSON
       ▼
┌─────────────────────────────────┐
│     FastAPI JSON Response       │
│  Plan sections + Plotly data    │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│     Streamlit Dashboard         │
│  Renders plan + interactive     │
│  Plotly charts                  │
└────────────┬────────────────────┘
             │
             ▼
           User views completed business plan
Step-by-step flow

User submits idea — fills out the Streamlit form with business name, industry, target market, and budget.
Streamlit → FastAPI — sends a POST request to the FastAPI backend at /generate.
FastAPI validates — checks the incoming data, builds a structured prompt, and calls the Grok API.
Grok API responds — grok-3-mini processes the prompt and returns a full business plan in text/JSON.
SQLite persists — the generated plan is saved via SQLAlchemy so users can revisit it later.
FastAPI returns JSON — sends the plan content along with chart-ready data back to the frontend.
Streamlit renders — displays the plan in sections and draws interactive Plotly charts (financial projections, market analysis, etc.).


🛠️ Tech Stack
LayerTechnology🤖 LLMGrok API (xAI) — grok-3-mini⚡ BackendFastAPI + Uvicorn🎨 FrontendStreamlit📊 ChartsPlotly🗄️ DatabaseSQLite + SQLAlchemy🐍 RuntimePython (Anaconda)

📁 Project Structure
bizgenie-ai/
├── backend/
│   ├── main.py               # FastAPI app entry point
│   └── requirements.txt      # Backend dependencies
├── frontend/
│   ├── app.py                # Streamlit UI
│   └── requirements.txt      # Frontend dependencies
├── .env                      # Environment variables (API keys)
├── start_backend.bat         # Windows quick-start for backend
├── start_frontend.bat        # Windows quick-start for frontend
└── README.md

⚙️ Setup & Installation
Prerequisites

Python 3.8+ (Anaconda recommended)
A valid xAI Grok API key


1. Clone the Repository
bashgit clone https://github.com/your-username/bizgenie-ai.git
cd bizgenie-ai
2. Configure Environment Variables
Edit the .env file in the root directory:
envGROK_API_KEY=your_actual_grok_api_key_here
GROK_BASE_URL=https://api.x.ai/v1
GROK_MODEL=grok-3-mini
BACKEND_URL=http://localhost:8000

⚠️ Never commit your .env file. It is listed in .gitignore by default.


3. Install Backend Dependencies
bashcd backend
pip install -r requirements.txt
4. Install Frontend Dependencies
bashcd frontend
pip install -r requirements.txt

🚀 Running the App
Option A — Manual (Cross-platform)
Terminal 1 — Start Backend:
bashcd backend
uvicorn main:app --reload --port 8000
Terminal 2 — Start Frontend:
bashcd frontend
streamlit run app.py
Option B — Windows Quick Start
Double-click the provided .bat files:
start_backend.bat    ← Starts FastAPI on port 8000
start_frontend.bat   ← Starts Streamlit on port 8501

🌐 Accessing the App
ServiceURLFrontend (Streamlit)http://localhost:8501Backend API (FastAPI)http://localhost:8000API Docs (Swagger)http://localhost:8000/docs

✨ Features

📝 AI-generated business plans using Grok LLM
📊 Interactive charts and financial projections via Plotly
💾 Save and retrieve past business plans (SQLite)
🔌 Clean REST API via FastAPI
🖥️ Intuitive dashboard UI with Streamlit


🔐 Environment Variables Reference
VariableDescriptionDefaultGROK_API_KEYYour xAI Grok API key(required)GROK_BASE_URLGrok API base URLhttps://api.x.ai/v1GROK_MODELModel to usegrok-3-miniBACKEND_URLFastAPI backend URLhttp://localhost:8000


Demo:

Author:Premchandar



