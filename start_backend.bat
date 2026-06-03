@echo off
echo Starting BizGenie AI Backend (FastAPI)...
cd /d "%~dp0backend"
C:\Users\premchandar\anaconda3\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
