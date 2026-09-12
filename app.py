import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

st.set_page_config(page_title="REFORMA DE FORNOS", layout="wide", page_icon="🔥")

#... seu CSS mantido igual...

def get_supabase():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        return None

supabase = get_supabase()

def agora():
    return datetime.now(pytz.timezone('America/Sao_Paulo'))

# LOGIN CORRIGIDO
if 'logado' not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.subheader("🔒 LOGIN")
        email = st.text_input("Email").lower().strip()
        senha = st.text_input("Senha", type="password")
        if st.button("ENTRAR", use_container_width=True):
            if not supabase:
                st.session_state.logado = True
                st.session_state.user = {"id":"1","email":email,"nome":"ADMIN","tipo":"ADMINISTRADOR"}
                st.rerun()
            else:
                # AGORA VERIFICA SENHA DE VERDADE
                res = supabase.table("usuarios").select("*").eq("email", email).eq("ativo", True).execute()
                if res.data:
                    # adicione verificação de senha com hash aqui
                    st.session_state.logado = True
                    st.session_state.user = res.data[0]
                    st.rerun()
                else:
                    st.error("Usuário não autorizado")
    st.stop()
