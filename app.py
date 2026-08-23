import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="ESTOQUE")
st.title("🗄️ ESTOQUE GAVETA")

if 'dados' not in st.session_state:
    st.session_state.dados = [
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"BARRACÃO", "SALDO":0.0}, # ZERADO
        {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"BARRACÃO", "SALDO":0.0}, # ZERADO
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

df = pd.DataFrame(st.session_state.dados)
df_anexa = df[df["LOCAL"]=="SALA ANEXA"]
saldo_total_anexa = min(df_anexa["SALDO"].tolist()) if not df_anexa.empty else 0

df_mov = pd.DataFrame(st.session_state.mov) if st.session_state.mov else pd.DataFrame(columns=["DATA","TIPO","ID","LOCAL","QTD"])
if not df_mov.empty:
    df_mov['DATA'] = pd.to_datetime(df_mov['DATA'])
    df_mes_anexa = df_mov[(df_mov['DATA'].dt.month==datetime.now().month) & (df_mov["LOCAL"]=="SALA ANEXA") & (df_mov["TIPO"]=="ENTRADA")]
else:
    df_mes_anexa = pd.DataFrame()

soma_mes = df_mes_anexa["QTD"].sum() if not df_mes_anexa.empty else 0
ultima = df_mes_anexa.iloc[-1]["QTD"] if not df_mes_anexa.empty else 0
produzido = saldo_total_anexa - ultima
pct = (soma_mes / META * 100) if META>0 else 0

df_barracao = df[df["LOCAL"]=="BARRACÃO"]
saldo_total_barracao = min(df_barracao["SALDO"].tolist()) if not df_barracao.empty else 0

tab_anexa, tab_barracao, tab_consulta = st.tabs(["📦 SALA ANEXA", "🏚️ BARRACÃO (ZERADO)", "📊 GRÁFICOS"])

with tab_anexa:
    st.markdown(f"#### SALA ANEXA - MÊS {datetime.now().month}/{datetime.now().year} - META {META:.0f}=100%")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("SALDO TOTAL", f"{saldo_total_anexa:.0f}")
    c2.metric("SOMA MÊS", f"{soma_mes:.0f}")
    c3.metric("ULTIMA", f"{ultima:.0f}")
    c4.metric("PRODUZIDO", f"{produzido:.0f}", f"{saldo_total_anexa:.0f}-{ultima:.0f}")
    c5.metric("% META", f"{pct:.1f}%")

    st.divider()
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        with st.container(border=True):
            st.subheader("➕ NOVA ENTRADA")
            id_ent = st.selectbox("ID", [15, 16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="ent_anexa")
            qtd_ent = st.number_input("Qtd", min_value=1.0, value=24.0, step=1.0, key="qtd_ent_anexa")
            if st.button("✅ ENTRADA", type="primary", use_container_width=True, key="btn_ent_anexa"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent and d["LOCAL"]=="SALA ANEXA"), None)
                st.session_state.dados[idx]["SALDO"] += qtd_ent
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"SALA ANEXA", "QTD":qtd_ent})
                st.rerun()
    with col2:
        with st.container(border=True):
            st.subheader("➖ NOVA SAIDA")
            id_sai = st.selectbox("ID", [15, 16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="sai_anexa")
            qtd_sai = st.number_input("Qtd", min_value=1.0, value=1.0, step=1.0, key="qtd_sai_anexa")
            if st.button("✅ SAIDA", use_container_width=True, key="btn_sai_anexa"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai and d["LOCAL"]=="SALA ANEXA"), None)
                if qtd_sai <= st.session_state.dados[idx]["SALDO"]:
                    st.session_state.dados[idx]["SALDO"] -= qtd_sai
                    st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"SALA ANEXA", "QTD":qtd_sai})
                    st.rerun()
    with col3:
        with st.container(border=True):
            st.subheader("🗑️ EXCLUIR REGISTRO")
            st.write("SALA ANEXA")
            mov_anexa = [f"{i} - {m['DATA'].strftime('%d/%m %H:%M')} - {m['TIPO']} ID{m['ID']} QTD{m['QTD']}" for i,m in enumerate(st.session_state.mov) if m["LOCAL"]=="SALA ANEXA"]
            idx_excluir = st.selectbox("Registro", mov_anexa, key="exc_anexa") if mov_anexa else None
            if st.button("❌ EXCLUIR", use_container_width=True, key="btn_exc_anexa"):
                if idx_excluir:
                    i = int(idx_excluir.split(" - ")[0])
                    reg = st.session_state.mov[i]
                    # reverte saldo
                    idx_dado = next((j for j,d in enumerate(st.session_state.dados) if d["ID"]==reg["ID"] and d["LOCAL"]==reg["LOCAL"]), None)
                    if reg["TIPO"]=="ENTRADA":
                        st.session_state.dados[idx_dado]["SALDO"] -= reg["QTD"]
                    else:
                        st.session_state.dados[idx_dado]["SALDO"] += reg["QTD"]
                    st.session_state.mov.pop(i)
                    st.rerun()

