import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Função para ler a planilha diretamente do Google Drive
def ler_planilha_google(link_original):
    try:
        if "/d/" in link_original:
            id_planilha = link_original.split("/d/")[1].split("/")[0]
        else:
            id_planilha = link_original
        
        # Link para exportação em CSV para garantir leitura estável dos dados
        url_csv = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
        
        # Lê o CSV ignorando linhas problemáticas
        df_raw = pd.read_csv(url_csv, header=None, on_bad_lines='skip')
        return df_raw
    except Exception as e:
        st.error(f"Erro ao ligar ao Google Drive: {e}")
        return None

# 2. Lógica para extrair os dados reais (Agosto a Dezembro)
def extrair_dados_pat(df_raw):
    # Lista de meses presentes no seu relatório 
    lista_meses = ["AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
    dados_extraidos = []
    mes_atual = None

    for i in range(len(df_raw)):
        celula_texto = str(df_raw.iloc[i, 0]).strip().upper()

        # Identifica o mês atual na planilha 
        if celula_texto in lista_meses:
            mes_atual = celula_texto
        
        # Busca a linha numérica após o título da quinzena 
        if "QUINZENA" in celula_texto and mes_atual:
            label_q = "1ª" if "PRIMEIRA" in celula_texto else "2ª"
            
            # Percorre as próximas 5 linhas procurando os números [cite: 2, 3]
            for offset in range(1, 6):
                if i + offset < len(df_raw):
                    linha_futura = df_raw.iloc[i + offset]
                    vagas = pd.to_numeric(linha_futura[0], errors='coerce')
                    
                    # Se encontrar um número, extrai os dados daquela quinzena [cite: 2, 3]
                    if pd.notnull(vagas):
                        dados_extraidos.append({
                            "Mês": mes_atual.capitalize(),
                            "Quinzena": label_q,
                            "Vagas": vagas,
                            "PCD": pd.to_numeric(linha_futura[1], errors='coerce'),
                            "Contratados": pd.to_numeric(linha_futura[4], errors='coerce')
                        })
                        break 
                
    return pd.DataFrame(dados_extraidos)

# --- Configuração da Interface ---
st.set_page_config(page_title="PAT Jacareí Dashboard", layout="wide")
st.title("📊 Painel de Monitoramento PAT Jacareí")

# Substitua pelo seu link real do Google Sheets se for diferente
LINK_GOOGLE = "https://docs.google.com/spreadsheets/d/13BRpo6qrOXvq0C2Xot4T0MHCOK5WekAc/edit"

df_bruto = ler_planilha_google(LINK_GOOGLE)

if df_bruto is not None:
    df = extrair_dados_pat(df_bruto)
    
    if not df.empty:
        # Exibição de métricas baseadas nos dados reais [cite: 2, 3, 4]
        m1, m2, m3 = st.columns(3)
        total_vagas = int(df["Vagas"].sum())
        total_contratados = int(df["Contratados"].sum())
        
        m1.metric("Vagas Totais", total_vagas)
        m2.metric("Total Contratados", total_contratados)
        m3.metric("Taxa de Sucesso", f"{(total_contratados/total_vagas)*100:.1f}%")

        # Gráfico comparativo por mês [cite: 2, 3, 5, 7]
        fig = px.bar(df, x="Mês", y="Contratados", color="Quinzena", 
                     title="Contratações Realizadas", barmode="group")
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela para conferência dos dados extraídos [cite: 2, 3, 4, 5, 7]
        st.subheader("Dados Extraídos da Planilha")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Não foram encontrados dados numéricos. Verifique a formatação da planilha.")
