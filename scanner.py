import yfinance as yf
import pandas as pd
import numpy as np
import os
import requests  # NEW: For sending to Discord
from datetime import datetime

# --- CONFIGURATION ---
# Get Webhook URL from GitHub Secrets (Environment Variable)
DISCORD_WEBHOOK_URL = os.environ.get("https://discord.com/api/webhooks/1447796936244723834/MUUN2Mk86StPaA38FTicu5pvOAuyJhjWUgxaQ0Ojo9De7DPUpBmb5alpK8UU8tLY9j9_")

# Tickers List (You can also load this from a file if you commit the file)
tickers = [
"A", "AA", "AAPL", "AAVL", "AAP", "ABBV", "ABNB", "ACAD", "ACGL", "ACHC", "ACN",
"ADC", "ADBE", "ADMA", "ADSK", "AEO", "AER", "AEVA", "AFL", "AG", "AGCO", "AGI",
"AGNC", "AIG", "AKAM", "ALB", "ALGN", "ALK", "ALL", "ALNY", "AMAT", "AMAZ", 
"AMCR", "AMD", "AME", "AMGN", "AMKR", "AMT", "AMZN", "ANET", "ANF", "APD", 
"APH", "APO", "APP", "APTV", "AR", "AROC", "ARWR", "ASML", "ATEC", "ATVI", 
"AUTO", "AVB", "AVGO", "AVY", "AXP", "AXTI", "BALL", "BA", "BBWI", "BDX", 
"BEN", "BE", "BHP", "BIDU", "BIG", "BILI", "BIO", "BLDR", "BMRN", "BN", "BNS",
"BRO", "BSX", "BTI", "BURL", "BWIN", "BX", "C", "CABA", "CAG", "CAL", "CAVA", 
"CAT", "CBRE", "CCI", "CC", "CCJ", "CCK", "CDAY", "CDE", "CDNS", "CDW", "CELH", 
"CENC", "CENX", "CF", "CFG", "CFLT", "CI", "CIEN", "CINF", "CLF", "CLX", 
"CM", "CMA", "CMCSA", "CME", "CMG", "CNC", "CNP", "CNQ", "CNX", "COF", "COHR", 
"COO", "COP", "COST", "COUR", "CP", "CPRT", "CRH", "CRL", "CRMD", "CRM", 
"CRWD", "CSCO", "CSX", "CTAS", "CTSH", "CTVA", "CVLT", "CVNA", "CVS", "CZR", 
"DAN", "DAR", "DD", "DE", "DECK", "DELL", "DEO", "DHI", "DHR", "DK", "DKS", 
"DLR", "DLTR", "DOCU", "DXCM", "EA", "EAT", "EBAY", "EC", "ECL", "ED", "EL", 
"ELF", "ELV", "EMB", "EMN", "EMR", "ENPH", "EOG", "EOS", "EPAM", "EQIX", 
"EQT", "ES", "ESI", "ETN", "ETR", "ETSY", "EVRG", "EXAS", "EXC", "EXPE", 
"EXR", "F", "FANG", "FERG", "FFIV", "FIS", "FISV", "FITB", "FLEX", "FLS", 
"FMC", "FNF", "FOXA", "FSLR", "FTI", "FTNT", "FWONK", "G", "GDDY", "GD", 
"GEHC", "GEOG", "GEO", "GGAL", "GFL", "GFS", "GILD", "GIS", "GLW", "GM", 
"GME", "GOOGL", "GOOG", "GPK", "GPN", "GRMN", "GS", "GSK", "GTLB", "GWW", 
"HAS", "HBAN", "HCA", "HD", "HDB", "HIG", "HII", "HPE", "HPQ", "HRC", "HSIC", 
"HSY", "HUBB", "HUM", "HUN", "HXL", "IAC", "IBM", "ICE", "ILMN", "INCY", 
"INDV", "INFN", "INTC", "INTU", "INVZ", "INSM", "IP", "IPG", "IR", "IRM", 
"ISRG", "ITT", "IVZ", "J", "JAZZ", "JBHT", "JNJ", "JPM", "JWN", "K", "KDP", 
"KEY", "KKR", "KLAC", "KMB", "KMI", "KMX", "KO", "KR", "KURA", "L", "LAZ", 
"LHX", "LMT", "LNC", "LEN", "LITE", "LIVN", "LKQ", "LLY", "LMT", "LNG", 
"LOW", "LRCX", "LULU", "LUV", "LYV", "M", "MA", "MAR", "MAS", "MCD", "MCK", 
"MCO", "MDB", "MDLZ", "MDT", "META", "MET", "METC", "MFC", "MGM", "MKC", 
"MOS", "MPC", "MRO", "MRK", "MRNA", "MRVL", "MS", "MSFT", "MSI", "MSTR", 
"MT", "MTCH", "MTD", "MTG", "MU", "NDAQ", "NB", "NCLH", "NEM", "NET", "NFLX", 
"NI", "NKE", "NOC", "NOG", "NOW", "NUE", "NVDA", "NVO", "NTAP", "NTLA", 
"NTRA", "NUE", "NVAX", "NWS", "NWSA", "NXPI", "OCUL", "ODFL", "OKE", "OMC", 
"ON", "ORCL", "ORI", "ORLY", "OTIS", "OVV", "OXY", "PANW", "PARA", "PAYC", 
"PENN", "PEP", "PFE", "PG", "PGR", "PH", "PHM", "PLNT", "PLTR", "PM", "PNC", 
"PNR", "PODD", "POOL", "PPG", "PPL", "PRMB", "PRU", "PSA", "PSX", "PSTG", 
"PTC", "PVH", "PYPL", "QCOM", "QDEL", "QURE", "RBLX", "RCL", "RDFN", "REGN", 
"RGTI", "RH", "RIVN", "RJF", "RL", "RMD", "RNG", "ROL", "ROKU", "ROP", 
"RRC", "RSG", "RTX", "RVLV", "RVTY", "SAGE", "SBAC", "SBLK", "SBUX", "SCHW",
"SE", "SEDG", "SGEN", "SGML", "SGRY", "SHOP", "SHW", "SIG", "SIRI", "SJM", 
"SKX", "SLB", "SLG", "SLGN", "SLM", "SMCI", "SNA", "SNAP", "SNDK", "SNP", 
"SFM", "SPG", "SPGI", "SPOT", "SPT", "SQM", "SSNC", "SSRM", "STAA", "STLD", 
"STNG", "STT", "STX", "SW", "SWK", "SYF", "SYK", "SYY", "T", "TAP", "TD", 
"TDC", "TDG", "TEAM", "TECK", "TEL", "TER", "TGT", "TICK", "TJX", "TMO", 
"TMUS", "TOL", "TPR", "TREX", "TRGP", "TRV", "TSCO", "TSLA", "TSN", "TT", 
"TTD", "TTMI", "TTWO", "UAL", "UBER", "UDR", "UHS", "ULTA", "UNH", "UNFI", 
"UNP", "UPS", "URI", "URBN", "USB", "V", "VEEV", "VFC", "VIPS", "VLO", 
"VMC", "VNET", "VNOM", "VRSN", "VRT", "VRSK", "VST", "VTR", "VZ", "WAB", 
"WBA", "WBD", "WDAY", "WELL", "WFC", "WGO", "WMB", "WMT", "WM", "WOOF", 
"WPM", "WRB", "WST", "WTW", "WYNN", "XOM", "XPO", "XYL", "YUM", "ZBH", "ZBRA",
"ZION", "ZM", "ZS", "ZTS"

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