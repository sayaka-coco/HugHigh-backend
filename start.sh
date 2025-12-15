#!/bin/bash
echo "Starting HugHigh Backend API..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if database exists, if not create test data
if [ ! -f "app.db" ]; then
    echo "Creating database and test data..."
    python seed_data.py
fi

# Start the server
echo ""
echo "====================================="
echo "Backend API is starting..."
echo "API URL: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "====================================="
echo ""
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
