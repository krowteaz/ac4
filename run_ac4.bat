@echo off
title AC4 IPTV Launcher
echo =====================================================
echo        Launching AC4 IPTV v4.4.1 Portable
echo =====================================================
where python >nul 2>&1
if %errorlevel% neq 0 (
  echo Python not found! Please install Python 3.10+ and try again.
  pause
  exit /b
)
set PORT=8501
echo Installing dependencies...
python -m  pip install --upgrade pip >nul
python -m  pip install -r requirements.txt
echo Clearing cache...
python -m streamlit cache clear >nul 2>&1
echo Starting app on http://localhost:%PORT% ...
start http://localhost:%PORT%
python -m streamlit run app.py --server.port %PORT%
pause
