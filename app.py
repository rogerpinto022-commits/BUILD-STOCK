import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide", page_title="ESTOQUE")
st.title("🗄️ ESTOQUE GAVETA - ATUALIZA AUTOMÁTICO")

ARQ_DADOS = "dados_estoque.csv"
ARQ_MOV = "mov_estoque.csv"

if 'dados' not in st.session_state:
    if os.path.exists(ARQ_DADOS):
        st.session_state.dados = pd.read_csv(ARQ_DADOS).to_dict('records')
    else:
        st.session_state.dados = [
            {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"SALA ANEXA", "SALDO":118.0},
            {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
            {"ID":15, "DESCRIÇÃO":"BLOCOS DE FUNDO", "LOCAL":"BARRACÃO", "SALDO":0.0},
            {"ID":16, "DESCRIÇÃO":"BARRAS CATODICAS", "LOCAL":"BARRACÃO", "SALDO":0.0},
        ]

if 'mov' not in st.session_state:
    if os.path.exists(ARQ_MOV):
        df_temp = pd.read_csv(ARQ_MOV)
        df_temp['DATA'] = pd.to_datetime(df_temp['DATA'])
        st.session_state.mov = df_temp.to_dict('records')
    else:
        st.session_state.mov = [
            {"DATA": datetime(2026, 8, 5, 8, 0), "TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":50},
            {"DATA": datetime(2026, 8, 15, 10, 0), "TIPO":"ENTRADA", "ID":16, "LOCAL":"SALA ANEXA", "QTD":44},
            {"DATA": datetime(2026, 8, 22, 9, 15), "TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":24},
        ]

if 'meta' not in st.session_state:
    st.session_state.meta = 104.0

def salvar_tudo():
    pd.DataFrame(st.session_state.dados).to_csv(ARQ_DADOS, index=False)
    pd.DataFrame(st.session_state.mov).to_csv(ARQ_MOV, index=False)
    st.toast(f"✅ SALVO {datetime.now().strftime('%H:%M:%S')}")

META = st.sidebar.number_input("META = 100%", value=st.session_state.meta, step=1.0)
st.session_state.meta = META
st.sidebar.button("💾 SALVAR ENTRADA E SAIDA", type="primary", use_container_width=True, on_click=salvar_tudo)

# CALCULO ATUALIZADO SEMPRE
df = pd.DataFrame(st.session_state.dados)
df_anexa = df[df["LOCAL"]=="SALA ANEXA"]
blocos_anexa = df_anexa[df_anexa["ID"]==15]["SALDO"].sum()
barras_anexa = df_anexa[df_anexa["ID"]==16]["SALDO"].sum()
saldo_total_anexa = min(blocos_anexa, barras_anexa) # ATUALIZA SEMPRE

df_mov = pd.DataFrame(st.session_state.mov) if st.session_state.mov else pd.DataFrame(columns=["DATA","TIPO","ID","LOCAL","QTD"])
if not df_mov.empty:
    df_mov['DATA'] = pd.to_datetime(df_mov['DATA'])
    df_mes = df_mov[(df_mov['DATA'].dt.month==datetime.now().month) & (df_mov["LOCAL"]=="SALA ANEXA") & (df_mov["TIPO"]=="ENTRADA")]
else:
    df_mes = pd.DataFrame()

soma_mes = df_mes["QTD"].sum() if not df_mes.empty else 0
ultima = df_mes.iloc[-1]["QTD"] if not df_mes.empty else 0
produzido = saldo_total_anexa - ultima # PRODUZIDO = SALDO ATUAL - ULTIMA
pct = (soma_mes / META * 100) if META>0 else 0

st.markdown(f"### MÊS {datetime.now().month}/{datetime.now().year} - ATUALIZA A CADA MOVIMENTAÇÃO")
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("SALDO TOTAL ANEXA", f"{saldo_total_anexa:.0f}", f"BLOCOS {blocos_anexa:.0f} / BARRAS {barras_anexa:.0f}")
c2.metric("SOMA ENTRADAS MÊS", f"{soma_mes:.0f}")
c3.metric("ULTIMA ENTRADA", f"{ultima:.0f}")
c4.metric("PRODUZIDO", f"{produzido:.0f}", f"{saldo_total_anexa:.0f}-{ultima:.0f}")
c5.metric("% META", f"{pct:.1f}%", f"{soma_mes:.0f}/{META:.0f}")

st.divider()

tab_anexa, tab_barracao, tab_consulta = st.tabs(["📦 SALA ANEXA", "🏚️ BARRACÃO", "📊 GRÁFICOS"])

with tab_anexa:
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("➕ NOVA ENTRADA - SALA ANEXA")
            id_ent = st.selectbox("ID", [15, 16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="ent_anexa")
            qtd_ent = st.number_input("Qtd", min_value=1.0, value=24.0, step=1.0, key="qtd_ent_anexa")
            if st.button("✅ REGISTRAR E SALVAR ENTRADA", type="primary", use_container_width=True, key="btn_ent_anexa"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent and d["LOCAL"]=="SALA ANEXA"), None)
                st.session_state.dados[idx]["SALDO"] += qtd_ent
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"SALA ANEXA", "QTD":qtd_ent})
                salvar_tudo()
                st.rerun()

    with col2:
        with st.container(border=True):
            st.subheader("➖ NOVA SAIDA - SALA ANEXA")
            id_sai = st.selectbox("ID", [15, 16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="sai_anexa")
            qtd_sai = st.number_input("Qtd", min_value=1.0, value=1.0, step=1.0, key="qtd_sai_anexa")
            if st.button("✅ REGISTRAR E SALVAR SAIDA", use_container_width=True, key="btn_sai_anexa"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai and d["LOCAL"]=="SALA ANEXA"), None)
                if qtd_sai <= st.session_state.dados[idx]["SALDO"]:
                    st.session_state.dados[idx]["SALDO"] -= qtd_sai
                    st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"SALA ANEXA", "QTD":qtd_sai})
                    salvar_tudo()
                    st.rerun()

    with col3:
        with st.container(border=True):
            st.subheader("🗑️ EXCLUIR + 💾 SALVAR")
            mov_anexa = [f"{i} - {m['DATA'].strftime('%d/%m %H:%M')} - {m['TIPO']} ID{m['ID']} QTD{m['QTD']}" for i,m in enumerate(st.session_state.mov) if m["LOCAL"]=="SALA ANEXA"]
            idx_sel = st.selectbox("Registro", mov_anexa, key="exc_anexa") if mov_anexa else None
            if st.button("❌ EXCLUIR REGISTRO", use_container_width=True, key="btn_exc_anexa"):
                if idx_sel:
                    i = int(idx_sel.split(" - ")[0])
                    reg = st.session_state.mov[i]
                    idx_dado = next((j for j,d in enumerate(st.session_state.dados) if d["ID"]==reg["ID"] and d["LOCAL"]==reg["LOCAL"]), None)
                    if reg["TIPO"]=="ENTRADA":
                        st.session_state.dados[idx_dado]["SALDO"] -= reg["QTD"]
                    else:
                        st.session_state.dados[idx_dado]["SALDO"] += reg["QTD"]
                    st.session_state.mov.pop(i)
                    salvar_tudo()
                    st.rerun()
            st.button("💾 SALVAR ENTRADA E SAIDA", type="primary", use_container_width=True, key="salvar_geral_anexa", on_click=salvar_tudo)

