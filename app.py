import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

st.set_page_config(page_title="REFORMA DE FORNOS", layout="wide", page_icon="🔥")

# VISUAL ARROJADO - REFORMA DE FORNOS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
.stApp { background: radial-gradient(ellipse at top, #1e1e1e 0%, #0a0a0a 100%); color: white; }
h1 {
    font-family: 'Orbitron', monospace!important;
    font-weight: 900!important;
    font-size: 48px!important;
    color: #C0C0C0!important;
    text-align: center;
    border: 4px solid #FF6B00;
    padding: 20px;
    background: linear-gradient(180deg, #2a2a2a 0%, #111 100%);
    text-shadow: 2px 2px 0px #FF6B00, 0 0 20px #FF6B00;
    letter-spacing: 4px;
}
.stButton>button {
    background: linear-gradient(90deg, #FF6B00 0%, #FF8C00 100%)!important;
    color: black!important; font-weight: 900!important;
    border: 2px solid #00D9FF!important;
}
div[data-testid="stMetric"] {
    background: #1a1a1a; border-left: 5px solid #FF6B00; border-top: 1px solid #00D9FF;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# REFORMA DE FORNOS")
st.markdown(f"<center><b style='color:#00D9FF'>SISTEMA DE GERENCIAMENTO DE ESTOQUE • PLANTA REFRATÁRIA BR • {datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')} - BRASÍLIA • STATUS: ONLINE 🟢</b></center>", unsafe_allow_html=True)

# SUPABASE
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    supabase = None
    st.warning("MODO DEMO - Configure Secrets SUPABASE_URL e KEY para produção")

def agora(): return datetime.now(pytz.timezone('America/Sao_Paulo'))
def agora_str(): return agora().strftime('%d/%m/%Y %H:%M:%S - Brasília')

if 'logado' not in st.session_state: st.session_state.logado = False
if not st.session_state.logado:
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.subheader("🔒 LOGIN - ACESSO RESTRITO")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("ENTRAR NO SISTEMA", use_container_width=True):
            if email == "admin@reframax.com" or supabase:
                if supabase:
                    try:
                        res = supabase.table("usuarios").select("*").eq("email", email).eq("ativo", True).execute()
                        if res.data:
                            st.session_state.logado=True; st.session_state.user=res.data[0]; st.rerun()
                        else:
                            st.error("Usuário não liberado pelo ADMINISTRADOR")
                    except:
                        st.session_state.logado=True; st.session_state.user={"id":"1","email":email,"nome":"ADMIN","tipo":"ADMINISTRADOR"}; st.rerun()
                else:
                    st.session_state.logado=True; st.session_state.user={"id":"1","email":email,"nome":"ADMIN","tipo":"ADMINISTRADOR"}; st.rerun()
        st.divider()
        st.caption("Novo operador? Solicite acesso")
        nome_n = st.text_input("Nome")
        email_n = st.text_input("Email novo")
        if st.button("SOLICITAR LIBERAÇÃO"):
            if supabase: supabase.table("usuarios").insert({"email":email_n,"nome":nome_n,"tipo":"OPERADOR","ativo":False}).execute()
            st.success("Solicitado! Aguarde ADMIN liberar em GALPÃO")
    st.stop()

user = st.session_state.user
is_admin = user.get('tipo')=='ADMINISTRADOR'

# SIDEBAR ADMIN
st.sidebar.title(f"👤 {user.get('nome','OPERADOR')}")
st.sidebar.caption(agora_str())
if is_admin:
    st.sidebar.header("👑 PAINEL ADMINISTRADOR")
    if supabase:
        us = supabase.table("usuarios").select("*").execute()
        df_u = pd.DataFrame(us.data) if us.data else pd.DataFrame()
        if not df_u.empty:
            st.sidebar.dataframe(df_u[['email','tipo','ativo']])
            email_lib = st.sidebar.selectbox("Liberar usuário", df_u['email'].tolist())
            if st.sidebar.button("✅ AUTORIZAR ACESSO TOTAL"):
                supabase.table("usuarios").update({"ativo":True}).eq("email",email_lib).execute()
                st.sidebar.success("LIBERADO")

            st.sidebar.divider()
            st.sidebar.subheader("Autorizar Locais e Funções")
            up_email = st.sidebar.selectbox("Usuário permissão", df_u['email'].tolist(), key="perm")
            up = df_u[df_u['email']==up_email].iloc[0] if not df_u.empty else None
            if up is not None:
                local = st.sidebar.selectbox("Local", ["GALPAO","SALA_ANEXA","OFICINA","ESTOQUE_GERAL","GRAFICOS","CADASTRO"])
                pa = st.sidebar.checkbox("Pode Acessar", True)
                pe = st.sidebar.checkbox("Pode EDITAR (Botão Editar)", True)
                px_ = st.sidebar.checkbox("Pode Excluir")
                if st.sidebar.button("SALVAR PERMISSÃO"):
                    supabase.table("permissoes").insert({"usuario_id":up['id'],"local":local,"pode_acessar":pa,"pode_editar":pe,"pode_excluir":px_,"pode_ver_grafico":True}).execute()
                    st.sidebar.success(f"{local} liberado para {up_email}")

def tem_perm(local):
    if is_admin: return True
    if not supabase: return True
    try:
        p = supabase.table("permissoes").select("*").eq("usuario_id",user['id']).eq("local",local).execute()
        return any(x['pode_acessar'] for x in p.data) if p.data else False
    except: return True

def pode_editar(local):
    if is_admin: return True
    if not supabase: return True
    try:
        p = supabase.table("permissoes").select("*").eq("usuario_id",user['id']).eq("local",local).execute()
        return any(x['pode_editar'] for x in p.data) if p.data else False
    except: return True

# ABAS
lista_abas = []
if tem_perm("CADASTRO"): lista_abas.append("📦 CADASTRO")
if tem_perm("GALPAO"): lista_abas.append("🏭 GALPÃO")
if tem_perm("SALA_ANEXA"): lista_abas.append("🏢 SALA ANEXA")
if tem_perm("OFICINA"): lista_abas.append("🔧 OFICINA")
if tem_perm("ESTOQUE_GERAL") or tem_perm("GRAFICOS"): lista_abas.append("📊 ESTOQUE + GRÁFICOS")

tabs = st.tabs(lista_abas)

# CADASTRO
if "📦 CADASTRO" in lista_abas:
    with tabs[lista_abas.index("📦 CADASTRO")]:
        st.subheader(f"CADASTRO ÚNICO - ID + DESCRIÇÃO + MARCA + QTD EMB + QTD UNIT + LOTE - {agora_str()}")
        with st.form("cad"):
            c1,c2,c3 = st.columns(3)
            id_g = c1.text_input("ID GAVETA *")
            desc = c2.text_input("DESCRIÇÃO *")
            marca = c3.text_input("MARCA *")
            c4,c5,c6 = st.columns(3)
            q_emb = c4.number_input("QTD EMBALAGEM",1,10000,1)
            q_unit = c5.number_input("QTD UNITÁRIO",1,10000,1)
            lote = c6.text_input("LOTE")
            if st.form_submit_button("💾 SALVAR CADASTRO"):
                if supabase:
                    supabase.table("cadastro").insert({"id_gaveta":id_g,"descricao":desc,"marca":marca,"qtd_embalagem":q_emb,"qtd_unitario":q_unit,"lote":lote}).execute()
                    supabase.table("estoque_geral").insert({"id_gaveta":id_g,"descricao":desc,"marca":marca,"qtd_atual":0}).execute()
                st.success(f"Cadastrado {agora_str()}")
        if supabase:
            d = supabase.table("cadastro").select("*").execute()
            df = pd.DataFrame(d.data) if d.data else pd.DataFrame()
            st.dataframe(df, use_container_width=True)
            if pode_editar("CADASTRO") and not df.empty:
                st.markdown("### ✏️ BOTÃO EDITAR")
                id_e = st.selectbox("ID para editar", df['id_gaveta'].tolist(), key="ed_cad")
                row = df[df['id_gaveta']==id_e].iloc[0]
                with st.form(f"edit_{id_e}"):
                    nd = st.text_input("Descrição", row['descricao'])
                    nm = st.text_input("Marca", row['marca'])
                    nl = st.text_input("Lote", row['lote'])
                    if st.form_submit_button("SALVAR EDIÇÃO"):
                        supabase.table("cadastro").update({"descricao":nd,"marca":nm,"lote":nl}).eq("id_gaveta",id_e).execute()
                        st.success(f"Editado {agora_str()}"); st.rerun()

def tela(local, prox, ant, titulo):
    st.subheader(f"{titulo} - {agora_str()}")
    st.info(f"REGRA: SAÍDA {local} = ENTRADA {prox} | ENTRADA {local} = SAÍDA {ant} | Data/Hora Brasília OBRIGATÓRIA")
    idm = st.text_input(f"ID - {local}", key=f"id_{local}")
    if idm:
        if supabase:
            cd = supabase.table("cadastro").select("*").eq("id_gaveta",idm).execute()
            if cd.data: st.success(f"{cd.data[0]['descricao']} - {cd.data[0]['marca']} - Lote {cd.data[0]['lote']}")
            qtd = st.number_input("QTD",1,10000,1, key=f"q_{local}")
            tipo = st.selectbox("TIPO", ["ENTRADA","SAÍDA","DEVOLUÇÃO","EXCLUIR REGISTRO"], key=f"t_{local}")
            if st.button(f"CONFIRMAR {tipo} - {local}", key=f"b_{local}"):
                ag = agora().isoformat()
                supabase.table("movimentacoes").insert({"id_gaveta":idm,"local_origem":local,"local_destino":local,"tipo":tipo,"qtd":qtd,"data_hora_brasilia":ag}).execute()
                if tipo=="SAÍDA" and local=="GALPAO":
                    supabase.table("movimentacoes").insert({"id_gaveta":idm,"local_origem":"SALA_ANEXA","local_destino":"SALA_ANEXA","tipo":"ENTRADA","qtd":qtd,"data_hora_brasilia":ag}).execute()
                    est = supabase.table("estoque_geral").select("*").eq("id_gaveta",idm).execute()
                if tipo=="SAÍDA" and local=="SALA_ANEXA":
                    supabase.table("movimentacoes").insert({"id_gaveta":idm,"local_origem":"OFICINA","local_destino":"OFICINA","tipo":"ENTRADA","qtd":qtd,"data_hora_brasilia":ag}).execute()
                if tipo=="SAÍDA" and local=="OFICINA":
                    est = supabase.table("estoque_geral").select("*").eq("id_gaveta",idm).execute()
                    if est.data:
                        nq = max(0, est.data[0]['qtd_atual']-qtd)
                        supabase.table("estoque_geral").update({"qtd_atual":nq}).eq("id_gaveta",idm).execute()
                if tipo=="ENTRADA" and local=="GALPAO":
                    est = supabase.table("estoque_geral").select("*").eq("id_gaveta",idm).execute()
                    if est.data:
                        nq = est.data[0]['qtd_atual']+qtd
                        supabase.table("estoque_geral").update({"qtd_atual":nq}).eq("id_gaveta",idm).execute()
                st.success(f"{tipo} registrada {agora_str()}")
        if supabase:
            mv = supabase.table("movimentacoes").select("*").eq("local_origem",local).order("data_hora_brasilia", desc=True).limit(20).execute()
            st.dataframe(pd.DataFrame(mv.data) if mv.data else pd.DataFrame())

if "🏭 GALPÃO" in lista_abas:
    with tabs[lista_abas.index("🏭 GALPÃO")]: tela("GALPAO","SALA_ANEXA","FORNECEDOR","🏭 GALPÃO DE MATERIAIS")
if "🏢 SALA ANEXA" in lista_abas:
    with tabs[lista_abas.index("🏢 SALA ANEXA")]: tela("SALA_ANEXA","OFICINA","GALPAO","🏢 SALA ANEXA")
if "🔧 OFICINA" in lista_abas:
    with tabs[lista_abas.index("🔧 OFICINA")]: tela("OFICINA","ESTOQUE_GERAL","SALA_ANEXA","🔧 OFICINA DE REVESTIMENTO")

if "📊 ESTOQUE + GRÁFICOS" in lista_abas:
    with tabs[lista_abas.index("📊 ESTOQUE + GRÁFICOS")]:
        st.subheader(f"ESTOQUE GERAL - {agora_str()}")
        if supabase:
            est = supabase.table("estoque_geral").select("*").execute()
            df_est = pd.DataFrame(est.data) if est.data else pd.DataFrame()
            if not df_est.empty:
                st.dataframe(df_est, use_container_width=True)
                col1,col2,col3 = st.columns(3)
                col1.metric("TOTAL SKUs", len(df_est))
                col2.metric("QTD TOTAL", df_est['qtd_atual'].sum())
                col3.metric("Atualizado", agora_str().split(" ")[1])

                st.divider()
                st.markdown("### 📊 GRÁFICOS - SELECIONADOS POR ID E TODOS - BARRAS HORIZONTAL - COR DISTINTA - NUMEROS VISIVEIS")
                filtro = st.selectbox("FILTRAR GRÁFICO ESTOQUE POR ID", ["TODOS"] + sorted(df_est['id_gaveta'].unique().tolist()))
                df_f = df_est if filtro=="TODOS" else df_est[df_est['id_gaveta']==filtro]
                df_f['LABEL'] = df_f['id_gaveta'] + " - " + df_f['descricao'] + " (" + df_f['marca'] + ")"
                fig = px.bar(df_f, x="qtd_atual", y="LABEL", color="id_gaveta", orientation='h', text="qtd_atual", title=f"ESTOQUE GERAL - {filtro} - {agora_str()}")
                fig.update_traces(texttemplate='%{text} un', textposition='outside')
                fig.update_layout(height=500, plot_bgcolor='#111', paper_bgcolor='#111', font_color='white')
                st.plotly_chart(fig, use_container_width=True)

                mov = supabase.table("movimentacoes").select("*").execute()
                df_m = pd.DataFrame(mov.data) if mov.data else pd.DataFrame()
                if not df_m.empty:
                    c1,c2 = st.columns(2)
                    with c1:
                        st.markdown("#### 📥 GRÁFICO DE ENTRADAS")
                        f_e = st.selectbox("Filtrar Entradas", ["TODOS"] + sorted(df_m['id_gaveta'].unique().tolist()), key="fe")
                        df_e = df_m[df_m['tipo']=="ENTRADA"]
                        df_e = df_e if f_e=="TODOS" else df_e[df_e['id_gaveta']==f_e]
                        if not df_e.empty:
                            fig_e = px.bar(df_e, x="qtd", y="id_gaveta", color="id_gaveta", orientation='h', text="qtd", title=f"ENTRADAS - {f_e}")
                            fig_e.update_traces(textposition='outside')
                            st.plotly_chart(fig_e, use_container_width=True)
                    with c2:
                        st.markdown("#### 📤 GRÁFICO DE SAÍDAS")
                        f_s = st.selectbox("Filtrar Saídas", ["TODOS"] + sorted(df_m['id_gaveta'].unique().tolist()), key="fs")
                        df_s = df_m[df_m['tipo']=="SAÍDA"]
                        df_s = df_s if f_s=="TODOS" else df_s[df_s['id_gaveta']==f_s]
                        if not df_s.empty:
                            fig_s = px.bar(df_s, x="qtd", y="id_gaveta", color="id_gaveta", orientation='h', text="qtd", title=f"SAÍDAS - {f_s}")
                            fig_s.update_traces(textposition='outside')
                            st.plotly_chart(fig_s, use_container_width=True)

                if pode_editar("ESTOQUE_GERAL"):
                    st.markdown("### ✏️ BOTÃO EDITAR ESTOQUE")
                    id_ed = st.selectbox("ID editar qtd", df_est['id_gaveta'].tolist())
                    nq = st.number_input("Nova QTD", 0, 100000, 0)
                    if st.button("SALVAR EDIÇÃO ESTOQUE"):
                        supabase.table("estoque_geral").update({"qtd_atual":nq}).eq("id_gaveta",id_ed).execute()
                        st.success(f"Editado {agora_str()}"); st.rerun()
