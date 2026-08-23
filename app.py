import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🗄️ GAVETA ESPECIAL")

if 'dados' not in st.session_state:
    st.session_state.dados = [
        {"id":0, "ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "MARCA":"IBAR", "ENTRADA":0.0, "SAIDA":0.0, "SALDO":0.0},
        {"id":1, "ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"BARRACÃO", "MARCA":"CEMAÇO", "ENTRADA":0.0, "SAIDA":0.0, "SALDO":0.0},
        {"id":2, "ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "MARCA":"ALUBASE", "ENTRADA":0.0, "SAIDA":0.0, "SALDO":0.0},
        {"id":3, "ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"BARRACÃO", "MARCA":"ALUBASE", "ENTRADA":0.0, "SAIDA":0.0, "SALDO":0.0},
    ]

# SALDO LIVRE = ENTRADA - SAIDA
for d in st.session_state.dados:
    d["SALDO"] = d["ENTRADA"] - d["SAIDA"]

df = pd.DataFrame(st.session_state.dados)
total_geral = df["SALDO"].sum() if not df.empty else 0
ent_anexa = df[df["LOCAL"]=="SALA ANEXA"]["ENTRADA"].sum() if not df.empty else 0
sai_anexa = df[df["LOCAL"]=="SALA ANEXA"]["SAIDA"].sum() if not df.empty else 0
saldo_anexa = df[df["LOCAL"]=="SALA ANEXA"]["SALDO"].sum() if not df.empty else 0
ent_bar = df[df["LOCAL"]=="BARRACÃO"]["ENTRADA"].sum() if not df.empty else 0
sai_bar = df[df["LOCAL"]=="BARRACÃO"]["SAIDA"].sum() if not df.empty else 0
saldo_bar = df[df["LOCAL"]=="BARRACÃO"]["SALDO"].sum() if not df.empty else 0

# TOTAIS NA TELA - ATUALIZAM SOZINHO
c1,c2,c3,c4 = st.columns(4)
c1.metric("SALA ANEXA - TOTAL DE ENTRADAS", f"{ent_anexa:.0f}")
c2.metric("SALA ANEXA - TOTAL DE SAIDAS", f"{sai_anexa:.0f}")
c3.metric("BARRACÃO - TOTAL DE ENTRADAS", f"{ent_bar:.0f}")
c4.metric("BARRACÃO - TOTAL DE SAIDAS", f"{sai_bar:.0f}")

st.info(f"🟡 TOTAL GERAL {total_geral:.0f} = ANEXA {saldo_anexa:.0f} + BARRACÃO {saldo_bar:.0f} | SALDO = ENTRADA - SAIDA | ATUALIZA SOZINHO")

# TOTAL GERAL POR MATERIAL
st.markdown("### 🟡 TOTAL GERAL POR MATERIAL = SOMA ANEXA + BARRACÃO")
if not df.empty:
    df_mat = df.groupby(["ID","DESCRIÇÃO"])[["ENTRADA","SAIDA","SALDO"]].sum().reset_index()
    for _, r in df_mat.iterrows():
        anexa_s = df[(df["ID"]==r["ID"]) & (df["LOCAL"]=="SALA ANEXA")]["SALDO"].sum()
        bar_s = df[(df["ID"]==r["ID"]) & (df["LOCAL"]=="BARRACÃO")]["SALDO"].sum()
        st.write(f"**ID {int(r['ID'])} {r['DESCRIÇÃO']} | TOTAL GERAL {r['SALDO']:.0f} = ANEXA {anexa_s:.0f} + BARRACÃO {bar_s:.0f}**")

st.divider()

# CAMPOS COM NOMES QUE VOCÊ PEDIU
tab1, tab2, tab3, tab4 = st.tabs(["REGISTRAR ENTRADA", "REGISTRAR SAIDA", "EXCLUIR REGISTRO", "RELATÓRIO"])

with tab1:
    st.header("REGISTRAR ENTRADA")
    st.caption("Digite a quantidade que vai entrar - Saldo calcula sozinho: ENTRADA - SAIDA")

    col1, col2 = st.columns(2)
    with col1:
        idx = st.selectbox("Selecione o Material *", range(len(st.session_state.dados)), format_func=lambda x: f"ID {st.session_state.dados[x]['ID']} - {st.session_state.dados[x]['DESCRIÇÃO']} - {st.session_state.dados[x]['LOCAL']} - Saldo atual {st.session_state.dados[x]['SALDO']:.0f}", key="sel_entrada")
        qtd_entrada = st.number_input("Quantidade de ENTRADA *", min_value=0.1, value=10.0, step=1.0, key="qtd_entrada")

    with col2:
        st.write("**Dados atuais:**")
        st.write(f"ENTRADA: {st.session_state.dados[idx]['ENTRADA']:.0f}")
        st.write(f"SAIDA: {st.session_state.dados[idx]['SAIDA']:.0f}")
        st.write(f"SALDO: {st.session_state.dados[idx]['SALDO']:.0f}")
        st.write(f"**Depois da ENTRADA:**")
        st.write(f"SALDO: {st.session_state.dados[idx]['SALDO'] + qtd_entrada:.0f}")

    if st.button("✅ REGISTRAR ENTRADA", type="primary", use_container_width=True):
        prod = st.session_state.dados[idx]
        if prod["LOCAL"]=="SALA ANEXA":
            idx_bar = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==prod["ID"] and d["LOCAL"]=="BARRACÃO"), None)
            if idx_bar is not None and qtd_entrada > st.session_state.dados[idx_bar]["SALDO"]:
                st.error(f"BARRACÃO só tem {st.session_state.dados[idx_bar]['SALDO']:.0f}")
            else:
                st.session_state.dados[idx]["ENTRADA"] += qtd_entrada
                st.session_state.dados[idx]["SALDO"] = st.session_state.dados[idx]["ENTRADA"] - st.session_state.dados[idx]["SAIDA"]
                if idx_bar is not None:
                    st.session_state.dados[idx_bar]["SAIDA"] += qtd_entrada
                    st.session_state.dados[idx_bar]["SALDO"] = st.session_state.dados[idx_bar]["ENTRADA"] - st.session_state.dados[idx_bar]["SAIDA"]
                st.success(f"REGISTRAR ENTRADA +{qtd_entrada:.0f} OK - TOTAL ENTRADAS ANEXA {ent_anexa+qtd_entrada:.0f}")
                st.rerun()
        else:
            st.session_state.dados[idx]["ENTRADA"] += qtd_entrada
            st.session_state.dados[idx]["SALDO"] = st.session_state.dados[idx]["ENTRADA"] - st.session_state.dados[idx]["SAIDA"]
            st.success(f"REGISTRAR ENTRADA +{qtd_entrada:.0f} OK - TOTAL ENTRADAS BARRACÃO {ent_bar+qtd_entrada:.0f} - TOTAL GERAL {total_geral+qtd_entrada:.0f}")
            st.rerun()

with tab2:
    st.header("REGISTRAR SAIDA")
    st.caption("Digite a quantidade que vai sair - Saldo calcula sozinho: ENTRADA - SAIDA")

    col1, col2 = st.columns(2)
    with col1:
        idx = st.selectbox("Selecione o Material *", range(len(st.session_state.dados)), format_func=lambda x: f"ID {st.session_state.dados[x]['ID']} - {st.session_state.dados[x]['DESCRIÇÃO']} - {st.session_state.dados[x]['LOCAL']} - Saldo atual {st.session_state.dados[x]['SALDO']:.0f} - TOTAL SAIDAS ANEXA {sai_anexa:.0f}", key="sel_saida")
        qtd_saida = st.number_input("Quantidade de SAIDA *", min_value=0.1, value=5.0, step=1.0, key="qtd_saida")

    with col2:
        st.write("**Dados atuais:**")
        st.write(f"ENTRADA: {st.session_state.dados[idx]['ENTRADA']:.0f}")
        st.write(f"SAIDA: {st.session_state.dados[idx]['SAIDA']:.0f}")
        st.write(f"SALDO: {st.session_state.dados[idx]['SALDO']:.0f}")
        st.info(f"TOTAL DE SAIDAS NA SALA ANEXA: {sai_anexa:.0f}")

    if st.button("✅ REGISTRAR SAIDA", type="primary", use_container_width=True):
        if qtd_saida > st.session_state.dados[idx]["SALDO"]:
            st.error(f"Saldo insuficiente: só tem {st.session_state.dados[idx]['SALDO']:.0f}")
        else:
            st.session_state.dados[idx]["SAIDA"] += qtd_saida
            st.session_state.dados[idx]["SALDO"] = st.session_state.dados[idx]["ENTRADA"] - st.session_state.dados[idx]["SAIDA"]
            if st.session_state.dados[idx]["LOCAL"]=="SALA ANEXA":
                st.success(f"REGISTRAR SAIDA -{qtd_saida:.0f} OK - TOTAL DE SAIDAS NA SALA ANEXA {sai_anexa:.0f} → {sai_anexa+qtd_saida:.0f}")
            else:
                st.success(f"REGISTRAR SAIDA -{qtd_saida:.0f} OK - TOTAL SAIDAS BARRACÃO {sai_bar:.0f} → {sai_bar+qtd_saida:.0f}")
            st.rerun()

with tab3:
    st.header("EXCLUIR REGISTRO")
    st.error("⚠️ Cuidado: Excluir vai reduzir TOTAL GERAL")

    idx = st.selectbox("Selecione o Registro para EXCLUIR *", range(len(st.session_state.dados)), format_func=lambda x: f"ID {st.session_state.dados[x]['ID']} - {st.session_state.dados[x]['DESCRIÇÃO']} - {st.session_state.dados[x]['LOCAL']} - Saldo {st.session_state.dados[x]['SALDO']:.0f}", key="sel_excluir")

    st.write("**Registro selecionado:**")
    st.json(st.session_state.dados[idx])

    confirma = st.checkbox("Confirmo que quero EXCLUIR REGISTRO", key="conf_excluir")

    if st.button("🗑️ EXCLUIR REGISTRO", type="primary", disabled=not confirma, use_container_width=True):
        prod = st.session_state.dados[idx]
        del st.session_state.dados[idx]
        st.success(f"EXCLUIR REGISTRO ID {prod['ID']} OK - TOTAL GERAL {total_geral:.0f} → {total_geral-prod['SALDO']:.0f}")
        st.rerun()

with tab4:
    st.header("RELATÓRIO")
    st.dataframe(pd.DataFrame(st.session_state.dados), use_container_width=True)
