@echo off
echo Starting NeuroCore...

python -m venv venv
call venv\Scripts\activate

pip install -r requirements.txt

start cmd /k uvicorn backend.main:app --host 0.0.0.0 --port 8000
start cmd /k python -m cli.main
start cmd /k python -m http.server 5500 --directory dashboard