@echo off
echo ============================================
echo   CampusConnect Backend Setup
echo ============================================

:: Check Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found. Install from https://python.org
    pause
    exit /b 1
)

:: Check PostgreSQL
psql --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [WARNING] psql not in PATH. Make sure PostgreSQL is running.
)

echo.
echo [1/5] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo [2/5] Installing dependencies...
pip install -r requirements.txt

echo [3/5] Creating PostgreSQL database...
psql -U postgres -c "CREATE USER campususer WITH PASSWORD 'campuspass';" 2>nul
psql -U postgres -c "CREATE DATABASE campusconnect OWNER campususer;" 2>nul
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE campusconnect TO campususer;" 2>nul

echo [4/5] Seeding database with sample data...
python seed.py

echo [5/5] Starting server...
echo.
echo ============================================
echo  Server running at http://localhost:8000
echo  API Docs at     http://localhost:8000/docs
echo  Login: 12305182 / campus123
echo ============================================
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000
