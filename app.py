import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide", page_title="ESTOQUE EMAIL")
ARQ_DADOS = "dados_estoque.csv"
ARQ_MOV = "mov_estoque.csv"
ARQ_EMAILS = "acessos_emails.csv"

# CRIA ARQUIVO DE EMAILS SE NÃO EXISTE
if not os.path.exists(ARQ_EMAILS):
    pd.DataFrame([
        {"EMAIL":"admin@empresa.com", "STATUS":"LIBERADO", "PERFIL":"ADMINISTRADOR", "DATA_LIBERACAO": datetime.now()},
        {"EMAIL":"operador@empresa.com", "STATUS":"LIBERADO", "PERFIL":"OPERADOR", "DATA_LIBERACAO": datetime.now()},
    ]).to_csv(ARQ_EMAILS, index=False)

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

def carrega_emails():
    return pd.read_csv(ARQ_EMAILS)

def salva_emails(df):
    df.to_csv(ARQ_EMAILS, index=False)

# ============ LOGIN POR EMAIL ============
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 LOGIN POR EMAIL - CONTROLE DE ACESSO")
    st.markdown("### ESTOQUE GAVETA")

    with st.container(border=True):
        email = st.text_input("Digite seu EMAIL").lower().strip()
        senha = st.text_input("Senha (admin: admin123)", type="password")

        if st.button("✅ ENTRAR", type="primary", use_container_width=True):
            df_emails = carrega_emails()

            # ADMIN MASTER
            if email == "admin@empresa.com" and senha == "admin123":
                st.session_state.logado = True
                st.session_state.usuario = email
                st.session_state.perfil = "ADMINISTRADOR"
                st.rerun()

            # VERIFICA EMAIL LIBERADO
            acesso = df_emails[df_emails["EMAIL"]==email]
            if not acesso.empty:
                if acesso.iloc[0]["STATUS"] == "BLOQUEADO":
                    st.error(f"❌ EMAIL {email} BLOQUEADO pelo administrador")
                elif acesso.iloc[0]["STATUS"] == "LIBERADO":
                    # senha simples = 123 para operador
                    if senha == "123" or email == "operador@empresa.com":
                        st.session_state.logado = True
                        st.session_state.usuario = email
                        st.session_state.perfil = acesso.iloc[0]["PERFIL"]
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta - operador use 123")
                else:
                    st.error("❌ Email não liberado")
            else:
                st.error(f"❌ Email {email} NÃO CADASTRADO - peça liberação ao admin")

    st.info("**Admin:** admin@empresa.com / admin123\n**Operador teste:** operador@empresa.com / 123")
    st.stop()

# ============ LOGADO ============
st.sidebar.markdown(f"👤 {st.session_state.usuario}\n**{st.session_state.perfil}**")
if st.sidebar.button("🚪 SAIR"):
    st.session_state.logado = False
    st.rerun()

# AREA ADMIN - LIBERAR/BLOQUEAR EMAIL
if st.session_state.perfil == "ADMINISTRADOR":
    st.sidebar.divider()
    st.sidebar.markdown("### 🔑 CONTROLE DE ACESSO POR EMAIL")
    with st.sidebar.expander("📧 LIBERAR / BLOQUEAR EMAIL", expanded=False):
        novo_email = st.text_input("Email do operador", placeholder="operador@empresa.com").lower().strip()
        perfil_novo = st.selectbox("Perfil", ["OPERADOR", "ADMINISTRADOR"])
        if st.button("✅ LIBERAR ACESSO", type="primary", use_container_width=True):
            if novo_email and "@" in novo_email:
                df_e = carrega_emails()
                if novo_email in df_e["EMAIL"].values:
                    df_e.loc[df_e["EMAIL"]==novo_email, "STATUS"] = "LIBERADO"
                    df_e.loc[df_e["EMAIL"]==novo_email, "PERFIL"] = perfil_novo
                else:
                    novo = pd.DataFrame([{"EMAIL":novo_email, "STATUS":"LIBERADO", "PERFIL":perfil_novo, "DATA_LIBERACAO": datetime.now()}])
                    df_e = pd.concat([df_e, novo], ignore_index=True)
                salva_emails(df_e)
                st.success(f"✅ {novo_email} LIBERADO")
                st.rerun()

        st.markdown("---")
        df_e = carrega_emails()
        st.dataframe(df_e, use_container_width=True, hide_index=True)

        email_bloq = st.selectbox("Selecione email para bloquear/desbloquear", df_e["EMAIL"].tolist())
        c1,c2,c3 = st.columns(3)
        if c1.button("🚫 BLOQUEAR"):
            df_e.loc[df_e["EMAIL"]==email_bloq, "STATUS"] = "BLOQUEADO"
            salva_emails(df_e)
            st.error(f"🚫 {email_bloq} BLOQUEADO")
            st.rerun()
        if c2.button("✅ DESBLOQUEAR"):
            df_e.loc[df_e["EMAIL"]==email_bloq, "STATUS"] = "LIBERADO"
            salva_emails(df_e)
            st.success(f"✅ {email_bloq} DESBLOQUEADO")
            st.rerun()
        if c3.button("❌ EXCLUIR"):
            df_e = df_e[df_e["EMAIL"]!=email_bloq]
            salva_emails(df_e)
            st.warning(f"❌ {email_bloq} EXCLUÍDO")
            st.rerun()

    st.sidebar.button("💾 SALVAR ENTRADA E SAIDA", type="primary", use_container_width=True, on_click=salvar)

