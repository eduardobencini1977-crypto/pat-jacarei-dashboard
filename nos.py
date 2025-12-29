import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Função para ler a planilha diretamente do Google Drive (versão CSV para estabilidade)
def ler_planilha_google(link_original):
    try:
        if "/d/" in link_original:
            id_planilha = link_original.split("/d/")[1].split("/")[0]
        else:
            id_planilha = link_original
        
        # Link de exportação em CSV (mais leve e direto para o Pandas)
        url_csv = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
        
        # Lê o arquivo CSV ignorando erros de formatação (header=None para garimpar)
        df_raw = pd.read_csv(url_csv, header=None, on_bad_lines='skip')
        return df_raw
    except Exception as e:
        st.error(f"Erro ao ligar ao Google Drive: {e}")
        return None

# 2. Lógica "Garimpeira" ajustada para os dados reais enviados
def extrair_dados_pat(df_raw):
    lista_meses = ["AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
    dados_extraidos = []
    mes_atual = None

    for i in range(len(df_raw)):
        # Limpa o texto da primeira célula
        celula_texto = str(df_raw.iloc[i, 0]).strip().upper()

        # Identifica o mês
        if celula_texto in lista_meses:
            mes_atual = celula_texto
        
        # Procura a linha que contém os títulos das colunas ("VAGAS CAPTADAS")
        # Os números estão exatamente na linha de baixo (i + 1)
        if "VAGAS CAPTADAS" in celula_texto and mes_atual:
            try:
                # No seu CSV, os números estão na linha imediatamente seguinte aos títulos
                linha_valores = df_raw.iloc[i + 1]
                
                # Converte o primeiro valor (Vagas) para testar se é uma linha de dados
                vagas = pd.to_numeric(linha_valores[0], errors='coerce')
                
                if pd.notnull(vagas):
                    # Identifica se é 1ª ou 2ª quinzena olhando 1 linha para cima (i - 1)
                    info_quinzena = str(df_raw.iloc[i-1, 0]).upper()
                    label_q = "1ª" if "PRIMEIRA" in info_quinzena else "2ª"
                    
                    dados_extraidos.append({
                        "Mês": mes_atual.capitalize(),
                        "Quinzena": label_q,
                        "Vagas Captadas": vagas,
                        "Captadas PCD": pd.to_numeric(linha_valores[1], errors='coerce'),
                        "Atend. Candidatos": pd.to_numeric(linha_valores[3], errors='coerce'),
                        "Contratados": pd.to_numeric(linha_valores[4], errors='coerce')
                    })
            except:
                continue 
                
    return pd.DataFrame(dados_extraidos)

# --- INTERFACE DO DASHBOARD ---
st.set_page_config(page_title="PAT Jacareí - Dashboard", layout="wide")

st.title("📊 PAT Jacareí - Monitoramento Real")
st.caption("Conectado diretamente à planilha da Meire.")

# SEU LINK DO GOOGLE DRIVE
LINK_GOOGLE = "https://docs.google.com/spreadsheets/d/13BRpo6qrOXvq0C2Xot4T0MHCOK5WekAc/edit"

df_bruto = ler_planilha_google(LINK_GOOGLE)

if df_bruto is not None:
    df = extrair_dados_pat(df_bruto)
    
    if not df.empty:
        # Bloco de Métricas
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Vagas Totais", int(df["Vagas Captadas"].sum()))
        m2.metric("Total Contratados", int(df["Contratados"].sum()))
        m3.metric("Atendimentos", int(df["Atend. Candidatos"].fillna(0).sum()))
        
        # Eficiência
        taxa = (df["Contratados"].sum() / df["Vagas Captadas"].sum()) * 100
        m4.metric("Taxa de Colocação", f"{taxa:.1f}%")

        st.markdown("---")

        # Visualização
        col_graf, col_tab = st.columns([2, 1])

        with col_graf:
            fig = px.bar(df, x="Mês", y="Contratados", color="Quinzena", 
                         barmode="group", title="Contratações por Mês",
                         color_discrete_map={"1ª": "#2E86C1", "2ª": "#AED6F1"})
            st.plotly_chart(fig, use_container_width=True)
        
        with col_tab:
            st.subheader("Dados Extraídos")
            st.dataframe(df[["Mês", "Quinzena", "Contratados", "Vagas Captadas"]], use_container_width=True)
    else:
        st.error("Não foi possível encontrar dados. Verifique se os nomes dos meses estão em maiúsculo na planilha.")

st.sidebar.markdown("### Comandos")
if st.sidebar.button("Forçar Atualização"):
    st.rerun()
