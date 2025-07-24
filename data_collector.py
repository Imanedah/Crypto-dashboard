import requests
import sqlite3
import datetime
import time

# Liste des cryptos qui fonctionnent bien (sans Polkadot qui bug)
CRYPTOS = {
    'bitcoin': 'Bitcoin (BTC)',
    'ethereum': 'Ethereum (ETH)', 
    'solana': 'Solana (SOL)',
    'cardano': 'Cardano (ADA)'
}

def fetch_historical_prices(crypto='bitcoin', days=30, currency='eur'):
    """Récupère les prix historiques d'une crypto"""
    url = f'https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency={currency}&days={days}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        prices = data['prices']  # liste de [timestamp_ms, price]
        
        # Convertir timestamp ms en datetime ISO8601 string
        formatted_prices = []
        for p in prices:
            dt = datetime.datetime.fromtimestamp(p[0] / 1000).isoformat()
            formatted_prices.append((dt, p[1]))
        return formatted_prices
    except Exception as e:
        print(f"Erreur lors de la récupération des prix pour {crypto}: {e}")
        return []

def store_historical_prices(prices, crypto='bitcoin'):
    """Stocke les prix historiques en base"""
    conn = sqlite3.connect('crypto_data.db')
    cursor = conn.cursor()
    
    # Créer la table si elle n'existe pas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crypto TEXT,
            price REAL,
            timestamp TEXT,
            UNIQUE(crypto, timestamp)
        )
    ''')
    
    # Insérer les données
    for timestamp, price in prices:
        try:
            cursor.execute('INSERT INTO prices (crypto, price, timestamp) VALUES (?, ?, ?)',
                           (crypto, price, timestamp))
        except sqlite3.IntegrityError:
            # Ignorer les doublons
            pass
    
    conn.commit()
    conn.close()

def fetch_all_current_prices(currency='eur'):
    """Récupère tous les prix actuels en une seule requête"""
    crypto_ids = ','.join(CRYPTOS.keys())
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_ids}&vs_currencies={currency}&include_24hr_change=true'
    
    try:
        print(f"🔍 Récupération des prix actuels...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        result = {}
        for crypto_id in CRYPTOS.keys():
            if crypto_id in data:
                result[crypto_id] = {
                    'price': data[crypto_id][currency],
                    'change_24h': data[crypto_id].get(f'{currency}_24h_change', 0)
                }
            else:
                result[crypto_id] = {'price': 0, 'change_24h': 0}
        
        print(f"✅ Prix actuels récupérés pour {len(result)} cryptos")
        return result
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des prix actuels: {e}")
        # Retourner des valeurs par défaut
        return {crypto_id: {'price': 0, 'change_24h': 0} for crypto_id in CRYPTOS.keys()}

def fetch_all_current_prices(currency='eur'):
    """Récupère tous les prix actuels en une seule requête"""
    crypto_ids = ','.join(CRYPTOS.keys())
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_ids}&vs_currencies={currency}&include_24hr_change=true'
    
    try:
        print(f"🔍 Récupération des prix actuels...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        result = {}
        for crypto_id in CRYPTOS.keys():
            if crypto_id in data:
                result[crypto_id] = {
                    'price': data[crypto_id][currency],
                    'change_24h': data[crypto_id].get(f'{currency}_24h_change', 0)
                }
            else:
                result[crypto_id] = {'price': 0, 'change_24h': 0}
        
        print(f"✅ Prix actuels récupérés pour {len(result)} cryptos")
        return result
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des prix actuels: {e}")
        # Retourner des valeurs par défaut
        return {crypto_id: {'price': 0, 'change_24h': 0} for crypto_id in CRYPTOS.keys()}

def fetch_current_price(crypto='bitcoin', currency='eur'):
    """Fonction de compatibilité - utilise le cache global"""
    all_prices = fetch_all_current_prices(currency)
    return all_prices.get(crypto, {'price': 0, 'change_24h': 0})

def fetch_price(crypto='bitcoin', currency='eur'):
    """Fonction de compatibilité - récupère juste le prix"""
    current_data = fetch_current_price(crypto, currency)
    return current_data['price']

def update_all_cryptos(days=30):
    """Met à jour toutes les cryptos en base"""
    print("Mise à jour de toutes les cryptomonnaies...")
    for crypto_id in CRYPTOS.keys():
        print(f"Récupération de {CRYPTOS[crypto_id]}...")
        prices = fetch_historical_prices(crypto_id, days=days)
        if prices:
            store_historical_prices(prices, crypto_id)
            print(f"✅ {len(prices)} prix stockés pour {CRYPTOS[crypto_id]}")
        else:
            print(f"❌ Erreur pour {CRYPTOS[crypto_id]}")

if __name__ == "__main__":
    # Mettre à jour toutes les cryptos
    update_all_cryptos()
    print("✅ Mise à jour terminée !")