with tab_barracao:
    df_barracao = df[df["LOCAL"]=="BARRACÃO"]
    blocos_b = df_barracao[df_barracao["ID"]==15]["SALDO"].sum() if not df_barracao.empty else 0
    barras_b = df_barracao[df_barracao["ID"]==16]["SALDO"].sum() if not df_barracao.empty else 0
    st.markdown(f"#### BARRACÃO - BLOCOS {blocos_b:.0f} | BARRAS {barras_b:.0f} | TOTAL {min(blocos_b, barras_b):.0f} - ZERADO INICIAL")
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.subheader("➕ ENTRADA BARRACÃO")
            id_ent = st.selectbox("ID", [15, 16], key="ent_bar")
            qtd_ent = st.number_input("Qtd", value=10.0, key="qtd_ent_bar")
            if st.button("✅ REGISTRAR E SALVAR ENTRADA", type="primary", key="btn_ent_bar"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent and d["LOCAL"]=="BARRACÃO"), None)
                st.session_state.dados[idx]["SALDO"] += qtd_ent
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"BARRACÃO", "QTD":qtd_ent})
                salvar_tudo()
                st.rerun()
    with col2:
        with st.container(border=True):
            st.subheader("➖ SAIDA BARRACÃO")
            id_sai = st.selectbox("ID", [15, 16], key="sai_bar")
            qtd_sai = st.number_input("Qtd", value=1.0, key="qtd_sai_bar")
            if st.button("✅ REGISTRAR E SALVAR SAIDA", key="btn_sai_bar"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai and d["LOCAL"]=="BARRACÃO"), None)
                if qtd_sai <= st.session_state.dados[idx]["SALDO"]:
                    st.session_state.dados[idx]["SALDO"] -= qtd_sai
                    st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"BARRACÃO", "QTD":qtd_sai})
                    salvar_tudo()
                    st.rerun()
    with col3:
        with st.container(border=True):
            st.subheader("🗑️ EXCLUIR + SALVAR")
            mov_bar = [f"{i} - {m['DATA'].strftime('%d/%m %H:%M')} ID{m['ID']} QTD{m['QTD']}" for i,m in enumerate(st.session_state.mov) if m["LOCAL"]=="BARRACÃO"]
            idx_sel = st.selectbox("Registro", mov_bar, key="exc_bar") if mov_bar else None
            if st.button("❌ EXCLUIR BARRACÃO", key="btn_exc_bar"):
                if idx_sel:
                    i = int(idx_sel.split(" - ")[0])
                    reg = st.session_state.mov[i]
                    idx_dado = next((j for j,d in enumerate(st.session_state.dados) if d["ID"]==reg["ID"] and d["LOCAL"]=="BARRACÃO"), None)
                    if reg["TIPO"]=="ENTRADA":
                        st.session_state.dados[idx_dado]["SALDO"] -= reg["QTD"]
                    else:
                        st.session_state.dados[idx_dado]["SALDO"] += reg["QTD"]
                    st.session_state.mov.pop(i)
                    salvar_tudo()
                    st.rerun()
            st.button("💾 SALVAR ENTRADA E SAIDA", type="primary", use_container_width=True, key="salvar_geral_bar", on_click=salvar_tudo)

with tab_consulta:
    df_graf = pd.DataFrame([
        {"TIPO":"SALDO TOTAL", "QTD":saldo_total_anexa},
        {"TIPO":"SOMA MÊS", "QTD":soma_mes},
        {"TIPO":"ULTIMA", "QTD":ultima},
        {"TIPO":"PRODUZIDO", "QTD":produzido},
        {"TIPO":"META", "QTD":META},
    ])
    st.bar_chart(df_graf.set_index("TIPO"))
    st.dataframe(df_mov.sort_values("DATA", ascending=False) if not df_mov.empty else df_mov, use_container_width=True)
    st.button("💾 SALVAR ENTRADA E SAIDA - GERAL", type="primary", on_click=salvar_tudo)
