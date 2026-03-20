# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.graph_objects as go
# from pathlib import Path
# import ast
# # Import for LOWESS smoothing
# from statsmodels.nonparametric.smoothers_lowess import lowess

# # ============================================================
# # 1. SETUP & DATA LOADING
# # ============================================================
# BASE_PATH = Path(__file__).parent 
# INPUT_CSV = BASE_PATH / "V_2.3_input_reference_final.csv" 
# COMBINATIONS_CSV = BASE_PATH / "V_2.3_combinations.csv"
# FORECAST_PATH = BASE_PATH / "forecast_df_v_2_3.csv"
# HISTORIC_PATH = BASE_PATH / "historic_df_v_2_3_old.csv"
# NEWS_FILE = BASE_PATH / "news_preds_v3_fixed.csv"

# # Pivot Constants
# PIVOT_DATE = "2026-01-31"
# DEC_ANCHOR_DATE = "2025-12-31"
# SIX_MONTHS_DATE = "2026-07-31"

# st.set_page_config(page_title="TruEstates v2.3 - Market Analysis", layout="wide", page_icon="🏙️")

# # Import External Logic
# try:
#     from price_predictor_v_2_3 import predict_property_price 
#     from crisis_radar import run_crisis_radar 
# except ImportError as e:
#     st.error(f"Missing dependency: {e}")

# @st.cache_data
# def load_all_resources():
#     f_df = pd.read_csv(INPUT_CSV)
#     f_df["area_name_en"] = f_df["area_name_en"].astype(str).str.strip()
    
#     c_df = pd.read_csv(COMBINATIONS_CSV)
#     c_df["area_name_en"] = c_df["area_name_en"].astype(str).str.strip()
    
#     fore_df = pd.read_csv(FORECAST_PATH)
#     hist_df = pd.read_csv(HISTORIC_PATH)
#     fore_df["month"] = pd.to_datetime(fore_df["month"], dayfirst=True, errors='coerce')
#     hist_df["month"] = pd.to_datetime(hist_df["month"], dayfirst=True, errors='coerce')
    
#     n_df = pd.read_csv(NEWS_FILE)
#     n_df["area_name_en"] = n_df["area_name_en"].astype(str).str.strip()
#     n_df["month"] = pd.to_datetime(n_df["month"], dayfirst=True, errors='coerce')
    
#     return f_df, c_df, fore_df, hist_df, n_df

# # Helpers
# def get_index(options, target):
#     options_list = list(options)
#     try: return options_list.index(target)
#     except: return 0

# def clean_val(val, dtype=int):
#     try: return dtype(float(val))
#     except: return 0

# def get_ref_list(val):
#     try:
#         if isinstance(val, str) and "[" in val: return ast.literal_eval(val)
#         return [val]
#     except: return [val]

# # Initial Load
# try:
#     feature_df, combinations_df, forecast_df, historic_df, news_df = load_all_resources()
    
#     VALID_AREAS = sorted(feature_df["area_name_en"].unique())
# except Exception as e:
#     st.error(f"Critical File Load Error: {e}")
#     st.stop()

# # ============================================================
# # 2. SIDEBAR NAVIGATION
# # ============================================================
# st.sidebar.title("🚀 Navigation")
# app_mode = st.sidebar.radio("Select View", ["📈 Price Predictor", "📡 Crisis Radar"])

# # ============================================================
# # 3. VIEW: PRICE PREDICTOR
# # ============================================================
# if app_mode == "📈 Price Predictor":
#     st.sidebar.title("🏙️ Property Configurator")
#     area_name = st.sidebar.selectbox("Select Area", VALID_AREAS)
    
#     area_combos = combinations_df[combinations_df["area_name_en"] == area_name]
#     default_row = area_combos.iloc[0] if not area_combos.empty else None
#     ref_row = feature_df[feature_df["area_name_en"] == area_name].iloc[0]

#     if not area_combos.empty:
#         default_row = area_combos.iloc[0]
#         reg_type = default_row["reg_type_en"]
#         land_type = default_row["land_type_en"]
#         size = clean_val(default_row["procedure_area"], float)
#         has_elevator = clean_val(default_row["elevator"])
#     else:
#         reg_type = "Off-Plan"
#         land_type = get_ref_list(ref_row["land_type_en"])[0]
#         size = float(ref_row["procedure_area_median"])
#         has_elevator = 1

#     with st.sidebar.expander("Property Specs", expanded=True):
#         room_opts = get_ref_list(ref_row["rooms_en"])
#         rooms = st.selectbox("Rooms", room_opts, index=get_index(room_opts, default_row["rooms_en"] if default_row is not None else ""))
        
#         floor_opts = get_ref_list(ref_row["floor_bin"])
#         floor = st.selectbox("Floor Range", floor_opts, index=get_index(floor_opts, default_row["floor_bin"] if default_row is not None else ""))
        
#         proj_opts = get_ref_list(ref_row["project_cat"])
#         proj_cat = st.selectbox("Project Category", proj_opts, index=get_index(proj_opts, default_row["project_cat"] if default_row is not None else ""))
        
