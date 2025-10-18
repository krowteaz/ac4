# 🛰️ AC4 IPTV v4.4 Pro (Loop + Retry + Favorites + Counter)

**Author:** Jef  
**Version:** v4.4 Pro (Loop Edition)  
**Release Date:** 2025-10-18  
**Built With:** Streamlit + Python + iptv-org sources

---

## 🎯 Overview
AC4 IPTV is a Streamlit-based global live TV streaming dashboard featuring:
- 🇵🇭 Default PH playlist with optional Extend PH
- 🌍 International playlists (US, UK, JP, KR, AU, Global Master)
- ⭐ Favorites system with persistent storage (favorites.json)
- 🎞️ HLS player with retry logic and gradient background
- 🔁 Circular Next/Back navigation with “Try Next” and channel counter
- ⚠️ Auto-retry mechanism for failed streams (up to 3x)

---

## 🧰 System Requirements

| Component | Minimum Requirement |
|------------|---------------------|
| Python | 3.10+ |
| Streamlit | 1.33+ |
| Requests | Latest |
| OS | Windows / macOS / Linux |
| Network | 10 Mbps+ stable (recommended) |

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

**Folder Structure:**
```
AC4_IPTV_v4_4_Pro_Final/
├── app.py
├── requirements.txt
├── favorites.json (auto-created)
└── assets/
    └── ac4_logo.png
```

---

## 🖥️ Interface Overview

### 🧭 Sidebar
- 🌏 Select source (PH, US, JP, etc.)
- 🔠 Enter ISO code manually
- 🧩 Extend PH list toggle
- 🔎 Search bar
- ⭐ Clickable favorites list (persistent)
- 🔄 Refresh / 🗑 Clear buttons

### 🎬 Main Panel
- ▶ Gradient player with overlay
- ⚙ Fade-in “Now Playing” overlay
- ⏮ ⏭ Loop navigation
- 🔄 Try Next button
- ⭐ Favorite toggle
- 📊 Channel counter

---

## 🧩 Technical Highlights

- HLS.js player with auto-retry (3x)
- Cache-busting querystring to avoid stale buffers
- Circular navigation (loop playlist)
- Persistent favorites saved to local JSON
- Modern dark gradient theme with toasts

---

## 🧪 Troubleshooting

| Issue | Cause | Solution |
|--------|--------|-----------|
| Video not playing | HLS not supported or geo-locked | Click “Try Next” or use VPN |
| Slow loading | Low bandwidth | Filter by country or group |
| Empty playlist | Source site temporary outage | Click “Refresh Playlist” |

---

## 📸 Screenshot Placeholders

- 🖼️ Header + Sidebar
- 🖼️ Player + Overlay
- 🖼️ Favorites Sidebar
- 🖼️ Retry Alert

---

## 💬 Credits
- **Playlists:** [iptv-org GitHub](https://github.com/iptv-org/iptv)
- **Framework:** [Streamlit](https://streamlit.io)
- **Design:** Gradient UI + Logo by Jef

