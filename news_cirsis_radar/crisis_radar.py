import streamlit as st
import feedparser
import pandas as pd
from collections import Counter
import re
import folium
from folium.plugins import HeatMap
from folium import DivIcon
from streamlit_folium import st_folium

# --- Configuration & Constants ---
RSS_FEEDS = {
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Arab Times": "https://www.arabtimesonline.com/rssfeed/47/",
    "Khaleej Times": "https://www.khaleejtimes.com/stories.rss?botrequest=true"
}

WAR_KEYWORDS = ['iran', 'uae', 'united arab emirates', 'dubai', 'abu dhabi', 'emirate', 'oil', 'trade', 'israel', 'usa', 'war', 'strike', 'attack', 'missile', 'tehran', 'gaza', 'lebanon']

LOCATION_COORDS = {
    'Tehran': (35.6892, 51.3890), 'Tel Aviv': (32.0853, 34.7818), 'Beirut': (33.8938, 35.5018),
    'Baghdad': (33.3152, 44.3661), 'Kuwait City': (29.3759, 47.9774), 'Dubai': (25.2048, 55.2708),
    'Abu Dhabi': (24.4539, 54.3773), 'Riyadh': (24.7136, 46.6753), 'Manama': (26.2235, 50.5876),
    'Doha': (25.2854, 51.5310), 'Amman': (31.9515, 35.9349), 'Erbil': (36.1924, 43.9935), 'Haifa': (32.7940, 34.9896)
}

LOCATION_PATTERNS = {
    'Tehran': 'tehran|iran', 'Tel Aviv': 'tel aviv|israel', 'Beirut': 'beirut|lebanon',
    'Baghdad': 'baghdad|iraq', 'Kuwait City': 'kuwait', 'Dubai': 'dubai|uae',
    'Abu Dhabi': 'abu dhabi|uae', 'Riyadh': 'riyadh|saudi', 'Manama': 'manama|bahrain',
    'Doha': 'doha|qatar', 'Amman': 'amman|jordan', 'Erbil': 'erbil', 'Haifa': 'haifa'
}

# --- Core Logic Functions ---

@st.cache_data(ttl=300)
def fetch_and_filter_news():
    all_entries = []
    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:
                title = entry.title.lower()
                summary = (entry.get('summary', '') + ' ' + entry.get('description', '')).lower()
                if any(kw in title or kw in summary for kw in WAR_KEYWORDS):
                    all_entries.append({
                        'source': name, 'title': entry.title, 'link': entry.link,
                        'summary': entry.get('summary', ''), 'published': entry.get('published', '')
                    })
        except Exception as e:
            st.warning(f"Failed to fetch {name}: {e}")
    return all_entries

def extract_locations(text):
    locations = []
    text_lower = text.lower()
    for loc, pattern in LOCATION_PATTERNS.items():
        if re.search(pattern, text_lower):
            locations.append(loc)
    return locations

# --- UI Components ---

def render_news_ticker(news):
    if not news:
        st.sidebar.info('No recent headlines available')
        return

    items_html = ""
    for entry in news:
        title = entry.get('title', '').replace('"', '&quot;')
        items_html += f"<div class='ticker__item'><a href='{entry['link']}' target='_blank'>{title}</a><div class='meta'>{entry['source']} • {entry['published']}</div></div>"

    ticker_html = f"""
    <div class='ticker'><div class='ticker__wrap'>{items_html}{items_html}</div></div>
    <style>
        .ticker{{ height: 420px; overflow: hidden; background: #000; padding: 10px; border-radius: 8px; }}
        .ticker__wrap{{ display: flex; flex-direction: column; animation: scroll 45s linear infinite; }}
        .ticker__item{{ padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 4px; }}
        .ticker__item a{{ color: #7CFC00; text-decoration: none; font-weight: 600; font-family: 'Courier New', monospace; font-size: 14px; }}
        .ticker__item .meta{{ font-size: 11px; color: #888; margin-top: 4px; }}
        @keyframes scroll{{ 0% {{ transform: translateY(0%); }} 100% {{ transform: translateY(-50%); }} }}
    </style>
    """
    st.sidebar.markdown("## Latest News", unsafe_allow_html=False)
    st.sidebar.markdown(ticker_html, unsafe_allow_html=True)

def render_map(location_counts):
    data = []
    for loc, count in location_counts.items():
        if loc in LOCATION_COORDS:
            data.append({'Location': loc, 'Lat': LOCATION_COORDS[loc][0], 'Lon': LOCATION_COORDS[loc][1], 'Mentions': count})
    
    df = pd.DataFrame(data)
    m = folium.Map(location=[30, 45], zoom_start=3, tiles='CartoDB dark_matter')
    HeatMap([[r['Lat'], r['Lon'], r['Mentions']] for _, r in df.iterrows()], radius=25, blur=15, gradient={0.2: 'lime', 0.6: 'orange', 1.0: 'red'}).add_to(m)

    for _, row in df.iterrows():
        color = '#32CD32' if row['Mentions'] <= 2 else '#FF4500'
        size = max(12, min(50, row['Mentions'] * 8))
        pulse_html = f"""
        <div style="position:relative; width:{size}px; height:{size}px;">
            <div style="width:{size}px; height:{size}px; border-radius:50%; background:{color}; box-shadow:0 0 12px {color}; position:absolute;"></div>
            <div style="width:{size}px; height:{size}px; border-radius:50%; background:{color}; position:absolute; animation:pulse 1.8s infinite; opacity:0.6;"></div>
        </div>
        <style>@keyframes pulse {{ 0% {{ transform: scale(0.8); opacity: 0.9; }} 100% {{ transform: scale(2.8); opacity: 0.0; }} }}</style>
        """
        folium.Marker(location=(row['Lat'], row['Lon']), icon=DivIcon(html=pulse_html), popup=f"{row['Location']}: {row['Mentions']}").add_to(m)
    
    st_folium(m, width=700, height=500)

# --- Entry Point Function ---

def run_crisis_radar():
    """Call this function from your main app to display the radar."""
    st.title("TruEstates Crisis Radar")
    
    news = fetch_and_filter_news()
    st.success(f"Fetched {len(news)} relevant articles.")
    
    render_news_ticker(news)
    
    loc_counts = Counter()
    for entry in news:
        loc_counts.update(extract_locations(entry['title'] + ' ' + entry['summary']))
    
    if loc_counts:
        render_map(loc_counts)
        st.subheader("Location Mentions")
        df_counts = pd.DataFrame.from_dict(loc_counts, orient='index', columns=['No. of events']).sort_values('No. of events', ascending=False)
        st.write(df_counts)
    else:
        st.info("No war-related locations detected.")

    st.subheader("Sample Articles")
    for entry in news[:6]:
        with st.expander(entry['title'][:50] + '...'):
            st.write(f"**Source:** {entry['source']}\n\n{entry['summary'][:200]}...\n\n[Read more]({entry['link']})")