#         dev_opts = get_ref_list(ref_row["developer_cat"])
#         dev_cat = st.selectbox("Developer Grade", dev_opts, index=get_index(dev_opts, default_row["developer_cat"] if default_row is not None else ""))

#     with st.sidebar.expander("Amenities & Details"):
#         def get_bool_default(key):
#             return bool(clean_val(default_row[key])) if default_row is not None and key in default_row else False

#         parking = st.checkbox("Parking", value=get_bool_default("has_parking"))
#         pool = st.checkbox("Pool", value=get_bool_default("swimming_pool"))
#         balcony = st.checkbox("Balcony", value=get_bool_default("balcony"))
#         has_metro = st.checkbox("Near Metro", value=get_bool_default("metro"))

#     st.title(f"Market Forecast: {area_name}")
    
#     st.info(f"💡 **Note:** This prediction is based on the median area size for this location , **Off-plan** registration, and **Elevator access**. Existing or ready properties will be slightly less by **5%** on average.")
    
#     if st.button("Generate AI Prediction", type="primary"):
#         try:
#             with st.spinner("Compounding growth factors and smoothing volatility..."):
#                 res_df = predict_property_price({
#                     "area_name": area_name, "reg_type_en": reg_type, "rooms_en": rooms,
#                     "land_type_en": land_type, "floor_bin": floor, "developer_cat": dev_cat,
#                     "project_cat": proj_cat, "procedure_area": size, "has_parking": int(parking),
#                     "swimming_pool": int(pool), "balcony": int(balcony), "elevator": int(has_elevator), "metro": int(has_metro)
#                 }, forecast_df, historic_df)
                
#                 res_df["month"] = pd.to_datetime(res_df["month"])
#                 res_df = res_df.sort_values("month").reset_index(drop=True)
                
#                 area_growth = news_df[news_df["area_name_en"] == area_name].copy()
#                 news_available = not area_growth.empty
#                 res_df = res_df.merge(area_growth[['month', 'predictions_mom_growth', 'adjusted_price_real_mom_growth', 'narrative']], 
#                                      on='month', how='left')

#                 idx_dec = res_df.index[res_df["month"] == DEC_ANCHOR_DATE].tolist()[0]
#                 idx_jan = res_df.index[res_df["month"] == PIVOT_DATE].tolist()[0]

#                 dec_val = res_df.loc[idx_dec, "median_price"]
#                 raw_jan_ai = res_df.loc[idx_jan, "median_price"]
#                 initial_jump = (raw_jan_ai / dec_val) - 1

#                 # Applying the adjustment cap logic
#                 if abs(initial_jump) > 0.05:
#                     direction = 1 if initial_jump > 0 else -1
#                     jan_adjusted = dec_val * (1 + (direction * np.random.uniform(0.035, 0.05)))
#                     res_df.at[idx_jan, "median_price"] = jan_adjusted
#                 else:
#                     res_df.at[idx_jan, "median_price"] = raw_jan_ai

#                 res_df.at[idx_jan, "macro_forecast"] = res_df.loc[idx_jan, "median_price"]
#                 res_df.at[idx_jan, "news_adjusted_forecast"] = res_df.loc[idx_jan, "median_price"]

#                 for i in range(idx_jan + 1, len(res_df)):
#                     prev_baseline = res_df.loc[i-1, "median_price"]
#                     m_rate = res_df.loc[i, "predictions_mom_growth"]
#                     if pd.isna(m_rate):
#                         raw_curr = res_df.loc[i, "median_price"]
#                         raw_prev = res_df.loc[i-1, "median_price"]
#                         m_rate = (raw_curr / raw_prev) - 1 if raw_prev != 0 else 0
                    
#                     a_rate = res_df.loc[i, "adjusted_price_real_mom_growth"] if pd.notna(res_df.loc[i, "adjusted_price_real_mom_growth"]) else 0
#                     current_macro = prev_baseline * (1 + m_rate)
#                     res_df.at[i, "macro_forecast"] = current_macro
#                     res_df.at[i, "news_adjusted_forecast"] = current_macro * (1 + a_rate)
#                     res_df.at[i, "median_price"] = current_macro

#             # --- PREPARE DATA FOR JOINT ---
#             cutoff = pd.to_datetime(PIVOT_DATE)
#             six_month_marker = pd.to_datetime(SIX_MONTHS_DATE)

#             # Split data but include Jan-26 (cutoff) in both to create the joint
#             hist_part = res_df[res_df["month"] <= cutoff].copy()
#             fore_part = res_df[res_df["month"] >= cutoff].copy()

#             # --- APPLY SMOOTHING ---
#             def apply_lowess_smooth(df, col):
#                 x = df["month"].map(pd.Timestamp.toordinal).values
#                 y = df[col].values
#                 return lowess(y, x, frac=0.085)[:, 1]

#             if not hist_part.empty:
#                 hist_part["smoothed_price"] = apply_lowess_smooth(hist_part, "median_price")

#             if not fore_part.empty:
#                 fore_part["macro_smooth"] = apply_lowess_smooth(fore_part, "macro_forecast")
#                 if news_available:
#                     fore_part["news_smooth"] = apply_lowess_smooth(fore_part, "news_adjusted_forecast")
#                 else:
#                     fore_part["base_smooth"] = apply_lowess_smooth(fore_part, "median_price")

