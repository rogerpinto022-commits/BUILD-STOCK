import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🗄️ ESTOQUE GAVETA - CONTROLE MENSAL")

if 'dados' not in st.session_state:
    st.session_state.dados = [
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"BARRACÃO", "SALDO":0.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"BARRACÃO", "SALDO":0.0},
    ]

if 'mov' not in st.session_state:
    st.session_state.mov = [
        {"DATA": datetime(2026, 8, 1, 8, 0), "TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":50},
        {"DATA": datetime(2026, 8, 10, 14, 30), "TIPO":"ENTRADA", "ID":16, "LOCAL":"SALA ANEXA", "QTD":44},
        {"DATA": datetime(2026, 8, 22, 9, 15), "TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":24}, # ULTIMA
    ]

if 'meta' not in st.session_state:
    st.session_state.meta = 100.0

st.sidebar.header("🎯 META MENSAL = 100%")
META = st.sidebar.number_input("META DO MÊS (produtos) *", min_value=1.0, value=st.session_state.meta, step=1.0)
st.session_state.meta = META
mes_filtro = st.sidebar.selectbox("MÊS", list(range(1,13)), index=datetime.now().month-1)
ano_filtro = st.sidebar.number_input("ANO", value=datetime.now().year, step=1)

df = pd.DataFrame(st.session_state.dados)
blocos_anexa = df[(df["ID"]==15) & (df["LOCAL"]=="SALA ANEXA")]["SALDO"].sum()
barras_anexa = df[(df["ID"]==16) & (df["LOCAL"]=="SALA ANEXA")]["SALDO"].sum()
saldo_total_anexa = min(blocos_anexa, barras_anexa) # 118

# FILTRA POR MÊS
df_mov = pd.DataFrame(st.session_state.mov)
df_mov['DATA'] = pd.to_datetime(df_mov['DATA'])
df_mes = df_mov[(df_mov['DATA'].dt.month==mes_filtro) & (df_mov['DATA'].dt.year==ano_filtro)]

entradas_mes = df_mes[(df_mes["LOCAL"]=="SALA ANEXA") & (df_mes["TIPO"]=="ENTRADA")]
soma_entradas_mes = entradas_mes["QTD"].sum() if not entradas_mes.empty else 0
ultima_entrada_mes = entradas_mes.iloc[-1]["QTD"] if not entradas_mes.empty else 0

# PRODUZIDO = SALDO TOTAL - ULTIMA
produzido = saldo_total_anexa - ultima_entrada_mes

# % META = SOMA ENTRADAS DO MÊS / META
pct_meta = (soma_entradas_mes / META * 100) if META>0 else 0
pct_produzido_meta = (produzido / META * 100) if META>0 else 0

st.subheader("📦 BLOCOS E BARRAS SEPARADOS - SALA ANEXA")
c1,c2 = st.columns(2)
c1.metric("ID 15 - BLOCOS DE FUNDO", f"{blocos_anexa:.0f}")
c2.metric("ID 16 - BARRAS CATODICAS", f"{barras_anexa:.0f}")

st.divider()

st.subheader(f"📊 MÊS {mes_filtro}/{ano_filtro} - META {META:.0f} = 100%")

col1,col2,col3,col4,col5 = st.columns(5)
col1.metric("SALDO TOTAL ANEXA", f"{saldo_total_anexa:.0f}")
col2.metric("SOMA ENTRADAS NO MÊS", f"{soma_entradas_mes:.0f}")
col3.metric("ULTIMA ENTRADA MÊS", f"{ultima_entrada_mes:.0f}")
col4.metric("PRODUZIDO = 118-24", f"{produzido:.0f}", f"{saldo_total_anexa:.0f}-{ultima_entrada_mes:.0f}")
col5.metric(f"% META = SOMA/META", f"{pct_meta:.1f}%", f"{soma_entradas_mes:.0f}/{META:.0f}")

st.info(f"**META {META:.0f} = 100%** | SOMA ENTRADAS MÊS {soma_entradas_mes:.0f} = {pct_meta:.1f}% DA META | PRODUZIDO {produzido:.0f} = SALDO {saldo_total_anexa:.0f} - ULTIMA {ultima_entrada_mes:.0f}")

st.progress(min(pct_meta/100, 1.0))

# GRÁFICOS
st.markdown("### Gráfico 1 - SOMA ENTRADAS NO MÊS vs META 100%")
df_g1 = pd.DataFrame([
    {"TIPO":"SOMA ENTRADAS MÊS", "QTD":soma_entradas_mes},
    {"TIPO":"META 100%", "QTD":META},
    {"TIPO":"PRODUZIDO 118-24", "QTD":produzido},
])
st.bar_chart(df_g1.set_index("TIPO"))

st.markdown("### Gráfico 2 - PRODUZIDO = SALDO - ULTIMA")
df_g2 = pd.DataFrame([
    {"TIPO":"SALDO TOTAL ANEXA 118", "QTD":saldo_total_anexa},
    {"TIPO":"ULTIMA ENTRADA 24", "QTD":ultima_entrada_mes},
    {"TIPO":"PRODUZIDO 94", "QTD":produzido},
])
st.bar_chart(df_g2.set_index("TIPO"))

st.write(f"📅 Movimentações {mes_filtro}/{ano_filtro} com DATA e HORA:")
st.dataframe(df_mes.sort_values("DATA"), use_container_width=True)

st.divider()

tab1, tab2 = st.tabs(["NOVA ENTRADA COM DATA/HORA", "NOVA SAIDA"])

with tab1:
    st.header("NOVA ENTRADA - registra DATA e HORA automático")
    id_sel = st.selectbox("ID *", [15, 16], format_func=lambda x: f"ID {x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="ent_id")
    qtd = st.number_input("Qtd *", min_value=1.0, value=24.0, step=1.0, key="ent_qtd")
    data_hora = st.datetime_input = st.text_input("DATA/HORA (auto)", value=datetime.now().strftime("%d/%m/%Y %H:%M:%S"), disabled=True)
    if st.button("✅ REGISTRAR ENTRADA", type="primary", use_container_width=True):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sel and d["LOCAL"]=="SALA ANEXA"), None)
        st.session_state.dados[idx]["SALDO"] += qtd
        st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_sel, "LOCAL":"SALA ANEXA", "QTD":qtd})
        st.success(f"Entrada {qtd:.0f} registrada em {datetime.now().strftime('%d/%m/%Y %H:%M')} - SOMA MÊS agora {soma_entradas_mes+qtd:.0f}")
        st.rerun()

with tab2:
    st.header("NOVA SAIDA")
    id_sel = st.selectbox("ID *", [15, 16], format_func=lambda x: f"ID {x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="sai_id")
    qtd = st.number_input("Qtd *", min_value=1.0, value=1.0, step=1.0, key="sai_qtd")
    if st.button("✅ SAIDA", type="primary", use_container_width=True):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sel and d["LOCAL"]=="SALA ANEXA"), None)
        st.session_state.dados[idx]["SALDO"] -= qtd
        st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sel, "LOCAL":"SALA ANEXA", "QTD":qtd})
        st.rerun()
