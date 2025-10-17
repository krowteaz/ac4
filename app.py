import streamlit as st
import requests
import re
import json
from pathlib import Path

st.set_page_config(page_title="AC4 - Global IPTV", layout="wide")

LOGO_PATH = "assets/ac4_logo.png"

# -------------------------- THEME --------------------------
DARK_CSS = """
<style>
:root, .stApp { background: #0f1116; color: #e6e6e6; }
h1,h2,h3,h4,h5 { color: #ffffff; }
.block-container { padding-top: 0.6rem; }
hr { border: 1px solid #1f2230; }
.badge { display:inline-block; padding:2px 6px; border-radius:8px; background:#1e2233; font-size:12px; margin-left:6px; }
.logo { height: 28px; vertical-align: middle; margin-right: 8px; border-radius: 4px; }
.meta { color:#9aa4b2; font-size: 12px; }
.footer { color:#8b939f; font-size:12px; margin-top:1.5rem }
.header-wrap { text-align:center; margin-bottom: 10px; }
.header-title { margin:0; color:#fff; }
.sub { color:#b0b0b0; margin-top:4px; }
.topbar { display:flex; justify-content:flex-end; }
.topbar button { margin-left: 8px; }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

# -------------------------- HEADER --------------------------
st.markdown(
    f"""
    <div class="header-wrap">
        <img src="{LOGO_PATH}" style="width:180px;border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.4);margin-bottom:5px;" />
        <h1 class="header-title">AC4 IPTV</h1>
        <div class="sub">Global IPTV Player — powered by iptv-org</div>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------- DATA SOURCES --------------------------
BASE_COUNTRY_URL = "https://iptv-org.github.io/iptv/countries/{code}.m3u"
MASTER_ALL_URL = "https://iptv-org.github.io/iptv/index.m3u"
PH_URL = BASE_COUNTRY_URL.format(code="ph")
FIL_LANGUAGE_URL = "https://iptv-org.github.io/iptv/languages/fil.m3u"

CURATED = {
    "🇵🇭 Philippines (default)": PH_URL,
    "🇺🇸 United States": BASE_COUNTRY_URL.format(code="us"),
    "🇯🇵 Japan": BASE_COUNTRY_URL.format(code="jp"),
    "🇰🇷 South Korea": BASE_COUNTRY_URL.format(code="kr"),
    "🇬🇧 United Kingdom": BASE_COUNTRY_URL.format(code="gb"),
    "🇦🇺 Australia": BASE_COUNTRY_URL.format(code="au"),
    "🌍 All Countries (master)": MASTER_ALL_URL,
}

# -------------------------- FAVORITES (persistent) --------------------------
FAV_FILE = Path("favorites.json")

def load_favorites():
    try:
        if FAV_FILE.exists():
            return set(json.loads(FAV_FILE.read_text(encoding="utf-8")))
    except Exception:
        pass
    return set()

def save_favorites(favs: set):
    try:
        FAV_FILE.write_text(json.dumps(sorted(list(favs))), encoding="utf-8")
    except Exception:
        pass

if "favorites" not in st.session_state:
    st.session_state.favorites = load_favorites()

# -------------------------- HELPERS --------------------------
HDRS = {"User-Agent": "Mozilla/5.0 (AC4-Global-IPTV)"}

@st.cache_data(show_spinner=True)
def fetch_text(url: str, timeout: int = 15) -> str:
    r = requests.get(url, headers=HDRS, timeout=timeout)
    r.raise_for_status()
    return r.text

def _extract_attr(pattern: str, line: str):
    m = re.search(pattern, line)
    return m.group(1).strip() if m else ""

def parse_m3u(raw: str):
    channels = []
    name, logo, group, tvg_id = None, "", "", ""
    for line in raw.splitlines():
        s = line.strip()
        if s.startswith("#EXTINF:"):
            tvg_id = _extract_attr(r'tvg-id="(.*?)"', s)
            logo = _extract_attr(r'tvg-logo="(.*?)"', s) or _extract_attr(r'logo="(.*?)"', s)
            group = _extract_attr(r'group-title="(.*?)"', s)
            name_match = re.search(r",\s*(.+)$", s)
            name = name_match.group(1).strip() if name_match else "Unknown"
        elif s.startswith("http"):
            if ".m3u8" in s:
                channels.append({"name": name or "Unknown", "url": s, "logo": logo, "group": group, "tvg_id": tvg_id})
            name, logo, group, tvg_id = None, "", "", ""
    return channels

@st.cache_data(show_spinner=True)
def load_playlist(url: str):
    try:
        text = fetch_text(url)
        return parse_m3u(text)
    except Exception:
        return []

def merge_playlists(urls):
    merged, seen = [], set()
    for u in urls:
        for ch in load_playlist(u):
            key = (ch["name"], ch["url"])
            if key not in seen:
                merged.append(ch)
                seen.add(key)
    return merged