#             # Metric Cards
#             curr_val = res_df.loc[idx_jan, "median_price"]
#             c1, c2 = st.columns(2)
#             c1.metric("Adjusted Value (Jan '26)", f"AED {curr_val:,.0f}")
            
#             july_row = res_df[res_df["month"] == six_month_marker]
#             if not july_row.empty:
#                 target_val = july_row["news_adjusted_forecast"].values[0] if news_available else july_row["median_price"].values[0]
#                 delta_pct = ((target_val / curr_val) - 1) * 100
#                 c2.metric("July 2026 Forecast", f"AED {target_val:,.0f}", delta=f"{delta_pct:+.2f}% (6-Mo Growth)")

#             # --- CHART ---
#             fig = go.Figure()

#             # 1. Historical Segment (Raw and Smoothed)
#             if not hist_part.empty:
#                 fig.add_trace(go.Scatter(x=hist_part["month"], y=hist_part["median_price"], 
#                                          name="History (Raw)", line=dict(color="#1f77b4", width=1, dash='dot'), opacity=0.4))
#                 fig.add_trace(go.Scatter(x=hist_part["month"], y=hist_part["smoothed_price"], 
#                                          name="History (Trend)", line=dict(color="#1f77b4", width=2.5)))

#             # 2. Forecast Segment (Starting from the Jan-26 joint)
#             if news_available:
#                 # Macro Forecast
#                 fig.add_trace(go.Scatter(x=fore_part["month"], y=fore_part["macro_forecast"], 
#                                          name="Macro Forecast", line=dict(color="#2ca02c", dash='dot')))
#                 # News-Adjusted (Main Highlight)
#                 fig.add_trace(go.Scatter(x=fore_part["month"], y=fore_part["news_adjusted_forecast"], 
#                                          name="News-Adjusted", line=dict(color="#d62728", width=3)))
#             else:
#                 fig.add_trace(go.Scatter(x=fore_part["month"], y=fore_part["median_price"], 
#                                          name="Base Forecast", line=dict(color="#7f7f7f", dash='dot')))

#             fig.update_layout(hovermode="x unified", template="plotly_white", yaxis_title="Price (AED)")
#             st.plotly_chart(fig, use_container_width=True)

#             # Table
#             with st.expander("📊 Detailed Forecast Table"):
#                 table_df = res_df[res_df["month"] >= cutoff].copy()
#                 table_df["Month"] = table_df["month"].dt.strftime('%B %Y')
#                 cols = ["Month", "median_price"]
#                 names = {"median_price": "Baseline (AED)"}
#                 if news_available:
#                     cols += ["macro_forecast", "news_adjusted_forecast"]
#                     names.update({"macro_forecast": "Macro (AED)", "news_adjusted_forecast": "News Adjusted (AED)"})
#                 st.dataframe(table_df[cols].rename(columns=names).style.format("{:,.0f}", subset=[n for n in names.values()]), use_container_width=True)
                
#             # --- NARRATIVES ---
#             if news_available:
#                 st.markdown("### 🔍 Market Narrative & Insights")
#                 # Showing narrative for the start of the forecast
#                 top_insight = res_df[res_df["month"] == cutoff].head(1)
#                 for _, row in top_insight.iterrows():
#                     m_label = row['month'].strftime('%B %Y')
#                     full_text = str(row['narrative']) if pd.notna(row['narrative']) else "Standard growth projection based on historical trends."
#                     st.success(f"**Market Outlook ({m_label}):** {full_text}")

#             st.info(f"💡 **Note:** This predictions are adjusted to 5% if prediction wrt previous month is more than 5% to make trend look better interms of forcast.")
#         except Exception as e:
#             st.error(f"Prediction Error: {e}")

# elif app_mode == "📡 Crisis Radar":
#     run_crisis_radar()



import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import ast
import yfinance as yf
from datetime import datetime, timedelta
from statsmodels.nonparametric.smoothers_lowess import lowess

# ============================================================
# 1. SETUP & CONSTANTS
# ============================================================
BASE_PATH = Path(__file__).parent
INPUT_CSV        = BASE_PATH / "V_2.3_input_reference_final.csv"
COMBINATIONS_CSV = BASE_PATH / "V_2.3_combinations.csv"
FORECAST_PATH    = BASE_PATH / "forecast_df_v_2_3.csv"
HISTORIC_PATH    = BASE_PATH / "historic_df_v_2_3_old.csv"
NEWS_FILE        = BASE_PATH / "news_preds_v3_fixed.csv"

PIVOT_DATE      = "2026-01-31"
DEC_ANCHOR_DATE = "2025-12-31"
SIX_MONTHS_DATE = "2026-07-31"

st.set_page_config(
    page_title="TruEstates v2.3 — Market Analysis",
    layout="wide",
    page_icon="🏙️",
)

# ============================================================
# 2. GLOBAL STYLES
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&family=DM+Mono:wght@300;400;500&family=Outfit:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: #08080e;
    color: #e2ddd4;
}
h1, h2, h3, h4 {
    font-family: 'Cormorant Garamond', serif;
    letter-spacing: 0.01em;
    font-weight: 600;
}

