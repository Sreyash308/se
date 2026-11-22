@echo off
REM PlantCare AI - Cross-Platform Execution Script for Windows

echo ==========================================================
echo   Starting PlantCare AI Platform (Windows)
echo ==========================================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Creating virtual environment in .venv...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing/verifying dependencies...
pip install -q -r requirements.txt

echo Running system verification check...
python scripts\verify_system.py

echo.
echo ==========================================================
echo   Starting FastAPI ASGI Server on http://localhost:8000
echo   - Web Dashboard: http://localhost:8000
echo   - Interactive Swagger API: http://localhost:8000/docs
echo   - ReDoc Documentation: http://localhost:8000/redoc
echo ==========================================================
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
