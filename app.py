import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide", page_title="ESTOQUE 2 GRAFICOS")
ARQ_DADOS = "dados_estoque.csv"
ARQ_MOV = "mov_estoque.csv"
ARQ_EMAILS = "acessos_emails.csv"

if not os.path.exists(ARQ_EMAILS):
    pd.DataFrame([
        {"EMAIL":"admin@empresa.com", "STATUS":"LIBERADO", "PERFIL":"ADMINISTRADOR", "DATA_LIBERACAO": datetime.now()},
        {"EMAIL":"operador@empresa.com", "STATUS":"LIBERADO", "PERFIL":"OPERADOR", "DATA_LIBERACAO": datetime.now()},
    ]).to_csv(ARQ_EMAILS, index=False)

if 'dados' not in st.session_state:
    st.session_state.dados = pd.read_csv(ARQ_DADOS).to_dict('records') if os.path.exists(ARQ_DADOS) else [
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

def carrega_emails():
    return pd.read_csv(ARQ_EMAILS)
def salva_emails(df):
    df.to_csv(ARQ_EMAILS, index=False)

if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 LOGIN POR EMAIL")
    with st.container(border=True):
        email = st.text_input("EMAIL").lower().strip()
        senha = st.text_input("Senha", type="password")
        if st.button("✅ ENTRAR", type="primary", use_container_width=True):
            df_emails = carrega_emails()
            if email == "admin@empresa.com" and senha == "admin123":
                st.session_state.logado = True
                st.session_state.usuario = email
                st.session_state.perfil = "ADMINISTRADOR"
                st.rerun()
            acesso = df_emails[df_emails["EMAIL"]==email]
            if not acesso.empty and acesso.iloc[0]["STATUS"]=="LIBERADO":
                if senha=="123":
                    st.session_state.logado = True
                    st.session_state.usuario = email
                    st.session_state.perfil = acesso.iloc[0]["PERFIL"]
                    st.rerun()
                else:
                    st.error("Senha operador = 123")
            elif not acesso.empty and acesso.iloc[0]["STATUS"]=="BLOQUEADO":
                st.error(f"🚫 {email} BLOQUEADO")
            else:
                st.error("Email não cadastrado")
    st.info("admin@empresa.com / admin123 | operador@empresa.com / 123")
    st.stop()

st.sidebar.markdown(f"👤 {st.session_state.usuario} - {st.session_state.perfil}")
if st.sidebar.button("🚪 SAIR"):
    st.session_state.logado = False
    st.rerun()

if st.session_state.perfil == "ADMINISTRADOR":
    st.sidebar.markdown("### 🔑 CONTROLE EMAIL")
    with st.sidebar.expander("📧 LIBERAR / BLOQUEAR", expanded=False):
        novo_email = st.text_input("Email operador").lower().strip()
        perfil_novo = st.selectbox("Perfil", ["OPERADOR","ADMINISTRADOR"])
        if st.button("✅ LIBERAR", type="primary", use_container_width=True):
            if "@" in novo_email:
                df_e = carrega_emails()
                if novo_email in df_e["EMAIL"].values:
                    df_e.loc[df_e["EMAIL"]==novo_email, "STATUS"]="LIBERADO"
                else:
                    df_e = pd.concat([df_e, pd.DataFrame([{"EMAIL":novo_email,"STATUS":"LIBERADO","PERFIL":perfil_novo,"DATA_LIBERACAO":datetime.now()}])], ignore_index=True)
                salva_emails(df_e)
                st.success(f"LIBERADO {novo_email}")
                st.rerun()
        df_e = carrega_emails()
        st.dataframe(df_e, hide_index=True, use_container_width=True)
        email_bloq = st.selectbox("Selecionar", df_e["EMAIL"].tolist())
        c1,c2 = st.columns(2)
        if c1.button("🚫 BLOQUEAR"):
            df_e.loc[df_e["EMAIL"]==email_bloq, "STATUS"]="BLOQUEADO"
            salva_emails(df_e)
            st.rerun()
        if c2.button("✅ DESBLOQUEAR"):
            df_e.loc[df_e["EMAIL"]==email_bloq, "STATUS"]="LIBERADO"
            salva_emails(df_e)
            st.rerun()
    st.sidebar.button("💾 SALVAR ENTRADA E SAIDA", type="primary", use_container_width=True, on_click=salvar)

# CALCULOS SALA ANEXA E BARRACÃO
df = pd.DataFrame(st.session_state.dados)
df_anexa = df[df["LOCAL"]=="SALA ANEXA"]
blocos_a = df_anexa[df_anexa["ID"]==15]["SALDO"].sum()
barras_a = df_anexa[df_anexa["ID"]==16]["SALDO"].sum()
saldo_a = min(blocos_a, barras_a)

df_barracao = df[df["LOCAL"]=="BARRACÃO"]
blocos_b = df_barracao[df_barracao["ID"]==15]["SALDO"].sum()
barras_b = df_barracao[df_barracao["ID"]==16]["SALDO"].sum()
saldo_b = min(blocos_b, barras_b)

df_mov = pd.DataFrame(st.session_state.mov) if st.session_state.mov else pd.DataFrame()
if not df_mov.empty:
    df_mov['DATA'] = pd.to_datetime(df_mov['DATA'])
    df_mes_anexa = df_mov[(df_mov['DATA'].dt.month==datetime.now().month) & (df_mov["LOCAL"]=="SALA ANEXA") & (df_mov["TIPO"]=="ENTRADA")]
    df_mes_bar = df_mov[(df_mov['DATA'].dt.month==datetime.now().month) & (df_mov["LOCAL"]=="BARRACÃO") & (df_mov["TIPO"]=="ENTRADA")]
    soma_mes_a = df_mes_anexa["QTD"].sum()
    soma_mes_b = df_mes_bar["QTD"].sum()
    ultima_a = df_mes_anexa.iloc[-1]["QTD"] if not df_mes_anexa.empty else 0
    ultima_b = df_mes_bar.iloc[-1]["QTD"] if not df_mes_bar.empty else 0
else:
    soma_mes_a, soma_mes_b, ultima_a, ultima_b = 0,0,0,0

produzido_a = saldo_a - ultima_a
produzido_b = saldo_b - ultima_b

st.title("🗄️ ESTOQUE - ATUALIZA AUTOMÁTICO")
c1,c2,c3 = st.columns(3)
if c1.button("📦 SALA ANEXA", type="primary", use_container_width=True):
    st.session_state.tela = "ANEXA"
if c2.button("🏚️ BARRACÃO", use_container_width=True):
    st.session_state.tela = "BARRACAO"
if c3.button("📊 CONSULTAR GRÁFICOS", use_container_width=True):
    st.session_state.tela = "CONSULTA"
if 'tela' not in st.session_state:
    st.session_state.tela = "ANEXA"

st.divider()

if st.session_state.tela == "ANEXA":
    st.subheader("📦 SALA ANEXA")
    if st.button("👁️ VER INFORMAÇÕES SALA ANEXA"):
        st.session_state.ver_info = not st.session_state.get('ver_info', False)
    if st.session_state.get('ver_info', False):
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("SALDO TOTAL", f"{saldo_a:.0f}", f"BLOCOS {blocos_a:.0f} / BARRAS {barras_a:.0f}")
        c2.metric("SOMA MÊS", f"{soma_mes_a:.0f}")
        c3.metric("ULTIMA", f"{ultima_a:.0f}")
        c4.metric("PRODUZIDO", f"{produzido_a:.0f}")
    op = st.radio("O que fazer?", ["NOVA ENTRADA","NOVA SAIDA","SALVAR ENTRADA E SAIDA"], horizontal=True)
    if op == "NOVA ENTRADA":
        id_ent = st.selectbox("ID", [15,16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}")
        qtd = st.number_input("Qtd", value=24.0)
        if st.button("✅ SALVAR ENTRADA", type="primary"):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent and d["LOCAL"]=="SALA ANEXA"), None)
            st.session_state.dados[idx]["SALDO"] += qtd
            st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"SALA ANEXA", "QTD":qtd})
            salvar()
            st.rerun()
    elif op == "NOVA SAIDA":
        id_sai = st.selectbox("ID", [15,16], key="sai_a")
        qtd = st.number_input("Qtd", value=1.0, key="qtd_sai_a")
        if st.button("✅ SALVAR SAIDA"):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai and d["LOCAL"]=="SALA ANEXA"), None)
            st.session_state.dados[idx]["SALDO"] -= qtd
            st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"SALA ANEXA", "QTD":qtd})
            salvar()
            st.rerun()
    else:
        st.button("💾 SALVAR ENTRADA E SAIDA", type="primary", on_click=salvar)

