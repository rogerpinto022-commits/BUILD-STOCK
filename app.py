import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🗄️ ESTOQUE GAVETA")

if 'dados' not in st.session_state:
    st.session_state.dados = [
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
    ]

if 'mov' not in st.session_state:
    st.session_state.mov = [
        {"DATA": datetime(2026, 8, 5, 8, 0), "TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":50},
        {"DATA": datetime(2026, 8, 15, 10, 0), "TIPO":"ENTRADA", "ID":16, "LOCAL":"SALA ANEXA", "QTD":44},
        {"DATA": datetime(2026, 8, 22, 9, 15), "TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":24},
    ]

if 'meta' not in st.session_state:
    st.session_state.meta = 104.0

# CONFIG META
st.sidebar.header("🎯 CONFIG SALA ANEXA")
META = st.sidebar.number_input("META 104 = 100% *", min_value=1.0, value=st.session_state.meta, step=1.0)
st.session_state.meta = META

# DADOS SALA ANEXA
df = pd.DataFrame(st.session_state.dados)
blocos = df[df["ID"]==15]["SALDO"].sum()
barras = df[df["ID"]==16]["SALDO"].sum()
saldo_total = min(blocos, barras) # 118

df_mov = pd.DataFrame(st.session_state.mov)
df_mov['DATA'] = pd.to_datetime(df_mov['DATA'])
mes_atual = datetime.now().month
ano_atual = datetime.now().year
df_mes = df_mov[(df_mov['DATA'].dt.month==mes_atual) & (df_mov['DATA'].dt.year==ano_atual) & (df_mov["LOCAL"]=="SALA ANEXA")]

entradas_mes = df_mes[df_mes["TIPO"]=="ENTRADA"]
soma_entradas_mes = entradas_mes["QTD"].sum() # 118 na sua foto
ultima_entrada = entradas_mes.iloc[-1]["QTD"] if not entradas_mes.empty else 24.0 # 24
produzido = saldo_total - ultima_entrada # 118-24=94
pct_meta = (soma_entradas_mes / META * 100) if META>0 else 0 # 118/104=113.5%

# ===== MODULO SALA ANEXA COMO NA FOTO =====
st.markdown(f"### 📊 MÊS {mes_atual}/{ano_atual} - META {META:.0f} = 100%")

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("SALDO TOTAL A...", f"{saldo_total:.0f}")
c2.metric("SOMA ENTRADA...", f"{soma_entradas_mes:.0f}")
c3.metric("ULTIMA ENTRA...", f"{ultima_entrada:.0f}")
c4.metric("PRODUZIDO = 1...", f"{produzido:.0f}", f"{saldo_total:.0f}-{ultima_entrada:.0f}")
c5.metric("% META = SOMA..", f"{pct_meta:.1f}%", f"{soma_entradas_mes:.0f}/{META:.0f}")

st.info(f"**META {META:.0f} = 100% | SOMA ENTRADAS MÊS {soma_entradas_mes:.0f} = {pct_meta:.1f}% DA META | PRODUZIDO {produzido:.0f} = SALDO {saldo_total:.0f} - ULTIMA {ultima_entrada:.0f}**")

# GRAFICO TOTAL PRODUZIDO A PARTIR DA SOMA DE ENTRADA MENSAL
st.markdown("### 📈 TOTAL PRODUZIDO A PARTIR DA SOMA DE ENTRADA MENSAL NA SALA ANEXA")

df_graf = pd.DataFrame([
    {"TIPO":"SALDO TOTAL", "QTD":saldo_total},
    {"TIPO":"SOMA ENTRADAS MÊS", "QTD":soma_entradas_mes},
    {"TIPO":"ULTIMA ENTRADA", "QTD":ultima_entrada},
    {"TIPO":"PRODUZIDO", "QTD":produzido},
    {"TIPO":f"META {META:.0f}=100%", "QTD":META},
])
st.bar_chart(df_graf.set_index("TIPO"))

st.divider()

# BOTOES NOVA ENTRADA E NOVA SAIDA NESSE MODULO COMO SALA ANEXA
st.subheader("📦 MÓDULO SALA ANEXA - ENTRADA / SAÍDA")

col_ent, col_sai = st.columns(2)

with col_ent:
    st.markdown("#### ➕ NOVA ENTRADA - SALA ANEXA")
    id_ent = st.selectbox("ID *", [15, 16], format_func=lambda x: f"ID {x} - {'BLOCOS DE FUNDO' if x==15 else 'BARRAS CATODICAS'}", key="ent_id")
    qtd_ent = st.number_input("Quantidade *", min_value=1.0, value=24.0, step=1.0, key="ent_qtd")
    st.text(f"DATA/HORA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    if st.button("✅ REGISTRAR ENTRADA SALA ANEXA", type="primary", use_container_width=True):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent), None)
        st.session_state.dados[idx]["SALDO"] += qtd_ent
        st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"SALA ANEXA", "QTD":qtd_ent})
        st.success(f"Entrada {qtd_ent:.0f} em {datetime.now().strftime('%d/%m %H:%M')} registrada!")
        st.rerun()

with col_sai:
    st.markdown("#### ➖ NOVA SAIDA - SALA ANEXA")
    id_sai = st.selectbox("ID *", [15, 16], format_func=lambda x: f"ID {x} - {'BLOCOS DE FUNDO' if x==15 else 'BARRAS CATODICAS'}", key="sai_id")
    qtd_sai = st.number_input("Quantidade *", min_value=1.0, value=1.0, step=1.0, key="sai_qtd")
    st.text(f"DATA/HORA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    if st.button("✅ REGISTRAR SAIDA SALA ANEXA", type="primary", use_container_width=True):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai), None)
        if qtd_sai > st.session_state.dados[idx]["SALDO"]:
            st.error(f"Só tem {st.session_state.dados[idx]['SALDO']:.0f}")
        else:
            st.session_state.dados[idx]["SALDO"] -= qtd_sai
            st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"SALA ANEXA", "QTD":qtd_sai})
            st.success(f"Saida {qtd_sai:.0f} registrada!")
            st.rerun()

st.divider()
st.write("📅 Histórico SALA ANEXA com DATA e HORA (para cálculo mensal):")
st.dataframe(df_mes.sort_values("DATA", ascending=False), use_container_width=True)
