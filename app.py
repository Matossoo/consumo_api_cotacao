import streamlit as st
import requests
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