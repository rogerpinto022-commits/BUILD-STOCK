import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="GAVETA")
st.title("🗄️ GAVETA ESPECIAL")

if 'dados' not in st.session_state:
    st.session_state.dados = [
        {"id":0, "ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "MARCA":"IBAR", "ENTRADA":100.0, "SAIDA":13.0, "SALDO":87.0, "UNIDADE":"UNIDADES", "DATA/HORA":"26/05/2026"},
        {"id":1, "ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"BARRACÃO", "MARCA":"CEMAÇO", "ENTRADA":100.0, "SAIDA":13.0, "SALDO":87.0, "UNIDADE":"UNIDADES", "DATA/HORA":"26/05/2026"},
        {"id":2, "ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "MARCA":"ALUBASE", "ENTRADA":100.0, "SAIDA":13.0, "SALDO":87.0, "UNIDADE":"UNIDADES", "DATA/HORA":"26/05/2026"},
        {"id":3, "ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"BARRACÃO", "MARCA":"ALUBASE", "ENTRADA":100.0, "SAIDA":13.0, "SALDO":87.0, "UNIDADE":"UNIDADES", "DATA/HORA":"26/05/2026"},
    ]

df = pd.DataFrame(st.session_state.dados)

# TOTAIS QUE ATUALIZAM SOZINHOS
total_geral = df["SALDO"].sum()
ent_anexa = df[df["LOCAL"]=="SALA ANEXA"]["ENTRADA"].sum()
sai_anexa = df[df["LOCAL"]=="SALA ANEXA"]["SAIDA"].sum()
saldo_anexa = df[df["LOCAL"]=="SALA ANEXA"]["SALDO"].sum()
ent_bar = df[df["LOCAL"]=="BARRACÃO"]["ENTRADA"].sum()
sai_bar = df[df["LOCAL"]=="BARRACÃO"]["SAIDA"].sum()
saldo_bar = df[df["LOCAL"]=="BARRACÃO"]["SALDO"].sum()

# CARDS GRANDES
c1,c2,c3,c4 = st.columns(4)
c1.metric("SALA ANEXA - TOTAL ENTRADAS", f"{ent_anexa:.0f}", f"Saldo {saldo_anexa:.0f}")
c2.metric("SALA ANEXA - TOTAL SAIDAS", f"{sai_anexa:.0f}", f"Você pediu", delta_color="inverse")
c3.metric("BARRACÃO - TOTAL ENTRADAS", f"{ent_bar:.0f}", f"Saldo {saldo_bar:.0f}")
c4.metric("BARRACÃO - TOTAL SAIDAS", f"{sai_bar:.0f}", f"Saldo {saldo_bar:.0f}")

st.success(f"🟡 TOTAL GERAL {total_geral:.0f} = ANEXA {saldo_anexa:.0f} + BARRACÃO {saldo_bar:.0f} | ATUALIZA SOZINHO A CADA MOVIMENTAÇÃO")

# TOTAL GERAL POR MATERIAL
st.markdown("### 🟡 TOTAL GERAL POR MATERIAL = SOMA ANEXA + BARRACÃO")
df_mat = df.groupby(["ID","DESCRIÇÃO"])[["ENTRADA","SAIDA","SALDO"]].sum().reset_index()
df_mat["ANEXA"] = df_mat.apply(lambda r: df[(df["ID"]==r["ID"]) & (df["LOCAL"]=="SALA ANEXA")]["SALDO"].sum(), axis=1)
df_mat["BARRACAO"] = df_mat.apply(lambda r: df[(df["ID"]==r["ID"]) & (df["LOCAL"]=="BARRACÃO")]["SALDO"].sum(), axis=1)
df_mat["ENT_ANEXA"] = df_mat.apply(lambda r: df[(df["ID"]==r["ID"]) & (df["LOCAL"]=="SALA ANEXA")]["ENTRADA"].sum(), axis=1)
df_mat["SAI_ANEXA"] = df_mat.apply(lambda r: df[(df["ID"]==r["ID"]) & (df["LOCAL"]=="SALA ANEXA")]["SAIDA"].sum(), axis=1)
df_mat["ENT_BAR"] = df_mat.apply(lambda r: df[(df["ID"]==r["ID"]) & (df["LOCAL"]=="BARRACÃO")]["ENTRADA"].sum(), axis=1)
df_mat["SAI_BAR"] = df_mat.apply(lambda r: df[(df["ID"]==r["ID"]) & (df["LOCAL"]=="BARRACÃO")]["SAIDA"].sum(), axis=1)

for _, r in df_mat.iterrows():
    st.markdown(f"**ID {int(r['ID'])} - {r['DESCRIÇÃO']} | TOTAL GERAL {r['SALDO']:.0f} = ANEXA {r['ANEXA']:.0f} + BARRACÃO {r['BARRACAO']:.0f} | ANEXA ENTRADA {r['ENT_ANEXA']:.0f} SAIDA {r['SAI_ANEXA']:.0f} | BARRACÃO ENTRADA {r['ENT_BAR']:.0f} SAIDA {r['SAI_BAR']:.0f}**")

st.divider()

# MOVIMENTAÇÃO
tab1, tab2, tab3 = st.tabs(["📥 ENTRADA", "📤 SAÍDA", "📊 RELATÓRIO"])

with tab1:
    idx = st.selectbox("Material ENTRADA", range(len(st.session_state.dados)), format_func=lambda x: f"ID {st.session_state.dados[x]['ID']} - {st.session_state.dados[x]['DESCRIÇÃO']} - {st.session_state.dados[x]['LOCAL']} - Saldo {st.session_state.dados[x]['SALDO']:.0f}", key="e1")
    qtd = st.number_input("Qtd ENTRADA *", value=10.0, min_value=0.1, key="q1")
    if st.button("✅ CONFIRMAR ENTRADA", type="primary", use_container_width=True):
        prod = st.session_state.dados[idx]
        if prod["LOCAL"]=="SALA ANEXA":
            idx_bar = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==prod["ID"] and d["LOCAL"]=="BARRACÃO"), None)
            if idx_bar is not None and qtd > st.session_state.dados[idx_bar]["SALDO"]:
                st.error(f"BARRACÃO só tem {st.session_state.dados[idx_bar]['SALDO']:.0f}")
            else:
                st.session_state.dados[idx]["ENTRADA"]+=qtd
                st.session_state.dados[idx]["SALDO"]+=qtd
                if idx_bar is not None:
                    st.session_state.dados[idx_bar]["SAIDA"]+=qtd
                    st.session_state.dados[idx_bar]["SALDO"]-=qtd
                st.rerun()
        else:
            st.session_state.dados[idx]["ENTRADA"]+=qtd
            st.session_state.dados[idx]["SALDO"]+=qtd
            st.rerun()

with tab2:
    idx = st.selectbox("Material SAÍDA", range(len(st.session_state.dados)), format_func=lambda x: f"ID {st.session_state.dados[x]['ID']} - {st.session_state.dados[x]['DESCRIÇÃO']} - {st.session_state.dados[x]['LOCAL']} - Saldo {st.session_state.dados[x]['SALDO']:.0f} - Total Saidas Anexa {sai_anexa:.0f}", key="e2")
    qtd = st.number_input("Qtd SAÍDA *", value=5.0, min_value=0.1, key="q2")
    st.info(f"TOTAL DE SAIDAS NA SALA ANEXA: {sai_anexa:.0f} | TOTAL DE SAIDAS NO BARRACÃO: {sai_bar:.0f} - Atualiza sozinho")
    if st.button("✅ CONFIRMAR SAÍDA", type="primary", use_container_width=True):
        if qtd > st.session_state.dados[idx]["SALDO"]:
            st.error("Saldo insuficiente")
        else:
            st.session_state.dados[idx]["SAIDA"]+=qtd
            st.session_state.dados[idx]["SALDO"]-=qtd
            st.rerun()

with tab3:
    st.dataframe(pd.DataFrame(st.session_state.dados), use_container_width=True)
    st.dataframe(df_mat, use_container_width=True)
