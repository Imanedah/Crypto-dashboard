import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from data_collector import CRYPTOS, fetch_all_current_prices, update_all_cryptos
from technical_indicators import get_all_indicators, generate_signals

# Configuration de la page
st.set_page_config(
    page_title="🚀 Dashboard Crypto Ultimate",
    page_icon="₿",
    layout="wide"
)

# CSS personnalisé amélioré
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .positive { color: #00D4AA; font-weight: bold; }
    .negative { color: #FF6B6B; font-weight: bold; }
    .metric-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 5px;
        color: white;
        text-align: center;
    }
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

# Options d'affichage avec design amélioré
st.sidebar.markdown("### 📊 Indicateurs Techniques")
show_indicators = st.sidebar.multiselect(
    "Sélectionner les indicateurs:",
    ["RSI", "MACD", "Bollinger Bands", "Moyennes Mobiles", "Stochastique"],
    default=["RSI", "MACD", "Bollinger Bands"]
)

# Récupération des données optimisée
@st.cache_data(ttl=300)
def load_crypto_data(crypto):
    df, indicators = get_all_indicators(crypto)
    signals = generate_signals(df, indicators) if df is not None and not df.empty else []
    return df, indicators, signals

@st.cache_data(ttl=60)
def load_all_current_prices():
    return fetch_all_current_prices()

df, indicators, signals = load_crypto_data(selected_crypto)
all_current_prices = load_all_current_prices()
current_data = all_current_prices.get(selected_crypto, {'price': 0, 'change_24h': 0})

# Affichage des métriques principales avec design amélioré
if current_data and df is not None and not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        change_color = "normal" if current_data['change_24h'] >= 0 else "inverse"
        st.metric(
            f"💰 Prix {CRYPTOS[selected_crypto]}", 
            f"{current_data['price']:,.2f} €",
            f"{current_data['change_24h']:+.2f}%",
            delta_color=change_color
        )
    
    with col2:
        st.metric("📈 Prix Max (30j)", f"{df['price'].max():,.2f} €")
    
    with col3:
        st.metric("📉 Prix Min (30j)", f"{df['price'].min():,.2f} €")
    
    with col4:
        if 'rsi' in indicators:
            rsi_current = indicators['rsi'].iloc[-1]
            rsi_status = "🟢" if 30 <= rsi_current <= 70 else "🔴"
            st.metric(f"{rsi_status} RSI Actuel", f"{rsi_current:.1f}")

    # Alertes et signaux avec design amélioré
    if signals:
        st.subheader("🚨 Alertes et Signaux de Trading")
        
        alert_cols = st.columns(min(len(signals), 3))
        for i, signal in enumerate(signals):
            with alert_cols[i % 3]:
                if signal['type'] == 'warning':
                    st.warning(f"⚠️ **{signal['title']}**\n\n{signal['message']}")
                elif signal['type'] == 'success':
                    st.success(f"✅ **{signal['title']}**\n\n{signal['message']}")
                else:
                    st.info(f"ℹ️ **{signal['title']}**\n\n{signal['message']}")

    # Graphiques principaux avec design amélioré
    st.subheader(f"📈 Analyse Technique Professionnelle - {CRYPTOS[selected_crypto]}")
    
    # Définir les couleurs et le thème
    colors = {
        'price': '#F7931A',          # Orange Bitcoin
        'ma20': '#9C27B0',           # Violet
        'ma50': '#FF9800',           # Orange
        'ma200': '#795548',          # Marron
        'bb_upper': '#F44336',       # Rouge
        'bb_lower': '#4CAF50',       # Vert
        'bb_middle': '#2196F3',      # Bleu
        'rsi': '#1f77b4',            # Bleu
        'macd': '#2E86C1',           # Bleu foncé
        'signal': '#E74C3C',         # Rouge
        'stoch_k': '#8E44AD',        # Violet foncé
        'stoch_d': '#D35400'         # Orange foncé
    }
    
    # Créer le graphique principal avec sous-graphiques
    selected_indicators = [x for x in show_indicators if x in ["RSI", "MACD", "Stochastique"]]
    rows = 1 + len(selected_indicators)
    
    subplot_titles = [f"💰 Prix {CRYPTOS[selected_crypto]} (EUR)"]
    for indicator in selected_indicators:
        if indicator == "RSI":
            subplot_titles.append("📊 RSI (Relative Strength Index)")
        elif indicator == "MACD":
            subplot_titles.append("📈 MACD (Moving Average Convergence Divergence)")
        elif indicator == "Stochastique":
            subplot_titles.append("🎯 Oscillateur Stochastique")
    
    # Hauteurs des graphiques optimisées
    if rows == 1:
        row_heights = [1.0]
    else:
        row_heights = [0.5] + [0.5/(rows-1)]*(rows-1)
    
    fig = make_subplots(
        rows=rows, cols=1,
        subplot_titles=subplot_titles,
        vertical_spacing=0.06,
        row_heights=row_heights,
        shared_xaxes=True
    )
    
    current_row = 1
    
    # Graphique des prix principal avec design amélioré
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['price'],
            mode='lines',
            name=f'Prix {selected_crypto.upper()}',
            line=dict(color=colors['price'], width=3),
            hovertemplate='<b>💰 Prix</b>: %{y:,.2f} €<br>' +
                         '<b>📅 Date</b>: %{x}<br>' +
                         '<extra></extra>'
        ),
        row=current_row, col=1
    )
    
    # Bollinger Bands avec design amélioré
    if "Bollinger Bands" in show_indicators and 'bb_upper' in indicators:
        # Bande supérieure
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['bb_upper'],
                mode='lines',
                name='BB Supérieure',
                line=dict(color=colors['bb_upper'], width=1.5, dash='dot'),
                opacity=0.7,
                hovertemplate='<b>🔴 BB Sup</b>: %{y:,.2f} €<extra></extra>'
            ),
            row=current_row, col=1
        )
        
        # Zone de remplissage entre les bandes
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['bb_lower'],
                mode='lines',
                name='BB Inférieure',
                line=dict(color=colors['bb_lower'], width=1.5, dash='dot'),
                fill='tonexty',
                fillcolor='rgba(100, 149, 237, 0.1)',
                opacity=0.7,
                hovertemplate='<b>🟢 BB Inf</b>: %{y:,.2f} €<extra></extra>'
            ),
            row=current_row, col=1
        )
        
        # Moyenne mobile (ligne centrale)
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['bb_middle'],
                mode='lines',
                name='BB Moyenne',
                line=dict(color=colors['bb_middle'], width=2, dash='dash'),
                opacity=0.8,
                hovertemplate='<b>🔵 BB Moy</b>: %{y:,.2f} €<extra></extra>'
            ),
            row=current_row, col=1
        )
    
    # Moyennes mobiles avec design amélioré
    if "Moyennes Mobiles" in show_indicators:
        ma_config = {
            'MA20': {'color': colors['ma20'], 'name': 'MA20 (Court terme)', 'width': 2},
            'MA50': {'color': colors['ma50'], 'name': 'MA50 (Moyen terme)', 'width': 2.5},
            'MA200': {'color': colors['ma200'], 'name': 'MA200 (Long terme)', 'width': 3}
        }
        
        for key, ma in [(k, v) for k, v in indicators.items() if k.startswith('MA')]:
            config = ma_config.get(key, {'color': 'gray', 'name': key, 'width': 2})
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'], 
                    y=ma,
                    mode='lines',
                    name=config['name'],
                    line=dict(color=config['color'], width=config['width']),
                    opacity=0.8,
                    hovertemplate=f'<b>📊 {key}</b>: %{{y:,.2f}} €<extra></extra>'
                ),
                row=current_row, col=1
            )
    
    # RSI avec design professionnel
    if "RSI" in show_indicators and 'rsi' in indicators:
        current_row += 1
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color=colors['rsi'], width=3),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.1)',
                hovertemplate='<b>📊 RSI</b>: %{y:.1f}<br>' +
                             '<b>État</b>: %{customdata}<extra></extra>',
                customdata=['Suracheté' if x > 70 else 'Survendu' if x < 30 else 'Neutre' 
                           for x in indicators['rsi']]
            ),
            row=current_row, col=1
        )
        
        # Zones critiques RSI avec annotations
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255, 0, 0, 0.1)", 
                     layer="below", line_width=0, row=current_row, col=1)
        fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0, 255, 0, 0.1)", 
                     layer="below", line_width=0, row=current_row, col=1)
        
        # Lignes de référence
        fig.add_hline(y=70, line_dash="dash", line_color="red", line_width=2, 
                     opacity=0.8, row=current_row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", line_width=2, 
                     opacity=0.8, row=current_row, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", line_width=1, 
                     opacity=0.5, row=current_row, col=1)
    
    # MACD avec histogramme coloré
    if "MACD" in show_indicators and 'macd' in indicators:
        current_row += 1
        
        # Ligne MACD
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['macd'],
                mode='lines',
                name='MACD',
                line=dict(color=colors['macd'], width=3),
                hovertemplate='<b>📈 MACD</b>: %{y:.4f}<extra></extra>'
            ),
            row=current_row, col=1
        )
        
        # Ligne Signal
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['signal'],
                mode='lines',
                name='Signal',
                line=dict(color=colors['signal'], width=2, dash='dash'),
                hovertemplate='<b>🎯 Signal</b>: %{y:.4f}<extra></extra>'
            ),
            row=current_row, col=1
        )
        
        # Histogramme avec couleurs dynamiques
        histogram_colors = []
        for i, val in enumerate(indicators['histogram']):
            if val > 0:
                histogram_colors.append('#27AE60')  # Vert
            else:
                histogram_colors.append('#E74C3C')  # Rouge
        
        fig.add_trace(
            go.Bar(
                x=df['timestamp'], 
                y=indicators['histogram'],
                name='Histogramme',
                marker_color=histogram_colors,
                opacity=0.7,
                hovertemplate='<b>📊 Histogramme</b>: %{y:.4f}<br>' +
                             '<b>Tendance</b>: %{customdata}<extra></extra>',
                customdata=['Haussière' if x >= 0 else 'Baissière' 
                           for x in indicators['histogram']]
            ),
            row=current_row, col=1
        )
        
        # Ligne zéro
        fig.add_hline(y=0, line_color="black", line_width=2, opacity=0.5, 
                     row=current_row, col=1)
    
    # Stochastique avec zones critiques
    if "Stochastique" in show_indicators and 'stoch_k' in indicators:
        current_row += 1
        
        # Zone critique haute
        fig.add_hrect(y0=80, y1=100, fillcolor="rgba(255, 0, 0, 0.1)", 
                     layer="below", line_width=0, row=current_row, col=1)
        # Zone critique basse
        fig.add_hrect(y0=0, y1=20, fillcolor="rgba(0, 255, 0, 0.1)", 
                     layer="below", line_width=0, row=current_row, col=1)
        
        # Ligne %K
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['stoch_k'],
                mode='lines',
                name='%K (Rapide)',
                line=dict(color=colors['stoch_k'], width=3),
                hovertemplate='<b>🎯 %K</b>: %{y:.1f}<br>' +
                             '<b>État</b>: %{customdata}<extra></extra>',
                customdata=['Suracheté' if x > 80 else 'Survendu' if x < 20 else 'Neutre' 
                           for x in indicators['stoch_k']]
            ),
            row=current_row, col=1
        )
        
        # Ligne %D
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=indicators['stoch_d'],
                mode='lines',
                name='%D (Lent)',
                line=dict(color=colors['stoch_d'], width=2, dash='dash'),
                hovertemplate='<b>🎯 %D</b>: %{y:.1f}<extra></extra>'
            ),
            row=current_row, col=1
        )
        
        # Lignes de référence
        fig.add_hline(y=80, line_dash="dash", line_color="red", line_width=2, 
                     opacity=0.8, row=current_row, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", line_width=2, 
                     opacity=0.8, row=current_row, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", line_width=1, 
                     opacity=0.5, row=current_row, col=1)
    
    # Configuration du layout professionnel
    fig.update_layout(
        title={
            'text': f"📈 Analyse Technique Professionnelle - {CRYPTOS[selected_crypto]}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2E86C1'}
        },
        height=200 + (300 * rows),
        showlegend=True,
        hovermode='x unified',
        template='plotly_white',
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(0, 0, 0, 0.2)",
            borderwidth=1
        ),
        margin=dict(l=80, r=80, t=100, b=80)
    )
    
    # Configuration des axes avec titres personnalisés
    axis_configs = {}
    current_row = 1
    
    # Configuration axe principal (prix)
    fig.update_yaxes(
        title_text="💰 Prix (EUR)", 
        title_standoff=20,
        tickformat=",.0f",
        gridcolor="rgba(128, 128, 128, 0.2)",
        row=current_row, col=1
    )
    
    if "RSI" in show_indicators:
        current_row += 1
        fig.update_yaxes(
            title_text="📊 RSI", 
            title_standoff=20,
            range=[0, 100], 
            tickvals=[0, 20, 30, 50, 70, 80, 100],
            gridcolor="rgba(128, 128, 128, 0.2)",
            row=current_row, col=1
        )
        
    if "MACD" in show_indicators:
        current_row += 1
        fig.update_yaxes(
            title_text="📈 MACD", 
            title_standoff=20,
            gridcolor="rgba(128, 128, 128, 0.2)",
            row=current_row, col=1
        )
        
    if "Stochastique" in show_indicators:
        current_row += 1
        fig.update_yaxes(
            title_text="🎯 Stoch %", 
            title_standoff=20,
            range=[0, 100], 
            tickvals=[0, 20, 50, 80, 100],
            gridcolor="rgba(128, 128, 128, 0.2)",
            row=current_row, col=1
        )
    
    # Configuration axe X (uniquement pour le dernier graphique)
    fig.update_xaxes(
        title_text="📅 Date", 
        title_standoff=20,
        gridcolor="rgba(128, 128, 128, 0.2)",
        row=rows, col=1
    )
    
    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse rapide textuelle
    st.subheader("🧠 Analyse Rapide")
    
    analysis_cols = st.columns(3)
    
    with analysis_cols[0]:
        if 'rsi' in indicators:
            rsi_current = indicators['rsi'].iloc[-1]
            if rsi_current > 70:
                st.error("🔴 **RSI:** Zone de surachat - Possible correction à venir")
            elif rsi_current < 30:
                st.success("🟢 **RSI:** Zone de survente - Opportunité d'achat potentielle")
            else:
                st.info("🔵 **RSI:** Zone neutre - Pas de signal fort")
    
    with analysis_cols[1]:
        if 'macd' in indicators and 'signal' in indicators:
            macd_current = indicators['macd'].iloc[-1]
            signal_current = indicators['signal'].iloc[-1]
            if macd_current > signal_current:
                st.success("🟢 **MACD:** Signal haussier - Momentum positif")
            else:
                st.error("🔴 **MACD:** Signal baissier - Momentum négatif")
    
    with analysis_cols[2]:
        price_change = ((df['price'].iloc[-1] - df['price'].iloc[0]) / df['price'].iloc[0]) * 100
        if price_change > 0:
            st.success(f"📈 **Tendance 30j:** +{price_change:.1f}% (Haussière)")
        else:
            st.error(f"📉 **Tendance 30j:** {price_change:.1f}% (Baissière)")
    
    # Tableau de bord multi-crypto amélioré
    st.subheader("💎 Tableau de bord Multi-Crypto")
    
    crypto_data = []
    for crypto_id in CRYPTOS.keys():
        if crypto_id in all_current_prices:
            current = all_current_prices[crypto_id]
            
            # Émoji en fonction du changement
            if current['change_24h'] > 5:
                emoji = "🚀"
            elif current['change_24h'] > 0:
                emoji = "📈"
            elif current['change_24h'] > -5:
                emoji = "📉"
            else:
                emoji = "💥"
                
            crypto_data.append({
                'Status': emoji,
                'Cryptomonnaie': CRYPTOS[crypto_id],
                'Prix (EUR)': f"{current['price']:,.2f} €",
                'Variation 24h': f"{current['change_24h']:+.2f}%"
            })
        else:
            crypto_data.append({
                'Status': "❌",
                'Cryptomonnaie': CRYPTOS[crypto_id],
                'Prix (EUR)': "Indisponible",
                'Variation 24h': "N/A"
            })
    
    if crypto_data:
        df_dashboard = pd.DataFrame(crypto_data)
        
        # Styling du dataframe
        def style_dataframe(df):
            def color_change(val):
                if 'N/A' in str(val) or 'Indisponible' in str(val):
                    return 'color: gray'
                elif '+' in str(val):
                    return 'color: #00D4AA; font-weight: bold'
                elif '-' in str(val):
                    return 'color: #FF6B6B; font-weight: bold'
                return ''
            
            return df.style.applymap(color_change, subset=['Variation 24h'])
        
        st.dataframe(
            style_dataframe(df_dashboard), 
            use_container_width=True,
            hide_index=True
        )

