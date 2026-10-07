import streamlit as st
import requests
<<<<<<< HEAD
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. Configuração da página (Sem emojis)
st.set_page_config(
    page_title="Terminal de Cotações",
    layout="wide"
)

# 2. Estilização CSS Minimalista e Limpa
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #f1f5f9 !important; }
    .stCaption, small { color: #94a3b8 !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 600 !important; }
    [data-testid="stMetricLabel"] { color: #cbd5e1 !important; }
    /* Estilização das abas limpas */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #1e293b; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border: none; color: #94a3b8 !important; padding: 12px 20px; font-weight: 500; }
    .stTabs [aria-selected="true"] { background-color: #1e293b !important; color: #ffffff !important; border-bottom: 2px solid #3b82f6; }
    .card-moeda { background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 20px; }
    </style>
""", unsafe_allow_html=True)

# Dicionário de moedas (Nome limpo para a interface)
MOEDAS_DISPONIVEIS = {
    "BRL": "Real Brasileiro",
    "USD": "Dólar Americano",
    "EUR": "Euro",
    "GBP": "Libra Esterlina",
    "ARS": "Peso Argentino",
    "BTC": "Bitcoin",
    "ETH": "Ethereum"
}

# --- FUNÇÕES DE DADOS ---

@st.cache_data(ttl=30)
def obter_cotacoes_gerais():
    # Pega todas as moedas contra o Real para criar a base
    pares = "USD-BRL,EUR-BRL,GBP-BRL,ARS-BRL,BTC-BRL,ETH-BRL"
    url = f"https://economia.awesomeapi.com.br/json/last/{pares}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            dados = res.json()
            
            # Constrói dicionário de taxas baseadas no BRL (BRL vale 1)
            taxas = {"BRL": 1.0}
            metricas = {}
            
            for chave, info in dados.items():
                codigo = info['code']
                taxas[codigo] = float(info['bid'])
                metricas[codigo] = {
                    "valor": float(info['bid']),
                    "variacao": float(info['pctChange'])
                }
            return taxas, metricas, None
        return None, None, "Erro ao carregar dados do mercado."
    except Exception as e:
        return None, None, f"Erro de conexão: {e}"

def obter_historico(codigo_moeda, dias):
    # Se pedir BRL não tem histórico na API, pois é a base
    if codigo_moeda == "BRL":
        return None, "Selecione uma moeda estrangeira para ver o histórico."
        
    par = f"{codigo_moeda}-BRL"
    url = f"https://economia.awesomeapi.com.br/json/daily/{par}/{dias}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            dados = res.json()
            lista = []
            for item in dados:
                dt = datetime.fromtimestamp(int(item['timestamp']))
                lista.append({
                    'Data_Obj': dt,
                    'Valor': float(item['bid'])
                })
            # O Segredo para não bugar o gráfico: Ordernar estritamente pela data
            df = pd.DataFrame(lista).sort_values('Data_Obj').reset_index(drop=True)
            return df, None
        return None, f"Erro na API."
    except Exception as e:
        return None, f"Erro de conexão: {e}"

# --- CABEÇALHO ---
st.title("Terminal Financeiro")
st.caption("Visão de mercado, gráficos e conversões de moedas globais.")
st.write("") # Espaçamento

# Abas limpas
tab_geral, tab_analise, tab_conversor, tab_comparador = st.tabs([
    "Panorama Geral", 
    "Análise de Tendência", 
    "Conversor Multi-Moedas", 
    "Comparador"
])

# Carrega os dados globais
taxas_globais, metricas_globais, erro_global = obter_cotacoes_gerais()

# ==========================================
# ABA 1: PANORAMA GERAL
# ==========================================
with tab_geral:
    if erro_global:
        st.error(erro_global)
    else:
        st.subheader("Cotações contra o Real (BRL)")
        st.write("")
        
        # Filtra apenas as moedas estrangeiras para os cards
        codigos_estrangeiros = [c for c in MOEDAS_DISPONIVEIS.keys() if c != "BRL"]
        
        col1, col2, col3 = st.columns(3)
        for i, codigo in enumerate(codigos_estrangeiros):
            coluna_atual = [col1, col2, col3][i % 3]
            with coluna_atual:
                with st.container(border=True):
                    nome = MOEDAS_DISPONIVEIS[codigo]
                    val = metricas_globais[codigo]['valor']
                    var = metricas_globais[codigo]['variacao']
                    
                    st.markdown(f"<p style='color:#94a3b8; font-size:14px; margin-bottom:0;'>{codigo} - {nome}</p>", unsafe_allow_html=True)
                    st.metric(
                        label="",
                        value=f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                        delta=f"{var:+.2f}%"
                    )

# ==========================================
# ABA 2: ANÁLISE DE TENDÊNCIA
# ==========================================
with tab_analise:
    c_moeda, c_dias = st.columns([2, 1])
    with c_moeda:
        lista_analise = [c for c in MOEDAS_DISPONIVEIS.keys() if c != "BRL"]
        sel_analise = st.selectbox("Moeda para análise:", lista_analise, format_func=lambda x: f"{x} - {MOEDAS_DISPONIVEIS[x]}")
    with c_dias:
        dias_analise = st.selectbox("Período (Dias):", [15, 30, 60, 90, 180], index=1)

    df_hist, erro_hist = obter_historico(sel_analise, dias_analise)

    if erro_hist:
        st.error(erro_hist)
    elif df_hist is not None:
        # Média Móvel
        df_hist['SMA'] = df_hist['Valor'].rolling(window=7).mean()
        
        fig = go.Figure()

        # Linha limpa do preço
        fig.add_trace(go.Scatter(
            x=df_hist['Data_Obj'], y=df_hist['Valor'],
            mode='lines', name='Cotação',
            line=dict(color='#3b82f6', width=2),
            fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)',
            hovertemplate='Data: %{x|%d/%m/%Y}<br>Valor: R$ %{y:.4f}<extra></extra>'
        ))

        # Linha da Média Móvel
        fig.add_trace(go.Scatter(
            x=df_hist['Data_Obj'], y=df_hist['SMA'],
            mode='lines', name='Média Móvel (7d)',
            line=dict(color='#fbbf24', width=1.5, dash='dot'),
            hoverinfo='skip'
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(showgrid=True, gridcolor='#1e293b', tickformat='%d/%m'),
            yaxis=dict(showgrid=True, gridcolor='#1e293b'),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# ABA 3: CONVERSOR UNIVERSAL
# ==========================================
with tab_conversor:
    st.subheader("Conversão Direta")
    st.caption("Converta valores livremente entre qualquer par de moedas.")
    st.write("")
    
    if taxas_globais:
        col_inp, col_out = st.columns(2)
        
        with col_inp:
            moeda_origem = st.selectbox("De:", list(MOEDAS_DISPONIVEIS.keys()), format_func=lambda x: f"{x} - {MOEDAS_DISPONIVEIS[x]}", index=1)
            valor_origem = st.number_input("Valor:", min_value=0.01, value=100.00, step=10.0)
            
        with col_out:
            moeda_destino = st.selectbox("Para:", list(MOEDAS_DISPONIVEIS.keys()), format_func=lambda x: f"{x} - {MOEDAS_DISPONIVEIS[x]}", index=0)
            
            # Lógica de conversão cruzada: (Origem -> BRL) -> Destino
            valor_em_brl = valor_origem * taxas_globais[moeda_origem]
            valor_final = valor_em_brl / taxas_globais[moeda_destino]
            
            st.markdown("<p style='font-size:14px; margin-bottom:5px; margin-top:22px;'>Resultado:</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:#3b82f6; margin-top:0;'>{valor_final:,.4f} {moeda_destino}</h2>", unsafe_allow_html=True)

# ==========================================
# ABA 4: COMPARADOR CORRIGIDO
# ==========================================
with tab_comparador:
    st.subheader("Comparador de Desempenho (%)")
    
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        m1 = st.selectbox("Moeda 1:", [c for c in MOEDAS_DISPONIVEIS.keys() if c != "BRL"], index=0)
    with c2:
        m2 = st.selectbox("Moeda 2:", [c for c in MOEDAS_DISPONIVEIS.keys() if c != "BRL"], index=1)
    with c3:
        dias_comp = st.selectbox("Dias:", [15, 30, 60, 90], index=1)

    df1, erro1 = obter_historico(m1, dias_comp)
    df2, erro2 = obter_historico(m2, dias_comp)

    if erro1 or erro2:
        st.error("Erro ao processar as moedas selecionadas.")
    elif df1 is not None and df2 is not None:
        # Calcula variação percentual desde o primeiro dia do período
        df1['Var'] = ((df1['Valor'] / df1['Valor'].iloc[0]) - 1) * 100
        df2['Var'] = ((df2['Valor'] / df2['Valor'].iloc[0]) - 1) * 100

        fig_comp = go.Figure()

        # Linhas limpas usando o eixo de tempo nativo do Plotly (Data_Obj)
        fig_comp.add_trace(go.Scatter(
            x=df1['Data_Obj'], y=df1['Var'],
            mode='lines', name=m1, line=dict(color='#3b82f6', width=2.5),
            hovertemplate='%{x|%d/%m/%Y}: %{y:+.2f}%<extra></extra>'
        ))

        fig_comp.add_trace(go.Scatter(
            x=df2['Data_Obj'], y=df2['Var'],
            mode='lines', name=m2, line=dict(color='#fbbf24', width=2.5),
            hovertemplate='%{x|%d/%m/%Y}: %{y:+.2f}%<extra></extra>'
        ))

        fig_comp.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(showgrid=True, gridcolor='#1e293b', tickformat='%d/%m'),
            yaxis=dict(showgrid=True, gridcolor='#1e293b', title="Variação (%)"),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        with st.container(border=True):
            st.plotly_chart(fig_comp, use_container_width=True)
=======
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Cotação de Moedas",
    page_icon="🪙",
    layout="centered"
)

# Estilização visível e com alto contraste
st.markdown("""
    <style>
    /* Cor de fundo principal */
    .stApp {
        background-color: #0f172a;
    }
    
    /* Títulos e textos gerais em branco alto contraste */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #f8fafc !important;
    }
    
    /* Legendas e subtextos num tom claro e legível */
    .stCaption, small {
        color: #94a3b8 !important;
    }

    /* Estilização das métricas para destacar os números */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Dicionário com informações e ícones das moedas
MOEDAS = {
    "USD-BRL": {"nome": "Dólar Americano", "icone": "🇺🇸"},
    "EUR-BRL": {"nome": "Euro", "icone": "🇪🇺"},
    "GBP-BRL": {"nome": "Libra Esterlina", "icone": "🇬🇧"},
    "ARS-BRL": {"nome": "Peso Argentino", "icone": "🇦🇷"},
    "BTC-BRL": {"nome": "Bitcoin", "icone": "₿"},
    "ETH-BRL": {"nome": "Ethereum", "icone": "Ξ"}
}

def consultar_moeda(par_moeda):
    url = f"https://economia.awesomeapi.com.br/json/last/{par_moeda}"
    try:
        resposta = requests.get(url, timeout=5)
        if resposta.status_code == 200:
            return resposta.json(), None
        else:
            return None, f"Erro na API (Código {resposta.status_code})"
    except Exception as e:
        return None, f"Erro de conexão: {str(e)}"

# --- INTERFACE ---

st.title("🪙 Painel de Cotação de Moedas")
st.caption("Consumo em tempo real via AwesomeAPI")

st.divider()

# Seleção da moeda
opcoes_formatadas = [f"{info['icone']} {par} - {info['nome']}" for par, info in MOEDAS.items()]
opcao_selecionada = st.selectbox("Escolha a moeda para consultar:", opcoes_formatadas)

# Extrai a chave (ex: "BTC-BRL") da opção selecionada
moeda_chave = opcao_selecionada.split(" ")[1]

if st.button("Consultar Cotação", type="primary", use_container_width=True):
    with st.spinner("Buscando cotação atualizada..."):
        dados, erro = consultar_moeda(moeda_chave)

    if erro:
        st.error(erro)
    else:
        chave_api = moeda_chave.replace("-", "")
        if chave_api in dados:
            cotacao = dados[chave_api]
            
            valor_atual = float(cotacao["bid"])
            variacao_pct = float(cotacao["pctChange"])
            maxima = float(cotacao["high"])
            minima = float(cotacao["low"])
            
            # Formatação da data
            data_atualizacao = datetime.strptime(cotacao["create_date"], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y às %H:%M:%S")

            st.success("Cotação obtida com sucesso!")

            # Utilizamos o container nativo do Streamlit para criar o cartão de resultados
            with st.container(border=True):
                
                # Exibição do valor principal
                st.metric(
                    label=f"Valor de Compra ({MOEDAS[moeda_chave]['nome']})",
                    value=f"R$ {valor_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    delta=f"{variacao_pct:+.2f}%"
                )

                st.divider()

                # Informações detalhadas em colunas
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="📈 Máxima do Dia", 
                        value=f"R$ {maxima:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    )
                with col2:
                    st.metric(
                        label="📉 Mínima do Dia", 
                        value=f"R$ {minima:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    )

                st.caption(f"🕒 Última atualização: {data_atualizacao}")
        else:
            st.warning("Não foi possível processar a resposta para a moeda informada.")
>>>>>>> fec7ec7407c244b54519e122aba8bbd4d955a7d0
