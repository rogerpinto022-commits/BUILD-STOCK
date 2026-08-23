import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide")

# LOGIN FIXO - NÃO DEPENDE DE ARQUIVO - 100% VAI ENTRAR
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔓 DESBLOQUEIO - SENHA FIXA")
    st.error("Se estava bloqueado, use essa senha fixa agora")

    email = st.text_input("EMAIL").lower().strip()
    senha = st.text_input("SENHA", type="password")

    if st.button("✅ ENTRAR - DESBLOQUEAR", type="primary", use_container_width=True):
        # SENHA FIXA NO CÓDIGO - NÃO DEPENDE DE CSV
        if email == "admin@empresa.com" and senha == "123":
            st.session_state.logado = True
            st.session_state.usuario = "admin@empresa.com"
            st.session_state.perfil = "ADMINISTRADOR"
            st.session_state.local_acesso = "AMBOS"
            st.session_state.perm_entrada = True
            st.session_state.perm_saida = True
            st.session_state.perm_grafico = True
            st.success("DESBLOQUEADO!")
            st.rerun()
        else:
            st.error("Use: admin@empresa.com / 123")

    st.info("ADMIN FIXO: admin@empresa.com / 123\nIsso vai desbloquear, depois você troca")
    st.stop()

# SE CHEGOU AQUI ESTÁ DESBLOQUEADO
st.sidebar.success(f"✅ DESBLOQUEADO: {st.session_state.usuario}")
if st.sidebar.button("🚪 SAIR"):
    st.session_state.logado = False
    st.rerun()

st.title("✅ VOCÊ DESBLOQUEOU!")
st.success("Agora apaga o arquivo acessos_emails.csv do GitHub e usa o app.py completo que te mandei antes")

# RECRIA ARQUIVO CORRETO AGORA
ARQ_EMAILS = "acessos_emails.csv"
if st.button("🔑 CRIAR ARQUIVO DE SENHAS CORRETO AGORA", type="primary"):
    pd.DataFrame([
        {"EMAIL":"admin@empresa.com", "SENHA":"123", "LOCAL":"AMBOS", "ENTRADA":True, "SAIDA":True, "GRAFICO":True, "STATUS":"LIBERADO", "PERFIL":"ADMINISTRADOR"},
        {"EMAIL":"anexa@empresa.com", "SENHA":"anexa123", "LOCAL":"SALA ANEXA", "ENTRADA":True, "SAIDA":True, "GRAFICO":True, "STATUS":"LIBERADO", "PERFIL":"OPERADOR"},
        {"EMAIL":"barracao@empresa.com", "SENHA":"barracao123", "LOCAL":"BARRACÃO", "ENTRADA":True, "SAIDA":True, "GRAFICO":True, "STATUS":"LIBERADO", "PERFIL":"OPERADOR"},
    ]).to_csv(ARQ_EMAILS, index=False)
    st.success("Arquivo criado! Agora volte para o app.py completo")
    st.dataframe(pd.read_csv(ARQ_EMAILS))

st.markdown("### Depois de desbloquear, volta para o app.py anterior completo")
     
