import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Estoque Simples", layout="centered")

# CONEXÃO SUPABASE - coloca suas keys em Settings > Secrets no Streamlit Cloud
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    MODO_SUPABASE = True
except:
    MODO_SUPABASE = False
    st.warning("MODO LOCAL - Configure Secrets pra salvar no Supabase")

# BUSCA ESTOQUE
def carregar_estoque():
    if MODO_SUPABASE:
        try:
            res = supabase.table("estoque_simples").select("*").order("ID").execute()
            if res.data:
                return res.data
        except:
            pass
    # Fallback local com dados da sua foto
    return [
        {"ID": 1, "DESCRICAO": "CIMENTO - FONDU", "QTD": 12},
        {"ID": 2, "DESCRICAO": "CARBETO DE SILICIO - SHINAGAWA", "QTD": 2.5},
        {"ID": 3, "DESCRICAO": "ARGAMASSA REFRATARIA - TECNOFIRE", "QTD": 5},
        {"ID": 4, "DESCRICAO": "CONCRETO REFRATARIO", "QTD": 3},
        {"ID": 5, "DESCRICAO": "LÃ DE ROCHA - IBAR", "QTD": 4},
        {"ID": 6, "DESCRICAO": "TIJOLO SEMI ISOLANTE", "QTD": 19},
        {"ID": 7, "DESCRICAO": "TIJOLO ISOLANTE", "QTD": 311},
        {"ID": 8, "DESCRICAO": "TIJOLO REFRATARIO", "QTD": 153},
        {"ID": 9, "DESCRICAO": "CORDÃO DE BARRAS", "QTD": 0},
        {"ID": 10, "DESCRICAO": "PLACAS DE BANHO", "QTD": 32},
        {"ID": 11, "DESCRICAO": "CHAMOTE - IBAR", "QTD": 18},
        {"ID": 12, "DESCRICAO": "PASTA FRIA - ELKEN", "QTD": 0},
        {"ID": 13, "DESCRICAO": "PASTA FRIA - CARBON", "QTD": 0},
        {"ID": 14, "DESCRICAO": "BLOCOS LATERAL", "QTD": 0},
        {"ID": 15, "DESCRICAO": "BLOCOS ENGUSADOS", "QTD": 0},
        {"ID": 16, "DESCRICAO": "BARRAS CATÓDICAS", "QTD": 0},
        {"ID": 17, "DESCRICAO": "BLOCOS DE FUNDO", "QTD": 0},
    ]

if "estoque" not in st.session_state:
    st.session_state.estoque = carregar_estoque()

st.title("🧱 ESTOQUE - ID | QTD | ENTRADA/SAÍDA")
st.dataframe(pd.DataFrame(st.session_state.estoque), use_container_width=True, hide_index=True)

st.divider()
id_sel = st.selectbox("ID", [f"{x['ID']} - {x['DESCRICAO']}" for x in st.session_state.estoque])
id_num = int(id_sel.split(" - ")[0])

c1,c2,c3 = st.columns(3)
with c1: qtd = st.number_input("QTD", 0.1, 10000.0, 1.0)
with c2: tipo = st.radio("Tipo", ["ENTRADA","SAÍDA"], horizontal=True)
with c3:
    if st.button("CONFIRMAR", type="primary", use_container_width=True):
        for item in st.session_state.estoque:
            if item["ID"] == id_num:
                nova_qtd = item["QTD"] + qtd if tipo=="ENTRADA" else item["QTD"] - qtd
                if nova_qtd < 0:
                    st.error(f"Sem saldo! Tem {item['QTD']}")
                    st.stop()
                item["QTD"] = nova_qtd
                if MODO_SUPABASE:
                    supabase.table("estoque_simples").update({"QTD": nova_qtd}).eq("ID", id_num).execute()
                st.success(f"{tipo} OK! Novo saldo: {nova_qtd}")
                st.rerun()
