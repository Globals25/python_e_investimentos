pip install yfinance
import streamlit as st
import pandas as pd
import numpy as np 
import yfinance as yf 
import plotly.express as px 
from datetime import datetime 
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid 

def build_sidebar():
    # Carrega a imagem da logo desejada
    st.image("logo-ptfgrupo-lp-principal.webp")
    
    # Faz a leitura das empresas listadas na bolda no arquivo csv
    ticker_list = pd.read_csv("acoes-listadas-b3.csv", 
                              index_col = 1)

    # Cria uma opção para escolher as empresas da lista importada 
    tickers = st.multiselect(label = "Selecione as Empresas",
                             options = ticker_list)
    
    # Adiciona o .SA nos códigos dos ativos para rodar o yfinance
    tickers = [t + ".SA" for t in tickers]

    # Seleção da data inicial
    start_date = st.date_input("De", 
                               format = "DD/MM/YYYY", 
                               value = datetime(2023,1,1))
    # Seleção da data final
    end_date = st.date_input("Até", 
                             format = "DD/MM/YYYY", 
                             value = "today")

    if tickers:
        # Adicção do IBRX-100 para comparação
        tickers.append("BRAX11.SA")

        # Busca as cotações dos ativos pelo yfinance
        prices = yf.download(tickers, 
                               start = start_date, 
                               end = end_date)["Adj Close"]
        
        prices.columns  = prices.columns.str.rstrip(".SA")

        return tickers, prices    
    return None, None
                        
def build_main(tickers, prices):
    # Criando um array de pesos cuja a soma é 1
    weights = np.ones(len(tickers))/len(tickers)

    # Multiplicação matricial entre os pesos e os valores dos ativos
    prices["Portfolio"] = prices @ weights

    # Normalização dos preços
    norm_prices = 100 * prices / prices.iloc[0]

    # Cálculo dos retornos
    returns = prices.pct_change()[1:]

    # Cálculo da volatilidade anualizada
    vols = returns.std()*np.sqrt(252)

    # Cálculo do retorno normalizado
    rets = (norm_prices.iloc[-1] - 100) / 100

    # Criação do drig de informações
    mygrid = grid(5, 5, 5, 5, 5, 5, vertical_align = "top")

    for t in prices.columns:
        c = mygrid.container(border = True)
        c.subheader(t, divider = "red")
        colA, colB, colC = c.columns(3)
        if t == "Portfolio":
            colA.image("portfolio.png", width = 85)
        else:
            colA.image(f"https://raw.githubusercontent.com/thefintz/icones-b3/main/icones/{t}.png", width = 85)
        
        colB.metric(label = "Retorno", 
                    value = f"{rets[t]:.0%}")
        colB.metric(label = "Volatilidade", 
                    value = f"{vols[t]:.0%}")
        
        style_metric_cards(background_color = "rgb(255,255,255,0)")

    col1, col2 = st.columns(2 , gap = "large")
    with col1:
        st.subheader("Desempenho Relativo")
        st.line_chart(norm_prices, height = 600)

    with col2:
        st.subheader("Risco Retorno")
        fig = px.scatter(x = vols, 
                         y = rets, 
                         text = vols.index,
                         color = rets/vols, 
                         color_continuous_scale = px.colors.sequential.Bluered_r)

        fig.update_traces(textfont_color = "white", 
                          marker = dict(size = 45), 
                          textfont_size = 10)
        
        fig.layout.yaxis.title = "Retorno Total"
        fig.layout.xaxis.title = "Volatilidade (Anualizada)"
        fig.layout.height = 600
        fig.layout.xaxis.tickformat = ".0%"
        fig.layout.yaxis.tickformat = ".0%"
        fig.layout.coloraxis.colorbar.title = "Sharpe"

        st.plotly_chart(fig, use_container_width = True)
    
st.set_page_config(layout = "wide")


with st.sidebar:
    tickers, prices = build_sidebar()

st.title("Python para Investidores")

if tickers:        
    build_main(tickers, prices)


