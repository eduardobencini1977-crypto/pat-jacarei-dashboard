import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Função para ler a planilha diretamente do Google Drive (via link)
def ler_planilha_google(link_original):
    # Transforma o link de visualização num link de download direto para o Pandas
    id_planilha = link_original.split("/d/")[1].split("/")[0]
    url_csv = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=xlsx"
    
    try:
        # Lê o ficheiro Excel diretamente da nuvem
        df_raw = pd.read_excel(url_csv, header=None)
        return df_raw
    except Exception as e:
        st.error(f"Erro ao ligar ao Google Drive: {e}")
        return None

# 2. Função "Garimpeira" (a lógica que você já conhece)
def extrair_dados_pat(df_raw):
    lista_meses = ["AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
    dados_extraidos = []
    mes_atual = None

    for i, linha in df_raw.iterrows():
        celula_texto = str(linha[0]).strip().upper()

        if celula_texto in lista_meses:
            mes_atual = celula_texto
        
        if "QUINZENA" in celula_texto and mes_atual:
            try:
                linha_numeros = df_raw.iloc[i + 2]
                if pd.notnull(linha_numeros[0]):
                    dados_extraidos.append({
                        "Mês": mes_atual.capitalize(),
                        "Quinzena": "1ª" if "PRIMEIRA" in celula_texto else "2ª",
                        "Vagas Captadas": float(linha_numeros[0]),
                        "Captadas PCD": float(linha_numeros[1]),
                        "Empresas": float(linha_numeros[2]),
                        "Atend. Candidatos": float(linha_numeros[3]),
                        "Contratados": float(linha_numeros[4])
                    })
            except:
                continue 
    return pd.DataFrame(dados_extraidos)

# --- DASHBOARD ---
st.set_page_config(page_title="PAT Jacareí Cloud", layout="wide")
st.title("📊 PAT Jacareí - Sistema na Nuvem")

LINK_GOOGLE = "https://docs.google.com/spreadsheets/d/1u2AbsJ-iiZLtHul2jv6yf1TEnYu8kOwe/edit?usp=sharing"

df_bruto = ler_planilha_google(LINK_GOOGLE)

if df_bruto is not None:
    df = extrair_dados_pat(df_bruto)
    
    if not df.empty:
        # Métricas
        m1, m2, m3 = st.columns(3)
        m1.metric("Vagas Totais", int(df["Vagas Captadas"].sum()))
        m2.metric("Total Contratados", int(df["Contratados"].sum()))
        m3.metric("Atendimentos", int(df["Atend. Candidatos"].sum()))

        # Gráfico
        fig = px.bar(df, x="Mês", y="Contratados", color="Quinzena", barmode="group", title="Resultados por Mês")
        st.plotly_chart(fig, width="stretch")
        
        st.subheader("Dados em Tempo Real (Google Drive)")
        st.dataframe(df, width="stretch")
    else:
        st.warning("Planilha lida, mas nenhum dado foi encontrado no formato esperado.")