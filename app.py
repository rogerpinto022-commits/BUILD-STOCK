import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide", page_title="CORRIGIDO")
ARQ_DADOS = "dados_estoque.csv"
ARQ_MOV = "mov_estoque.csv"
ARQ_EMAILS = "acessos_emails.csv"

# CORREÇÃO DO ERRO KeyError: SENHA
if os.path.exists(ARQ_EMAILS):
    try:
        df_test = pd.read_csv(ARQ_EMAILS)
        if "SENHA" not in df_test.columns or "STATUS" not in df_test.columns:
            os.remove(ARQ_EMAILS)
            st.warning("Arquivo antigo apagado - recriando com SENHA")
    except:
        if os.path.exists(ARQ_EMAILS):
            os.remove(ARQ_EMAILS)

# RECRIA COM TODAS COLUNAS CERTAS
if not os.path.exists(ARQ_EMAILS):
    pd.DataFrame([
        {"EMAIL":"admin@empresa.com", "SENHA":"123", "LOCAL":"AMBOS", "ENTRADA":True, "SAIDA":True, "GRAFICO":True, "STATUS":"LIBERADO", "PERFIL":"ADMINISTRADOR"},
        {"EMAIL":"anexa@empresa.com", "SENHA":"123", "LOCAL":"SALA ANEXA", "ENTRADA":True, "SAIDA":True, "GRAFICO":True, "STATUS":"LIBERADO", "PERFIL":"OPERADOR"},
        {"EMAIL":"barracao@empresa.com", "SENHA":"123", "LOCAL":"BARRACÃO", "ENTRADA":True, "SAIDA":True, "GRAFICO":True, "STATUS":"LIBERADO", "PERFIL":"OPERADOR"},
    ]).to_csv(ARQ_EMAILS, index=False)
    st.success("✅ Arquivo corrigido com SENHA")

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
    st.title("🔐 ENTRAR - ERRO CORRIGIDO")

    # MOSTRA ARQUIVO ATUAL PARA DEBUG
    if os.path.exists(ARQ_EMAILS):
        df_debug = pd.read_csv(ARQ_EMAILS)
        st.write("Colunas atuais:", df_debug.columns.tolist())
        st.dataframe(df_debug)

    with st.container(border=True):
        email = st.text_input("EMAIL").lower().strip()
        senha = st.text_input("SENHA - 123", type="password")
        if st.button("✅ ENTRAR", type="primary", use_container_width=True):
            df_e = pd.read_csv(ARQ_EMAILS)
            # CORREÇÃO COM TRY
            try:
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
                    st.error("Senha errada ou bloqueado")
            except KeyError as e:
                st.error(f"Erro ainda: {e} - Clique em RESETAR")
                if os.path.exists(ARQ_EMAILS):
                    os.remove(ARQ_EMAILS)
                st.rerun()

    with st.sidebar:
        if st.button("🔴 RESETAR - APAGAR TUDO E CORRIGIR", type="primary", use_container_width=True):
            for f in [ARQ_EMAILS, ARQ_DADOS, ARQ_MOV]:
                if os.path.exists(f):
                    os.remove(f)
            st.success("Tudo apagado - recarregue")
            st.rerun()

    st.info("Use: admin@empresa.com / 123")
    st.stop()

# LOGADO
st.sidebar.write(f"👤 {st.session_state.usuario} - {st.session_state.local_acesso}")
if st.sidebar.button("🚪 SAIR"):
    st.session_state.logado = False
    st.rerun()

