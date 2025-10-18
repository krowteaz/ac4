
#!/usr/bin/env bash
set -e
PORT="${PORT:-8501}"
echo "Launching AC4 IPTV v4.4.1 Portable on port ${PORT}..."
python3 -V >/dev/null 2>&1 || { echo "Python 3 not found. Please install it first."; exit 1; }
pip install --upgrade pip
pip install -r requirements.txt
streamlit cache clear || true
streamlit run app.py --server.port "${PORT}"