else:
    st.error(f"❌ Aucune donnée disponible pour {CRYPTOS[selected_crypto]}")
    st.info("💡 Cliquez sur le bouton '🔄 Mettre à jour les données' dans la barre latérale.")
    
    # Affichage d'un graphique de démonstration
    st.subheader("📊 Exemple de visualisation")
    
    # Créer des données de démonstration
    import numpy as np
    dates = pd.date_range(start='2024-06-01', end='2024-07-01', freq='D')
    demo_prices = 90000 + np.cumsum(np.random.randn(len(dates)) * 1000)
    
    demo_fig = go.Figure()
    demo_fig.add_trace(
        go.Scatter(
            x=dates,
            y=demo_prices,
            mode='lines',
            name='Prix Bitcoin (Demo)',
            line=dict(color='#F7931A', width=3)
        )
    )
    
    demo_fig.update_layout(
        title="📈 Exemple de graphique Bitcoin",
        xaxis_title="Date",
        yaxis_title="Prix (EUR)",
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(demo_fig, use_container_width=True)

# Footer amélioré
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-top: 20px;'>
    <h3>🚀 Dashboard Crypto Ultimate</h3>
    <p>Développé avec Python | 📊 Données CoinGecko API</p>
    <p><em>⚠️ Ce dashboard est à des fins éducatives uniquement. Ne constitue pas un conseil financier.</em></p>
</div>
""", unsafe_allow_html=True)