# CALCULOS
df = pd.DataFrame(st.session_state.dados)
df_anexa = df[df["LOCAL"]=="SALA ANEXA"]
saldo_a = min(df_anexa[df_anexa["ID"]==15]["SALDO"].sum(), df_anexa[df_anexa["ID"]==16]["SALDO"].sum())
df_mov = pd.DataFrame(st.session_state.mov) if st.session_state.mov else pd.DataFrame()
if not df_mov.empty:
    df_mov['DATA'] = pd.to_datetime(df_mov['DATA'])
    df_mes = df_mov[(df_mov['DATA'].dt.month==datetime.now().month) & (df_mov["LOCAL"]=="SALA ANEXA") & (df_mov["TIPO"]=="ENTRADA")]
    soma_mes, ultima = df_mes["QTD"].sum(), df_mes.iloc[-1]["QTD"] if not df_mes.empty else 0
else:
    soma_mes, ultima = 0, 0
produzido = saldo_a - ultima

st.title("🗄️ ESTOQUE - TELA LIMPA")
st.markdown(f"**Logado:** {st.session_state.usuario} | **SALDO ATUALIZA AUTOMÁTICO: {saldo_a:.0f}**")

c1,c2,c3 = st.columns(3)
if c1.button("📦 SALA ANEXA", type="primary", use_container_width=True):
    st.session_state.tela = "ANEXA"
if c2.button("🏚️ BARRACÃO", use_container_width=True):
    st.session_state.tela = "BARRACAO"
if c3.button("📊 CONSULTAR", use_container_width=True):
    st.session_state.tela = "CONSULTA"
if 'tela' not in st.session_state:
    st.session_state.tela = "ANEXA"

st.divider()

if st.session_state.tela == "ANEXA":
    st.subheader("📦 SALA ANEXA")
    if st.button("👁️ VER INFORMAÇÕES"):
        st.session_state.ver_info = not st.session_state.get('ver_info', False)
    if st.session_state.get('ver_info', False):
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("SALDO TOTAL", f"{saldo_a:.0f}")
        c2.metric("SOMA MÊS", f"{soma_mes:.0f}")
        c3.metric("ULTIMA", f"{ultima:.0f}")
        c4.metric("PRODUZIDO", f"{produzido:.0f}")

    opcoes = ["NOVA ENTRADA", "NOVA SAIDA"]
    if st.session_state.perfil == "ADMINISTRADOR":
        opcoes += ["EXCLUIR REGISTRO", "SALVAR ENTRADA E SAIDA"]
    op = st.radio("O que fazer?", opcoes, horizontal=True)

    if op == "NOVA ENTRADA":
        with st.container(border=True):
            id_ent = st.selectbox("ID", [15,16], format_func=lambda x: f"{x} - {'BLOCOS' if x==15 else 'BARRAS'}")
            qtd = st.number_input("Qtd", value=24.0)
            if st.button("✅ SALVAR ENTRADA", type="primary", use_container_width=True):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_ent and d["LOCAL"]=="SALA ANEXA"), None)
                st.session_state.dados[idx]["SALDO"] += qtd
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"ENTRADA", "ID":id_ent, "LOCAL":"SALA ANEXA", "QTD":qtd})
                salvar()
                st.rerun()
    elif op == "NOVA SAIDA":
        with st.container(border=True):
            id_sai = st.selectbox("ID", [15,16], key="sai_a")
            qtd = st.number_input("Qtd", value=1.0, key="qtd_sai")
            if st.button("✅ SALVAR SAIDA", use_container_width=True):
                idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_sai and d["LOCAL"]=="SALA ANEXA"), None)
                st.session_state.dados[idx]["SALDO"] -= qtd
                st.session_state.mov.append({"DATA": datetime.now(), "TIPO":"SAIDA", "ID":id_sai, "LOCAL":"SALA ANEXA", "QTD":qtd})
                salvar()
                st.rerun()
    elif op == "EXCLUIR REGISTRO" and st.session_state.perfil == "ADMINISTRADOR":
        lista = [f"{i} - {m['DATA'].strftime('%d/%m %H:%M')} - {m['TIPO']} ID{m['ID']} QTD{m['QTD']}" for i,m in enumerate(st.session_state.mov) if m["LOCAL"]=="SALA ANEXA"]
        sel = st.selectbox("Registro", lista) if lista else None
        if st.button("❌ EXCLUIR"):
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
    elif op == "SALVAR ENTRADA E SAIDA":
        st.button("💾 SALVAR ENTRADA E SAIDA", type="primary", on_click=salvar)

elif st.session_state.tela == "BARRACAO":
    st.subheader("🏚️ BARRACÃO ZERADO - ATUALIZA AUTOMÁTICO")
    op = st.radio("O que fazer?", ["NOVA ENTRADA", "NOVA SAIDA", "SALVAR"], horizontal=True, key="op_bar")
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

else:
    if st.session_state.perfil!= "ADMINISTRADOR":
        st.error("🔐 SÓ ADMINISTRADOR CONSULTA")
        st.stop()
    st.subheader("📊 GRÁFICOS - SÓ ADMIN")
    if st.button("👁️ MOSTRAR GRÁFICO"):
        df_graf = pd.DataFrame([{"TIPO":"SALDO","QTD":saldo_a},{"TIPO":"SOMA MÊS","QTD":soma_mes},{"TIPO":"ULTIMA","QTD":ultima},{"TIPO":"PRODUZIDO","QTD":produzido}])
        st.bar_chart(df_graf.set_index("TIPO"))
        st.dataframe(df_mov.sort_values("DATA", ascending=False) if not df_mov.empty else df_mov)
       
