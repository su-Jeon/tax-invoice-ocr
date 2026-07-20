@echo off
cd /d "%~dp0"
set PYTHONUTF8=1
"%USERPROFILE%\anaconda3\python.exe" gradio_app.py
pause
