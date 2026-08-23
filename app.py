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
    st.session_state.mov = [
        {"TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":118},
        {"TIPO":"ENTRADA", "ID":16, "LOCAL":"SALA ANEXA", "QTD":118},
    ]

if 'meta' not in st.session_state:
    st.session_state.meta = 150.0
if 'desconto' not in st.session_state:
    st.session_state.desconto = 24.0

st.sidebar.header("⚙️ CONFIGURAÇÃO")
META = st.sidebar.number_input("META (produtos) *", min_value=1.0, value=st.session_state.meta, step=1.0)
st.session_state.meta = META
DESCONTO = st.sidebar.number_input("DESCONTO PRODUZIDO *", min_value=0.0, value=st.session_state.desconto, step=1.0, help="PRODUZIDO = TOTAL ENTRADAS - DESCONTO")
st.session_state.desconto = DESCONTO

df = pd.DataFrame(st.session_state.dados)

blocos_anexa = df[(df["ID"]==15) & (df["LOCAL"]=="SALA ANEXA")]["SALDO"].sum()
barras_anexa = df[(df["ID"]==16) & (df["LOCAL"]=="SALA ANEXA")]["SALDO"].sum()
blocos_barracao = df[(df["ID"]==15) & (df["LOCAL"]=="BARRACÃO")]["SALDO"].sum()
barras_barracao = df[(df["ID"]==16) & (df["LOCAL"]=="BARRACÃO")]["SALDO"].sum()

df_mov = pd.DataFrame(st.session_state.mov) if st.session_state.mov else pd.DataFrame(columns=["TIPO","ID","LOCAL","QTD"])
total_entradas_anexa = df_mov[(df_mov["LOCAL"]=="SALA ANEXA") & (df_mov["TIPO"]=="ENTRADA")]["QTD"].sum() if not df_mov.empty else blocos_anexa + barras_anexa
total_entradas_geral = df_mov[df_mov["TIPO"]=="ENTRADA"]["QTD"].sum() if not df_mov.empty else blocos_anexa + barras_anexa

# PRODUZIDO = TOTAL DE ENTRADAS - 24 (ALTERÁVEL)
produzido = total_entradas_anexa - DESCONTO
produzido_geral = total_entradas_geral - DESCONTO

# APRESENTA SEPARADO
st.subheader("📦 BLOCOS DE FUNDO E BARRAS SEPARADOS - SALA ANEXA")

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

st.subheader(f"📊 SALDO TOTAL NA ANEXA 118 + PRODUZIDO = TOTAL ENTRADAS - {DESCONTO:.0f}")

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("TOTAL ENTRADAS SALA ANEXA", f"{total_entradas_anexa:.0f}", f"{blocos_anexa:.0f}+{barras_anexa:.0f}")
c2.metric(f"PRODUZIDO = ENTRADAS - {DESCONTO:.0f}", f"{produzido:.0f}", f"{total_entradas_anexa:.0f}-{DESCONTO:.0f}")
c3.metric("META", f"{META:.0f}")
c4.metric("PRODUZIDO %", f"{(produzido/META*100) if META>0 else 0:.1f}%", f"{produzido:.0f}/{META:.0f}")
c5.metric("SALDO TOTAL ANEXA", f"{min(blocos_anexa, barras_anexa):.0f} prod", f"{blocos_anexa:.0f} blocos + {barras_anexa:.0f} barras")

st.progress(min((produzido/META) if META>0 else 0, 1.0))

# GRÁFICOS SEPARADOS
st.markdown("### Gráfico 1 - BLOCOS DE FUNDO separado")
df_blocos = pd.DataFrame([
    {"LOCAL":"SALA ANEXA", "QTD":blocos_anexa},
    {"LOCAL":"BARRACÃO", "QTD":blocos_barracao},
])
st.bar_chart(df_blocos.set_index("LOCAL"))

st.markdown("### Gráfico 2 - BARRAS CATODICAS separado")
df_barras = pd.DataFrame([
    {"LOCAL":"SALA ANEXA", "QTD":barras_anexa},
    {"LOCAL":"BARRACÃO", "QTD":barras_barracao},
])
st.bar_chart(df_barras.set_index("LOCAL"))

st.markdown(f"### Gráfico 3 - PRODUZIDO = TOTAL ENTRADAS - {DESCONTO:.0f}")
df_prod = pd.DataFrame([
    {"TIPO":"TOTAL ENTRADAS SALA ANEXA", "QTD":total_entradas_anexa},
    {"TIPO":f"DESCONTO (-{DESCONTO:.0f})", "QTD":DESCONTO},
    {"TIPO":"PRODUZIDO", "QTD":produzido},
    {"TIPO":"META", "QTD":META},
])
st.bar_chart(df_prod.set_index("TIPO"))

st.dataframe(df, use_container_width=True)

st.divider()

tab1, tab2 = st.tabs(["NOVA ENTRADA", "NOVA SAIDA"])

with tab1:
    st.header("NOVA ENTRADA")
    st.info(f"PRODUZIDO = {total_entradas_anexa:.0f} - {DESCONTO:.0f} = {produzido:.0f} | Altere o {DESCONTO:.0f} na lateral se necessário")
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
