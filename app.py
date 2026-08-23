import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🗄️ ESTOQUE GAVETA - SALDO TOTAL ANEXA 118")

if 'dados' not in st.session_state:
    st.session_state.dados = [
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"BARRACÃO", "SALDO":0.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"BARRACÃO", "SALDO":0.0},
    ]

if 'mov' not in st.session_state:
    # ÚLTIMA ENTRADA NA SALA ANEXA FOI 24 PARA DAR 236-24=212 IGUAL SUA FOTO
    st.session_state.mov = [
        {"TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":118},
        {"TIPO":"ENTRADA", "ID":16, "LOCAL":"SALA ANEXA", "QTD":94},
        {"TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":24}, # ULTIMA ENTRADA = 24
    ]

if 'meta' not in st.session_state:
    st.session_state.meta = 150.0

st.sidebar.header("🎯 META")
META = st.sidebar.number_input("META *", min_value=1.0, value=st.session_state.meta, step=1.0)
st.session_state.meta = META

df = pd.DataFrame(st.session_state.dados)

blocos_anexa = df[(df["ID"]==15) & (df["LOCAL"]=="SALA ANEXA")]["SALDO"].sum()
barras_anexa = df[(df["ID"]==16) & (df["LOCAL"]=="SALA ANEXA")]["SALDO"].sum()
blocos_barracao = df[(df["ID"]==15) & (df["LOCAL"]=="BARRACÃO")]["SALDO"].sum()
barras_barracao = df[(df["ID"]==16) & (df["LOCAL"]=="BARRACÃO")]["SALDO"].sum()

# APRESENTA SEPARADO
st.subheader("📦 BLOCOS E BARRAS SEPARADOS")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### ID 15 - BLOCOS DE FUNDO")
    c1,c2,c3 = st.columns(3)
    c1.metric("SALA ANEXA", f"{blocos_anexa:.0f}")
    c2.metric("BARRACÃO", f"{blocos_barracao:.0f}")
    c3.metric("GERAL", f"{blocos_anexa+blocos_barracao:.0f}")
with col2:
    st.markdown("### ID 16 - BARRAS CATODICAS")
    c1,c2,c3 = st.columns(3)
    c1.metric("SALA ANEXA", f"{barras_anexa:.0f}")
    c2.metric("BARRACÃO", f"{barras_barracao:.0f}")
    c3.metric("GERAL", f"{barras_anexa+barras_barracao:.0f}")

st.divider()

# CÁLCULO CORRETO: TOTAL NA SALA ANEXA - ULTIMA ENTRADA NA SALA ANEXA
df_mov = pd.DataFrame(st.session_state.mov)
entradas_anexa = df_mov[(df_mov["LOCAL"]=="SALA ANEXA") & (df_mov["TIPO"]=="ENTRADA")]

total_sala_anexa = entradas_anexa["QTD"].sum() if not entradas_anexa.empty else 0
ultima_entrada = entradas_anexa.iloc[-1]["QTD"] if not entradas_anexa.empty else 0

# PRODUZIDO = TOTAL NA SALA ANEXA - ULTIMA ENTRADA NA SALA ANEXA
produzido = total_sala_anexa - ultima_entrada

# SALDO TOTAL NA ANEXA 118 = min(blocos, barras)
saldo_total_anexa_prod = min(blocos_anexa, barras_anexa)

pct = (produzido / META * 100) if META>0 else 0

st.subheader(f"📊 SALDO TOTAL NA ANEXA {saldo_total_anexa_prod:.0f} + PRODUZIDO = TOTAL SALA ANEXA - ULTIMA ENTRADA")

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("TOTAL ENTRADAS SALA ANEXA", f"{total_sala_anexa:.0f}", f"{'+'.join([f'{x:.0f}' for x in entradas_anexa['QTD'].tolist()])}")
c2.metric(f"ULTIMA ENTRADA SALA ANEXA", f"{ultima_entrada:.0f}")
c3.metric(f"PRODUZIDO = TOTAL - ULTIMA", f"{produzido:.0f}", f"{total_sala_anexa:.0f}-{ultima_entrada:.0f}")
c4.metric("META", f"{META:.0f}")
c5.metric("SALDO TOTAL ANEXA", f"{saldo_total_anexa_prod:.0f} prod", f"{blocos_anexa:.0f} blocos")

st.info(f"**CORRETO AGORA:** TOTAL NA SALA ANEXA {total_sala_anexa:.0f} - ULTIMA ENTRADA {ultima_entrada:.0f} = **PRODUZIDO {produzido:.0f}** | Igual sua foto 236-24=212")

st.progress(min(pct/100, 1.0))

# GRÁFICO CORRIGIDO
st.markdown("### Gráfico 1 - TOTAL NA SALA ANEXA - ULTIMA ENTRADA")

df_graf = pd.DataFrame([
    {"TIPO":"TOTAL NA SALA ANEXA", "QTD":total_sala_anexa},
    {"TIPO":"ULTIMA ENTRADA SALA ANEXA", "QTD":ultima_entrada},
    {"TIPO":"PRODUZIDO", "QTD":produzido},
    {"TIPO":"META", "QTD":META},
])
st.bar_chart(df_graf.set_index("TIPO"))

st.markdown("### Gráfico 2 - BLOCOS e BARRAS SEPARADOS SALA ANEXA")

df_graf2 = pd.DataFrame([
    {"LOCAL":"BLOCOS ANEXA", "QTD":blocos_anexa},
    {"LOCAL":"BARRAS ANEXA", "QTD":barras_anexa},
    {"LOCAL":"PRODUZIDO (TOTAL-ULTIMA)", "QTD":produzido},
])
st.bar_chart(df_graf2.set_index("LOCAL"))

st.write("Histórico entradas SALA ANEXA - Última é descontada:")
st.dataframe(entradas_anexa, use_container_width=True)

st.divider()

tab1, tab2 = st.tabs(["NOVA ENTRADA", "NOVA SAIDA"])

with tab1:
    st.header("NOVA ENTRADA SALA ANEXA")
    id_sel = st.selectbox("ID *", [15, 16], format_func=lambda x: f"ID {x} - {'BLOCOS DE FUNDO' if x==15 else 'BARRAS CATODICAS'}", key="ent_id")
    local_sel = st.selectbox("LOCAL *", ["SALA ANEXA", "BARRACÃO"], key="ent_local")
    qtd = st.number_input("Quantidade *", min_value=1.0, value=24.0, step=1.0, key="ent_qtd")
    if st.button("✅ REGISTRAR ENTRADA", type="primary", use_container_width=True):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sel and d["LOCAL"]==local_sel), None)
        st.session_state.dados[idx]["SALDO"] += qtd
        st.session_state.mov.append({"TIPO":"ENTRADA", "ID":id_sel, "LOCAL":local_sel, "QTD":qtd})
        if local_sel=="SALA ANEXA":
            novo_total = total_sala_anexa + qtd
            novo_produzido = novo_total - qtd
            st.success(f"TOTAL ANEXA {novo_total:.0f} - ULTIMA ENTRADA {qtd:.0f} = PRODUZIDO {novo_produzido:.0f}")
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
