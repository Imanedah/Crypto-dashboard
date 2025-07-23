import pandas as pd
import numpy as np
import sqlite3

def get_price_data(crypto='bitcoin'):
    """Récupère les données de prix d'une crypto"""
    conn = sqlite3.connect('crypto_data.db')
    df = pd.read_sql_query(f"SELECT * FROM prices WHERE crypto='{crypto}' ORDER BY timestamp", conn)
    conn.close()
    
    if df.empty:
        return df
    
    # Convertir en datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
    return df

def calculate_rsi(data, period=14):
    """Calcule le RSI (Relative Strength Index)"""
    if len(data) < period:
        return pd.Series([None] * len(data), index=data.index)
    
    delta = data['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss.replace(0, float('inf'))
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, fast=12, slow=26, signal=9):
    """Calcule le MACD (Moving Average Convergence Divergence)"""
    prices = data['price']
    
    # Exponential Moving Averages
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    
    # MACD Line
    macd_line = ema_fast - ema_slow
    
    # Signal Line
    signal_line = macd_line.ewm(span=signal).mean()
    
    # Histogram
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }

def calculate_moving_averages(data, periods=[20, 50]):
    """Calcule les moyennes mobiles"""
    result = {}
    for period in periods:
        result[f'MA{period}'] = data['price'].rolling(window=period).mean()
    return result

def calculate_bollinger_bands(data, period=20, std_dev=2):
    """Calcule les Bandes de Bollinger"""
    prices = data['price']
    
    # Moyenne mobile
    ma = prices.rolling(window=period).mean()
    
    # Écart-type
    std = prices.rolling(window=period).std()
    
    # Bandes
    upper_band = ma + (std * std_dev)
    lower_band = ma - (std * std_dev)
    
    return {
        'middle': ma,
        'upper': upper_band,
        'lower': lower_band
    }

def calculate_stochastic(data, k_period=14, d_period=3):
    """Calcule l'oscillateur stochastique"""
    high = data['price'].rolling(window=k_period).max()
    low = data['price'].rolling(window=k_period).min()
    
    # %K
    k_percent = 100 * ((data['price'] - low) / (high - low))
    
    # %D (moyenne mobile de %K)
    d_percent = k_percent.rolling(window=d_period).mean()
    
    return {
        'k_percent': k_percent,
        'd_percent': d_percent
    }

def calculate_volume_sma(data, period=20):
    """Calcule la moyenne mobile du volume (simulé)"""
    # Comme on n'a pas de volume, on simule avec la volatilité
    volatility = data['price'].pct_change().rolling(window=period).std() * 100
    return volatility

def get_all_indicators(crypto='bitcoin'):
    """Calcule tous les indicateurs pour une crypto"""
    df = get_price_data(crypto)
    
    if df.empty:
        return None
    
    indicators = {}
    
    # RSI
    indicators['rsi'] = calculate_rsi(df)
    
    # MACD
    macd_data = calculate_macd(df)
    indicators.update(macd_data)
    
    # Moyennes mobiles
    ma_data = calculate_moving_averages(df, [20, 50, 200])
    indicators.update(ma_data)
    
    # Bollinger Bands
    bb_data = calculate_bollinger_bands(df)
    indicators['bb_upper'] = bb_data['upper']
    indicators['bb_middle'] = bb_data['middle']
    indicators['bb_lower'] = bb_data['lower']
    
    # Stochastique
    stoch_data = calculate_stochastic(df)
    indicators['stoch_k'] = stoch_data['k_percent']
    indicators['stoch_d'] = stoch_data['d_percent']
    
    # Volatilité (simulant le volume)
    indicators['volatility'] = calculate_volume_sma(df)
    
    return df, indicators

def generate_signals(df, indicators):
    """Génère des signaux d'achat/vente"""
    signals = []
    current_price = df['price'].iloc[-1]
    current_rsi = indicators['rsi'].iloc[-1]
    
    # Signaux RSI
    if current_rsi > 70:
        signals.append({
            'type': 'warning',
            'title': 'RSI Suracheté',
            'message': f'RSI à {current_rsi:.1f} (>70) - Possible correction à venir',
            'value': current_rsi
        })
    elif current_rsi < 30:
        signals.append({
            'type': 'success',
            'title': 'RSI Survendu',
            'message': f'RSI à {current_rsi:.1f} (<30) - Opportunité d\'achat potentielle',
            'value': current_rsi
        })
    
    # Signaux MACD
    macd_current = indicators['macd'].iloc[-1]
    signal_current = indicators['signal'].iloc[-1]
    
    if macd_current > signal_current and indicators['macd'].iloc[-2] <= indicators['signal'].iloc[-2]:
        signals.append({
            'type': 'success',
            'title': 'Signal MACD Haussier',
            'message': 'MACD croise au-dessus de la ligne de signal',
            'value': macd_current
        })
    elif macd_current < signal_current and indicators['macd'].iloc[-2] >= indicators['signal'].iloc[-2]:
        signals.append({
            'type': 'warning',
            'title': 'Signal MACD Baissier',
            'message': 'MACD croise en-dessous de la ligne de signal',
            'value': macd_current
        })
    
    # Signaux Bollinger Bands
    bb_upper = indicators['bb_upper'].iloc[-1]
    bb_lower = indicators['bb_lower'].iloc[-1]
    
    if current_price >= bb_upper:
        signals.append({
            'type': 'warning',
            'title': 'Prix proche bande haute',
            'message': 'Prix près de la bande de Bollinger supérieure - Prudence',
            'value': current_price
        })
    elif current_price <= bb_lower:
        signals.append({
            'type': 'success',
            'title': 'Prix proche bande basse',
            'message': 'Prix près de la bande de Bollinger inférieure - Opportunité',
            'value': current_price
        })
    
    return signals