#!/bin/bash
set -e

echo "============================================"
echo "  CampusConnect Backend Setup"
echo "============================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found. Install it first."
    exit 1
fi

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "[WARNING] psql not found. Make sure PostgreSQL is installed and running."
fi

echo ""
echo "[1/5] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[2/5] Installing dependencies..."
pip install -r requirements.txt

echo "[3/5] Setting up PostgreSQL database..."
psql -U postgres -c "CREATE USER campususer WITH PASSWORD 'campuspass';" 2>/dev/null || true
psql -U postgres -c "CREATE DATABASE campusconnect OWNER campususer;" 2>/dev/null || true
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE campusconnect TO campususer;" 2>/dev/null || true

echo "[4/5] Seeding database with sample data..."
python seed.py

echo "[5/5] Starting server..."
echo ""
echo "============================================"
echo " Server running at http://localhost:8000"
echo " API Docs at     http://localhost:8000/docs"
echo " Login: 12305182 / campus123"
echo "============================================"
echo ""
uvicorn main:app --reload --host 0.0.0.0 --port 8000
