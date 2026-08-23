import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🗄️ ESTOQUE GAVETA - 1 PRODUTO = 1 BLOCO + 1 BARRA")

if 'dados' not in st.session_state:
    st.session_state.dados = [
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"BARRACÃO", "SALDO":210.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"BARRACÃO", "SALDO":502.0},
    ]

if 'mov' not in st.session_state:
    st.session_state.mov = [
        {"TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":118},
        {"TIPO":"ENTRADA", "ID":15, "LOCAL":"BARRACÃO", "QTD":210},
        {"TIPO":"ENTRADA", "ID":16, "LOCAL":"SALA ANEXA", "QTD":118},
        {"TIPO":"ENTRADA", "ID":16, "LOCAL":"BARRACÃO", "QTD":502},
    ]

if 'meta' not in st.session_state:
    st.session_state.meta = 150.0

# CAMPO META
st.sidebar.header("🎯 META MENSAL")
st.sidebar.write("Quantos produtos precisa fazer no mês")
meta = st.sidebar.number_input("META *", min_value=1.0, value=st.session_state.meta, step=1.0)
st.session_state.meta = meta
META = meta

df = pd.DataFrame(st.session_state.dados)

# SALDOS
for id_item in [15, 16]:
    df_item = df[df["ID"]==id_item]
    anexa = df_item[df_item["LOCAL"]=="SALA ANEXA"]["SALDO"].sum()
    barracao = df_item[df_item["LOCAL"]=="BARRACÃO"]["SALDO"].sum()
    geral = anexa + barracao
    st.markdown(f"### ID {id_item} - {df_item.iloc[0]['DESCRIÇÃO']}")
    c1,c2,c3 = st.columns(3)
    c1.metric("SALDO SALA ANEXA", f"{anexa:.0f}")
    c2.metric("SALDO BARRACÃO", f"{barracao:.0f}")
    c3.metric("ESTOQUE GERAL", f"{geral:.0f}")

st.divider()

# PRODUZIDO = BLOCOS E BARRAS = 1 PRODUTO
blocos_anexa = df[(df["ID"]==15) & (df["LOCAL"]=="SALA ANEXA")]["SALDO"].sum()
barras_anexa = df[(df["ID"]==16) & (df["LOCAL"]=="SALA ANEXA")]["SALDO"].sum()

# 1 BLOCO + 1 BARRA = 1 PRODUTO -> PRODUZIDO É O MENOR DOS DOIS
total_geral_sala_anexa = blocos_anexa + barras_anexa
produzido = min(blocos_anexa, barras_anexa) # 1 PRODUTO = 1 BLOCO + 1 BARRA

# % PRODUZIDO = META / PRODUZIDO e PRODUZIDO / META
pct_produzido_meta = (produzido / META * 100) if META>0 else 0
pct_meta_produzido = (META / produzido * 100) if produzido>0 else 0

st.subheader(f"🏭 TOTAL GERAL SALA ANEXA: BLOCOS {blocos_anexa:.0f} + BARRAS {barras_anexa:.0f}")

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("TOTAL GERAL BLOCOS+BARRAS SALA ANEXA", f"{total_geral_sala_anexa:.0f}", f"{blocos_anexa:.0f}+{barras_anexa:.0f}")
c2.metric("BLOCOS SALA ANEXA", f"{blocos_anexa:.0f}")
c3.metric("BARRAS SALA ANEXA", f"{barras_anexa:.0f}")
c4.metric("PRODUZIDO = 1 BLOCO+1 BARRA = 1 PRODUTO", f"{produzido:.0f}", f"min({blocos_anexa:.0f},{barras_anexa:.0f})")
c5.metric(f"PRODUZIDO % = {produzido:.0f}/{META:.0f}", f"{pct_produzido_meta:.1f}%")

st.info(f"**REGRA:** BLOCOS E BARRAS = 1 PRODUTO | Você tem {blocos_anexa:.0f} blocos e {barras_anexa:.0f} barras na SALA ANEXA, então consegue produzir **{produzido:.0f} produtos** | META {META:.0f} | **{pct_produzido_meta:.1f}% da META** | Falta {META-produzido:.0f} produtos")

st.progress(min(pct_produzido_meta/100, 1.0))

# GRÁFICO REFLETE EXATAMENTE - NÃO SOMA TUDO
st.markdown("### Gráfico 1 - Saldo por Local (exato da imagem)")

df_graf1 = pd.DataFrame([
    {"ITEM":"ID 15 BLOCOS - ANEXA", "QTD":blocos_anexa},
    {"ITEM":"ID 15 BLOCOS - BARRACÃO", "QTD":df[(df["ID"]==15) & (df["LOCAL"]=="BARRACÃO")]["SALDO"].sum()},
    {"ITEM":"ID 16 BARRAS - ANEXA", "QTD":barras_anexa},
    {"ITEM":"ID 16 BARRAS - BARRACÃO", "QTD":df[(df["ID"]==16) & (df["LOCAL"]=="BARRACÃO")]["SALDO"].sum()},
])
st.bar_chart(df_graf1.set_index("ITEM"))

