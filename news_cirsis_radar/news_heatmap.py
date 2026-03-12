# import streamlit as st
# import feedparser
# import pandas as pd
# from collections import Counter
# import re
# from geopy.geocoders import Nominatim
# import plotly.express as px
# import plotly.graph_objects as go

# # Streamlit app title
# st.title("News Heatmap: Iran-Israel-USA War Coverage")

# # RSS feeds - confirmed/discovered URLs
# rss_feeds = {
#     "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
#     "Arab Times": "https://www.arabtimesonline.com/rssfeed/47/",  # From web:17, web:20
#     "Khaleej Times": "https://www.khaleejtimes.com/stories.rss?botrequest=true"  # Assumed standard /rss
# }

# # Keywords for filtering war-related news
# war_keywords = ['iran', 'uae', 'united arab emirates', 'dubai', 'abu dhabi', 'emirate', 'oil', 'trade', 'israel', 'usa', 'war', 'strike', 'attack', 'missile', 'tehran', 'gaza', 'lebanon']

# @st.cache_data(ttl=300)  # Cache for 5 min
# def fetch_and_filter_news():
#     all_entries = []
#     for name, url in rss_feeds.items():
#         try:
#             feed = feedparser.parse(url)
#             for entry in feed.entries[:20]:  # Limit to recent 20 per feed
#                 title = entry.title.lower()
#                 summary = (entry.get('summary', '') + ' ' + entry.get('description', '')).lower()
#                 if any(kw in title or kw in summary for kw in war_keywords):
#                     all_entries.append({
#                         'source': name,
#                         'title': entry.title,
#                         'link': entry.link,
#                         'summary': entry.get('summary', ''),
#                         'published': entry.get('published', '')
#                     })
#         except Exception as e:
#             st.warning(f"Failed to fetch {name}: {e}")
#     return all_entries

# news = fetch_and_filter_news()
# st.success(f"Fetched {len(news)} relevant articles.")

# # Extract locations - simple regex for cities/countries + predefined war hot spots
# location_patterns = {
#     'Tehran': 'tehran|iran',
#     'Tel Aviv': 'tel aviv|israel',
#     'Beirut': 'beirut|lebanon',
#     'Baghdad': 'baghdad|iraq',
#     'Kuwait City': 'kuwait',
#     'Dubai': 'dubai|uae',
#     'Abu Dhabi': 'abu dhabi|uae',
#     'Riyadh': 'riyadh|saudi',
#     'Manama': 'manama|bahrain',
#     'Doha': 'doha|qatar',
#     'Amman': 'amman|jordan',
#     'Erbil': 'erbil',
#     'Haifa': 'haifa'
# }

# def extract_locations(text):
#     locations = []
#     text_lower = text.lower()
#     for loc, pattern in location_patterns.items():
#         if re.search(pattern, text_lower):
#             locations.append(loc)
#     return locations

# # Extract and count locations
# location_counts = Counter()
# for entry in news:
#     text = entry['title'] + ' ' + entry['summary']
#     locs = extract_locations(text)
#     location_counts.update(locs)

# st.subheader("Location Mentions")
# st.write(pd.DataFrame.from_dict(location_counts, orient='index', columns=['Count']).sort_values('Count', ascending=False))

# if location_counts:
#     # Coordinates for known locations (manual mapping for reliability)
#     coords = {
#         'Tehran': (35.6892, 51.3890),
#         'Tel Aviv': (32.0853, 34.7818),
#         'Beirut': (33.8938, 35.5018),
#         'Baghdad': (33.3152, 44.3661),
#         'Kuwait City': (29.3759, 47.9774),
#         'Dubai': (25.2048, 55.2708),
#         'Abu Dhabi': (24.4539, 54.3773),
#         'Riyadh': (24.7136, 46.6753),
#         'Manama': (26.2235, 50.5876),
#         'Doha': (25.2854, 51.5310),
#         'Amman': (31.9515, 35.9349),
#         'Erbil': (36.1924, 43.9935),
#         'Haifa': (32.7940, 34.9896)
#     }
    
#     # Filter to locations with coords and data
#     data = []
#     for loc, count in location_counts.items():
#         if loc in coords:
#             data.append({
#                 'Location': loc,
#                 'Latitude': coords[loc][0],
#                 'Longitude': coords[loc][1],
#                 'Mentions': count
#             })
    
#     df = pd.DataFrame(data)
    
#     # Heatmap with density
#     fig = px.density_mapbox(
#         df, lat='Latitude', lon='Longitude', z='Mentions',
#         radius=20,
#         center=dict(lat=30, lon=45),
#         zoom=3,
#         mapbox_style="open-street-map",
#         title="Heatmap of War-Related News Mentions"
#     )
#     st.plotly_chart(fig, use_container_width=True)
    
