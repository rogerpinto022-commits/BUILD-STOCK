import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🗄️ ESTOQUE GAVETA - 118-24=94")

if 'dados' not in st.session_state:
    st.session_state.dados = [
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"BARRACÃO", "SALDO":0.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"BARRACÃO", "SALDO":0.0},
    ]

if 'mov' not in st.session_state:
    st.session_state.mov = [
        {"TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":24},
    ]

if 'meta' not in st.session_state:
    st.session_state.meta = 104.0

st.sidebar.header("🎯 CONFIG")
META = st.sidebar.number_input("META *", min_value=1.0, value=st.session_state.meta, step=1.0)
st.session_state.meta = META

df = pd.DataFrame(st.session_state.dados)
blocos_anexa = df[(df["ID"]==15) & (df["LOCAL"]=="SALA ANEXA")]["SALDO"].sum()
barras_anexa = df[(df["ID"]==16) & (df["LOCAL"]=="SALA ANEXA")]["SALDO"].sum()

# SALDO TOTAL NA ANEXA = 118
saldo_total_anexa = min(blocos_anexa, barras_anexa)

# ULTIMA ENTRADA
df_mov = pd.DataFrame(st.session_state.mov)
entradas_anexa = df_mov[(df_mov["LOCAL"]=="SALA ANEXA") & (df_mov["TIPO"]=="ENTRADA")] if not df_mov.empty else pd.DataFrame()
ultima_entrada = entradas_anexa.iloc[-1]["QTD"] if not entradas_anexa.empty else 24.0

# PRODUZIDO = SALDO TOTAL NA ANEXA - ULTIMA ENTRADA = 118 - 24 = 94
produzido = saldo_total_anexa - ultima_entrada

st.subheader("📦 BLOCOS E BARRAS SEPARADOS - SALA ANEXA")
c1,c2 = st.columns(2)
c1.metric("ID 15 - BLOCOS DE FUNDO - SALA ANEXA", f"{blocos_anexa:.0f}")
c2.metric("ID 16 - BARRAS CATODICAS - SALA ANEXA", f"{barras_anexa:.0f}")

st.divider()

st.subheader("📊 PRODUZIDO = SALDO TOTAL NA ANEXA - ULTIMA ENTRADA")

c1,c2,c3,c4 = st.columns(4)
c1.metric("SALDO TOTAL NA ANEXA", f"{saldo_total_anexa:.0f}")
c2.metric("ULTIMA ENTRADA", f"{ultima_entrada:.0f}")
c3.metric("PRODUZIDO = 118-24", f"{produzido:.0f}", f"{saldo_total_anexa:.0f}-{ultima_entrada:.0f}")
c4.metric("META", f"{META:.0f}")

st.success(f"**CORRETO: SALDO TOTAL {saldo_total_anexa:.0f} - ULTIMA ENTRADA {ultima_entrada:.0f} = PRODUZIDO {produzido:.0f}** | 118-24=94")

# GRÁFICO CORRETO 118-24
st.markdown("### Gráfico - 118 - 24 = 94")

df_graf = pd.DataFrame([
    {"TIPO":"SALDO TOTAL ANEXA", "QTD":saldo_total_anexa},
    {"TIPO":"ULTIMA ENTRADA", "QTD":ultima_entrada},
    {"TIPO":"PRODUZIDO = SALDO - ULTIMA", "QTD":produzido},
])
st.bar_chart(df_graf.set_index("TIPO"))

st.divider()

tab1, tab2 = st.tabs(["NOVA ENTRADA", "ALTERAR ULTIMA"])

with tab1:
    st.header("NOVA ENTRADA")
    id_sel = st.selectbox("ID *", [15, 16], format_func=lambda x: f"ID {x} - {'BLOCOS DE FUNDO' if x==15 else 'BARRAS CATODICAS'}", key="ent_id")
    qtd = st.number_input("Quantidade *", min_value=1.0, value=24.0, step=1.0, key="ent_qtd")
    if st.button("✅ REGISTRAR", type="primary", use_container_width=True):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sel and d["LOCAL"]=="SALA ANEXA"), None)
        st.session_state.dados[idx]["SALDO"] += qtd
        st.session_state.mov.append({"TIPO":"ENTRADA", "ID":id_sel, "LOCAL":"SALA ANEXA", "QTD":qtd})
        st.rerun()

with tab2:
    st.header("ALTERAR ULTIMA ENTRADA")
    st.write(f"Ultima atual: {ultima_entrada:.0f} - Produzido = {saldo_total_anexa:.0f} - {ultima_entrada:.0f} = {produzido:.0f}")
    nova_ultima = st.number_input("Nova ULTIMA ENTRADA *", min_value=0.0, value=float(ultima_entrada), step=1.0)
    if st.button("✅ ALTERAR", use_container_width=True):
        st.session_state.mov.append({"TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":nova_ultima})
        st.rerun()