if st.session_state.perfil == "ADMINISTRADOR":
    with st.sidebar.expander("🔑 ADMIN - TROCAR SENHA", expanded=True):
        df_e = pd.read_csv(ARQ_EMAILS)
        st.dataframe(df_e, hide_index=True)

        sel = st.selectbox("Email para trocar senha", df_e["EMAIL"].unique())
        nova = st.text_input("Nova senha individual", type="password")
        if st.button("🔑 ATUALIZAR SENHA INDIVIDUAL"):
            if nova:
                df_e.loc[df_e["EMAIL"]==sel, "SENHA"] = nova
                df_e.to_csv(ARQ_EMAILS, index=False)
                st.success(f"Senha de {sel} = {nova}")
                st.rerun()

        st.divider()
        novo_email = st.text_input("Novo operador").lower().strip()
        nova_senha = st.text_input("Senha", type="password", key="n")
        local = st.selectbox("Local", ["SALA ANEXA","BARRACÃO","AMBOS"])
        if st.button("✅ LIBERAR COM SENHA INDIVIDUAL"):
            if "@" in novo_email and nova_senha:
                df_e = pd.read_csv(ARQ_EMAILS)
                df_e = df_e[~((df_e["EMAIL"]==novo_email) & (df_e["LOCAL"]==local))]
                df_e = pd.concat([df_e, pd.DataFrame([{"EMAIL":novo_email,"SENHA":nova_senha,"LOCAL":local,"ENTRADA":True,"SAIDA":True,"GRAFICO":True,"STATUS":"LIBERADO","PERFIL":"OPERADOR"}])], ignore_index=True)
                df_e.to_csv(ARQ_EMAILS, index=False)
                st.success(f"Liberado {novo_email}")
                st.rerun()

    st.sidebar.button("💾 SALVAR", type="primary", on_click=salvar)

# TELAS
df = pd.DataFrame(st.session_state.dados)
blocos_a = df[(df["LOCAL"]=="SALA ANEXA") & (df["ID"]==15)]["SALDO"].sum()
barras_a = df[(df["LOCAL"]=="SALA ANEXA") & (df["ID"]==16)]["SALDO"].sum()
blocos_b = df[(df["LOCAL"]=="BARRACÃO") & (df["ID"]==15)]["SALDO"].sum()
barras_b = df[(df["LOCAL"]=="BARRACÃO") & (df["ID"]==16)]["SALDO"].sum()

pode_anexa = st.session_state.local_acesso in ["SALA ANEXA", "AMBOS"]
pode_barracao = st.session_state.local_acesso in ["BARRACÃO", "AMBOS"]

c1,c2 = st.columns(2)
if pode_anexa:
    if c1.button("📦 SALA ANEXA", type="primary", use_container_width=True):
        st.session_state.tela = "ANEXA"
if pode_barracao:
    if c2.button("🏚️ BARRACÃO", use_container_width=True):
        st.session_state.tela = "BARRACAO"

if 'tela' not in st.session_state:
    st.session_state.tela = "ANEXA" if pode_anexa else "BARRACAO"

if st.session_state.tela == "ANEXA" and pode_anexa:
    st.subheader(f"📦 SALA ANEXA - BLOCOS {blocos_a:.0f} BARRAS {barras_a:.0f}")
    id_e = st.selectbox("Item", [15,16])
    qtd = st.number_input("Qtd", value=1.0)
    col1,col2 = st.columns(2)
    if col1.button("✅ ENTRADA", type="primary"):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="SALA ANEXA"), None)
        st.session_state.dados[idx]["SALDO"] += qtd
        salvar()
        st.rerun()
    if col2.button("✅ SAIDA"):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="SALA ANEXA"), None)
        st.session_state.dados[idx]["SALDO"] -= qtd
        salvar()
        st.rerun()
else:
    st.subheader(f"🏚️ BARRACÃO - BLOCOS {blocos_b:.0f} BARRAS {barras_b:.0f}")
    id_e = st.selectbox("Item", [15,16], key="b")
    qtd = st.number_input("Qtd", value=1.0, key="qb")
    col1,col2 = st.columns(2)
    if col1.button("✅ ENTRADA BARRACÃO", type="primary"):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="BARRACÃO"), None)
        st.session_state.dados[idx]["SALDO"] += qtd
        salvar()
        st.rerun()
    if col2.button("✅ SAIDA BARRACÃO"):
        idx = next((i for i,d in enumerate(st.session_state.dados) if d["ID"]==id_e and d["LOCAL"]=="BARRACÃO"), None)
        st.session_state.dados[idx]["SALDO"] -= qtd
        salvar()
        st.rerun()
