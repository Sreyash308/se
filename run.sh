#!/usr/bin/env bash
# PlantCare AI - Cross-Platform Execution Script for Unix/macOS/Linux

set -e

echo "=========================================================="
echo "  Starting PlantCare AI Platform"
echo "=========================================================="

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH."
    exit 1
fi

# Optional virtual environment check
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing/verifying dependencies..."
pip install -q -r requirements.txt

echo "Running system verification check..."
python3 scripts/verify_system.py

echo ""
echo "=========================================================="
echo "  Starting FastAPI ASGI Server on http://localhost:8000"
echo "  - Web Dashboard: http://localhost:8000"
echo "  - Interactive Swagger API: http://localhost:8000/docs"
echo "  - ReDoc Documentation: http://localhost:8000/redoc"
echo "=========================================================="
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
