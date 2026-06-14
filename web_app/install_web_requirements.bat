@echo off
cd /d "%~dp0\.."
python -m pip install -r web_app\requirements.txt
pause
