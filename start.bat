@echo off
chcp 65001 > nul
echo Starting HugHigh Backend API...
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check if database exists, if not create test data
if not exist app.db (
    echo Creating database and test data...
    python seed_data.py
)

REM Start the server
echo.
echo =====================================
echo Backend API is starting...
echo API URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo =====================================
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000
