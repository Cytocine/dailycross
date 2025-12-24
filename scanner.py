import yfinance as yf
import pandas as pd
import numpy as np
import os
import requests

# =========================
# CONFIGURATION
# =========================

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
adx_threshold = 25

tickers = [
    "PLNT","HP","AER","CRM","XYL","PRMB","GD","CF","MRVL","ROL",
    "ESI","NTAP","AAP","MAR","OCUL","RVTY","VIPS","AMT","FITB","HPQ",
    "ETSY","SPT","CHTR","JHX","NTRA","BILL","STX","AMD","VRT","CBRE",
    "AVGO","RIOT","CMG","FANG","XYZ","GEO","BALL","JBHT","BRO","ZS",
    "INCY","COO","NVDA","ELV","CPRT","CI","PEGA","CZR","MOD","RCL",
    "ACHC","PPC","ORLY","SW","AXTI","KO","PCG","QQQ","SMCI","DELL",
    "OWL","PG","WDC","CCL","BABA","GILD","BAC","CLSK","MARA","META",
    "QS","TIGR","LVS","PINS","COTY","RKT","CORZ","LYFT","ABBV",
    "ONDS","OPEN","EXE","KSS","ALHC","DJT","CLOV","AXON","SNAP",
    "SPY","ARM","HIMS","UPST","DKNG"
]

# =========================
# IN-MEMORY DAILY ALERT TRACKER
# =========================

alerted_tickers = set()  # resets every run

# =========================
# DISCORD ALERT
# =========================

def send_discord_alert(ticker, price, adx, status, custom_text=None):
    if not DISCORD_WEBHOOK_URL:
        return

    color = 5763719  # Green
    if "WATCH" in status:
        color = 16776960  # Yellow

    description = (
        f"**Price:** ${price}\n"
        f"**ADX:** {adx}\n"
        f"**Trend:** EMA20 > EMA70"
    )

    if custom_text:
        description += f"\n\n{custom_text}"

    payload = {
        "username": "Daily Trend Scanner",
        "embeds": [{
            "title": f"{ticker}: {status}",
            "description": description,
            "color": color,
            "footer": {"text": "Alerted once per run"}
        }]
    }

    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)

# =========================
# INDICATORS
# =========================

def calculate_indicators(df):
    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA_70"] = df["Close"].ewm(span=70, adjust=False).mean()

    period = 14
    df["UpMove"] = df["High"] - df["High"].shift(1)
    df["DownMove"] = df["Low"].shift(1) - df["Low"]

    df["+DM"] = np.where(
        (df["UpMove"] > df["DownMove"]) & (df["UpMove"] > 0),
        df["UpMove"], 0
    )
    df["-DM"] = np.where(
        (df["DownMove"] > df["UpMove"]) & (df["DownMove"] > 0),
        df["DownMove"], 0
    )

    df["TR"] = pd.concat([
        df["High"] - df["Low"],
        np.abs(df["High"] - df["Close"].shift(1)),
        np.abs(df["Low"] - df["Close"].shift(1))
    ], axis=1).max(axis=1)

    df["+DI"] = 100 * (df["+DM"].ewm(alpha=1/period).mean() /
                       df["TR"].ewm(alpha=1/period).mean())
    df["-DI"] = 100 * (df["-DM"].ewm(alpha=1/period).mean() /
                       df["TR"].ewm(alpha=1/period).mean())

    df["DX"] = 100 * np.abs(df["+DI"] - df["-DI"]) / (df["+DI"] + df["-DI"])
    df["ADX"] = df["DX"].ewm(alpha=1/period).mean()

    return df

# =========================
# MAIN SCAN
# =========================

print("🚀 Starting Scan...")

for ticker in tickers:
    try:
        if ticker in alerted_tickers:
            continue

        df = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=False
        )

        if df.empty or len(df) < 70:
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = calculate_indicators(df)
        curr = df.iloc[-1]

        if curr["EMA_20"] <= curr["EMA_70"]:
            continue

        if curr["ADX"] <= adx_threshold:
            continue

        if curr["Low"] <= curr["EMA_20"]:
            print(f"✅ ALERT: {ticker} BUY SIGNAL")

            send_discord_alert(
                ticker,
                round(curr["Close"], 2),
                round(curr["ADX"], 1),
                "BUY SIGNAL",
                custom_text="Pullback to EMA20 in a strong ADX trend."
            )

            alerted_tickers.add(ticker)

    except Exception as e:
        print(f"❌ Error {ticker}: {e}")

print("✅ Scan Complete")
