import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🗄️ ESTOQUE GAVETA")

if 'dados' not in st.session_state:
    # VALORES EXATOS DA SUA IMAGEM
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
    st.session_state.meta = 300.0

# CAMPO META
st.sidebar.header("🎯 META")
st.sidebar.caption("Campo para preencher META mensal")
meta_input = st.sidebar.number_input("META *", min_value=1.0, value=st.session_state.meta, step=1.0)
st.session_state.meta = meta_input
META = st.session_state.meta

df = pd.DataFrame(st.session_state.dados)

# SALDOS EXATOS
st.subheader("📦 SALDOS - COMO NA IMAGEM")

for id_item in [15, 16]:
    df_item = df[df["ID"]==id_item]
    anexa = df_item[df_item["LOCAL"]=="SALA ANEXA"]["SALDO"].sum()
    barracao = df_item[df_item["LOCAL"]=="BARRACÃO"]["SALDO"].sum()
    geral = anexa + barracao
    st.markdown(f"### ID {id_item} - {df_item.iloc[0]['DESCRIÇÃO']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("SALDO SALA ANEXA", f"{anexa:.0f}")
    c2.metric("SALDO BARRACÃO", f"{barracao:.0f}")
    c3.metric("ESTOQUE GERAL", f"{geral:.0f}")

st.divider()

# CALCULOS QUE VOCÊ PEDIU AGORA
# TOTAL GERAL DE BLOCOS E BARRAS NA SALA ANEXA
blocos_anexa = df[df["ID"]==15][df["LOCAL"]=="SALA ANEXA"]["SALDO"].sum()
barras_anexa = df[df["ID"]==16][df["LOCAL"]=="SALA ANEXA"]["SALDO"].sum()
total_geral_sala_anexa = blocos_anexa + barras_anexa

# TOTAL GERAL BLOCOS E BARRAS NA SALA ANEXA = 118 + 118 = 236
# PRODUZIDO = TOTAL GERAL SALA ANEXA
produzido_qtd = total_geral_sala_anexa

# PRODUZIDO EM % = PRODUZIDO / META * 100 (ou META/PRODUZIDO como você escreveu)
produzido_percent_meta_por_produzido = (META / produzido_qtd * 100) if produzido_qtd>0 else 0
produzido_percent_produzido_por_meta = (produzido_qtd / META * 100) if META>0 else 0

# TOTAL DE ENTRADAS
df_mov = pd.DataFrame(st.session_state.mov)
total_entradas = df_mov[df_mov["TIPO"]=="ENTRADA"]["QTD"].sum()
total_realizado = total_entradas
sai_anexa = df_mov[(df_mov["LOCAL"]=="SALA ANEXA") & (df_mov["TIPO"]=="SAIDA")]["QTD"].sum()
sai_anexa_div13 = sai_anexa / 13 if sai_anexa>0 else 0

st.subheader(f"📊 TOTAL GERAL SALA ANEXA: {total_geral_sala_anexa:.0f} | META: {META:.0f}")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("TOTAL GERAL BLOCOS+BARRAS SALA ANEXA", f"{total_geral_sala_anexa:.0f}", f"{blocos_anexa:.0f}+{barras_anexa:.0f}")
col2.metric("META", f"{META:.0f}")
col3.metric("PRODUZIDO (QTD)", f"{produzido_qtd:.0f}", "= TOTAL SALA ANEXA")
col4.metric("PRODUZIDO % = PRODUZIDO/META", f"{produzido_percent_produzido_por_meta:.1f}%", f"{produzido_qtd:.0f}/{META:.0f}")
col5.metric("META/PRODUZIDO %", f"{produzido_percent_meta_por_produzido:.1f}%", f"{META:.0f}/{produzido_qtd:.0f}")

st.progress(min(produzido_percent_produzido_por_meta/100, 1.0))

# GRÁFICO REFLETE EXATAMENTE AS INFORMAÇÕES - NÃO SOMA TUDO
st.markdown("### Gráfico 1 - Exato da imagem (por Item e Local)")

df_graf = pd.DataFrame([
    {"ITEM":"ID 15 BLOCOS DE FUNDO - SALA ANEXA", "SALDO": blocos_anexa},
    {"ITEM":"ID 15 BLOCOS DE FUNDO - BARRACÃO", "SALDO": df[df["ID"]==15][df["LOCAL"]=="BARRACÃO"]["SALDO"].sum()},
    {"ITEM":"ID 16 BARRAS CATODICAS - SALA ANEXA", "SALDO": barras_anexa},
    {"ITEM":"ID 16 BARRAS CATODICAS - BARRACÃO", "SALDO": df[df["ID"]==16][df["LOCAL"]=="BARRACÃO"]["SALDO"].sum()},
])
st.bar_chart(df_graf.set_index("ITEM"))

st.markdown("### Gráfico 2 - TOTAL GERAL BLOCOS E BARRAS NA SALA ANEXA")

df_total_anexa = pd.DataFrame([
    {"TIPO":"BLOCOS SALA ANEXA", "QTD":blocos_anexa},
    {"TIPO":"BARRAS SALA ANEXA", "QTD":barras_anexa},
    {"TIPO":"TOTAL GERAL SALA ANEXA", "QTD":total_geral_sala_anexa},
    {"TIPO":"META", "QTD":META},
])
st.bar_chart(df_total_anexa.set_index("TIPO"))

st.markdown("### Gráfico 3 - PRODUZIDO em % = META / PRODUZIDO")

df_perc = pd.DataFrame([
    {"TIPO":"PRODUZIDO QTD", "QTD":produzido_qtd},
    {"TIPO":"META", "QTD":META},
    {"TIPO":"PRODUZIDO % (PRODUZIDO/META)", "QTD":produzido_percent_produzido_por_meta},
    {"TIPO":"META/PRODUZIDO %", "QTD":produzido_percent_meta_por_produzido},
])
st.bar_chart(df_perc.set_index("TIPO"))

st.dataframe(df_total_anexa, use_container_width=True)

st.divider()

tab1, tab2, tab3 = st.tabs(["NOVA ENTRADA", "NOVA SAIDA", "EXCLUIR REGISTRO"])

with tab1:
    st.header("NOVA ENTRADA")
    st.info(f"TOTAL GERAL SALA ANEXA = {blocos_anexa:.0f} + {barras_anexa:.0f} = {total_geral_sala_anexa:.0f} | META {META:.0f} | PRODUZIDO {produzido_percent_produzido_por_meta:.1f}%")
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
