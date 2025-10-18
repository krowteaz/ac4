
# AC4 IPTV App v4.4.1 Portable Cloud

## Run (Windows)
1) Double-click `run_ac4.bat`

## Run (macOS / Linux / Cloud shell)
```bash
chmod +x start_ac4.sh
./start_ac4.sh
```

## Manual (any OS)
```bash
pip install -r requirements.txt
streamlit run app.py --server.port ${PORT:-8501}
```

Notes:
- Defaults to **Philippines (default)** playlist.
- Favorites persist in `favorites.json`.
- If a stream is down, click **Try Next** or use **Next/Back**.
