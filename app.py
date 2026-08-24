import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

st.set_page_config(page_title="Controle Estoque", layout="wide")
fuso = pytz.timezone('America/Sao_Paulo')
ARQUIVO = "estoque.csv"

# --- CRIA OU LÊ SEM DAR ERRO ---
colunas = ["id", "data", "produto", "local", "tipo", "quantidade"]
if os.path.exists(ARQUIVO):
    try:
        df = pd.read_csv(ARQUIVO)
        # garante que tem todas colunas
        for c in colunas:
            if c not in df.columns:
                df = pd.DataFrame(columns=colunas)
                break
    except:
        df = pd.DataFrame(columns=colunas)
else:
    df = pd.DataFrame(columns=colunas)

# --- SIDEBAR ---
st.sidebar.header("Lançamento")
agora = datetime.now(fuso)
st.sidebar.caption(f"Brasília: {agora.strftime('%d/%m/%Y %H:%M:%S')}")

# MANTÉM SEUS MATERIAIS ORIGINAIS AQUI - edite se quiser
materiais = ["Cimento", "Areia", "Brita", "Tijolo", "Cal", "Outros"]

produto = st.sidebar.selectbox("Produto", materiais)
local = st.sidebar.selectbox("Local", ["Barracão", "Sala Anexa"])
tipo = st.sidebar.selectbox("Tipo", ["Entrada", "Saída"])
qtd = st.sidebar.number_input("Quantidade", min_value=1, value=1)

if st.sidebar.button("Salvar", use_container_width=True):
    novo_id = 1 if df.empty else int(df['id'].max()) + 1
    nova = pd.DataFrame([{
        "id": novo_id,
        "data": agora.strftime('%Y-%m-%d %H:%M:%S'),
        "produto": produto,
        "local": local,
        "tipo": tipo,
        "quantidade": qtd
    }])
    df = pd.concat([df, nova], ignore_index=True)
    df.to_csv(ARQUIVO, index=False)
    st.sidebar.success("Salvo!")
    st.rerun()

# --- TELA ---
st.title("📦 Controle de Estoque")

if df.empty:
    st.info("Nenhum registro ainda. Faça o primeiro lançamento ao lado.")
    st.stop()

# mostra dados
df['data'] = pd.to_datetime(df['data'], errors='coerce')
st.dataframe(df.sort_values('data', ascending=False), use_container_width=True)

# --- EXCLUIR SÓ APARECE SE TIVER DADOS ---
st.divider()
st.subheader("🗑️ Excluir registro")
if 'id' in df.columns and not df.empty:
    id_del = st.selectbox("Escolha o ID para excluir", df['id'].tolist())
    if st.button(f"Excluir ID {id_del}"):
        df = df[df['id'] != id_del]
        df.to_csv(ARQUIVO, index=False)
        st.success(f"ID {id_del} excluído!")
        st.rerun()