#     # Or bubble map for counts
#     fig_bubble = px.scatter_mapbox(
#         df, lat='Latitude', lon='Longitude', size='Mentions', color='Mentions',
#         hover_name='Location', size_max=50,
#         mapbox_style="open-street-map",
#         center=dict(lat=30, lon=45), zoom=3,
#         title="Bubble Map: News Intensity by Location"
#     )
#     st.plotly_chart(fig_bubble, use_container_width=True)
#     print("Displayed heatmap and bubble map.")
# else:
#     st.info("No war-related locations detected. Check keywords or feeds.")
#     print("No war-related locations detected. Check keywords or feeds.")

# # Show sample news
# st.subheader("Sample Articles")
# for entry in news[:10]:
#     with st.expander(entry['title'][:50] + '...'):
#         st.write(f"**Source:** {entry['source']}")
#         st.write(entry['summary'][:200] + '...')
#         st.write(f"[Read more]({entry['link']})")




import streamlit as st
import feedparser
import pandas as pd
from collections import Counter
import re
from geopy.geocoders import Nominatim
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium import CircleMarker
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from folium import DivIcon

# Streamlit app title
st.title("TruEstates Crisis Radar")

# RSS feeds - confirmed/discovered URLs
rss_feeds = {
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Arab Times": "https://www.arabtimesonline.com/rssfeed/47/",  # From web:17, web:20
    "Khaleej Times": "https://www.khaleejtimes.com/stories.rss?botrequest=true"  # Assumed standard /rss
}

# Keywords for filtering war-related news
war_keywords = ['iran', 'uae', 'united arab emirates', 'dubai', 'abu dhabi', 'emirate', 'oil', 'trade', 'israel', 'usa', 'war', 'strike', 'attack', 'missile', 'tehran', 'gaza', 'lebanon']

@st.cache_data(ttl=300)  # Cache for 5 min
def fetch_and_filter_news():
    all_entries = []
    for name, url in rss_feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:  # Limit to recent 20 per feed
                title = entry.title.lower()
                summary = (entry.get('summary', '') + ' ' + entry.get('description', '')).lower()
                if any(kw in title or kw in summary for kw in war_keywords):
                    all_entries.append({
                        'source': name,
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', '')
                    })
        except Exception as e:
            st.warning(f"Failed to fetch {name}: {e}")
    return all_entries

news = fetch_and_filter_news()
st.success(f"Fetched {len(news)} relevant articles.")

# Sidebar: vertical rolling news ticker (auto-scroll)
try:
    if news:
        # Build ticker items HTML (duplicate for seamless loop)
        items_html = ""
        for entry in news:
            title = entry.get('title', '').replace('"', '&quot;')
            link = entry.get('link', '#')
            src = entry.get('source', '')
            pub = entry.get('published', '')
            items_html += f"<div class='ticker__item'><a href='{link}' target='_blank'>{title}</a><div class='meta'> {src} • {pub}</div></div>"

        # Duplicate items to create seamless scrolling
        ticker_html = f"""
        <div class='ticker'>
          <div class='ticker__wrap'>
            {items_html}
            {items_html}
          </div>
        </div>
        <style>
        .ticker{{
            height: 420px; 
            overflow: hidden;
            background: #000;
            padding: 10px;
            border-radius: 8px;
        }}
        .ticker__wrap{{
            display: flex;
            flex-direction: column; 
            animation: scroll 45s linear infinite;
        }}
        .ticker__item{{
            padding: 12px 16px; 
            border-bottom: 1px solid rgba(255,255,255,0.08);
            background: rgba(0,0,0,0.4);
            margin-bottom: 4px;
            border-radius: 6px;
        }}
        .ticker__item a{{
            color: #7CFC00; 
            text-decoration: none; 
            font-weight: 600;
            font-family: 'Courier New', monospace;
            font-size: 16px;
        }}
        .ticker__item a:hover{{
            color: #00ff00;
            text-shadow: 0 0 8px #7CFC00;
        }}
        .ticker__item .meta{{
            font-size: 12px; 
            color: #888;
            margin-top: 4px;
        }}
        @keyframes scroll{{
            0% {{ transform: translateY(0%); }}
            100% {{ transform: translateY(-50%); }}
        }}
        </style>
        """

        # Render ticker in main area and sidebar
        # st.markdown(ticker_html, unsafe_allow_html=True)
        st.sidebar.markdown("## Latest News", unsafe_allow_html=False)
        st.sidebar.markdown(ticker_html, unsafe_allow_html=True)
    else:
        st.sidebar.info('No recent headlines available')
except Exception:
    # Fall back to simple list of titles if rendering fails
    with st.sidebar:
        st.write('Latest headlines')
        for entry in news:
            st.markdown(f"- [{entry.get('title','')}]({entry.get('link','#')})")

# Extract locations - simple regex for cities/countries + predefined war hot spots
location_patterns = {
    'Tehran': 'tehran|iran',
    'Tel Aviv': 'tel aviv|israel',
    'Beirut': 'beirut|lebanon',
    'Baghdad': 'baghdad|iraq',
    'Kuwait City': 'kuwait',
    'Dubai': 'dubai|uae',
    'Abu Dhabi': 'abu dhabi|uae',
    'Riyadh': 'riyadh|saudi',
    'Manama': 'manama|bahrain',
    'Doha': 'doha|qatar',
    'Amman': 'amman|jordan',
    'Erbil': 'erbil',
    'Haifa': 'haifa'
}

