@echo off
echo Starting BizGenie AI Frontend (Streamlit)...
cd /d "%~dp0frontend"
C:\Users\premchandar\anaconda3\python.exe -m streamlit run app.py --server.port 8501
pause
