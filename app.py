import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="SALA ANEXA")
st.title("🗄️ SALA ANEXA")

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

# SIDEBAR SÓ META
META = st.sidebar.number_input("META 104 = 100%", value=st.session_state.meta, step=1.0)
st.session_state.meta = META

# CALCULOS
df = pd.DataFrame(st.session_state.dados)
saldo_total = min(df["SALDO"].tolist()) if not df.empty else 0

df_mov = pd.DataFrame(st.session_state.mov)
df_mov['DATA'] = pd.to_datetime(df_mov['DATA'])
df_mes = df_mov[(df_mov['DATA'].dt.month==datetime.now().month) & (df_mov['TIPO']=="ENTRADA")]

soma_mes = df_mes["QTD"].sum()
ultima = df_mes.iloc[-1]["QTD"] if not df_mes.empty else 24.0
produzido = saldo_total - ultima
pct = (soma_mes / META * 100) if META>0 else 0

# TELA LIMPA - SÓ INDICADORES
st.markdown(f"### MÊS {datetime.now().month}/{datetime.now().year} - META {META:.0f} = 100%")
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("SALDO TOTAL", f"{saldo_total:.0f}")
c2.metric("SOMA ENTRADAS", f"{soma_mes:.0f}")
c3.metric("ULTIMA", f"{ultima:.0f}")
c4.metric("PRODUZIDO", f"{produzido:.0f}", f"{saldo_total:.0f}-{ultima:.0f}")
c5.metric("% META", f"{pct:.1f}%")

st.divider()

# SÓ 2 BOTÕES NA TELA PRINCIPAL
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("➕ NOVA ENTRADA")
        st.write("SALA ANEXA")
        id_ent = st.selectbox("ID", [15, 16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="ent_id", label_visibility="collapsed")
        qtd_ent = st.number_input("Qtd", min_value=1.0, value=24.0, step=1.0, key="ent_qtd", label_visibility="collapsed", placeholder="Qtd")
        if st.button("✅ ENTRADA SALA ANEXA", type="primary", use_container_width=True):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent), None)
            st.session_state.dados[idx]["SALDO"] += qtd_ent
            st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"SALA ANEXA", "QTD":qtd_ent})
            st.rerun()

with col2:
    with st.container(border=True):
        st.subheader("➖ NOVA SAIDA")
        st.write("SALA ANEXA")
        id_sai = st.selectbox("ID", [15, 16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="sai_id", label_visibility="collapsed")
        qtd_sai = st.number_input("Qtd", min_value=1.0, value=1.0, step=1.0, key="sai_qtd", label_visibility="collapsed", placeholder="Qtd")
        if st.button("✅ SAIDA SALA ANEXA", use_container_width=True):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai), None)
            if qtd_sai <= st.session_state.dados[idx]["SALDO"]:
                st.session_state.dados[idx]["SALDO"] -= qtd_sai
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"SALA ANEXA", "QTD":qtd_sai})
                st.rerun()

st.divider()

# DEMAIS SÓ COM SELECIONAR GRAFICOS
st.markdown("### 📊 CONSULTA")
consulta = st.selectbox("Selecione para consultar", ["---", "Ver Gráfico Produzido (Soma Mensal)", "Ver Histórico com Data/Hora", "Ver Saldo Detalhado"], label_visibility="collapsed")

if consulta == "Ver Gráfico Produzido (Soma Mensal)":
    df_graf = pd.DataFrame([
        {"TIPO":"SALDO TOTAL", "QTD":saldo_total},
        {"TIPO":"SOMA ENTRADAS MÊS", "QTD":soma_mes},
        {"TIPO":"ULTIMA", "QTD":ultima},
        {"TIPO":"PRODUZIDO", "QTD":produzido},
        {"TIPO":"META", "QTD":META},
    ])
    st.bar_chart(df_graf.set_index("TIPO"))
    st.info(f"META {META:.0f}=100% | SOMA {soma_mes:.0f}={pct:.1f}% | PRODUZIDO {produzido:.0f}= SALDO {saldo_total:.0f}-ULTIMA {ultima:.0f}")

elif consulta == "Ver Histórico com Data/Hora":
    st.dataframe(df_mov.sort_values("DATA", ascending=False), use_container_width=True, hide_index=True)

elif consulta == "Ver Saldo Detalhado":
    st.dataframe(pd.DataFrame(st.session_state.dados), use_container_width=True, hide_index=True)
