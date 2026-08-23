import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="ESTOQUE")
st.title("🗄️ ESTOQUE GAVETA - SALA ANEXA + BARRACÃO")

if 'dados' not in st.session_state:
    st.session_state.dados = [
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"BARRACÃO", "SALDO":40.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"BARRACÃO", "SALDO":35.0},
    ]
if 'mov' not in st.session_state:
    st.session_state.mov = [
        {"DATA": datetime(2026, 8, 5, 8, 0), "TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":50},
        {"DATA": datetime(2026, 8, 15, 10, 0), "TIPO":"ENTRADA", "ID":16, "LOCAL":"SALA ANEXA", "QTD":44},
        {"DATA": datetime(2026, 8, 22, 9, 15), "TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":24},
    ]
if 'meta' not in st.session_state:
    st.session_state.meta = 104.0

META = st.sidebar.number_input("META SALA ANEXA = 100%", value=st.session_state.meta, step=1.0)
st.session_state.meta = META

# CALCULOS SALA ANEXA
df = pd.DataFrame(st.session_state.dados)
df_anexa = df[df["LOCAL"]=="SALA ANEXA"]
saldo_total_anexa = min(df_anexa["SALDO"].tolist()) if not df_anexa.empty else 0

df_mov = pd.DataFrame(st.session_state.mov)
df_mov['DATA'] = pd.to_datetime(df_mov['DATA'])
df_mes_anexa = df_mov[(df_mov['DATA'].dt.month==datetime.now().month) & (df_mov["LOCAL"]=="SALA ANEXA") & (df_mov["TIPO"]=="ENTRADA")]

soma_mes = df_mes_anexa["QTD"].sum()
ultima = df_mes_anexa.iloc[-1]["QTD"] if not df_mes_anexa.empty else 24.0
produzido = saldo_total_anexa - ultima
pct = (soma_mes / META * 100) if META>0 else 0

# CALCULOS BARRACÃO
df_barracao = df[df["LOCAL"]=="BARRACÃO"]
saldo_total_barracao = min(df_barracao["SALDO"].tolist()) if not df_barracao.empty else 0

# ABAS LIMPA
tab_anexa, tab_barracao, tab_consulta = st.tabs(["📦 SALA ANEXA", "🏚️ BARRACÃO", "📊 GRÁFICOS / CONSULTA"])

with tab_anexa:
    st.markdown(f"#### MÊS {datetime.now().month}/{datetime.now().year} - META {META:.0f}=100%")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("SALDO TOTAL", f"{saldo_total_anexa:.0f}")
    c2.metric("SOMA MÊS", f"{soma_mes:.0f}")
    c3.metric("ULTIMA", f"{ultima:.0f}")
    c4.metric("PRODUZIDO", f"{produzido:.0f}", f"{saldo_total_anexa:.0f}-{ultima:.0f}")
    c5.metric("% META", f"{pct:.1f}%")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("➕ NOVA ENTRADA - SALA ANEXA")
            id_ent = st.selectbox("ID", [15, 16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="ent_anexa")
            qtd_ent = st.number_input("Qtd", min_value=1.0, value=24.0, step=1.0, key="qtd_ent_anexa")
            if st.button("✅ ENTRADA SALA ANEXA", type="primary", use_container_width=True, key="btn_ent_anexa"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent and d["LOCAL"]=="SALA ANEXA"), None)
                st.session_state.dados[idx]["SALDO"] += qtd_ent
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"SALA ANEXA", "QTD":qtd_ent})
                st.rerun()
    with col2:
        with st.container(border=True):
            st.subheader("➖ NOVA SAIDA - SALA ANEXA")
            id_sai = st.selectbox("ID", [15, 16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="sai_anexa")
            qtd_sai = st.number_input("Qtd", min_value=1.0, value=1.0, step=1.0, key="qtd_sai_anexa")
            if st.button("✅ SAIDA SALA ANEXA", use_container_width=True, key="btn_sai_anexa"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai and d["LOCAL"]=="SALA ANEXA"), None)
                if qtd_sai <= st.session_state.dados[idx]["SALDO"]:
                    st.session_state.dados[idx]["SALDO"] -= qtd_sai
                    st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"SALA ANEXA", "QTD":qtd_sai})
                    st.rerun()