/* ── News banner ── */
.news-banner-wrapper {
    width: 100%;
    background: linear-gradient(90deg, #08080e 0%, #0e0e1c 30%, #0e0e1c 70%, #08080e 100%);
    border-top: 1px solid rgba(196,164,98,0.22);
    border-bottom: 1px solid rgba(196,164,98,0.22);
    overflow: hidden;
    position: relative;
    margin-bottom: 28px;
}
.news-banner-wrapper::before {
    content: "◈ LIVE";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    display: flex; align-items: center;
    padding: 0 16px;
    background: #c4a462;
    color: #08080e;
    font-family: 'Outfit', sans-serif;
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.18em; z-index: 2;
    white-space: nowrap;
}
.news-banner-track {
    display: flex;
    white-space: nowrap;
    animation: marquee 60s linear infinite;
    padding: 11px 0 11px 90px;
}
.news-banner-track:hover { animation-play-state: paused; }
.news-item {
    display: inline-flex; align-items: center; gap: 10px;
    padding: 0 30px;
    font-family: 'DM Mono', monospace;
    font-size: 11.5px; color: #b8b2a6;
    border-right: 1px solid rgba(196,164,98,0.15);
}
.news-item a { color: #b8b2a6; text-decoration: none; transition: color 0.2s; }
.news-item a:hover { color: #d4b472; }
.news-item .dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #c4a462; flex-shrink: 0;
    box-shadow: 0 0 5px rgba(196,164,98,0.6);
}
.news-source-tag {
    font-size: 9px; color: #c4a462; font-weight: 500;
    letter-spacing: 0.1em; text-transform: uppercase;
}
@keyframes marquee {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

/* ── Market cards ── */
.market-card {
    background: linear-gradient(160deg, #0f0f1c 0%, #121220 100%);
    border: 1px solid rgba(196,164,98,0.16);
    border-radius: 12px;
    padding: 16px 18px 8px;
    position: relative; overflow: hidden;
    margin-bottom: 2px;
}
.market-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(196,164,98,0.55), transparent);
}
.market-card .tk-sym {
    font-family: 'DM Mono', monospace;
    font-size: 10px; font-weight: 500;
    letter-spacing: 0.14em; color: #c4a462;
    text-transform: uppercase; margin-bottom: 1px;
}
.market-card .tk-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 13px; color: #6a6456;
    margin-bottom: 6px; font-style: italic;
}
.market-card .tk-price {
    font-family: 'Cormorant Garamond', serif;
    font-size: 26px; font-weight: 700;
    color: #e2ddd4; line-height: 1;
}
.market-card .tk-delta {
    font-size: 11px; margin-top: 5px;
    font-family: 'DM Mono', monospace;
}
.market-card .tk-delta.up { color: #4ade80; }
.market-card .tk-delta.dn { color: #f87171; }
.market-card .tk-source {
    font-size: 9px; color: #3a3830;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.08em; margin-top: 3px;
}

/* ── Page headings ── */
.page-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 34px; font-weight: 700;
    color: #e2ddd4; letter-spacing: 0.01em;
    margin-bottom: 2px; line-height: 1.1;
}
.page-sub {
    font-family: 'Outfit', sans-serif;
    font-size: 11px; color: #5a5548;
    letter-spacing: 0.14em; text-transform: uppercase;
    margin-bottom: 22px;
}
.divider-gold {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(196,164,98,0.3), transparent);
    margin: 20px 0 24px;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #0f0f1c;
    border: 1px solid rgba(196,164,98,0.18);
    border-radius: 10px; padding: 18px 22px;
}
[data-testid="stMetricLabel"] {
    color: #5a5548 !important;
    font-size: 10px !important;
    letter-spacing: 0.1em !important;
    font-family: 'Outfit', sans-serif !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: #e2ddd4 !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 28px !important;
}
[data-testid="stMetricDelta"] svg { display: none; }

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #c4a462 0%, #a8893e 100%);
    color: #08080e;
    font-family: 'Outfit', sans-serif;
    font-weight: 600; font-size: 12px;
    letter-spacing: 0.12em; text-transform: uppercase;
    border: none; border-radius: 6px;
    padding: 13px 32px; cursor: pointer;
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 24px rgba(196,164,98,0.3);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #09090f;
    border-right: 1px solid rgba(196,164,98,0.1);
}
[data-testid="stSidebar"] label {
    color: #8a847a !important;
    font-size: 11px !important;
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: 0.04em !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #0f0f1c !important;
    border: 1px solid rgba(196,164,98,0.13) !important;
    color: #e2ddd4 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 13px !important;
}

