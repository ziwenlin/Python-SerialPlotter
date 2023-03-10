@echo off
python -m venv venv
cmd /k ".\venv\Scripts\activate & pip install -r requirements.txt & exit"
