import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

st.set_page_config(page_title="Controle Estoque", layout="wide")
fuso_brasil = pytz.timezone('America/Sao_Paulo')
ARQUIVO = "estoque.csv"

# --- CORREÇÃO DO ERRO AQUI ---
if os.path.exists(ARQUIVO):
    try:
        df = pd.read_csv(ARQUIVO)
        if 'data' in df.columns and not df.empty:
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
        else:
            df = pd.DataFrame(columns=["id", "data", "produto", "local", "tipo", "quantidade"])
    except:
        df = pd.DataFrame(columns=["id", "data", "produto", "local", "tipo", "quantidade"])
else:
    df = pd.DataFrame(columns=["id", "data", "produto", "local", "tipo", "quantidade"])

# --- SEU APP CONTINUA IGUAL ---
st.sidebar.header("Lançamento")
agora = datetime.now(fuso_brasil)
st.sidebar.caption(f"{agora.strftime('%d/%m/%Y %H:%M:%S')} - Brasília")

produto = st.sidebar.text_input("Produto") # Mantém seu campo original
if not produto:
    # Se você usava lista, troca a linha acima por: produto = st.sidebar.selectbox("Produto", ["Cimento", "Areia", "Brita"])
    produto = "Geral"

local = st.sidebar.selectbox("Local", ["Barracão", "Sala Anexa"])
tipo = st.sidebar.selectbox("Tipo", ["Entrada", "Saída"])
qtd = st.sidebar.number_input("Quantidade", min_value=1, value=1)

if st.sidebar.button("Salvar"):
    novo_id = 1 if df.empty else int(df['id'].max()) + 1
    nova = pd.DataFrame([{"id": novo_id, "data": agora, "produto": produto, "local": local, "tipo": tipo, "quantidade": qtd}])
    df = pd.concat([df, nova], ignore_index=True)
    df.to_csv(ARQUIVO, index=False)
    st.sidebar.success("Salvo!")
    st.rerun()

st.title("Estoque")

if not df.empty:
    st.dataframe(df.sort_values('data', ascending=False), use_container_width=True)

    st.divider()
    st.subheader("Excluir registro")
    id_del = st.selectbox("Escolha o ID para excluir", df['id'].tolist())
    if st.button("🗑️ Excluir"):
        df = df[df['id'] != id_del]
        df.to_csv(ARQUIVO, index=False)
        st.success("Excluído!")
        st.rerun()
else:
    st.info("Nenhum registro ainda.")
