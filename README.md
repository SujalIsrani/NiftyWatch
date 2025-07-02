# 📈 NiftyWatch

**NiftyWatch** is a smart, customizable technical screener built with Python and Streamlit that analyzes **NIFTY 50 stocks** using key financial and technical indicators like **RSI**, **PE Ratio**, **ROE**, and **SMA**.
It helps you visualize buy/sell signals, apply custom filters, and track performance — all in real time.

---

## 🚀 Features

* 📟 **Dynamic Ticker Loader** – Pulls latest NIFTY 50 from NSE
* 📊 **Custom Filters** – Set PE Ratio and ROE thresholds interactively
* 🔍 **Signal Detection** – Buy/Sell/Hold based on RSI and SMA crossovers
* 📈 **Visual Charts** – Save and view SMA + price line plots
* 📂 **Export Results** – Excel download of filtered stocks
* ⚙️ **Sort & Filter by Signal** – Interactive controls for deeper insights

---

## 🧠 Signal Logic

> **Buy** when RSI < 30 and price crosses above 20-day SMA
> **Sell** when RSI > 70 and price drops below 20-day SMA
> Else: **Hold**

---

## 📦 Installation

```bash
git clone https://github.com/SujalIsrani/niftywatch.git
cd niftywatch
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🧪 Usage

### ▶️ Run with Streamlit

```bash
streamlit run screener.py
```

### ⚙️ Run via CLI

```bash
python screener.py --plot TCS.NS,INFY.NS
```

---

## 📁 Project Structure

```
.
├── screener.py          # Main app logic (Streamlit + CLI)
├── tickers.csv          # Ticker list (auto-fetched from NSE)
├── exports/             # Excel exports of results
├── screenshots/         # Auto-saved charts
├── fetch_nifty50.py     # NSE ticker fetch script
├── requirements.txt
└── README.md
```

---

## 📚 Built With

* [Streamlit](https://streamlit.io/)
* [pandas](https://pandas.pydata.org/)
* [yfinance](https://pypi.org/project/yfinance/)
* [matplotlib](https://matplotlib.org/)
* [openpyxl](https://openpyxl.readthedocs.io/)
* [NSE CSV](https://www.nseindia.com/)

---

## 🧑‍💼 Ideal For

* Finance/Quant internships
* College portfolio projects
* Technical screening of Indian stocks
* Building real-time investment dashboards

---

## 📬 Contact

Made by **Sujal Israni**
🔗 [LinkedIn](https://www.linkedin.com/in/sujal-israni-b6998726b/)
📧 [isgisranisujal@gmail.com](mailto:isgisranisujal@gmail.com)

---