# -------------------------- PLAYER --------------------------
def render_player(hls_url: str, overlay_text: str):
    html = f"""
    <html>
      <head>
        <meta name="referrer" content="no-referrer" />
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
          body {{
            margin: 0;
            background: linear-gradient(180deg, #0d0f14 0%, #000 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 80vh;
          }}
          .wrap {{
            position: relative;
            width: min(90vw, 1280px);
          }}
          video {{
            width: 100%;
            height: 70vh;
            border-radius: 12px;
            box-shadow: 0 0 30px rgba(0,0,0,0.8);
            background: #000;
          }}
          .nowplaying {{
            position: absolute;
            top: 10px;
            left: 10px;
            padding: 6px 10px;
            background: rgba(0,0,0,0.55);
            color: #fff;
            border-radius: 8px;
            font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji';
            font-size: 14px;
            backdrop-filter: blur(3px);
          }}
        </style>
      </head>
      <body>
        <div class="wrap">
          <div class="nowplaying">{overlay_text}</div>
          <video id="video" controls autoplay playsinline></video>
        </div>
        <script>
          var video = document.getElementById('video');
          if (Hls.isSupported()) {{
              var hls = new Hls({{maxBufferLength: 30}});
              hls.loadSource("{hls_url}");
              hls.attachMedia(video);
              hls.on(Hls.Events.MANIFEST_PARSED, function() {{ video.play(); }});
          }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
              video.src = "{hls_url}";
              video.addEventListener('loadedmetadata', function() {{ video.play(); }});
          }} else {{
              document.body.innerHTML = '<div style="color:#eee;font-family:sans-serif;padding:12px">Your browser cannot play HLS.</div>';
          }}
        </script>
      </body>
    </html>
    """
    st.components.v1.html(html, height=720)

# -------------------------- SIDEBAR --------------------------
with st.sidebar:
    try:
        st.image(LOGO_PATH, width=120)
    except Exception:
        pass
    st.header("🌏 Country / Source")
    choice = st.selectbox("Select a country or global list", list(CURATED.keys()), index=0)
    url = CURATED[choice]

    custom_iso = st.text_input("Or enter ISO country code (e.g., ph, us, jp, gb)")
    if custom_iso.strip():
        url = BASE_COUNTRY_URL.format(code=custom_iso.lower())

    extend_ph = st.checkbox("Extend PH list", value=("Philippines" in choice))
    query = st.text_input("🔎 Search channels", "", help="Filter by name or group")
    favorites_only = st.checkbox("⭐ Favorites only", value=False)

    # Top-right refresh
    if st.button("🔄 Refresh playlist"):
        st.cache_data.clear()
        st.experimental_rerun()

    if st.button("🗑 Clear all favorites"):
        st.session_state.favorites = set()
        save_favorites(st.session_state.favorites)
        st.success("Favorites cleared.")

# -------------------------- LOAD CHANNELS --------------------------
channels = merge_playlists([url, FIL_LANGUAGE_URL]) if "Philippines" in choice and extend_ph else load_playlist(url)

if not channels:
    st.error("No channels found or source unreachable.")
    st.stop()

groups = sorted({c["group"] for c in channels if c.get("group")})
group_choice = st.selectbox("Filter by category", ["All"] + groups, index=0)

filtered = channels
if group_choice != "All":
    filtered = [c for c in filtered if c.get("group") == group_choice]

if query:
    q = query.lower()
    filtered = [c for c in filtered if q in (c["name"] or "").lower() or q in (c["group"] or "").lower()]

if favorites_only:
    favs = st.session_state.favorites
    filtered = [c for c in filtered if c["url"] in favs]

if not filtered:
    st.warning("No channels match your filters.")
    st.stop()

if "idx" not in st.session_state:
    st.session_state.idx = 0

names = [c["name"] for c in filtered]
st.session_state.idx = max(0, min(st.session_state.idx, len(filtered) - 1))

selected_name = st.selectbox("Select a channel", names, index=st.session_state.idx, key="channel_select")
st.session_state.idx = names.index(selected_name)

col1, col2, col3, col4 = st.columns([0.12, 0.12, 0.2, 0.56])
with col1:
    if st.button("⏮ Back"):
        st.session_state.idx = (st.session_state.idx - 1) % len(filtered)
        st.experimental_rerun()
with col2:
    if st.button("▶ Next"):
        st.session_state.idx = (st.session_state.idx + 1) % len(filtered)
        st.experimental_rerun()
with col3:
    current = filtered[st.session_state.idx]
    is_fav = current["url"] in st.session_state.favorites
    if st.button("⭐ Remove Favorite" if is_fav else "⭐ Add to Favorites"):
        if is_fav:
            st.session_state.favorites.discard(current["url"])
        else:
            st.session_state.favorites.add(current["url"])
        save_favorites(st.session_state.favorites)
        st.toast("Favorites updated", icon="⭐")

chan = filtered[st.session_state.idx]
logo_html = f"<img class='logo' src='{chan['logo']}' />" if chan.get("logo") else ""
group_html = f"<span class='badge'>{chan['group']}</span>" if chan.get("group") else ""
st.markdown(f"### {logo_html}{chan['name']} {group_html}", unsafe_allow_html=True)
if chan.get("tvg_id"):
    st.markdown(f"<div class='meta'>ID: {chan['tvg_id']}</div>", unsafe_allow_html=True)

overlay = f"Now Playing: {chan['name']}" + (f" • {chan['group']}" if chan.get("group") else "")
render_player(chan["url"], overlay)

st.markdown("<div class='footer'>Note: Streams are public/free and may be geo-restricted.</div>", unsafe_allow_html=True)
