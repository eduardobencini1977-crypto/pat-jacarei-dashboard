import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Função para ler a planilha diretamente do Google Drive
def ler_planilha_google(link_original):
    try:
        # Extrai o ID da planilha para criar o link de exportação direta
        if "/d/" in link_original:
            id_planilha = link_original.split("/d/")[1].split("/")[0]
        else:
            id_planilha = link_original
        
        # Link que força o download da versão mais recente em formato Excel (.xlsx)
        # O formato Excel preserva melhor a estrutura de colunas que vimos na imagem
        url_xlsx = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=xlsx"
        
        # Lê o arquivo Excel
        df_raw = pd.read_excel(url_xlsx, header=None)
        return df_raw
    except Exception as e:
        st.error(f"Erro ao ligar ao Google Drive: {e}")
        return None

# 2. Lógica "Garimpeira" ajustada para a imagem real
def extrair_dados_pat(df_raw):
    lista_meses = ["AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
    dados_extraidos = []
    mes_atual = None

    for i in range(len(df_raw)):
        # Limpa o texto da primeira coluna para busca
        celula_texto = str(df_raw.iloc[i, 0]).strip().upper()

        # Identifica quando muda o mês
        if celula_texto in lista_meses:
            mes_atual = celula_texto
        
        # Quando encontra "QUINZENA", os dados estão 2 linhas abaixo (conforme a imagem)
        if "QUINZENA" in celula_texto and mes_atual:
            try:
                # Pula 2 linhas para pegar os valores numéricos
                linha_valores = df_raw.iloc[i + 2]
                
                # Validação: verifica se a primeira célula é um número (Vagas Captadas)
                vagas = pd.to_numeric(linha_valores[0], errors='coerce')
                
                if pd.notnull(vagas):
                    dados_extraidos.append({
                        "Mês": mes_atual.capitalize(),
                        "Quinzena": "1ª" if "PRIMEIRA" in celula_texto else "2ª",
                        "Vagas Captadas": vagas,
                        "Captadas PCD": pd.to_numeric(linha_valores[1], errors='coerce'),
                        "Empresas": pd.to_numeric(linha_valores[2], errors='coerce'),
                        "Atend. Candidatos": pd.to_numeric(linha_valores[3], errors='coerce'),
                        "Contratados": pd.to_numeric(linha_valores[4], errors='coerce')
                    })
            except:
                continue 
                
    return pd.DataFrame(dados_extraidos)

# --- INTERFACE DO DASHBOARD ---
st.set_page_config(page_title="PAT Jacareí - Dashboard", layout="wide")

st.title("📊 PAT Jacareí - Sistema de Monitoramento")
st.caption("Os dados abaixo são extraídos em tempo real da planilha da Meire no Google Drive.")

# LINK DA SUA PLANILHA
LINK_GOOGLE = "https://docs.google.com/spreadsheets/d/13BRpo6qrOXvq0C2Xot4T0MHCOK5WekAc/edit"

# Execução do script
df_bruto = ler_planilha_google(LINK_GOOGLE)

if df_bruto is not None:
    df = extrair_dados_pat(df_bruto)
    
    if not df.empty:
        # Bloco de Métricas Principais
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Vagas Totais", int(df["Vagas Captadas"].sum()))
        m2.metric("Total Contratados", int(df["Contratados"].sum()))
        m3.metric("Atendimentos", int(df["Atend. Candidatos"].sum()))
        
        # Cálculo de eficiência (Contratados / Vagas)
        eficiencia = (df["Contratados"].sum() / df["Vagas Captadas"].sum()) * 100
        m4.metric("Taxa de Colocação", f"{eficiencia:.1f}%")

        st.markdown("---")

        # Gráfico de Colunas
        col_graf, col_tab = st.columns([2, 1])

        with col_graf:
            fig = px.bar(df, x="Mês", y="Contratados", color="Quinzena", 
                         barmode="group", title="Contratações por Quinzena",
                         color_discrete_sequence=["#2E86C1", "#AED6F1"])
            st.plotly_chart(fig, use_container_width=True)
        
        with col_tab:
            st.subheader("Resumo de Dados")
            st.dataframe(df[["Mês", "Quinzena", "Contratados", "Vagas Captadas"]], use_container_width=True)

    else:
        st.warning("Conectado à planilha, mas não encontrei dados de 'QUINZENA'. Verifique se a estrutura da planilha mudou.")

# Rodapé simples
st.sidebar.info("Para atualizar os dados, basta atualizar a página do navegador.")
