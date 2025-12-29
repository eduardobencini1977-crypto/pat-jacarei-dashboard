import pandas as pd
import streamlit as st
import plotly.express as px

def ler_planilha_google(link_original):
    try:
        if "/d/" in link_original:
            id_planilha = link_original.split("/d/")[1].split("/")[0]
        else:
            id_planilha = link_original
        # Usando exportação CSV para evitar erros de células mescladas
        url_csv = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
        df_raw = pd.read_csv(url_csv, header=None, on_bad_lines='skip')
        return df_raw
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

def extrair_dados_pat(df_raw):
    lista_meses = ["AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
    dados_extraidos = []
    mes_atual = None

    for i in range(len(df_raw)):
        # Limpa o texto da célula para verificação
        celula_texto = str(df_raw.iloc[i, 0]).strip().upper()

        if celula_texto in lista_meses:
            mes_atual = celula_texto
        
        # Procura por 'PRIMEIRA QUINZENA' ou 'SEGUNDA QUINZENA'
        if "QUINZENA" in celula_texto and mes_atual:
            label_q = "1ª" if "PRIMEIRA" in celula_texto else "2ª"
            
            # Procura nas 5 linhas seguintes pela primeira linha que comece com um número
            for offset in range(1, 6):
                if i + offset < len(df_raw):
                    linha_futura = df_raw.iloc[i + offset]
                    vagas = pd.to_numeric(linha_futura[0], errors='coerce')
                    
                    # Se encontrarmos um número, estes são os nossos dados
                    if pd.notnull(vagas):
                        dados_extraidos.append({
                            "Mês": mes_atual.capitalize(),
                            "Quinzena": label_q,
                            "Vagas Captadas": vagas,
                            "Captadas PCD": pd.to_numeric(linha_futura[1], errors='coerce'),
                            "Atendimentos": pd.to_numeric(linha_futura[3], errors='coerce'),
                            "Contratados": pd.to_numeric(linha_futura[4], errors='coerce')
                        })
                        break # Para de procurar nesta quinzena e vai para a próxima
                
    return pd.DataFrame(dados_extraidos)

# --- Layout do Streamlit ---
st.set_page_config(page_title="PAT Jacareí", layout="wide")
st.title("📊 PAT Jacareí - Dashboard")

LINK_GOOGLE = "https://docs.google.com/spreadsheets/d/13BRpo6qrOXvq0C2Xot4T0MHCOK5WekAc/edit"

df_bruto = ler_planilha_google(LINK_GOOGLE)

if df_bruto is not None:
    df = extrair_dados_pat(df_bruto)
    
    if not df.empty:
        # Métricas no topo
        c1, c2, c3 = st.columns(3)
        c1.metric("Vagas Totais", int(df["Vagas Captadas"].sum()))
        c2.metric("Total Contratados", int(df["Contratados"].sum()))
        
        # Gráfico
        fig = px.bar(df, x="Mês", y="Contratados", color="Quinzena", barmode="group",
                     title="Contratações Mensais", color_discrete_sequence=["#004A99", "#66A3FF"])
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela com os dados encontrados para conferência
        st.write("### Conferência de Dados (Extraídos da Planilha)")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("A planilha foi lida, mas os dados numéricos não foram encontrados. Verifique se os meses estão escritos corretamente na coluna A.")
