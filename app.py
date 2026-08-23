import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide", page_title="RESET SENHA")
ARQ_DADOS = "dados_estoque.csv"
ARQ_MOV = "mov_estoque.csv"
ARQ_EMAILS = "acessos_emails.csv"

# BOTÃO DE RESET - APAGA TODAS SENHAS E VOLTA PARA PADRÃO
with st.sidebar:
    if st.button("🔴 RESETAR TODAS AS SENHAS - CLIQUE AQUI SE NÃO CONSEGUE ENTRAR", type="primary"):
        if os.path.exists(ARQ_EMAILS):
            os.remove(ARQ_EMAILS)
        st.success("SENHAS RESETADAS! Use admin@empresa.com / 123")
        st.rerun()

# RECRIA COM SENHA FACIL 123
if not os.path.exists(ARQ_EMAILS):
    pd.DataFrame([
        {"EMAIL":"admin@empresa.com", "SENHA":"123", "LOCAL":"AMBOS", "ENTRADA":True, "SAIDA":True, "GRAFICO":True, "STATUS":"LIBERADO", "PERFIL":"ADMINISTRADOR"},
        {"EMAIL":"anexa@empresa.com", "SENHA":"123", "LOCAL":"SALA ANEXA", "ENTRADA":True, "SAIDA":True, "GRAFICO":True, "STATUS":"LIBERADO", "PERFIL":"OPERADOR"},
        {"EMAIL":"barracao@empresa.com", "SENHA":"123", "LOCAL":"BARRACÃO", "ENTRADA":True, "SAIDA":True, "GRAFICO":True, "STATUS":"LIBERADO", "PERFIL":"OPERADOR"},
    ]).to_csv(ARQ_EMAILS, index=False)

if 'dados' not in st.session_state:
    st.session_state.dados = pd.read_csv(ARQ_DADOS).to_dict('records') if os.path.exists(ARQ_DADOS) else [
        {"ID":15, "DESCRIÇÃO":"BLOCOS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS", "LOCAL":"SALA ANEXA", "SALDO":118.0},
        {"ID":15, "DESCRIÇÃO":"BLOCOS", "LOCAL":"BARRACÃO", "SALDO":0.0},
        {"ID":16, "DESCRIÇÃO":"BARRAS", "LOCAL":"BARRACÃO", "SALDO":0.0},
    ]

if 'mov' not in st.session_state:
    st.session_state.mov = pd.read_csv(ARQ_MOV).to_dict('records') if os.path.exists(ARQ_MOV) else []

def salvar():
    pd.DataFrame(st.session_state.dados).to_csv(ARQ_DADOS, index=False)
    pd.DataFrame(st.session_state.mov).to_csv(ARQ_MOV, index=False)
    st.toast("✅ SALVO")

if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 SENHA RESETADA - TODAS COM 123")
    st.warning("TODAS AS SENHAS AGORA SÃO 123 - ENTRE E TROQUE DEPOIS")

    with st.container(border=True):
        email = st.text_input("EMAIL").lower().strip()
        senha = st.text_input("SENHA - DIGITE 123", type="password")

        if st.button("✅ ENTRAR COM 123", type="primary", use_container_width=True):
            df_e = pd.read_csv(ARQ_EMAILS)
            user = df_e[(df_e["EMAIL"]==email) & (df_e["SENHA"]==senha) & (df_e["STATUS"]=="LIBERADO")]
            if not user.empty:
                st.session_state.logado = True
                st.session_state.usuario = email
                st.session_state.perfil = user.iloc[0]["PERFIL"]
                st.session_state.local_acesso = user.iloc[0]["LOCAL"]
                st.session_state.perm_entrada = user.iloc[0]["ENTRADA"]
                st.session_state.perm_saida = user.iloc[0]["SAIDA"]
                st.session_state.perm_grafico = user.iloc[0]["GRAFICO"]
                st.rerun()
            else:
                st.error(f"Email {email} não encontrado ou bloqueado. Clique no botão vermelho na lateral para RESETAR")

        st.divider()
        st.markdown("### 🔑 SENHAS ATUAIS - TODAS 123")
        df_e = pd.read_csv(ARQ_EMAILS)
        st.dataframe(df_e[["EMAIL","SENHA","LOCAL","STATUS"]], hide_index=True)

        st.divider()
        st.markdown("### 🆘 ATUALIZAR SENHA SEM ENTRAR - SE ESQUECEU")
        email_reset = st.text_input("Email para atualizar senha").lower().strip()
        nova_senha_reset = st.text_input("Nova senha", type="password", key="reset")
        if st.button("🔑 ATUALIZAR SENHA AGORA"):
            if "@" in email_reset and nova_senha_reset:
                df_e = pd.read_csv(ARQ_EMAILS)
                if email_reset in df_e["EMAIL"].values:
                    df_e.loc[df_e["EMAIL"]==email_reset, "SENHA"] = nova_senha_reset
                    df_e.loc[df_e["EMAIL"]==email_reset, "STATUS"] = "LIBERADO"
                    df_e.to_csv(ARQ_EMAILS, index=False)
                    st.success(f"✅ Senha de {email_reset} atualizada para: {nova_senha_reset} - AGORA ENTRE")
                else:
                    st.error("Email não existe - use um dos emails da lista acima")
    st.stop()

