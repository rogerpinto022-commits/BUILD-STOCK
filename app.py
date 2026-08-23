import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide", page_title="ESTOQUE LIMPO")
st.title("🗄️ ESTOQUE")

ARQ_DADOS = "dados_estoque.csv"
ARQ_MOV = "mov_estoque.csv"

if 'dados' not in st.session_state:
    if os.path.exists(ARQ_DADOS):
        st.session_state.dados = pd.read_csv(ARQ_DADOS).to_dict('records')
    else:
        st.session_state.dados = [
            {"ID":15, "DESCRIÇÃO":"BLOCOS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
            {"ID":16, "DESCRIÇÃO":"BARRAS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
            {"ID":15, "DESCRIÇÃO":"BLOCOS", "LOCAL":"BARRACÃO", "SALDO":0.0},
            {"ID":16, "DESCRIÇÃO":"BARRAS", "LOCAL":"BARRACÃO", "SALDO":0.0},
        ]

if 'mov' not in st.session_state:
    if os.path.exists(ARQ_MOV):
        df_t = pd.read_csv(ARQ_MOV)
        df_t['DATA'] = pd.to_datetime(df_t['DATA'])
        st.session_state.mov = df_t.to_dict('records')
    else:
        st.session_state.mov = [
            {"DATA": datetime(2026, 8, 5, 8, 0), "TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":50},
            {"DATA": datetime(2026, 8, 15, 10, 0), "TIPO":"ENTRADA", "ID":16, "LOCAL":"SALA ANEXA", "QTD":44},
            {"DATA": datetime(2026, 8, 22, 9, 15), "TIPO":"ENTRADA", "ID":15, "LOCAL":"SALA ANEXA", "QTD":24},
        ]

def salvar():
    pd.DataFrame(st.session_state.dados).to_csv(ARQ_DADOS, index=False)
    pd.DataFrame(st.session_state.mov).to_csv(ARQ_MOV, index=False)
    st.toast("✅ SALVO")

# CÁLCULOS
df = pd.DataFrame(st.session_state.dados)
df_anexa = df[df["LOCAL"]=="SALA ANEXA"]
blocos_a = df_anexa[df_anexa["ID"]==15]["SALDO"].sum()
barras_a = df_anexa[df_anexa["ID"]==16]["SALDO"].sum()
saldo_a = min(blocos_a, barras_a)

df_mov = pd.DataFrame(st.session_state.mov) if st.session_state.mov else pd.DataFrame()
if not df_mov.empty:
    df_mov['DATA'] = pd.to_datetime(df_mov['DATA'])
    df_mes = df_mov[(df_mov['DATA'].dt.month==datetime.now().month) & (df_mov["LOCAL"]=="SALA ANEXA") & (df_mov["TIPO"]=="ENTRADA")]
    soma_mes = df_mes["QTD"].sum()
    ultima = df_mes.iloc[-1]["QTD"] if not df_mes.empty else 0
else:
    soma_mes = 0
    ultima = 0

produzido = saldo_a - ultima
META = 104.0

# TELA LIMPA - SÓ 2 BOTÕES PRINCIPAIS
st.markdown("### O QUE VOCÊ QUER FAZER?")
c1, c2, c3 = st.columns(3)
if c1.button("📦 SALA ANEXA", type="primary", use_container_width=True):
    st.session_state.tela = "ANEXA"
if c2.button("🏚️ BARRACÃO", use_container_width=True):
    st.session_state.tela = "BARRACAO"
if c3.button("📊 CONSULTAR", use_container_width=True):
    st.session_state.tela = "CONSULTA"

if 'tela' not in st.session_state:
    st.session_state.tela = "ANEXA"

st.divider()

# SÓ MOSTRA SE CLICAR
if st.session_state.tela == "ANEXA":
    st.subheader("📦 SALA ANEXA")

    # Botão para ver informações
    if st.button("👁️ VER INFORMAÇÕES SALDO"):
        st.session_state.ver_info_anexa = not st.session_state.get('ver_info_anexa', False)

    if st.session_state.get('ver_info_anexa', False):
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("SALDO TOTAL", f"{saldo_a:.0f}")
        c2.metric("SOMA MÊS", f"{soma_mes:.0f}")
        c3.metric("ULTIMA", f"{ultima:.0f}")
        c4.metric("PRODUZIDO", f"{produzido:.0f}")

    st.divider()

    op = st.radio("Selecione:", ["NOVA ENTRADA", "NOVA SAIDA", "EXCLUIR REGISTRO", "SALVAR"], horizontal=True, key="op_anexa")

    if op == "NOVA ENTRADA":
        with st.container(border=True):
            id_ent = st.selectbox("ID", [15,16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}")
            qtd = st.number_input("Quantidade", value=24.0, min_value=1.0)
            if st.button("✅ SALVAR ENTRADA", type="primary", use_container_width=True):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent and d["LOCAL"]=="SALA ANEXA"), None)
                st.session_state.dados[idx]["SALDO"] += qtd
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"SALA ANEXA", "QTD":qtd})
                salvar()
                st.rerun()

    elif op == "NOVA SAIDA":
        with st.container(border=True):
            id_sai = st.selectbox("ID", [15,16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}", key="sai_a")
            qtd = st.number_input("Quantidade", value=1.0, min_value=1.0, key="qtd_sai_a")
            if st.button("✅ SALVAR SAIDA", use_container_width=True):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai and d["LOCAL"]=="SALA ANEXA"), None)
                if qtd <= st.session_state.dados[idx]["SALDO"]:
                    st.session_state.dados[idx]["SALDO"] -= qtd
                    st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"SALA ANEXA", "QTD":qtd})
                    salvar()
                    st.rerun()

    elif op == "EXCLUIR REGISTRO":
        with st.container(border=True):
            lista = [f"{i} - {m['DATA'].strftime('%d/%m %H:%M')} - {m['TIPO']} ID{m['ID']} QTD{m['QTD']}" for i,m in enumerate(st.session_state.mov) if m["LOCAL"]=="SALA ANEXA"]
            sel = st.selectbox("Registro para excluir", lista) if lista else None
            if st.button("❌ EXCLUIR E SALVAR"):
                if sel:
                    i = int(sel.split(" - ")[0])
                    reg = st.session_state.mov[i]
                    idx_d = next((j for j,d in enumerate(st.session_state.dados) if d["ID"]==reg["ID"] and d["LOCAL"]==reg["LOCAL"]), None)
                    if reg["TIPO"]=="ENTRADA":
                        st.session_state.dados[idx_d]["SALDO"] -= reg["QTD"]
                    else:
                        st.session_state.dados[idx_d]["SALDO"] += reg["QTD"]
                    st.session_state.mov.pop(i)
                    salvar()
                    st.rerun()
    else:
        st.button("💾 SALVAR ENTRADA E SAIDA", type="primary", on_click=salvar)

