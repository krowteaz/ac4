
import streamlit as st
import requests
import re
import json
from pathlib import Path

st.set_page_config(page_title='AC4 — Global IPTV', layout='wide')

# -------------------------- UI THEME --------------------------
DARK_CSS = '''
<style>
:root, .stApp { background: #0f1116; color: #e6e6e6; }
h1,h2,h3,h4,h5 { color: #ffffff; }
.block-container { padding-top: 1rem; }
hr { border: 1px solid #1f2230; }
.badge { display:inline-block; padding:2px 6px; border-radius:8px; background:#1e2233; font-size:12px; margin-left:6px; }
.logo { height: 28px; vertical-align: middle; margin-right: 8px; border-radius: 4px; }
.meta { color:#9aa4b2; font-size: 12px; }
.footer { color:#8b939f; font-size:12px; margin-top:1.5rem }
.controls button { margin-right: 8px; }
</style>
'''
st.markdown(DARK_CSS, unsafe_allow_html=True)

st.markdown('# 📺 AC4 — Global IPTV (PH default)')
st.caption('Loads public/free IPTV playlists from iptv-org. Uses hls.js for playback.')

# -------------------------- DATA SOURCES --------------------------
BASE_COUNTRY_URL = 'https://iptv-org.github.io/iptv/countries/{code}.m3u'
MASTER_ALL_URL = 'https://iptv-org.github.io/iptv/index.m3u'
PH_URL = BASE_COUNTRY_URL.format(code='ph')
FIL_LANGUAGE_URL = 'https://iptv-org.github.io/iptv/languages/fil.m3u'

CURATED = {
    '🇵🇭 Philippines (default)': PH_URL,
    '🇺🇸 United States': BASE_COUNTRY_URL.format(code='us'),
    '🇯🇵 Japan': BASE_COUNTRY_URL.format(code='jp'),
    '🇰🇷 South Korea': BASE_COUNTRY_URL.format(code='kr'),
    '🇬🇧 United Kingdom': BASE_COUNTRY_URL.format(code='gb'),
    '🇦🇺 Australia': BASE_COUNTRY_URL.format(code='au'),
    '🇸🇬 Singapore': BASE_COUNTRY_URL.format(code='sg'),
    '🇹🇭 Thailand': BASE_COUNTRY_URL.format(code='th'),
    '🇭🇰 Hong Kong': BASE_COUNTRY_URL.format(code='hk'),
    '🇹🇼 Taiwan': BASE_COUNTRY_URL.format(code='tw'),
    '🇮🇩 Indonesia': BASE_COUNTRY_URL.format(code='id'),
    '🇲🇾 Malaysia': BASE_COUNTRY_URL.format(code='my'),
    '🇨🇦 Canada': BASE_COUNTRY_URL.format(code='ca'),
    '🇫🇷 France': BASE_COUNTRY_URL.format(code='fr'),
    '🇩🇪 Germany': BASE_COUNTRY_URL.format(code='de'),
    '🇮🇹 Italy': BASE_COUNTRY_URL.format(code='it'),
    '🇪🇸 Spain': BASE_COUNTRY_URL.format(code='es'),
    '🌍 All Countries (master)': MASTER_ALL_URL,
}

# -------------------------- FAVORITES (persistent) --------------------------
FAV_FILE = Path('favorites.json')

def load_favorites():
    try:
        if FAV_FILE.exists():
            return set(json.loads(FAV_FILE.read_text(encoding='utf-8')))
    except Exception:
        pass
    return set()

def save_favorites(favs: set):
    try:
        FAV_FILE.write_text(json.dumps(sorted(list(favs))), encoding='utf-8')
    except Exception:
        pass

if "favorites" not in st.session_state:
    st.session_state.favorites = load_favorites()

# -------------------------- HELPERS --------------------------
HDRS = {'User-Agent': 'Mozilla/5.0 (AC4-Global-IPTV)'}

@st.cache_data(show_spinner=True)
def fetch_text(url: str, timeout: int = 15) -> str:
    r = requests.get(url, headers=HDRS, timeout=timeout)
    r.raise_for_status()
    return r.text

def _extract_attr(pattern: str, line: str):
    m = re.search(pattern, line)
    return m.group(1).strip() if m else ''

def parse_m3u(raw: str):
    '''
    Robust M3U/M3U8 EXTINF parser.
    Returns list of dicts: {name, url, logo, group, tvg_id}
    '''
    channels = []
    name, logo, group, tvg_id = None, '', '', ''
    for line in raw.splitlines():
        s = line.strip()
        if s.startswith('#EXTINF:'):
            # Attributes like tvg-id, tvg-logo, group-title
            tvg_id = _extract_attr(r'tvg-id="(.*?)"', s)
            logo = _extract_attr(r'tvg-logo="(.*?)"', s) or _extract_attr(r'logo="(.*?)"', s)
            group = _extract_attr(r'group-title="(.*?)"', s)
            # The part after the last comma is the display name
            name_match = re.search(r',\s*(.+)$', s)
            name = name_match.group(1).strip() if name_match else 'Unknown'
        elif s.startswith('http'):
            # Only accept HLS m3u8 links
            if '.m3u8' in s:
                channels.append({
                    'name': name or 'Unknown',
                    'url': s,
                    'logo': logo,
                    'group': group,
                    'tvg_id': tvg_id
                })
            # reset
            name, logo, group, tvg_id = None, '', '', ''
    return channels

