
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🗄️ ESTOQUE - SALDO POR ITEM")

if 'dados' not in st.session_state:
    st.session_state.dados = [
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "ENTRADA":0.0, "SAIDA":0.0, "SALDO":0.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"BARRACÃO", "ENTRADA":0.0, "SAIDA":0.0, "SALDO":0.0},
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "ENTRADA":0.0, "SAIDA":0.0, "SALDO":0.0},
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"BARRACÃO", "ENTRADA":0.0, "SAIDA":0.0, "SALDO":0.0},
    ]

for d in st.session_state.dados:
    d["SALDO"] = d["ENTRADA"] - d["SAIDA"]

df = pd.DataFrame(st.session_state.dados)

# MOSTRA SALDOS PARA CADA ITEM
st.subheader("📦 SALDOS POR ITEM")

for id_item in sorted(df["ID"].unique()):
    df_item = df[df["ID"]==id_item]
    desc = df_item.iloc[0]["DESCRIÇÃO"]

    anexa = df_item[df_item["LOCAL"]=="SALA ANEXA"]["SALDO"].sum() if not df_item[df_item["LOCAL"]=="SALA ANEXA"].empty else 0
    barracao = df_item[df_item["LOCAL"]=="BARRACÃO"]["SALDO"].sum() if not df_item[df_item["LOCAL"]=="BARRACÃO"].empty else 0
    geral = anexa + barracao

    ent_anexa = df_item[df_item["LOCAL"]=="SALA ANEXA"]["ENTRADA"].sum()
    sai_anexa = df_item[df_item["LOCAL"]=="SALA ANEXA"]["SAIDA"].sum()
    ent_bar = df_item[df_item["LOCAL"]=="BARRACÃO"]["ENTRADA"].sum()
    sai_bar = df_item[df_item["LOCAL"]=="BARRACÃO"]["SAIDA"].sum()

    st.markdown(f"**ID {int(id_item)} - {desc}**")
    col1, col2, col3 = st.columns(3)
    col1.metric(f"SALDO SALA ANEXA", f"{anexa:.0f}", f"E {ent_anexa:.0f} S {sai_anexa:.0f}")
    col2.metric(f"SALDO BARRACÃO", f"{barracao:.0f}", f"E {ent_bar:.0f} S {sai_bar:.0f}")
    col3.metric(f"ESTOQUE GERAL", f"{geral:.0f}", f"{anexa:.0f}+{barracao:.0f}")

st.divider()

# SÓ 2 CAMPOS QUE VOCÊ PEDIU
tab1, tab2 = st.tabs(["NOVA ENTRADA", "NOVA SAIDA"])

with tab1:
    st.header("NOVA ENTRADA")
    st.caption("Saldo começa em 0 - Entrada inicia o saldo")

    c1, c2 = st.columns(2)
    with c1:
        idx = st.selectbox("Item *", range(len(st.session_state.dados)), format_func=lambda i: f"ID {st.session_state.dados[i]['ID']} - {st.session_state.dados[i]['DESCRIÇÃO']} - {st.session_state.dados[i]['LOCAL']} | SALDO {st.session_state.dados[i]['SALDO']:.0f}", key="ent")
        qtd = st.number_input("Qtd ENTRADA *", min_value=0.1, value=10.0, step=1.0)

    with c2:
        st.write(f"**Item:** {st.session_state.dados[idx]['DESCRIÇÃO']}")
        st.write(f"**Local:** {st.session_state.dados[idx]['LOCAL']}")
        st.write(f"**Saldo neste local:** {st.session_state.dados[idx]['SALDO']:.0f}")
        st.write(f"**Saldo depois:** {st.session_state.dados[idx]['SALDO']+qtd:.0f}")

    if st.button("✅ REGISTRAR ENTRADA", type="primary", use_container_width=True):
        st.session_state.dados[idx]["ENTRADA"] += qtd
        st.session_state.dados[idx]["SALDO"] = st.session_state.dados[idx]["ENTRADA"] - st.session_state.dados[idx]["SAIDA"]
        st.success(f"ENTRADA +{qtd:.0f} em {st.session_state.dados[idx]['LOCAL']}")
        st.rerun()

with tab2:
    st.header("NOVA SAIDA")

    c1, c2 = st.columns(2)
    with c1:
        idx = st.selectbox("Item *", range(len(st.session_state.dados)), format_func=lambda i: f"ID {st.session_state.dados[i]['ID']} - {st.session_state.dados[i]['DESCRIÇÃO']} - {st.session_state.dados[i]['LOCAL']} | SALDO {st.session_state.dados[i]['SALDO']:.0f}", key="sai")
        qtd = st.number_input("Qtd SAIDA *", min_value=0.1, value=5.0, step=1.0, key="qtd_sai")

    with c2:
        st.write(f"**Item:** {st.session_state.dados[idx]['DESCRIÇÃO']}")
        st.write(f"**Local:** {st.session_state.dados[idx]['LOCAL']}")
        st.write(f"**Saldo neste local:** {st.session_state.dados[idx]['SALDO']:.0f}")
        if qtd > st.session_state.dados[idx]['SALDO']:
            st.error("Saldo insuficiente neste local")

    if st.button("✅ REGISTRAR SAIDA", type="primary", use_container_width=True):
        if qtd > st.session_state.dados[idx]["SALDO"]:
            st.error(f"Só tem {st.session_state.dados[idx]['SALDO']:.0f} em {st.session_state.dados[idx]['LOCAL']}")
        else:
            st.session_state.dados[idx]["SAIDA"] += qtd
            st.session_state.dados[idx]["SALDO"] = st.session_state.dados[idx]["ENTRADA"] - st.session_state.dados[idx]["SAIDA"]
            st.success(f"SAIDA -{qtd:.0f} de {st.session_state.dados[idx]['LOCAL']}")
            st.rerun()

st.divider()
st.caption("Relatório")
st.dataframe(pd.DataFrame(st.session_state.dados), use_container_width=True)
