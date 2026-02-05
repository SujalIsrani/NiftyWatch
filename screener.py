import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import argparse
import streamlit as st
import datetime

# Create export folders
os.makedirs("exports", exist_ok=True)
os.makedirs("screenshots", exist_ok=True)

# RSI Calculation

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Screener logic
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_bundle(ticker):
    """
    Cached per ticker for 1 hour
    Prevents repeated Yahoo hits on Streamlit reruns
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="6mo")
    return info, hist


def run_screener(selected_tickers, plot_tickers, max_pe_filter=30, min_roe_filter=15):
    summary_data = []

    for ticker in selected_tickers:
        try:
            info, data = fetch_stock_bundle(ticker)

            pe = info.get("trailingPE")
            roe = info.get("returnOnEquity")

            if pe is None or roe is None or data.empty:
                continue

            # ⭐ Rate limit protection
            time.sleep(1.1)

            roe_percent = round(roe * 100, 2)

            # ===== Indicators =====
            data['RSI'] = calculate_rsi(data['Close'])
            data['SMA20'] = data['Close'].rolling(20).mean()
            volume_mean = data['Volume'].rolling(20).mean()
            data['Volume Spike'] = data['Volume'] > 1.5 * volume_mean

            last_row = data.iloc[-1]

            signal = "Hold"
            if last_row['RSI'] < 30 and last_row['Close'] > last_row['SMA20']:
                signal = "Buy"
            elif last_row['RSI'] > 70 and last_row['Close'] < last_row['SMA20']:
                signal = "Sell"

            # ===== Charts =====
            if ticker in plot_tickers:
                plt.figure(figsize=(10, 5))
                plt.plot(data['Close'])
                plt.plot(data['SMA20'])
                plt.tight_layout()
                plt.savefig(f"screenshots/{ticker}_chart.png")
                plt.close()

            summary_data.append({
                "Ticker": ticker,
                "PE Ratio": round(pe, 2),
                "ROE (%)": roe_percent,
                "RSI": round(last_row['RSI'], 2),
                "Volume Spike Today": "Yes" if last_row["Volume Spike"] else "No",
                "Signal": signal
            })

        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    # ===== SAFE DATAFRAME CREATION =====
    result_df = pd.DataFrame(summary_data)

    if result_df.empty:
        return result_df, result_df   # ⭐ prevents crash

    # Ensure required columns exist
    for col in ['PE Ratio', 'ROE (%)']:
        if col not in result_df.columns:
            result_df[col] = np.nan

    filtered_df = result_df[
        (result_df['PE Ratio'] <= max_pe_filter) &
        (result_df['ROE (%)'] >= min_roe_filter)
    ]

    result_df.to_excel("exports/all_results.xlsx", index=False)
    filtered_df.to_excel("exports/filtered_results.xlsx", index=False)

    return result_df, filtered_df


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nifty50_cached():
    """
    Cached for 1 hour. Fetches the NIFTY 50 tickers from NSE.
    """
    url = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
    df = pd.read_csv(url)
    df['Ticker'] = df['Symbol'].apply(lambda x: x.strip().upper() + ".NS")
    return df[['Ticker']], datetime.datetime.now()

def refresh_nifty50_csv():
    try:
        df = fetch_nifty50_cached()
        df.to_csv("tickers.csv", index=False)
        return True, "✅ Updated and cached NIFTY 50 tickers."
    except Exception as e:
        return False, f"❌ Failed to update: {e}"

    
# CLI mode
def run_cli():
    tickers_df = pd.read_csv("tickers.csv")
    tickers = tickers_df['Ticker'].tolist()

    parser = argparse.ArgumentParser()
    parser.add_argument('--plot', help='Comma-separated tickers to plot', default='')
    args = parser.parse_args()

    plot_tickers = [t.strip().upper() for t in args.plot.split(',') if t.strip()]
    result_df, filtered_df = run_screener(tickers, plot_tickers)
    print(filtered_df)

#GUI mode
def run_gui():
    st.set_page_config(page_title="📊 NiftyWatch", layout="wide")
    
    # Read tickers from CSV
    tickers_df = pd.read_csv("tickers.csv")
    tickers = tickers_df['Ticker'].tolist()

st.title("📊 NiftyWatch")

st.markdown("""
A smart technical screener that analyzes NIFTY 50 stocks using RSI, PE, ROE, and SMA.  
Customize filters and spot Buy/Sell signals in real-time with clean visual insights.
""")

# 🔄 Refresh ticker list button
if st.button("🔄 Refresh Ticker List from NSE"):
    try:
        df, fetched_time = fetch_nifty50_cached()
        df.to_csv("tickers.csv", index=False)
        st.success("✅ List refreshed and saved.")
        st.caption(f"📅 Updated at: {fetched_time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        st.error(f"❌ Failed to fetch: {e}")

# 📥 Load tickers
tickers_df = pd.read_csv("tickers.csv")
tickers = tickers_df['Ticker'].tolist()

if os.path.exists("tickers.csv"):
    file_time = datetime.datetime.fromtimestamp(os.path.getmtime("tickers.csv"))
    st.caption(f"🕒 Last updated from file: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")

# 🧾 Stock Selection
st.subheader("🧾 Stock Selection")

selected = st.multiselect("Select stocks to analyze:", tickers, default=tickers[:5])
plot_selected = st.multiselect("Select stocks to visualize:", selected)

# 📊 Filter Criteria
with st.expander("📊 Filter Criteria", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        max_pe = st.slider("Max PE Ratio (Price-to-Earnings)", min_value=0, max_value=100, value=30)
    with col2:
        min_roe = st.slider("Min ROE (%) (Return on Equity)", min_value=0, max_value=100, value=15)
    
    col3, col4 = st.columns(2)
    with col3:
        signal_filter = st.selectbox("Filter by Signal", options=["All", "Buy", "Sell", "Hold"], index=0)
    with col4:
        sort_by = st.selectbox("Sort results by", options=["None", "PE Ratio", "ROE (%)", "RSI"], index=0)

    # ℹ️ Signal logic info
    st.caption("📌 Signal Logic: Buy when RSI < 30 and price > 20-day SMA; Sell when RSI > 70 and price < 20-day SMA; otherwise Hold.")

    # 🚀 Run Screener Button
    run_button = st.button("🚀 Run Screener")

    if run_button:
        if not selected:
            st.warning("⚠️ Please select at least one stock to analyze.")
        else:
            with st.spinner("Fetching and analyzing data..."):
                result_df, filtered_df = run_screener(selected, plot_selected, max_pe, min_roe)
                
                # 🔹 Apply Signal filter
                if signal_filter != "All":
                    filtered_df = filtered_df[filtered_df["Signal"] == signal_filter]

                # 🔹 Sort by selected column
                if sort_by != "None":
                    filtered_df = filtered_df.sort_values(by=sort_by)

                st.success("✅ Done")
                st.subheader("Filtered Results")
                st.dataframe(filtered_df)

                for ticker in plot_selected:
                    chart_path = f"screenshots/{ticker}_chart.png"
                    if os.path.exists(chart_path):
                        st.image(chart_path, caption=f"{ticker} - Price vs SMA", use_container_width=True)


# Entry Point
if __name__ == '__main__':
    run_gui()