def extract_locations(text):
    locations = []
    text_lower = text.lower()
    for loc, pattern in location_patterns.items():
        if re.search(pattern, text_lower):
            locations.append(loc)
    return locations

# Extract and count locations
location_counts = Counter()
for entry in news:
    text = entry['title'] + ' ' + entry['summary']
    locs = extract_locations(text)
    location_counts.update(locs)



if location_counts:
    # Coordinates for known locations (manual mapping for reliability)
    coords = {
        'Tehran': (35.6892, 51.3890),
        'Tel Aviv': (32.0853, 34.7818),
        'Beirut': (33.8938, 35.5018),
        'Baghdad': (33.3152, 44.3661),
        'Kuwait City': (29.3759, 47.9774),
        'Dubai': (25.2048, 55.2708),
        'Abu Dhabi': (24.4539, 54.3773),
        'Riyadh': (24.7136, 46.6753),
        'Manama': (26.2235, 50.5876),
        'Doha': (25.2854, 51.5310),
        'Amman': (31.9515, 35.9349),
        'Erbil': (36.1924, 43.9935),
        'Haifa': (32.7940, 34.9896)
    }
    
    # Filter to locations with coords and data
    data = []
    for loc, count in location_counts.items():
        if loc in coords:
            data.append({
                'Location': loc,
                'Latitude': coords[loc][0],
                'Longitude': coords[loc][1],
                'Mentions': count
            })
    
    df = pd.DataFrame(data)
    
    # Prefer a Folium / Leaflet map with a dark basemap for a neon look
    try:
        m = folium.Map(location=[30, 45], zoom_start=3, tiles='CartoDB dark_matter')

        # Build heatmap data (lat, lon, weight)
        heat_data = [[row['Latitude'], row['Longitude'], row['Mentions']] for _, row in df.iterrows()]

        # Add heat layer for glowing intensity
        HeatMap(heat_data, radius=25, blur=15, gradient={0.2: 'lime', 0.6: 'orange', 1.0: 'red'}).add_to(m)

        # Add pulsing markers using DivIcon + CSS for neon/pulse effect
        
        for _, row in df.iterrows():
                weight = int(row['Mentions'])
                color = '#32CD32' if weight <= 2 else '#FF4500'
                size_px = max(12, min(50, weight * 8))
                html = f"""
                <div style="position:relative; width:{size_px}px; height:{size_px}px;">
                    <div style="
                        width:{size_px}px; height:{size_px}px; border-radius:50%; background:{color}; opacity:0.9;
                        box-shadow:0 0 12px {color}, 0 0 24px {color}; position:absolute; left:0; top:0;
                    "></div>
                    <div style="
                        width:{size_px}px; height:{size_px}px; border-radius:50%; background:{color};
                        position:absolute; left:0; top:0; animation:pulse 1.8s infinite;
                        opacity:0.6;
                    "></div>
                </div>
                <style>
                @keyframes pulse {{
                    0% {{ transform: scale(0.8); opacity: 0.9; }}
                    70% {{ transform: scale(2.4); opacity: 0.0; }}
                    100% {{ transform: scale(2.8); opacity: 0.0; }}
                }}
                </style>
                """

                folium.map.Marker(
                        location=(row['Latitude'], row['Longitude']),
                        icon=DivIcon(html=html),
                        popup=f"{row['Location']}: {row['Mentions']} mentions"
                ).add_to(m)

        # Display Folium map in Streamlit
        st_folium(m, width=900)
        print("Displayed Folium neon-style heatmap with pulsing markers.")

    except Exception:
        # Fallback to Plotly if folium/streamlit_folium are unavailable
        fig = px.density_mapbox(
            df, lat='Latitude', lon='Longitude', z='Mentions',
            radius=20,
            center=dict(lat=30, lon=45),
            zoom=3,
            mapbox_style="open-street-map",
            title="Heatmap of War-Related News Mentions (fallback)"
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No war-related locations detected. Check keywords or feeds.")
    print("No war-related locations detected. Check keywords or feeds.")


st.subheader("Location Mentions")
# Build a DataFrame with the index named 'Location' and column 'No. of events'
df_counts = pd.DataFrame.from_dict(location_counts, orient='index', columns=['No. of events'])
df_counts.index.name = 'Location'
df_counts = df_counts.sort_values('No. of events', ascending=False)
st.write(df_counts)

# Show sample news
st.subheader("Sample Articles")
for entry in news[:6]:
    with st.expander(entry['title'][:50] + '...'):
        st.write(f"**Source:** {entry['source']}")
        st.write(entry['summary'][:200] + '...')
        st.write(f"[Read more]({entry['link']})")