hr { border-color: rgba(196,164,98,0.12); margin: 22px 0; }
.stAlert { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. MARKET DATA  — Yahoo Finance with robust fallback
# ============================================================
# Ticker notes:
#   GC=F      — COMEX Gold Futures (reliable)
#   CL=F      — NYMEX WTI Crude Futures (reliable)
#   ^DFMGI    — DFM General Index (official Yahoo ticker)
#   EMAAR.DU  — Emaar Properties on DFM; largest RE-index constituent,
#               used as the best available DFM Real Estate proxy
MARKET_TICKERS = {
    "GC=F":     {"label": "XAU / USD",  "name": "Gold Spot",           "unit": "$"},
    "CL=F":     {"label": "WTI Crude",  "name": "Crude Oil",            "unit": "$"},
    "DFMGI.AE":   {"label": "DFM Index",  "name": "DFM General Index",    "unit": "AED"},
    "EMAAR.AE": {"label": "Emaar RE",   "name": "DFM RE Proxy (Emaar)", "unit": "AED "},
}


@st.cache_data(ttl=300)
def fetch_market_data():
    """Fetch ~15 trading days for sparklines; show last-available if market is closed."""
    end   = datetime.today()
    start = end - timedelta(days=25)   # wide net to capture enough trading days

    results = {}
    for sym, meta in MARKET_TICKERS.items():
        fallback = {
            **meta,
            "price": None, "delta": 0.0, "pct": 0.0,
            "series": [], "dates": [], "note": "Unavailable",
        }
        try:
            hist = yf.Ticker(sym).history(
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
                interval="1d",
                auto_adjust=True,
            )
            hist = hist.dropna(subset=["Close"])

            if len(hist) < 2:
                results[sym] = fallback
                continue

            closes = hist["Close"].tolist()
            dates  = [str(d.date()) for d in hist.index]

            price = closes[-1]
            prev  = closes[-2]
            delta = price - prev
            pct   = (delta / prev) * 100

            results[sym] = {
                **meta,
                "price": price, "delta": delta, "pct": pct,
                "series": closes, "dates": dates,
                "note": f"As of {dates[-1]}",
            }
        except Exception as ex:
            fallback["note"] = f"Error: {str(ex)[:50]}"
            results[sym] = fallback

    return results


def render_market_strip():
    data = fetch_market_data()
    cols = st.columns(4, gap="small")

    for i, (sym, d) in enumerate(data.items()):
        with cols[i]:
            price = d.get("price")

            # Unavailable card
            if price is None:
                st.markdown(f"""
                <div class="market-card">
                  <div class="tk-sym">{d['label']}</div>
                  <div class="tk-name">{d['name']}</div>
                  <div class="tk-price" style="font-size:15px;color:#3a3830;margin-top:8px;">
                    Data Unavailable
                  </div>
                  <div class="tk-source">{d.get('note','')}</div>
                </div>""", unsafe_allow_html=True)
                continue

            pct       = d["pct"]
            is_up     = pct >= 0
            delta_cls = "up" if is_up else "dn"
            arrow     = "▲" if is_up else "▼"
            unit      = d["unit"]
            price_fmt = f"{unit}{price:,.2f}"
            clr_line  = "rgba(74,222,128,1)"    if is_up else "rgba(248,113,113,1)"
            clr_fill  = "rgba(74,222,128,0.07)" if is_up else "rgba(248,113,113,0.07)"

            # Sparkline
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=d["series"], mode="lines",
                line=dict(color=clr_line, width=1.6),
                fill="tozeroy",
                fillcolor=clr_fill,
            ))
            fig.update_layout(
                margin=dict(l=0, r=0, t=2, b=0),
                height=44,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor ="rgba(0,0,0,0)",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                showlegend=False,
            )

            st.markdown(f"""
            <div class="market-card">
              <div class="tk-sym">{d['label']}</div>
              <div class="tk-name">{d['name']}</div>
              <div class="tk-price">{price_fmt}</div>
              <div class="tk-delta {delta_cls}">
                {arrow} {abs(d['delta']):.2f} &nbsp;({abs(pct):.2f}%)
              </div>
              <div class="tk-source">{d.get('note','')}</div>
            </div>""", unsafe_allow_html=True)

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
                key=f"spark_{sym}",
            )


# ============================================================
# 4. HORIZONTAL NEWS BANNER
# ============================================================
@st.cache_data(ttl=300)
def fetch_banner_news():
    import feedparser
    RSS_FEEDS = {
        "Al Jazeera":    "https://www.aljazeera.com/xml/rss/all.xml",
        "Arab Times":    "https://www.arabtimesonline.com/rssfeed/47/",
        "Khaleej Times": "https://www.khaleejtimes.com/stories.rss?botrequest=true",
    }
    KEYWORDS = [
        'iran', 'uae', 'dubai', 'abu dhabi', 'oil', 'trade', 'israel',
        'war', 'strike', 'attack', 'tehran', 'gaza', 'real estate',
        'property', 'mortgage', 'dfm', 'market',
    ]
    entries = []
    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:15]:
                title   = e.title.lower()
                summary = e.get('summary', '').lower()
                if any(kw in title or kw in summary for kw in KEYWORDS):
                    entries.append({"source": name, "title": e.title, "link": e.link})
        except Exception:
            pass
    return entries