elif st.session_state.tela == "BARRACAO":
    st.subheader("🏚️ BARRACÃO")
    if st.button("👁️ VER INFORMAÇÕES BARRACÃO"):
        st.session_state.ver_info_b = not st.session_state.get('ver_info_b', False)
    if st.session_state.get('ver_info_b', False):
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("BLOCOS", f"{blocos_b:.0f}")
        c2.metric("BARRAS", f"{barras_b:.0f}")
        c3.metric("SALDO TOTAL", f"{saldo_b:.0f}")
        c4.metric("SOMA MÊS", f"{soma_mes_b:.0f}")
    op = st.radio("O que fazer?", ["NOVA ENTRADA","NOVA SAIDA","SALVAR ENTRADA E SAIDA"], horizontal=True, key="op_b")
    if op == "NOVA ENTRADA":
        id_ent = st.selectbox("ID", [15,16], key="ent_b")
        qtd = st.number_input("Qtd", value=10.0, key="qtd_b")
        if st.button("✅ SALVAR ENTRADA BARRACÃO", type="primary"):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent and d["LOCAL"]=="BARRACÃO"), None)
            st.session_state.dados[idx]["SALDO"] += qtd
            st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"BARRACÃO", "QTD":qtd})
            salvar()
            st.rerun()
    elif op == "NOVA SAIDA":
        id_sai = st.selectbox("ID", [15,16], key="sai_b")
        qtd = st.number_input("Qtd", value=1.0, key="qtd_sai_b")
        if st.button("✅ SALVAR SAIDA BARRACÃO"):
            idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai and d["LOCAL"]=="BARRACÃO"), None)
            st.session_state.dados[idx]["SALDO"] -= qtd
            st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"BARRACÃO", "QTD":qtd})
            salvar()
            st.rerun()
    else:
        st.button("💾 SALVAR ENTRADA E SAIDA", type="primary", on_click=salvar)

