import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Função para ler a planilha diretamente do Google Drive
def ler_planilha_google(link_original):
    try:
        # Extrai o ID da nova planilha do link fornecido
        if "/d/" in link_original:
            id_planilha = link_original.split("/d/")[1].split("/")[0]
        else:
            id_planilha = link_original
        
        # Link para exportação em CSV para garantir leitura estável
        url_csv = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
        
        # Lê o CSV ignorando linhas problemáticas
        df_raw = pd.read_csv(url_csv, header=None, on_bad_lines='skip')
        return df_raw
    except Exception as e:
        st.error(f"Erro ao ligar ao Google Drive: {e}")
        return None

# 2. Lógica para extrair os dados reais (Agosto a Dezembro)
def extrair_dados_pat(df_raw):
    # Meses presentes no seu relatório real
    lista_meses = ["AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
    dados_extraidos = []
    mes_atual = None

    for i in range(len(df_raw)):
        # Limpa o texto da primeira coluna
        celula_texto = str(df_raw.iloc[i, 0]).strip().upper()

        # Identifica o mês
        if celula_texto in lista_meses:
            mes_atual = celula_texto
        
        # Procura a quinzena e depois "garimpa" os números nas linhas abaixo
        if "QUINZENA" in celula_texto and mes_atual:
            label_q = "1ª" if "PRIMEIRA" in celula_texto else "2ª"
            
            # Procura nas próximas 5 linhas pela linha que contém os números
            for offset in range(1, 6):
                if i + offset < len(df_raw):
                    linha_futura = df_raw.iloc[i + offset]
                    # Tenta converter a primeira coluna para número (Vagas)
                    vagas = pd.to_numeric(linha_futura[0], errors='coerce')
                    
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

# --- CONFIGURAÇÃO DO DASHBOARD (STREAMLIT) ---
st.set_page_config(page_title="PAT Jacareí - Oficial", layout="wide")

st.title("📊 PAT Jacareí - Dashboard de Monitoramento")
st.caption("Dados extraídos em tempo real da planilha Google Drive.")

# NOVO LINK QUE VOCÊ ENVIOU
LINK_ATUALIZADO = "https://docs.google.com/spreadsheets/d/1u2AbsJ-iiZLtHul2jv6yf1TEnYu8kOwe/edit?gid=479008521#gid=479008521"

df_bruto = ler_planilha_google(LINK_ATUALIZADO)

if df_bruto is not None:
    df = extrair_dados_pat(df_bruto)
    
    if not df.empty:
        # Blocos de Números (Métricas)
        c1, c2, c3 = st.columns(3)
        total_vagas = int(df["Vagas"].sum())
        total_contratados = int(df["Contratados"].sum())
        
        c1.metric("Total de Vagas", total_vagas)
        c2.metric("Total de Contratados", total_contratados)
        c3.metric("Taxa de Colocação", f"{(total_contratados/total_vagas)*100:.1f}%")

        st.markdown("---")

        # Gráfico e Tabela
        col_esq, col_dir = st.columns([2, 1])

        with col_esq:
            fig = px.bar(df, x="Mês", y="Contratados", color="Quinzena", 
                         title="Contratações por Mês e Quinzena", 
                         barmode="group",
                         color_discrete_map={"1ª": "#1f77b4", "2ª": "#aec7e8"})
            st.plotly_chart(fig, use_container_width=True)
        
        with col_dir:
            st.write("### Resumo de Dados")
            st.dataframe(df[["Mês", "Quinzena", "Vagas", "Contratados"]], use_container_width=True)
    else:
        st.warning("A planilha foi lida, mas os dados numéricos não foram encontrados. Verifique se os nomes dos meses estão na Coluna A.")

st.sidebar.info("Clique em 'R' no teclado para atualizar os dados.")

