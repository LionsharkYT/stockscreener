
import streamlit as st
import requests
import pandas as pd

# --- API KEYS ---
POLYGON_API_KEY = "vnabixfVrjUujUpV7zOUGu2bBt623T_S"
FINNHUB_API_KEY = "d1o8je1r01qtrauvqfagd1o8je1r01qtrauvqfb0"

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="Pre-Market Screener", layout="wide")
st.title("🔥 Cameron Ross-Style Pre-Market Screener")
st.caption("Built with Polygon.io + Finnhub APIs — Live float, % change, and more.")

# --- HELPER FUNCTION TO FETCH GAINERS ---
@st.cache_data(ttl=60)
def get_gainers():
    url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/gainers?apiKey={POLYGON_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    return response.json().get("tickers", [])

# --- HELPER FUNCTION TO GET FLOAT DATA FROM FINNHUB ---
@st.cache_data(ttl=3600)
def get_float(symbol):
    url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("shareOutstanding", None)
    return None

# --- MAIN LOGIC ---
gainers = get_gainers()
filtered = []

for stock in gainers:
    try:
        symbol = stock["ticker"]
        price = stock["lastTrade"]["p"]
        change = stock["todaysChangePerc"]
        volume = stock["day"]["v"]
        prev_close = stock["prevDay"]["c"]
        float_val = get_float(symbol)

        if (
            1 <= price <= 20 and
            change >= 10 and
            float_val is not None and
            float_val <= 50
        ):
            filtered.append({
                "Symbol": symbol,
                "Price": price,
                "% Change": round(change, 2),
                "Float (M)": round(float_val, 2),
                "Volume": volume,
                "Prev Close": prev_close
            })
    except:
        continue

# --- DISPLAY RESULTS ---
if filtered:
    df = pd.DataFrame(filtered)
    df = df.sort_values(by="% Change", ascending=False)
    st.success(f"🎯 {len(df)} Momentum Stocks Found")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No stocks match your current criteria. Try again in a few minutes.")
