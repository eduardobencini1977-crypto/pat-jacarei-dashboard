import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import datetime
import plotly.express as px # Biblioteca para gráficos precisos

st.set_page_config(page_title="PAT Jacareí", layout="wide")

# Refresh de 2 minutos
st_autorefresh(interval=120000, key="datarefresh")

@st.cache_data(ttl=120)
def carregar_dados():
    # Dados idênticos aos da sua imagem
    dados = {
        "Vaga": ["Auxiliar de Produção", "Estoquista", "Vendedor Externo", "Recepcionista"],
        "Quantidade": [12, 7, 4, 2],
        "Bairro": ["Centro", "Parque Meia Lua", "Jd. Califórnia", "Vila Branca"]
    }
    return pd.DataFrame(dados)

df = carregar_dados()

st.title("📊 Painel de Vagas PAT Jacareí")
st.caption(f"Última atualização: {datetime.datetime.now().strftime('%H:%M:%S')}")

# --- MÉTRICAS ---
m1, m2, m3 = st.columns(3)
m1.metric("Total de Vagas", df["Quantidade"].sum())
m2.metric("Vaga em Destaque", df.iloc[0]["Vaga"])
m3.metric("Cidade", "Jacareí")

st.divider()

col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("Distribuição por Vaga")
    # Criando um gráfico que respeita exatamente os valores numéricos
    fig = px.bar(
        df, 
        x="Vaga", 
        y="Quantidade", 
        text="Quantidade", # Mostra o número em cima da barra
        color="Vaga",
        color_discrete_sequence=["#0068c9"] # Cor azul padrão
    )
    fig.update_traces(textposition='outside') # Coloca o número fora da barra
    fig.update_layout(showlegend=False, yaxis_title="Nº de Vagas")
    
    st.plotly_chart(fig, use_container_width=True)

with col_dir:
    st.subheader("Lista Detalhada")
    st.dataframe(df, use_container_width=True, hide_index=True)

st.caption("Configurado para atualização automática a cada 120 segundos.")