# RESTO DO APP IGUAL - LOGADO
st.sidebar.markdown(f"👤 {st.session_state.usuario} - {st.session_state.local_acesso}")
if st.sidebar.button("🚪 SAIR"):
    st.session_state.logado = False
    st.rerun()

if st.session_state.perfil == "ADMINISTRADOR":
    with st.sidebar.expander("🔑 ATUALIZAR SENHA E LIBERAR ACESSO", expanded=True):
        st.markdown("**TROCAR SENHA DE QUALQUER UM**")
        df_e = pd.read_csv(ARQ_EMAILS)
        sel_email = st.selectbox("Email", df_e["EMAIL"].unique())
        nova_senha = st.text_input("Nova senha individual", type="password", key="nova")
        if st.button("🔑 TROCAR SENHA", type="primary", use_container_width=True):
            if nova_senha:
                df_e.loc[df_e["EMAIL"]==sel_email, "SENHA"] = nova_senha
                df_e.to_csv(ARQ_EMAILS, index=False)
                st.success(f"Senha de {sel_email} agora é: {nova_senha}")
                st.rerun()

        st.divider()
        st.markdown("**LIBERAR NOVO ACESSO**")
        novo_email = st.text_input("Novo email").lower().strip()
        nova_senha2 = st.text_input("Senha", type="password", key="n2")
        local = st.selectbox("Local", ["SALA ANEXA","BARRACÃO","AMBOS"])
        if st.button("✅ LIBERAR"):
            if "@" in novo_email and nova_senha2:
                df_e = pd.read_csv(ARQ_EMAILS)
                df_e = df_e[~((df_e["EMAIL"]==novo_email) & (df_e["LOCAL"]==local))]
                df_e = pd.concat([df_e, pd.DataFrame([{"EMAIL":novo_email,"SENHA":nova_senha2,"LOCAL":local,"ENTRADA":True,"SAIDA":True,"GRAFICO":True,"STATUS":"LIBERADO","PERFIL":"OPERADOR"}])], ignore_index=True)
                df_e.to_csv(ARQ_EMAILS, index=False)
                st.success(f"Liberado {novo_email} / {nova_senha2}")
                st.rerun()

        st.dataframe(df_e, hide_index=True, use_container_width=True)

    st.sidebar.button("💾 SALVAR", type="primary", on_click=salvar)

# TELAS
df = pd.DataFrame(st.session_state.dados)
blocos_a = df[(df["LOCAL"]=="SALA ANEXA") & (df["ID"]==15)]["SALDO"].sum()
barras_a = df[(df["LOCAL"]=="SALA ANEXA") & (df["ID"]==16)]["SALDO"].sum()
blocos_b = df[(df["LOCAL"]=="BARRACÃO") & (df["ID"]==15)]["SALDO"].sum()
barras_b = df[(df["LOCAL"]=="BARRACÃO") & (df["ID"]==16)]["SALDO"].sum()

pode_anexa = st.session_state.local_acesso in ["SALA ANEXA", "AMBOS"]
pode_barracao = st.session_state.local_acesso in ["BARRACÃO", "AMBOS"]

st.title(f"Logado: {st.session_state.usuario}")

c1,c2,c3 = st.columns(3)
if pode_anexa:
    if c1.button("📦 SALA ANEXA", type="primary", use_container_width=True):
        st.session_state.tela = "ANEXA"
if pode_barracao:
    if c2.button("🏚️ BARRACÃO", use_container_width=True):
        st.session_state.tela = "BARRACAO"
if st.session_state.perm_grafico:
    if c3.button("📊 GRÁFICOS", use_container_width=True):
        st.session_state.tela = "CONSULTA"

if 'tela' not in st.session_state:
    st.session_state.tela = "ANEXA" if pode_anexa else "BARRACAO"

if st.session_state.tela == "ANEXA" and pode_anexa:
    st.subheader(f"📦 SALA ANEXA - BLOCOS {blocos_a:.0f} BARRAS {barras_a:.0f}")
    id_e = st.selectbox("Item", [15,16])
    qtd = st.number_input("Qtd", value=1.0)
    if st.button("ENTRADA ANEXA", type="primary"):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="SALA ANEXA"), None)
        st.session_state.dados[idx]["SALDO"] += qtd
        salvar()
        st.rerun()
    if st.button("SAIDA ANEXA"):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="SALA ANEXA"), None)
        st.session_state.dados[idx]["SALDO"] -= qtd
        salvar()
        st.rerun()

elif st.session_state.tela == "BARRACAO" and pode_barracao:
    st.subheader(f"🏚️ BARRACÃO - BLOCOS {blocos_b:.0f} BARRAS {barras_b:.0f}")
    id_e = st.selectbox("Item", [15,16], key="b")
    qtd = st.number_input("Qtd", value=1.0, key="qb")
    if st.button("ENTRADA BARRACÃO", type="primary"):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="BARRACÃO"), None)
        st.session_state.dados[idx]["SALDO"] += qtd
        salvar()
        st.rerun()
    if st.button("SAIDA BARRACÃO"):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="BARRACÃO"), None)
        st.session_state.dados[idx]["SALDO"] -= qtd
        salvar()
        st.rerun()