elif st.session_state.tela == "BARRACAO":
    st.subheader("🏚️ BARRACÃO - ZERADO")

    if st.button("👁️ VER SALDO BARRACÃO"):
        st.session_state.ver_info_bar = not st.session_state.get('ver_info_bar', False)

    if st.session_state.get('ver_info_bar', False):
        df_b = df[df["LOCAL"]=="BARRACÃO"]
        blocos_b = df_b[df_b["ID"]==15]["SALDO"].sum()
        barras_b = df_b[df_b["ID"]==16]["SALDO"].sum()
        c1,c2,c3 = st.columns(3)
        c1.metric("BLOCOS", f"{blocos_b:.0f}")
        c2.metric("BARRAS", f"{barras_b:.0f}")
        c3.metric("TOTAL", f"{min(blocos_b, barras_b):.0f}")

    op = st.radio("Selecione:", ["NOVA ENTRADA", "NOVA SAIDA", "EXCLUIR", "SALVAR"], horizontal=True, key="op_bar")

    if op == "NOVA ENTRADA":
        with st.container(border=True):
            id_ent = st.selectbox("ID", [15,16], key="ent_b")
            qtd = st.number_input("Qtd", value=10.0, key="qtd_ent_b")
            if st.button("✅ SALVAR ENTRADA BARRACÃO", type="primary"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent and d["LOCAL"]=="BARRACÃO"), None)
                st.session_state.dados[idx]["SALDO"] += qtd
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"BARRACÃO", "QTD":qtd})
                salvar()
                st.rerun()
    elif op == "NOVA SAIDA":
        with st.container(border=True):
            id_sai = st.selectbox("ID", [15,16], key="sai_b")
            qtd = st.number_input("Qtd", value=1.0, key="qtd_sai_b")
            if st.button("✅ SALVAR SAIDA BARRACÃO"):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai and d["LOCAL"]=="BARRACÃO"), None)
                if qtd <= st.session_state.dados[idx]["SALDO"]:
                    st.session_state.dados[idx]["SALDO"] -= qtd
                    st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"BARRACÃO", "QTD":qtd})
                    salvar()
                    st.rerun()
    elif op == "EXCLUIR":
        lista = [f"{i} - {m['DATA'].strftime('%d/%m %H:%M')} ID{m['ID']} QTD{m['QTD']}" for i,m in enumerate(st.session_state.mov) if m["LOCAL"]=="BARRACÃO"]
        sel = st.selectbox("Registro", lista) if lista else None
        if st.button("❌ EXCLUIR"):
            if sel:
                i = int(sel.split(" - ")[0])
                reg = st.session_state.mov[i]
                idx_d = next((j for j,d in enumerate(st.session_state.dados) if d["ID"]==reg["ID"] and d["LOCAL"]=="BARRACÃO"), None)
                if reg["TIPO"]=="ENTRADA":
                    st.session_state.dados[idx_d]["SALDO"] -= reg["QTD"]
                else:
                    st.session_state.dados[idx_d]["SALDO"] += reg["QTD"]
                st.session_state.mov.pop(i)
                salvar()
                st.rerun()
    else:
        st.button("💾 SALVAR ENTRADA E SAIDA", type="primary", on_click=salvar)

else: # CONSULTA
    st.subheader("📊 CONSULTAR GRÁFICOS")
    tipo = st.selectbox("O que consultar?", ["Grafico Produzido", "Historico com Data/Hora", "Saldo Detalhado"])

    if tipo == "Grafico Produzido":
        if st.button("👁️ MOSTRAR GRÁFICO"):
            df_graf = pd.DataFrame([
                {"TIPO":"SALDO", "QTD":saldo_a},
                {"TIPO":"SOMA MÊS", "QTD":soma_mes},
                {"TIPO":"ULTIMA", "QTD":ultima},
                {"TIPO":"PRODUZIDO", "QTD":produzido},
            ])
            st.bar_chart(df_graf.set_index("TIPO"))

    elif tipo == "Historico com Data/Hora":
        if st.button("👁️ MOSTRAR HISTÓRICO"):
            st.dataframe(df_mov.sort_values("DATA", ascending=False) if not df_mov.empty else df_mov, use_container_width=True)

    else:
        if st.button("👁️ MOSTRAR SALDO"):
            st.dataframe(df, use_container_width=True)

    st.button("💾 SALVAR ENTRADA E SAIDA", type="primary", on_click=salvar)