else: # CONSULTA COM 2 GRAFICOS
    st.subheader("📊 GRÁFICOS - SALA ANEXA E BARRACÃO")

    if st.session_state.perfil!="ADMINISTRADOR":
        st.error("🔐 SÓ ADMINISTRADOR")
        st.stop()

    tipo = st.selectbox("Escolha:", ["Gráficos Comparativos", "Histórico Completo com Data/Hora"])

    if st.button("👁️ MOSTRAR GRÁFICOS", type="primary"):
        if tipo == "Gráficos Comparativos":
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📦 SALA ANEXA")
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("SALDO", f"{saldo_a:.0f}")
                c2.metric("SOMA MÊS", f"{soma_mes_a:.0f}")
                c3.metric("ULTIMA", f"{ultima_a:.0f}")
                c4.metric("PRODUZIDO", f"{produzido_a:.0f}")
                df_graf_a = pd.DataFrame([
                    {"TIPO":"SALDO ANEXA", "QTD":saldo_a},
                    {"TIPO":"SOMA MÊS ANEXA", "QTD":soma_mes_a},
                    {"TIPO":"ULTIMA ANEXA", "QTD":ultima_a},
                    {"TIPO":"PRODUZIDO ANEXA", "QTD":produzido_a},
                ])
                st.bar_chart(df_graf_a.set_index("TIPO"))
                st.markdown(f"**BLOCOS:** {blocos_a:.0f} | **BARRAS:** {barras_a:.0f} | **TOTAL:** {saldo_a:.0f}")

            with col2:
                st.markdown("### 🏚️ BARRACÃO - ZERADO")
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("BLOCOS", f"{blocos_b:.0f}")
                c2.metric("BARRAS", f"{barras_b:.0f}")
                c3.metric("SALDO", f"{saldo_b:.0f}")
                c4.metric("SOMA MÊS", f"{soma_mes_b:.0f}")
                df_graf_b = pd.DataFrame([
                    {"TIPO":"BLOCOS BARRACÃO", "QTD":blocos_b},
                    {"TIPO":"BARRAS BARRACÃO", "QTD":barras_b},
                    {"TIPO":"SALDO BARRACÃO", "QTD":saldo_b},
                    {"TIPO":"SOMA MÊS BARRACÃO", "QTD":soma_mes_b},
                ])
                st.bar_chart(df_graf_b.set_index("TIPO"))
                st.markdown(f"**TOTAL BARRACÃO:** {saldo_b:.0f} (BLOCOS {blocos_b:.0f} + BARRAS {barras_b:.0f})")

            st.divider()
            st.markdown("### 📊 COMPARATIVO GERAL")
            df_geral = pd.DataFrame([
                {"LOCAL":"SALA ANEXA", "SALDO":saldo_a, "SOMA MÊS":soma_mes_a},
                {"LOCAL":"BARRACÃO", "SALDO":saldo_b, "SOMA MÊS":soma_mes_b},
            ])
            st.bar_chart(df_geral.set_index("LOCAL"))

        else:
            st.markdown("### 📋 HISTÓRICO COMPLETO COM DATA/HORA")
            st.dataframe(df_mov.sort_values("DATA", ascending=False) if not df_mov.empty else df_mov, use_container_width=True)

        st.button("💾 SALVAR ENTRADA E SAIDA", type="primary", on_click=salvar)