st.markdown("### Gráfico 2 - TOTAL GERAL BLOCOS E BARRAS NA SALA ANEXA + PRODUZIDO")

df_graf2 = pd.DataFrame([
    {"TIPO":"BLOCOS SALA ANEXA", "QTD":blocos_anexa},
    {"TIPO":"BARRAS SALA ANEXA", "QTD":barras_anexa},
    {"TIPO":"TOTAL GERAL SALA ANEXA", "QTD":total_geral_sala_anexa},
    {"TIPO":"PRODUZIDO (1 BLOCO+1 BARRA=1 PRODUTO)", "QTD":produzido},
    {"TIPO":"META", "QTD":META},
])
st.bar_chart(df_graf2.set_index("TIPO"))

st.markdown("### Gráfico 3 - PRODUZIDO % = META / PRODUZIDO")

df_graf3 = pd.DataFrame([
    {"TIPO":"PRODUZIDO", "QTD":produzido},
    {"TIPO":"META", "QTD":META},
])
st.bar_chart(df_graf3.set_index("TIPO"))

st.dataframe(df_graf2, use_container_width=True)

st.divider()

tab1, tab2, tab3 = st.tabs(["NOVA ENTRADA", "NOVA SAIDA", "EXCLUIR REGISTRO"])

with tab1:
    st.header("NOVA ENTRADA")
    st.warning(f"Para fazer 1 PRODUTO precisa: 1 BLOCO + 1 BARRA | SALA ANEXA: {blocos_anexa:.0f} blocos e {barras_anexa:.0f} barras = {produzido:.0f} produtos | META {META:.0f} = {pct_produzido_meta:.1f}%")
    id_sel = st.selectbox("ID *", [15, 16], format_func=lambda x: f"ID {x} - {'BLOCOS DE FUNDO' if x==15 else 'BARRAS CATODICAS'}", key="ent_id")
    local_sel = st.selectbox("LOCAL *", ["SALA ANEXA", "BARRACÃO"], key="ent_local")
    qtd = st.number_input("Quantidade *", min_value=1.0, value=1.0, step=1.0, key="ent_qtd")
    if st.button("✅ REGISTRAR ENTRADA", type="primary", use_container_width=True):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sel and d["LOCAL"]==local_sel), None)
        st.session_state.dados[idx]["SALDO"] += qtd
        st.session_state.mov.append({"TIPO":"ENTRADA", "ID":id_sel, "LOCAL":local_sel, "QTD":qtd})
        st.rerun()

with tab2:
    st.header("NOVA SAIDA")
    id_sel = st.selectbox("ID *", [15, 16], format_func=lambda x: f"ID {x} - {'BLOCOS DE FUNDO' if x==15 else 'BARRAS CATODICAS'}", key="sai_id")
    local_sel = st.selectbox("LOCAL *", ["SALA ANEXA", "BARRACÃO"], key="sai_local")
    qtd = st.number_input("Quantidade *", min_value=1.0, value=1.0, step=1.0, key="sai_qtd")
    if st.button("✅ REGISTRAR SAIDA", type="primary", use_container_width=True):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sel and d["LOCAL"]==local_sel), None)
        if qtd > st.session_state.dados[idx]["SALDO"]:
            st.error(f"Só tem {st.session_state.dados[idx]['SALDO']:.0f}")
        else:
            st.session_state.dados[idx]["SALDO"] -= qtd
            st.session_state.mov.append({"TIPO":"SAIDA", "ID":id_sel, "LOCAL":local_sel, "QTD":qtd})
            st.rerun()

with tab3:
    st.header("EXCLUIR REGISTRO")
    if st.session_state.mov:
        st.dataframe(pd.DataFrame(st.session_state.mov), use_container_width=True)
        idx_mov = st.selectbox("Registro para EXCLUIR *", range(len(st.session_state.mov)), format_func=lambda i: f"{st.session_state.mov[i]['TIPO']} ID {st.session_state.mov[i]['ID']} {st.session_state.mov[i]['LOCAL']} {st.session_state.mov[i]['QTD']:.0f}", key="exc")
        if st.checkbox("Confirmo EXCLUIR REGISTRO"):
            if st.button("🗑️ EXCLUIR REGISTRO", use_container_width=True):
                reg = st.session_state.mov[idx_mov]
                idx_dado = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==reg["ID"] and d["LOCAL"]==reg["LOCAL"]), None)
                if reg["TIPO"]=="ENTRADA":
                    st.session_state.dados[idx_dado]["SALDO"] -= reg["QTD"]
                else:
                    st.session_state.dados[idx_dado]["SALDO"] += reg["QTD"]
                del st.session_state.mov[idx_mov]
                st.rerun()
