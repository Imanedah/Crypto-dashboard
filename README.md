# Dashboard Cryptomonnaies
https://crypto-dashboard-4.streamlit.app/

Dashboard crypto en Python avec Streamlit.  
Fonctionnalités :
- Récupération des prix (CoinGecko)
- Calcul RSI
- Alertes par email
- Interface web

## Lancer le projet

```bash
pip install -r requirements.txt
python src/data_collector.py
streamlit run src/dashboard.py