with tab_barracao:
    st.markdown("#### BARRACÃO - ESTOQUE ZERADO")
    c1,c2,c3 = st.columns(3)
    blocos_b = df_barracao[df_barracao["ID"]==15]["SALDO"].sum() if not df_barracao.empty else 0
    barras_b = df_barracao[df_barracao["ID"]==16]["SALDO"].sum() if not df_barracao.empty else 0
    c1.metric("BLOCOS BARRACÃO", f"{blocos_b:.0f}")
    c2.metric("BARRAS BARRACÃO", f"{barras_b:.0f}")
    c3.metric("SALDO TOTAL", f"{saldo_total_barracao:.0f}")

    st.divider()
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        with st.container(border=True):
            st.subheader("➕ NOVA ENTRADA")
            id_ent = st.selectbox("ID", [15, 16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="ent_bar")
            qtd_ent = st.number_input("Qtd", min_value=1.0, value=10.0, step=1.0, key="qtd_ent_bar")
            if st.button("✅ ENTRADA", type="primary", use_container_width=True, key="btn_ent_bar"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent and d["LOCAL"]=="BARRACÃO"), None)
                st.session_state.dados[idx]["SALDO"] += qtd_ent
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"BARRACÃO", "QTD":qtd_ent})
                st.rerun()
    with col2:
        with st.container(border=True):
            st.subheader("➖ NOVA SAIDA")
            id_sai = st.selectbox("ID", [15, 16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="sai_bar")
            qtd_sai = st.number_input("Qtd", min_value=1.0, value=1.0, step=1.0, key="qtd_sai_bar")
            if st.button("✅ SAIDA", use_container_width=True, key="btn_sai_bar"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai and d["LOCAL"]=="BARRACÃO"), None)
                if qtd_sai <= st.session_state.dados[idx]["SALDO"]:
                    st.session_state.dados[idx]["SALDO"] -= qtd_sai
                    st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"BARRACÃO", "QTD":qtd_sai})
                    st.rerun()
    with col3:
        with st.container(border=True):
            st.subheader("🗑️ EXCLUIR REGISTRO")
            st.write("BARRACÃO")
            mov_bar = [f"{i} - {m['DATA'].strftime('%d/%m %H:%M')} - {m['TIPO']} ID{m['ID']} QTD{m['QTD']}" for i,m in enumerate(st.session_state.mov) if m["LOCAL"]=="BARRACÃO"]
            idx_excluir = st.selectbox("Registro", mov_bar, key="exc_bar") if mov_bar else None
            if st.button("❌ EXCLUIR", use_container_width=True, key="btn_exc_bar"):
                if idx_excluir:
                    i = int(idx_excluir.split(" - ")[0])
                    reg = st.session_state.mov[i]
                    idx_dado = next((j for j,d in enumerate(st.session_state.dados) if d["ID"]==reg["ID"] and d["LOCAL"]==reg["LOCAL"]), None)
                    if reg["TIPO"]=="ENTRADA":
                        st.session_state.dados[idx_dado]["SALDO"] -= reg["QTD"]
                    else:
                        st.session_state.dados[idx_dado]["SALDO"] += reg["QTD"]
                    st.session_state.mov.pop(i)
                    st.rerun()

with tab_consulta:
    opcao = st.selectbox("Consultar", ["Grafico Produzido Sala Anexa", "Comparar Anexa x Barracão", "Historico Data/Hora"])
    if opcao == "Grafico Produzido Sala Anexa":
        df_graf = pd.DataFrame([
            {"TIPO":"SALDO TOTAL", "QTD":saldo_total_anexa},
            {"TIPO":"SOMA MÊS", "QTD":soma_mes},
            {"TIPO":"ULTIMA", "QTD":ultima},
            {"TIPO":"PRODUZIDO", "QTD":produzido},
            {"TIPO":"META", "QTD":META},
        ])
        st.bar_chart(df_graf.set_index("TIPO"))
    elif opcao == "Comparar Anexa x Barracão":
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.dataframe(df_mov.sort_values("DATA", ascending=False) if not df_mov.empty else df_mov, use_container_width=True, hide_index=True)
