@echo off
echo Starting DocPortal...
set PYTHONPATH=%~dp0
.\venv\Scripts\python.exe unified_doc_tool\app.py
pause