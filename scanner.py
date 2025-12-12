import yfinance as yf
import pandas as pd
import numpy as np
import os
import requests  # NEW: For sending to Discord
from datetime import datetime

# --- CONFIGURATION ---
# Get Webhook URL from GitHub Secrets (Environment Variable)
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Tickers List (You can also load this from a file if you commit the file)
tickers = [
"PLNT", "HP", "AER", "CRM", "XYL", "PRMB", "GD", "CF", "MRVL", "ROL",
"ESI", "NTAP", "AAP", "MAR", "OCUL", "RVTY", "VIPS", "AMT", "FITB", "HPQ",
"ETSY", "SPT", "CHTR", "JHX", "NTRA", "BILL", "STX", "AMD", "VRT", "CBRE",
"AVGO", "RIOT", "CMG", "FANG", "XYZ", "GEO", "BALL", "JBHT", "BRO", "ZS",
"INCY", "COO", "NVDA", "ELV", "CPRT", "CI", "PEGA", "CZR", "MOD", "RCL",
"ACHC", "PPC", "ORLY", "SW", "AXTI"

]
adx_threshold = 25

def send_discord_alert(ticker, price, adx, status):
    if not DISCORD_WEBHOOK_URL:
        return
    
    # Determine color (Green for Buy, Yellow for Watch)
    color = 5763719 # Green
    if "WATCH" in status:
        color = 16776960 # Yellow

    data = {
        "username": "Trend Scanner",
        "embeds": [{
            "title": f"{ticker}: {status}",
            "description": f"**Price:** ${price}\n**ADX:** {adx}\n**Trend:** Bullish (20 > 70)",
            "color": color,
            "footer": {"text": "Daily Scanner Bot"}
        }]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=data)

def calculate_indicators(df):
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_70'] = df['Close'].ewm(span=70, adjust=False).mean()
    
    period = 14
    df['UpMove'] = df['High'] - df['High'].shift(1)
    df['DownMove'] = df['Low'].shift(1) - df['Low']
    df['+DM'] = np.where((df['UpMove'] > df['DownMove']) & (df['UpMove'] > 0), df['UpMove'], 0)
    df['-DM'] = np.where((df['DownMove'] > df['UpMove']) & (df['DownMove'] > 0), df['DownMove'], 0)
    df['TR'] = pd.concat([
        df['High'] - df['Low'],
        np.abs(df['High'] - df['Close'].shift(1)),
        np.abs(df['Low'] - df['Close'].shift(1))
    ], axis=1).max(axis=1)
    df['+DI'] = 100 * (df['+DM'].ewm(alpha=1/period).mean() / df['TR'].ewm(alpha=1/period).mean())
    df['-DI'] = 100 * (df['-DM'].ewm(alpha=1/period).mean() / df['TR'].ewm(alpha=1/period).mean())
    df['DX'] = 100 * np.abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'])
    df['ADX'] = df['DX'].ewm(alpha=1/period).mean()
    return df

print("Starting Scan...")

for ticker in tickers:
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if len(df) < 70: continue

        df = calculate_indicators(df)
        curr = df.iloc[-1]
        
        trend_bullish = curr['EMA_20'] > curr['EMA_70']
        trend_strong = curr['ADX'] > adx_threshold
        
        if trend_bullish and trend_strong:
            dist_to_ema = ((curr['Close'] - curr['EMA_20']) / curr['EMA_20']) * 100
            
            if curr['Low'] <= curr['EMA_20']:
                print(f"ALERT: {ticker} BUY SIGNAL")
                send_discord_alert(ticker, round(curr['Close'], 2), round(curr['ADX'], 1), ">>> BUY SIGNAL <<<")
            
            # Optional: Uncomment if you want Watch alerts too
            # elif dist_to_ema <= 3:
            #    send_discord_alert(ticker, round(curr['Close'], 2), round(curr['ADX'], 1), "WATCH (Near Zone)")

    except Exception as e:

        print(f"Error {ticker}: {e}")

