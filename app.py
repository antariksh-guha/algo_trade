import streamlit as st
import pandas as pd
import yfinance as yf
from newsdataapi import NewsDataApiClient
import os

st.set_page_config(page_title="Indian Market Algo Trading Dashboard", layout="wide")

# Load Nifty 100 CSV constituent file
csv_file = "nifty_100.csv"

if not os.path.exists(csv_file):
    st.error(
        "NIFTY 100 stock list CSV not found!\n"
        "Please download it manually from NSE Indices page:\n"
        "https://www.niftyindices.com/indices/equity/sectoral-indices/NIFTY-100\n"
        "Save as 'nifty_100.csv' and upload to your app folder."
    )
    st.stop()

try:
    top100_df = pd.read_csv(csv_file)
    # Strip spaces/newlines from headers
    top100_df.columns = top100_df.columns.str.strip()

    # Use exact CSV column names for symbol and company
    symbols = top100_df['SYMBOL'].str.strip().tolist()
    # No company names; fallback to symbols:
    companies = symbols.copy()
except Exception as e:
    st.error(f"Failed to load NIFTY 100 CSV: {e}")
    st.stop()

# Sidebar dropdown for stock selection
def format_stock(symbol):
    try:
        idx = symbols.index(symbol)
        company = companies[idx]
    except ValueError:
        company = "N/A"
    return f"{symbol} – {company}"

st.sidebar.header("Stock Selector")
ticker = st.sidebar.selectbox("Select Stock", symbols, format_func=format_stock)

# Helper to fix MultiIndex columns when using yfinance
def fix_multiindex_df(df, symbol):
    if isinstance(df.columns, pd.MultiIndex):
        if (f"{symbol}.NS") in df.columns.levels[0]:
            df = df.xs(f"{symbol}.NS", axis=1, level=0)
        else:
            df.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in df.columns.values]
    return df

# Fetch stock data & add SMA signals
@st.cache_data(show_spinner=False)
def get_stock_data(symbol):
    df = yf.download(f"{symbol}.NS", period="1y", group_by="ticker")
    df = fix_multiindex_df(df, symbol)
    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()
    df['SMA50'] = df['Close'].rolling(50).mean()
    df['SMA200'] = df['Close'].rolling(200).mean()
    df['Signal'] = (df['SMA50'] > df['SMA200']).astype(int)
    return df

data = get_stock_data(ticker)
required_cols = ["Close", "SMA50", "SMA200", "Signal"]

if data.empty or not all(col in data.columns for col in required_cols):
    st.error(f"No sufficient market data for {ticker}. Please select another stock.")
    st.stop()

st.title(f"Trading Dashboard – {format_stock(ticker)}")
st.line_chart(data[["Close", "SMA50", "SMA200"]])

latest_signal = "BUY" if data["Signal"].iloc[-1] == 1 else "NO TRADE / SELL"
st.markdown(f"### Latest Trading Suggestion: {latest_signal}")

# Calculate signal strength for sorting
def calculate_signal_strength(row):
    if pd.isna(row["SMA50"]) or pd.isna(row["SMA200"]) or row["SMA200"] == 0:
        return 0
    return (row["SMA50"] - row["SMA200"]) / row["SMA200"]

# Scan top 100 stocks for buy/sell signals
@st.cache_data(show_spinner=False)
def scan_top_stocks(symbol_list, period="1y"):
    buy_list = []
    sell_list = []
    skipped = []
    for sym in symbol_list:
        try:
            df = yf.download(f"{sym}.NS", period=period, group_by="ticker")
            df = fix_multiindex_df(df, sym)
            if df.empty or "Close" not in df.columns:
                skipped.append((sym, "Empty Data or missing 'Close'"))
                continue
            df['SMA50'] = df['Close'].rolling(50).mean()
            df['SMA200'] = df['Close'].rolling(200).mean()
            latest = df.iloc[-1]
            if pd.isna(latest['SMA50']) or pd.isna(latest['SMA200']):
                skipped.append((sym, "SMA50 or SMA200 is NaN"))
                continue
            strength = calculate_signal_strength(latest)
            if latest['SMA50'] > latest['SMA200']:
                buy_list.append({"Stock": sym, "Strength": strength})
            elif latest['SMA50'] < latest['SMA200']:
                sell_list.append({"Stock": sym, "Strength": strength})
        except Exception as e:
            skipped.append((sym, f"Exception: {e}"))
            continue

    st.info(f"Scanned {len(symbol_list)} stocks, skipped {len(skipped)} due to missing/bad data.")

    if skipped:
        st.warning("Skipped stocks:")
        for symbol, reason in skipped:
            st.write(f"- {symbol}: {reason}")

    buy_sorted = sorted(buy_list, key=lambda x: x['Strength'], reverse=True)[:10]
    sell_sorted = sorted(sell_list, key=lambda x: x['Strength'])[:10]
    return buy_sorted, sell_sorted

st.info("Scan top 100 stocks for buy/sell signals based on SMA crossovers.")
if st.button("Show Top 10 Buy/Sell Stocks"):
    with st.spinner("Scanning market signals... this may take a while."):
        top_buys, top_sells = scan_top_stocks(symbols)
        st.subheader("Top 10 BUY Signals")
        st.table(pd.DataFrame(top_buys))
        st.subheader("Top 10 SELL Signals")
        st.table(pd.DataFrame(top_sells))

##############################
# NewsData.io API Integration
##############################

api_key = st.secrets.get("NEWS_API_KEY")
if not api_key:
    st.error("Please add your NewsData.io API key to Streamlit secrets as NEWS_API_KEY")
    st.stop()

@st.cache_resource
def get_news_client():
    return NewsDataApiClient(apikey=api_key)

news_api = get_news_client()

@st.cache_data(ttl=3600)
def fetch_news(ticker):
    try:
        company = None
        try:
            company = top100_df.loc[top100_df["SYMBOL"] == ticker, "NAME OF COMPANY"].values[0]
        except Exception:
            company = ticker
        query = f'"{ticker}" OR "{company}"'
        result = news_api.news_api(
            q=query,
            country="in",
            language="en",
            category="business",
            page=0
        )
        return result.get("results", [])[:5]
    except Exception as e:
        st.warning(f"Could not fetch news: {e}")
        return []

st.subheader(f"Latest News for {format_stock(ticker)}")
news_items = fetch_news(ticker)

if news_items:
    for item in news_items:
        title = item.get("title", "No Title")
        source = item.get("source_id", "")
        pubdate = item.get("pubDate", "")
        st.markdown(f"- **{title}**")
        if source or pubdate:
            st.caption(f"{source} | {pubdate}")
else:
    st.write("No recent news available.")