@st.cache_data(show_spinner=True)
def load_playlist(url: str):
    try:
        text = fetch_text(url)
        return parse_m3u(text)
    except Exception:
        return []

def merge_playlists(urls):
    merged = []
    seen = set()
    for u in urls:
        for ch in load_playlist(u):
            key = (ch['name'], ch['url'])
            if key not in seen:
                merged.append(ch); seen.add(key)
    return merged

def render_player(hls_url: str, height: int = 520):
    html = f'''
    <html>
      <head>
        <meta name="referrer" content="no-referrer" />
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
      </head>
      <body style="margin:0;padding:0;background:#0f1116;">
        <video id="video" width="100%" height="100%" controls autoplay playsinline></video>
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
    '''
    st.components.v1.html(html, height=height)

# -------------------------- SIDEBAR --------------------------
with st.sidebar:
    st.header('🌏 Country / Source')
    choice = st.selectbox('Select a country or global list', list(CURATED.keys()), index=0)
    url = CURATED[choice]

    custom_iso = st.text_input('Or enter ISO country code (e.g., ph, us, jp, gb)')
    if custom_iso.strip():
        url = BASE_COUNTRY_URL.format(code=custom_iso.lower())

    extend_ph = st.checkbox('Extend PH list (merge Filipino language list)', value=('Philippines' in choice))
    st.markdown('---')
    query = st.text_input('🔎 Search channels (name/group)', '', help='Type to filter by channel name or group')
    favorites_only = st.checkbox('⭐ Favorites only', value=False)
    clear_fav = st.button('Clear all favorites')

    if clear_fav:
        st.session_state.favorites = set()
        save_favorites(st.session_state.favorites)
        st.success('Favorites cleared.')

# -------------------------- LOAD CHANNELS --------------------------
if 'Philippines' in choice and extend_ph:
    channels = merge_playlists([url, FIL_LANGUAGE_URL])
else:
    channels = load_playlist(url)

if not channels:
    st.error('No channels found or source unreachable. Try another country or the master list.')
    st.stop()

# Build category list (group-title)
groups = sorted({c['group'] for c in channels if c.get('group')})
group_choice = st.selectbox('Filter by category (group-title)', ['All'] + groups, index=0)

# Apply filters
filtered = channels
if group_choice != 'All':
    filtered = [c for c in filtered if c.get('group') == group_choice]

if query:
    q = query.lower()
    filtered = [c for c in filtered if q in (c['name'] or '').lower() or q in (c['group'] or '').lower()]

if favorites_only:
    favs = st.session_state.favorites
    filtered = [c for c in filtered if c['url'] in favs]

if not filtered:
    st.warning('No channels match your filters/search.')
    st.stop()

st.markdown(f'**Found {len(filtered)} channels** from **{choice}** ' + ('(extended)' if ('Philippines' in choice and extend_ph) else ''))
st.markdown('---')

# -------------------------- SELECTION + NAV --------------------------
# Maintain index in session for Next/Back behavior
if 'idx' not in st.session_state:
    st.session_state.idx = 0

names = [c['name'] for c in filtered]

# Keep idx in bounds if filters changed
st.session_state.idx = max(0, min(st.session_state.idx, len(filtered) - 1))

# Selectbox synced with current index
selected_name = st.selectbox('Select a channel', names, index=st.session_state.idx, key='channel_select')

# If user picks a different channel via selectbox, update idx
st.session_state.idx = names.index(selected_name)

# Buttons for Back/Next
c1, c2, c3, c4 = st.columns([0.12,0.12,0.12,0.64])
with c1:
    if st.button('⏮ Back'):
        st.session_state.idx = (st.session_state.idx - 1) % len(filtered)
        st.session_state.channel_select = names[st.session_state.idx]
with c2:
    if st.button('▶ Next'):
        st.session_state.idx = (st.session_state.idx + 1) % len(filtered)
        st.session_state.channel_select = names[st.session_state.idx]
with c3:
    # Favorites toggle
    current = filtered[st.session_state.idx]
    is_fav = current['url'] in st.session_state.favorites
    if st.button('⭐ Remove Favorite' if is_fav else '⭐ Add to Favorites'):
        if is_fav:
            st.session_state.favorites.discard(current['url'])
        else:
            st.session_state.favorites.add(current['url'])
        save_favorites(st.session_state.favorites)
        st.toast('Favorites updated', icon='⭐')

chan = filtered[st.session_state.idx]

logo_html = f'<img class="logo" src="{chan["logo"]}" />' if chan.get('logo') else ''
group_html = f'<span class="badge">{chan["group"]}</span>' if chan.get('group') else ''

st.markdown(f'### {logo_html}{chan["name"]} {group_html}', unsafe_allow_html=True)
if chan.get('tvg_id'):
    st.markdown(f"<div class='meta'>ID: {chan['tvg_id']}</div>", unsafe_allow_html=True)

# Player
render_player(chan['url'], height=520)

st.markdown("<div class='footer'>Note: Streams are community-sourced and may be geo-restricted or intermittently available.</div>", unsafe_allow_html=True)