with tab_barracao:
    st.markdown("#### ESTOQUE BARRACÃO")
    c1,c2,c3 = st.columns(3)
    blocos_b = df_barracao[df_barracao["ID"]==15]["SALDO"].sum()
    barras_b = df_barracao[df_barracao["ID"]==16]["SALDO"].sum()
    c1.metric("BLOCOS BARRACÃO", f"{blocos_b:.0f}")
    c2.metric("BARRAS BARRACÃO", f"{barras_b:.0f}")
    c3.metric("SALDO TOTAL BARRACÃO", f"{saldo_total_barracao:.0f}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("➕ NOVA ENTRADA - BARRACÃO")
            id_ent = st.selectbox("ID", [15, 16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="ent_bar")
            qtd_ent = st.number_input("Qtd", min_value=1.0, value=10.0, step=1.0, key="qtd_ent_bar")
            if st.button("✅ ENTRADA BARRACÃO", type="primary", use_container_width=True, key="btn_ent_bar"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent and d["LOCAL"]=="BARRACÃO"), None)
                st.session_state.dados[idx]["SALDO"] += qtd_ent
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"BARRACÃO", "QTD":qtd_ent})
                st.rerun()
    with col2:
        with st.container(border=True):
            st.subheader("➖ NOVA SAIDA - BARRACÃO")
            id_sai = st.selectbox("ID", [15, 16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="sai_bar")
            qtd_sai = st.number_input("Qtd", min_value=1.0, value=1.0, step=1.0, key="qtd_sai_bar")
            if st.button("✅ SAIDA BARRACÃO", use_container_width=True, key="btn_sai_bar"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai and d["LOCAL"]=="BARRACÃO"), None)
                if qtd_sai <= st.session_state.dados[idx]["SALDO"]:
                    st.session_state.dados[idx]["SALDO"] -= qtd_sai
                    st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"BARRACÃO", "QTD":qtd_sai})
                    st.rerun()

with tab_consulta:
    st.markdown("### 📊 CONSULTA")
    opcao = st.selectbox("Selecione", ["Grafico Produzido Sala Anexa (Soma Mensal)", "Comparar Sala Anexa x Barracão", "Historico com Data/Hora"])

    if opcao == "Grafico Produzido Sala Anexa (Soma Mensal)":
        df_graf = pd.DataFrame([
            {"TIPO":"SALDO TOTAL", "QTD":saldo_total_anexa},
            {"TIPO":"SOMA ENTRADAS MÊS", "QTD":soma_mes},
            {"TIPO":"ULTIMA", "QTD":ultima},
            {"TIPO":"PRODUZIDO", "QTD":produzido},
            {"TIPO":"META", "QTD":META},
        ])
        st.bar_chart(df_graf.set_index("TIPO"))
        st.info(f"META {META:.0f}=100% | SOMA {soma_mes:.0f}={pct:.1f}% | PRODUZIDO {produzido:.0f}= {saldo_total_anexa:.0f}-{ultima:.0f}")

    elif opcao == "Comparar Sala Anexa x Barracão":
        df_comp = pd.DataFrame([
            {"LOCAL":"SALA ANEXA", "BLOCOS": df_anexa[df_anexa["ID"]==15]["SALDO"].sum(), "BARRAS": df_anexa[df_anexa["ID"]==16]["SALDO"].sum()},
            {"LOCAL":"BARRACÃO", "BLOCOS": df_barracao[df_barracao["ID"]==15]["SALDO"].sum(), "BARRAS": df_barracao[df_barracao["ID"]==16]["SALDO"].sum()},
        ])
        st.bar_chart(df_comp.set_index("LOCAL"))
        st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        st.dataframe(df_mov.sort_values("DATA", ascending=False), use_container_width=True, hide_index=True)