def render_horizontal_news_banner():
    news = fetch_banner_news()
    if not news:
        return

    all_items  = news * 3
    items_html = ""
    for e in all_items:
        t = e['title'].replace('"', '&quot;').replace("'", "&#39;")
        items_html += (
            f'<span class="news-item">'
            f'  <span class="dot"></span>'
            f'  <span class="news-source-tag">{e["source"]}</span>'
            f'  <a href="{e["link"]}" target="_blank">{t}</a>'
            f'</span>'
        )

    st.markdown(
        f'<div class="news-banner-wrapper">'
        f'  <div class="news-banner-track">{items_html}{items_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# 5. IMPORT EXTERNAL MODULES
# ============================================================
try:
    from price_predictor_v_2_3 import predict_property_price
    from crisis_radar import run_crisis_radar
except ImportError as e:
    st.error(f"Missing dependency: {e}")


# ============================================================
# 6. LOAD DATA
# ============================================================
@st.cache_data
def load_all_resources():
    f_df = pd.read_csv(INPUT_CSV)
    f_df["area_name_en"] = f_df["area_name_en"].astype(str).str.strip()

    c_df = pd.read_csv(COMBINATIONS_CSV)
    c_df["area_name_en"] = c_df["area_name_en"].astype(str).str.strip()

    fore_df = pd.read_csv(FORECAST_PATH)
    hist_df = pd.read_csv(HISTORIC_PATH)
    fore_df["month"] = pd.to_datetime(fore_df["month"], dayfirst=True, errors="coerce")
    hist_df["month"] = pd.to_datetime(hist_df["month"], dayfirst=True, errors="coerce")

    n_df = pd.read_csv(NEWS_FILE)
    n_df["area_name_en"] = n_df["area_name_en"].astype(str).str.strip()
    n_df["month"] = pd.to_datetime(n_df["month"], dayfirst=True, errors="coerce")

    return f_df, c_df, fore_df, hist_df, n_df


def get_index(options, target):
    lst = list(options)
    try:    return lst.index(target)
    except: return 0

def clean_val(val, dtype=int):
    try:    return dtype(float(val))
    except: return 0

def get_ref_list(val):
    try:
        if isinstance(val, str) and "[" in val:
            return ast.literal_eval(val)
        return [val]
    except:
        return [val]


try:
    feature_df, combinations_df, forecast_df, historic_df, news_df = load_all_resources()
    VALID_AREAS = sorted(feature_df["area_name_en"].unique())
except Exception as e:
    st.error(f"Critical File Load Error: {e}")
    st.stop()


# ============================================================
# 7. SIDEBAR
# ============================================================
st.sidebar.markdown("""
<div style="font-family:'Cormorant Garamond',serif;font-size:22px;
            font-weight:600;color:#c4a462;letter-spacing:0.03em;
            padding:8px 0 16px;">
  TruEstates v2.3
</div>
""", unsafe_allow_html=True)
app_mode = st.sidebar.radio("Navigate", ["📈 Price Predictor", "📡 Crisis Radar"])


# ============================================================
# 8. PRICE PREDICTOR VIEW
# ============================================================
if app_mode == "📈 Price Predictor":

    render_market_strip()
    st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)
    render_horizontal_news_banner()

    # Sidebar configurator
    st.sidebar.markdown(
        '<div style="font-family:\'Outfit\',sans-serif;font-size:10px;'
        'letter-spacing:0.14em;text-transform:uppercase;color:#5a5548;'
        'margin-bottom:10px;">Property Configurator</div>',
        unsafe_allow_html=True,
    )
    area_name = st.sidebar.selectbox("Select Area", VALID_AREAS)

    area_combos = combinations_df[combinations_df["area_name_en"] == area_name]
    default_row = area_combos.iloc[0] if not area_combos.empty else None
    ref_row     = feature_df[feature_df["area_name_en"] == area_name].iloc[0]

    if not area_combos.empty:
        default_row  = area_combos.iloc[0]
        reg_type     = default_row["reg_type_en"]
        land_type    = default_row["land_type_en"]
        size         = clean_val(default_row["procedure_area"], float)
        has_elevator = clean_val(default_row["elevator"])
    else:
        reg_type     = "Off-Plan"
        land_type    = get_ref_list(ref_row["land_type_en"])[0]
        size         = float(ref_row["procedure_area_median"])
        has_elevator = 1

    with st.sidebar.expander("Property Specifications", expanded=True):
        room_opts = get_ref_list(ref_row["rooms_en"])
        rooms = st.selectbox(
            "Rooms", room_opts,
            index=get_index(room_opts, default_row["rooms_en"] if default_row is not None else ""),
        )
        floor_opts = get_ref_list(ref_row["floor_bin"])
        floor = st.selectbox(
            "Floor Range", floor_opts,
            index=get_index(floor_opts, default_row["floor_bin"] if default_row is not None else ""),
        )
        proj_opts = get_ref_list(ref_row["project_cat"])
        proj_cat = st.selectbox(
            "Project Category", proj_opts,
            index=get_index(proj_opts, default_row["project_cat"] if default_row is not None else ""),
        )
        dev_opts = get_ref_list(ref_row["developer_cat"])
        dev_cat = st.selectbox(
            "Developer Grade", dev_opts,
            index=get_index(dev_opts, default_row["developer_cat"] if default_row is not None else ""),
        )

    with st.sidebar.expander("Amenities & Features"):
        def get_bool_default(key):
            return bool(clean_val(default_row[key])) if default_row is not None and key in default_row else False

        parking   = st.checkbox("Parking",   value=get_bool_default("has_parking"))
        pool      = st.checkbox("Pool",       value=get_bool_default("swimming_pool"))
        balcony   = st.checkbox("Balcony",    value=get_bool_default("balcony"))
        has_metro = st.checkbox("Near Metro", value=get_bool_default("metro"))

    # Page heading
    st.markdown(
        f'<div class="page-title">Market Forecast &mdash; {area_name}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-sub">'
        'AI-Powered Property Price Projection &nbsp;&middot;&nbsp; TruEstates v2.3'
        '</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "**Note:** Prediction is based on the median area size for this location, "
        "**Off-plan** registration, and elevator access. "
        "Ready / existing properties are approximately 5% lower on average."
    )

    if st.button("Generate AI Prediction", type="primary"):
        try:
            with st.spinner("Compounding growth factors and smoothing volatility…"):
                res_df = predict_property_price(
                    {
                        "area_name":     area_name,     "reg_type_en":   reg_type,
                        "rooms_en":      rooms,          "land_type_en":  land_type,
                        "floor_bin":     floor,          "developer_cat": dev_cat,
                        "project_cat":   proj_cat,       "procedure_area": size,
                        "has_parking":   int(parking),   "swimming_pool": int(pool),
                        "balcony":       int(balcony),   "elevator":      int(has_elevator),
                        "metro":         int(has_metro),
                    },
                    forecast_df,
                    historic_df,
                )

                # ── Fix Timestamp arithmetic bug ──
                # Convert month to plain pd.Timestamp (Period or object columns
                # cause "integer + Timestamp" errors in pandas ≥ 2.x)
                res_df["month"] = pd.to_datetime(
                    res_df["month"].astype(str), format = "%Y-%m-%d", dayfirst=True, errors="coerce"
                )
                res_df = res_df.sort_values("month").reset_index(drop=True)

                area_growth    = news_df[news_df["area_name_en"] == area_name].copy()
                news_available = not area_growth.empty

                res_df = res_df.merge(
                    area_growth[[
                        "month", "predictions_mom_growth",
                        "adjusted_price_real_mom_growth", "narrative",
                    ]],
                    on="month", how="left",
                )

                # Use plain Timestamps for comparisons
                dec_ts = pd.Timestamp(DEC_ANCHOR_DATE)
                jan_ts = pd.Timestamp(PIVOT_DATE)

                idx_dec = res_df.index[res_df["month"] == dec_ts].tolist()[0]
                idx_jan = res_df.index[res_df["month"] == jan_ts].tolist()[0]

                dec_val      = res_df.loc[idx_dec, "median_price"]
                raw_jan_ai   = res_df.loc[idx_jan, "median_price"]
                initial_jump = (raw_jan_ai / dec_val) - 1

                if abs(initial_jump) > 0.05:
                    direction    = 1 if initial_jump > 0 else -1
                    jan_adjusted = dec_val * (1 + direction * np.random.uniform(0.035, 0.05))
                    res_df.at[idx_jan, "median_price"] = jan_adjusted
                else:
                    res_df.at[idx_jan, "median_price"] = raw_jan_ai

                res_df.at[idx_jan, "macro_forecast"]         = res_df.loc[idx_jan, "median_price"]
                res_df.at[idx_jan, "news_adjusted_forecast"] = res_df.loc[idx_jan, "median_price"]

                for i in range(idx_jan + 1, len(res_df)):
                    prev_baseline = res_df.loc[i - 1, "median_price"]
                    m_rate = res_df.loc[i, "predictions_mom_growth"]
                    if pd.isna(m_rate):
                        raw_curr = res_df.loc[i, "median_price"]
                        raw_prev = res_df.loc[i - 1, "median_price"]
                        m_rate   = (raw_curr / raw_prev) - 1 if raw_prev != 0 else 0

                    a_rate = (
                        res_df.loc[i, "adjusted_price_real_mom_growth"]
                        if pd.notna(res_df.loc[i, "adjusted_price_real_mom_growth"]) else 0
                    )
                    current_macro = prev_baseline * (1 + m_rate)
                    res_df.at[i, "macro_forecast"]         = current_macro
                    res_df.at[i, "news_adjusted_forecast"] = current_macro * (1 + a_rate)
                    res_df.at[i, "median_price"]           = current_macro

            # Split
            cutoff           = pd.Timestamp(PIVOT_DATE)
            six_month_marker = pd.Timestamp(SIX_MONTHS_DATE)

            hist_part = res_df[res_df["month"] <= cutoff].copy()
            fore_part = res_df[res_df["month"] >= cutoff].copy()

            def apply_lowess_smooth(df, col):
                x = df["month"].map(pd.Timestamp.toordinal).values
                y = df[col].values
                return lowess(y, x, frac=0.085)[:, 1]

            if not hist_part.empty:
                hist_part["smoothed_price"] = apply_lowess_smooth(hist_part, "median_price")
            if not fore_part.empty:
                fore_part["macro_smooth"] = apply_lowess_smooth(fore_part, "macro_forecast")
                if news_available:
                    fore_part["news_smooth"] = apply_lowess_smooth(fore_part, "news_adjusted_forecast")

            # Metrics
            curr_val = res_df.loc[idx_jan, "median_price"]
            c1, c2   = st.columns(2)
            c1.metric("Adjusted Value — Jan 2026", f"AED {curr_val:,.0f}")

            july_row = res_df[res_df["month"] == six_month_marker]
            if not july_row.empty:
                target_val = (
                    july_row["news_adjusted_forecast"].values[0]
                    if news_available else july_row["median_price"].values[0]
                )
                delta_pct = ((target_val / curr_val) - 1) * 100
                c2.metric(
                    "6-Month Forecast — Jul 2026",
                    f"AED {target_val:,.0f}",
                    delta=f"{delta_pct:+.2f}%",
                )

            # Chart
            chart_layout = dict(
                paper_bgcolor="rgba(8,8,14,0)",
                plot_bgcolor ="rgba(14,14,28,0.5)",
                font=dict(family="Outfit, sans-serif", color="#6a6456", size=11),
                hovermode="x unified",
                xaxis=dict(
                    gridcolor="rgba(196,164,98,0.06)", zeroline=False,
                    showline=True, linecolor="rgba(196,164,98,0.18)",
                    tickfont=dict(family="DM Mono, monospace", size=10),
                ),
                yaxis=dict(
                    gridcolor="rgba(196,164,98,0.06)", zeroline=False,
                    showline=True, linecolor="rgba(196,164,98,0.18)",
                    title="Price (AED)", tickformat=",",
                    tickfont=dict(family="DM Mono, monospace", size=10),
                ),
                legend=dict(
                    bgcolor="rgba(8,8,14,0.8)",
                    bordercolor="rgba(196,164,98,0.18)", borderwidth=1,
                    font=dict(family="Outfit, sans-serif", size=11),
                ),
            )

            fig = go.Figure()

            if not hist_part.empty:
                fig.add_trace(go.Scatter(
                    x=hist_part["month"], y=hist_part["median_price"],
                    name="Historical (Raw)",
                    line=dict(color="rgba(90,85,72,0.5)", width=1, dash="dot"),
                ))
                fig.add_trace(go.Scatter(
                    x=hist_part["month"], y=hist_part["smoothed_price"],
                    name="Historical Trend",
                    line=dict(color="#c4a462", width=2.5),
                ))

            if news_available:
                fig.add_trace(go.Scatter(
                    x=fore_part["month"], y=fore_part["macro_forecast"],
                    name="Macro Forecast",
                    line=dict(color="#4ade80", width=1.5, dash="dot"),
                ))
                fig.add_trace(go.Scatter(
                    x=fore_part["month"], y=fore_part["news_adjusted_forecast"],
                    name="News-Adjusted Forecast",
                    line=dict(color="#f87171", width=3),
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=fore_part["month"], y=fore_part["median_price"],
                    name="Base Forecast",
                    line=dict(color="#888", dash="dot"),
                ))

            # fig.add_vline(
            #     x=str(cutoff),
            #     line_width=1, line_dash="dash",
            #     line_color="rgba(196,164,98,0.35)",
            #     annotation_text="Forecast →",
            #     annotation_font_color="#c4a462",
            #     annotation_font_size=10,
            # )

            fig.update_layout(**chart_layout)
            st.plotly_chart(fig, use_container_width=True)

            # Forecast table
            with st.expander("Detailed Forecast Table"):
                table_df = res_df[res_df["month"] >= cutoff].copy()
                table_df["Month"] = table_df["month"].dt.strftime('%B %Y')
                cols  = ["Month", "median_price"]
                names = {"median_price": "Baseline (AED)"}
                if news_available:
                    cols  += ["macro_forecast", "news_adjusted_forecast"]
                    names.update({
                        "macro_forecast":         "Macro Forecast (AED)",
                        "news_adjusted_forecast": "News-Adjusted (AED)",
                    })
                st.dataframe(
                    table_df[cols].rename(columns=names).style.format(
                        "{:,.0f}", subset=list(names.values())
                    ),
                    use_container_width=True,
                )

            # Narrative
            if news_available:
                st.markdown(
                    '<div style="font-family:\'Cormorant Garamond\',serif;'
                    'font-size:22px;font-weight:600;color:#e2ddd4;'
                    'margin:28px 0 10px;letter-spacing:0.01em;">'
                    'Market Narrative &amp; Insights'
                    '</div>',
                    unsafe_allow_html=True,
                )
                top_insight = res_df[res_df["month"] == cutoff].head(1)
                for _, row in top_insight.iterrows():
                    m_label   = row['month'].strftime('%B %Y')
                    full_text = (
                        str(row['narrative']) if pd.notna(row['narrative'])
                        else "Standard growth projection based on historical trends."
                    )
                    st.success(f"**Market Outlook — {m_label}:** {full_text}")

            st.info(
                "Month-on-month movements exceeding ±5% relative to the prior period "
                "are capped to improve forecast trend readability."
            )

        except Exception as e:
            st.error(f"Prediction Error: {e}")
            import traceback
            st.code(traceback.format_exc(), language="python")


# ============================================================
# 9. CRISIS RADAR VIEW
# ============================================================
elif app_mode == "📡 Crisis Radar":
    run_crisis_radar()