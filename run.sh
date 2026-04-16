#!/bin/bash

echo "🧠 Starting NeuroCore Cyber Defense..."

# Activar entorno
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🚀 Starting FastAPI..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

sleep 3

echo "🖥 Starting CLI monitor..."
python3 -m cli.main &
CLI_PID=$!

echo "🌐 Starting Dashboard..."
cd dashboard
python3 -m http.server 5500 &
DASH_PID=$!

echo "✅ System running:"
echo "API → http://localhost:8000"
echo "Dashboard → http://localhost:5500"

wait