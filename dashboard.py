import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from data_collector import CRYPTOS, fetch_current_price, update_all_cryptos
from technical_indicators import get_all_indicators, generate_signals

# Configuration de la page
st.set_page_config(
    page_title="🚀 Dashboard Crypto Ultimate",
    page_icon="₿",
    layout="wide"
)

# CSS personnalisé pour un meilleur design
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #f7931a, #1f77b4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .crypto-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 0.5rem;
    }
    .positive { color: #00D4AA; }
    .negative { color: #FF6B6B; }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown('<h1 class="main-header">🚀 Dashboard Crypto Ultimate</h1>', unsafe_allow_html=True)

# Sidebar pour la sélection
st.sidebar.title("⚙️ Configuration")

# Sélection de la crypto
selected_crypto = st.sidebar.selectbox(
    "Choisir une cryptomonnaie:",
    options=list(CRYPTOS.keys()),
    format_func=lambda x: CRYPTOS[x],
    index=0
)

# Bouton de mise à jour
if st.sidebar.button("🔄 Mettre à jour les données", type="primary"):
    with st.spinner("Mise à jour en cours..."):
        update_all_cryptos(days=30)
    st.sidebar.success("✅ Données mises à jour !")

# Options d'affichage
show_indicators = st.sidebar.multiselect(
    "Indicateurs à afficher:",
    ["RSI", "MACD", "Bollinger Bands", "Moyennes Mobiles", "Stochastique"],
    default=["RSI", "MACD", "Bollinger Bands"]
)

# Récupération des données
@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def load_crypto_data(crypto):
    current_data = fetch_current_price(crypto)
    df, indicators = get_all_indicators(crypto)
    signals = generate_signals(df, indicators) if df is not None and not df.empty else []
    return current_data, df, indicators, signals

current_data, df, indicators, signals = load_crypto_data(selected_crypto)

# Affichage des métriques principales
if current_data and df is not None and not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        change_color = "normal" if current_data['change_24h'] >= 0 else "inverse"
        st.metric(
            f"Prix {CRYPTOS[selected_crypto]}", 
            f"{current_data['price']:,.2f} €",
            f"{current_data['change_24h']:+.2f}%",
            delta_color=change_color
        )
    
    with col2:
        st.metric("Prix Max (30j)", f"{df['price'].max():,.2f} €")
    
    with col3:
        st.metric("Prix Min (30j)", f"{df['price'].min():,.2f} €")
    
    with col4:
        if 'rsi' in indicators:
            rsi_current = indicators['rsi'].iloc[-1]
            st.metric("RSI Actuel", f"{rsi_current:.1f}")

    # Alertes et signaux
    if signals:
        st.subheader("🚨 Alertes et Signaux")
        
        for signal in signals:
            if signal['type'] == 'warning':
                st.warning(f"⚠️ **{signal['title']}**: {signal['message']}")
            elif signal['type'] == 'success':
                st.success(f"✅ **{signal['title']}**: {signal['message']}")
            else:
                st.info(f"ℹ️ **{signal['title']}**: {signal['message']}")

    # Graphiques principaux
    st.subheader(f"📈 Analyse Technique - {CRYPTOS[selected_crypto]}")
    
    # Créer le graphique principal avec sous-graphiques
    rows = 1 + len([x for x in show_indicators if x in ["RSI", "MACD", "Stochastique"]])
    subplot_titles = [f"Prix {CRYPTOS[selected_crypto]}"]
    
    if "RSI" in show_indicators:
        subplot_titles.append("RSI")
    if "MACD" in show_indicators:
        subplot_titles.append("MACD")
    if "Stochastique" in show_indicators:
        subplot_titles.append("Stochastique")
    
    fig = make_subplots(
        rows=rows, cols=1,
        subplot_titles=subplot_titles,
        vertical_spacing=0.05,
        row_heights=[0.5] + [0.5/(rows-1)]*(rows-1) if rows > 1 else [1.0]
    )
    
    current_row = 1
    
    # Graphique des prix avec Bollinger Bands et Moyennes Mobiles
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['price'],
            mode='lines',
            name=f'Prix {selected_crypto.upper()}',
            line=dict(color='#f7931a', width=2)
        ),
        row=current_row, col=1
    )
    
    # Bollinger Bands
    if "Bollinger Bands" in show_indicators and 'bb_upper' in indicators:
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['bb_upper'],
                mode='lines',
                name='BB Supérieure',
                line=dict(color='red', width=1, dash='dash'),
                opacity=0.7
            ),
            row=current_row, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['bb_lower'],
                mode='lines',
                name='BB Inférieure',
                line=dict(color='green', width=1, dash='dash'),
                opacity=0.7,
                fill='tonexty',
                fillcolor='rgba(100,100,100,0.1)'
            ),
            row=current_row, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['bb_middle'],
                mode='lines',
                name='BB Moyenne',
                line=dict(color='blue', width=1, dash='dot'),
                opacity=0.7
            ),
            row=current_row, col=1
        )
    
    # Moyennes mobiles
    if "Moyennes Mobiles" in show_indicators:
        colors = ['purple', 'orange', 'brown']
        for i, (key, ma) in enumerate([(k, v) for k, v in indicators.items() if k.startswith('MA')]):
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'], 
                    y=ma,
                    mode='lines',
                    name=key,
                    line=dict(color=colors[i % len(colors)], width=1),
                    opacity=0.8
                ),
                row=current_row, col=1
            )
    
    # RSI
    if "RSI" in show_indicators and 'rsi' in indicators:
        current_row += 1
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color='#1f77b4', width=2)
            ),
            row=current_row, col=1
        )
        
        # Lignes de référence RSI
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=current_row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=current_row, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=current_row, col=1)
    
    # MACD
    if "MACD" in show_indicators and 'macd' in indicators:
        current_row += 1
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['macd'],
                mode='lines',
                name='MACD',
                line=dict(color='blue', width=2)
            ),
            row=current_row, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['signal'],
                mode='lines',
                name='Signal',
                line=dict(color='red', width=2)
            ),
            row=current_row, col=1
        )
        
        # Histogramme MACD
        colors = ['green' if x >= 0 else 'red' for x in indicators['histogram']]
        fig.add_trace(
            go.Bar(
                x=df['timestamp'], 
                y=indicators['histogram'],
                name='Histogramme',
                marker_color=colors,
                opacity=0.6
            ),
            row=current_row, col=1
        )
    
    # Stochastique
    if "Stochastique" in show_indicators and 'stoch_k' in indicators:
        current_row += 1
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['stoch_k'],
                mode='lines',
                name='%K',
                line=dict(color='blue', width=2)
            ),
            row=current_row, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['stoch_d'],
                mode='lines',
                name='%D',
                line=dict(color='red', width=2)
            ),
            row=current_row, col=1
        )
        
        # Lignes de référence Stochastique
        fig.add_hline(y=80, line_dash="dash", line_color="red", opacity=0.5, row=current_row, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", opacity=0.5, row=current_row, col=1)
    
    # Configuration du layout
    fig.update_layout(
        title=f"Analyse complète - {CRYPTOS[selected_crypto]}",
        height=200 * rows + 100,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    # Configuration des axes
    for i in range(rows):
        if i == 0:
            fig.update_yaxes(title_text="Prix (EUR)", row=i+1, col=1)
        elif "RSI" in show_indicators and i == 1:
            fig.update_yaxes(title_text="RSI", range=[0, 100], row=i+1, col=1)
        elif "MACD" in show_indicators:
            fig.update_yaxes(title_text="MACD", row=i+1, col=1)
        elif "Stochastique" in show_indicators:
            fig.update_yaxes(title_text="Stoch %", range=[0, 100], row=i+1, col=1)
    
    fig.update_xaxes(title_text="Date", row=rows, col=1)
    
    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau de bord des cryptos
    st.subheader("💰 Tableau de bord Multi-Crypto")
    
    crypto_data = []
    for crypto_id in CRYPTOS.keys():  # Utiliser toutes les cryptos disponibles
        try:
            current = fetch_current_price(crypto_id)
            crypto_data.append({
                'Crypto': CRYPTOS[crypto_id],
                'Prix (EUR)': f"{current['price']:,.2f}",
                'Change 24h (%)': f"{current['change_24h']:+.2f}%"
            })
        except Exception as e:
            st.warning(f"⚠️ Erreur pour {CRYPTOS[crypto_id]}: {str(e)}")
            pass
    
    if crypto_data:
        df_dashboard = pd.DataFrame(crypto_data)
        st.dataframe(df_dashboard, use_container_width=True)

else:
    st.error(f"❌ Aucune donnée disponible pour {CRYPTOS[selected_crypto]}. Veuillez mettre à jour les données.")
    st.info("💡 Cliquez sur le bouton 'Mettre à jour les données' dans la barre latérale.")

# Footer
st.markdown("---")
st.markdown("🚀 **Dashboard Crypto Ultimate** - Développé avec Python")
st.markdown("📊 Données fournies par CoinGecko API")