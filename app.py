import streamlit as st
import pandas as pd
import sqlite3, os
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="BUILD STOCK PRO - Gestão", page_icon="📦", initial_sidebar_state="expanded")

DB = "estoque_fornos.db"

USUARIOS = {
    "admin@buildstock.com": {"nome": "Administrador", "admin": 1, "senha": "admin123"},
    "gerente@buildstock.com": {"nome": "Gerente", "admin": 1, "senha": "admin123"},
    "almoxarife@buildstock.com": {"nome": "Almoxarife", "admin": 0, "senha": "123"},
}

LISTA_UNIDADES = ["KG - Quilograma", "UN - Unidade", "PC - Peça", "CX - Caixa", "SC - Saco", "PL - Palete", "M² - Metro quadrado", "M³ - Metro cúbico", "L - Litro", "BAGS - Saco 1000KG"]

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS materiais (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE, nome TEXT, marca TEXT, categoria TEXT, peso REAL, unidade TEXT, custo_unit REAL DEFAULT 0)""")
    con.execute("""CREATE TABLE IF NOT EXISTS estoque (id INTEGER PRIMARY KEY AUTOINCREMENT, gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT, qtd REAL, unit_pal INT DEFAULT 1, kg_unit REAL DEFAULT 1, unidade TEXT, fab DATE, validade DATE, lote TEXT, local TEXT, observacao TEXT, custo_total REAL DEFAULT 0, data_entrada DATE)""")
    con.execute("""CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, gaveta_id INT, codigo TEXT, nome TEXT, tipo TEXT, qtd REAL, total_kg REAL, usuario TEXT, obs TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, nome TEXT, is_admin INTEGER DEFAULT 0, ativo INTEGER DEFAULT 1)""")
    con.execute("""CREATE TABLE IF NOT EXISTS gaveta_lock (gaveta_id INT PRIMARY KEY, trancada INTEGER DEFAULT 0, motivo TEXT, estoque_min REAL DEFAULT 100)""")
    for i in range(1,21):
        con.execute("INSERT OR IGNORE INTO gaveta_lock (gaveta_id, trancada, estoque_min) VALUES (?,0,100)", (i,))
    for email, d in USUARIOS.items():
        con.execute("INSERT OR IGNORE INTO usuarios (email, nome, is_admin, ativo) VALUES (?,?,?,1)", (email, d["nome"], d["admin"]))
        con.execute("UPDATE usuarios SET is_admin=?, ativo=1 WHERE email=?", (d["admin"], email))
    con.commit(); con.close()

def carregar_dados_reais():
    con = sqlite3.connect(DB)
    df = pd.read_sql("SELECT COUNT(*) as c FROM estoque", con)
    if df.iloc[0]["c"] > 0:
        con.close(); return
    dados = [
        (13, "PASTA-FRIA-772", "Pasta Fria Carbon", "Carbon", 40, 1, 1000, "BAGS", "2026-07-23", "2027-01-23", "772/773", "Barracão", "40 BAGS 40.000 KG", 40*1000*2.5, "2026-08-20"),
        (13, "PASTA-766", "Pasta Carbon", "Carbon", 3, 1, 1000, "BAGS", "2026-07-20", "2027-01-20", "766/767", "Barracão", "3 BAGS 3.000 KG", 3000*2.5, "2026-08-20"),
        (13, "PASTA-767", "Pasta Carbon", "Carbon", 1, 1, 1000, "BAGS", "2026-07-20", "2027-01-20", "767", "Barracão", "1 BAGS 1.000 KG", 1000*2.5, "2026-08-20"),
        (13, "PASTA-768", "Pasta Carbon", "Carbon", 29, 1, 1000, "BAGS", "2026-07-20", "2027-01-20", "768", "Barracão", "29 BAGS 29.000 KG", 29000*2.5, "2026-08-20"),
        (13, "PASTA-769", "Pasta Carbon", "Carbon", 20, 1, 1000, "BAGS", "2026-07-20", "2027-01-20", "769", "Barracão", "20 BAGS 20.000 KG", 20000*2.5, "2026-08-20"),
        (13, "PASTA-770", "Pasta Carbon", "Carbon", 20, 1, 1000, "BAGS", "2026-07-20", "2027-01-20", "770", "Barracão", "20 BAGS 20.000 KG", 20000*2.5, "2026-08-20"),
        (7, "SKAMOL-760", "Tijolo Isolante Skamol Sabão 760", "SKAMOL", 0, 1000, 1, "UN", "2026-08-21", "2027-08-21", "760", "Barracão", "ZEROU", 0, "2026-08-21"),
        (7, "SKAMOL-1140", "Tijolo Isolante Skamol Nove 1.140", "SKAMOL", 3520, 1, 1, "UN", "2026-08-21", "2027-08-21", "1140", "Barracão", "3 PALETES 3.520 UND", 3520*5, "2026-08-21"),
        (7, "MOSCONI-850", "Tijolo Isolante Mosconi AB55 850", "MOSCONI", 14450, 1, 1, "UN", "2026-08-21", "2027-08-21", "AB55-850", "Barracão", "17 PALETES 14.450 UND", 14450*4.5, "2026-08-21"),
        (7, "MOSCONI-1360", "Tijolo Isolante Mosconi AB55 1360", "MOSCONI", 13600, 1, 1, "UN", "2026-08-21", "2027-08-21", "AB55-1360", "Barracão", "10 PALETES 13.600 UND", 13600*4.5, "2026-08-21"),
        (3, "TECNOFIRE-1200", "Argamassa Tecnofire S-1200", "TECNOFIRE", 0, 1, 10, "KG", "2026-08-20", "2027-02-20", "S-1200", "Barracão", "Zerou", 0, "2026-08-20"),
        (3, "PLACIBAR-SG1250", "Argamassa Placibar SG-1250", "PLACIBAR", 7500, 1, 1, "KG", "2026-08-20", "2027-02-20", "SG-1250", "Barracão", "6 PALETES 7.500 KG", 7500*3, "2026-08-20"),
        (3, "PLACIBAR-SG1000", "Argamassa Placibar SG-1000", "PLACIBAR", 1000, 1, 1, "KG", "2026-08-20", "2027-02-20", "SG-1000", "Barracão", "1 PALETE 1.000 KG", 1000*3, "2026-08-20"),
        (4, "CASTIBAR-1250", "Concreto Castibar PSI UG 1250", "CASTIBAR", 5000, 1, 1, "KG", "2026-08-21", "2027-02-21", "PSI-1250", "Barracão", "4 PALETES 5.000 KG", 5000*2.8, "2026-08-21"),
        (4, "CASTIBAR-1000", "Concreto Castibar PSI UG 1000", "CASTIBAR", 1000, 1, 1, "KG", "2026-08-21", "2027-02-21", "PSI-1000", "Barracão", "1 PALETE 1.000 KG", 1000*2.8, "2026-08-21"),
        (5, "LA-ROCHA", "Lã de Rocha 8,64m² 1200x600x25", "ISOVER", 492, 1, 1, "M²", "2026-08-21", "2027-08-21", "LOTE-5", "Barracão", "57 PCT 492 m² - Recarga 25+8", 492*12, "2026-08-21"),
        (9, "PLACA-VERM", "Placas banho vermiculita", "VERMICULITA", 28, 1, 1, "PL", "2026-08-21", "2027-08-21", "BANHO", "Barracão", "28 paletes 13:46", 28*150, "2026-08-21"),
        (14, "BLOCO-M-CARBON", "Bloco M Lateral Carbon 46CX", "CARBON", 1242, 1, 1, "UN", "2026-08-20", "2027-08-20", "CARBON-46", "Barracão", "M 46cx 27=1242", 1242*8, "2026-08-20"),
        (14, "BLOCO-O-CARBON", "Bloco O Lateral Carbon 46CX", "CARBON", 92, 1, 1, "UN", "2026-08-20", "2027-08-20", "CARBON-46", "Barracão", "O(2)=92", 92*8, "2026-08-20"),
        (14, "BLOCO-O2-CARBON", "Bloco O' Lateral Carbon", "CARBON", 92, 1, 1, "UN", "2026-08-20", "2027-08-20", "CARBON-46", "Barracão", "O'(2)=92", 92*8, "2026-08-20"),
        (14, "BLOCO-P-CARBON", "Bloco P Lateral Carbon", "CARBON", 184, 1, 1, "UN", "2026-08-20", "2027-08-20", "CARBON-46", "Barracão", "P(4)=184", 184*8, "2026-08-20"),
        (14, "BLOCO-M-ALUBASE", "Bloco M Alubase c/70", "ALUBASE", 540, 1, 1, "UN", "2026-08-20", "2027-08-20", "ALUBASE", "Barracão", "M(54)=540", 540*8, "2026-08-20"),
        (15, "TIJ-15A", "Tijolo 15A", "MOSCONI", 94, 1, 1, "UN", "2026-08-20", "2027-08-20", "15A", "GRD", "94 UND 12:42", 94*6, "2026-08-20"),
        (16, "TIJ-16A", "Tijolo 16A", "MOSCONI", 0, 1, 1, "UN", "2026-08-20", "2027-08-20", "16A", "GRD", "0 ZERADO", 0, "2026-08-20"),
        (17, "TIJ-17A", "Tijolo 17A", "MOSCONI", 24, 1, 1, "UN", "2026-08-20", "2027-08-20", "17A", "GRD", "24 UND", 24*6, "2026-08-20"),
        (15, "TIJ-15B", "Tijolo 15B", "MOSCONI", 4, 1, 1, "UN", "2026-08-20", "2027-08-20", "15B", "GRD", "4 UND", 4*6, "2026-08-20"),
        (16, "TIJ-16B", "Tijolo 16B", "MOSCONI", 526, 1, 1, "UN", "2026-08-20", "2027-08-20", "16B", "GRD", "526 UND", 526*6, "2026-08-20"),
        (17, "TIJ-17B-SEC", "Tijolo 17B SEC", "MOSCONI", 186, 1, 1, "UN", "2026-08-20", "2027-08-20", "17B", "GRD", "186 UND SEC", 186*6, "2026-08-20"),
        (17, "TIJ-17B-CHINA", "Tijolo 17B ESSPEE CHINA", "ESSPEE CHINA", 165, 1, 1, "UN", "2026-08-20", "2027-08-20", "17B", "GRD", "165 UND CHINA", 165*6, "2026-08-20"),
    ]
    for d in dados:
        con.execute("INSERT INTO estoque (gaveta_id, codigo, nome, marca, qtd, unit_pal, kg_unit, unidade, fab, validade, lote, local, observacao, custo_total, data_entrada) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", d)
    con.commit(); con.close()

if not os.path.exists(DB):
    init_db(); carregar_dados_reais()
else:
    try: init_db(); carregar_dados_reais()
    except:
        if os.path.exists(DB): os.remove(DB)
        init_db(); carregar_dados_reais()

def calc_total(q, kg):
    try: return float(q or 0)*float(kg or 0)
    except: return 0.0

if 'logado' not in st.session_state: st.session_state.logado=False
if 'usuario_email' not in st.session_state: st.session_state.usuario_email=""
if 'is_admin' not in st.session_state: st.session_state.is_admin=False
if 'gaveta_sel' not in st.session_state: st.session_state.gaveta_sel=None

def check_login():
    if not st.session_state.logado:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #3B82F6 100%); padding:35px; border-radius:20px; color:white; text-align:center; box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>
            <h1 style='margin:0; font-size:32px;'>📦 BUILD STOCK PRO</h1>
            <p style='margin:10px 0 0 0; opacity:0.9;'>Gestão Inteligente - FEFO | ABC | Kanban | Giro de Estoque</p>
            <p style='margin:5px 0 0 0; font-size:12px; opacity:0.7;'>Atualizado 21/08/2026 13:46 - 36 itens - 155.000 KG</p>
        </div>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            c1,c2 = st.columns([2,1])
            email = c1.text_input("📧 Email", value="admin@buildstock.com")
            senha = c2.text_input("🔑 Senha", type="password", value="admin123")
            if st.button("🚀 ENTRAR NO SISTEMA", type="primary", use_container_width=True):
                email_low = email.strip().lower()
                if email_low in USUARIOS and senha == USUARIOS[email_low]["senha"]:
                    st.session_state.logado=True
                    st.session_state.usuario_email=email_low
                    st.session_state.is_admin=bool(USUARIOS[email_low]["admin"])
                    st.rerun()
                else: st.error("Email ou senha inválidos! admin@buildstock.com / admin123")
            st.info("👑 **Admin:** admin@buildstock.com / admin123\n👷 **Gerente:** gerente@buildstock.com / admin123\n📦 **Almoxarife:** almoxarife@buildstock.com / 123")
            if st.button("🗑️ RESETAR BANCO E CARREGAR DADOS REAIS 21/08/2026", use_container_width=True):
                if os.path.exists(DB): os.remove(DB)
                init_db(); carregar_dados_reais()
                st.success("Resetado!")
        st.stop()
check_login()

# CSS PRO
st.markdown("""
<style>
.kpi-card { background: white; border-radius: 15px; padding: 18px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-left: 5px solid #3B82F6; }
.kpi-card.alert { border-left-color: #EF4444; }
.kpi-card.warn { border-left-color: #F59E0B; }
.kpi-card.ok { border-left-color: #10B981; }
.gaveta-pro { background: linear-gradient(180deg, #E5E7EB 0%, #9CA3AF 20%, #6B7280 50%, #9CA3AF 80%, #E5E7EB 100%); border: 3px solid #374151; border-radius: 12px; height: 125px; display:flex; flex-direction:column; justify-content:center; align-items:center; color:#111; font-weight:900; box-shadow: 0 6px 15px rgba(0,0,0,0.25), inset 0 2px 3px rgba(255,255,255,0.6); transition: all 0.2s; position:relative; }
.gaveta-pro:hover { transform: translateY(-4px); box-shadow: 0 12px 25px rgba(0,0,0,0.3); }
.gaveta-pro.vazio { background: linear-gradient(180deg, #F3F4F6, #D1D5DB); border-style: dashed; }
.gaveta-pro.alerta { background: linear-gradient(180deg, #FEF3C7, #F59E0B); border-color: #D97706; }
.gaveta-pro.perigo { background: linear-gradient(180deg, #FEE2E2, #EF4444); border-color: #DC2626; color: white; }
.gaveta-pro.ok { background: linear-gradient(180deg, #D1FAE5, #10B981); border-color: #059669; }
.puxador-pro { width: 80px; height: 12px; background: linear-gradient(90deg, #111, #444, #111); border-radius: 6px; margin: 6px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.5); }
.etiqueta-pro { background: white; color: black; padding: 3px 10px; border-radius: 6px; font-size: 12px; font-weight: 900; border: 2px solid #111; }
.tabela-pro { background: white; border-radius: 15px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border-top: 8px solid #10B981; }
</style>
""", unsafe_allow_html=True)

def get_df():
    try:
        con = sqlite3.connect(DB)
        df = pd.read_sql("SELECT * FROM estoque", con)
        df_lock = pd.read_sql("SELECT * FROM gaveta_lock", con)
        df_hist = pd.read_sql("SELECT * FROM historico ORDER BY data DESC", con)
        con.close()
        if not df.empty:
            df["total"] = df.apply(lambda r: calc_total(r["qtd"], r["kg_unit"]), axis=1)
            df["validade"] = pd.to_datetime(df["validade"], errors='coerce')
            df["fab"] = pd.to_datetime(df["fab"], errors='coerce')
            df["dias_vencer"] = (df["validade"] - pd.to_datetime(date.today())).dt.days
            df["status_validade"] = df["dias_vencer"].apply(lambda x: "🔴 VENCIDO" if pd.notna(x) and x<0 else ("🟡 Vence 30d" if pd.notna(x) and x<=30 else ("🟢 OK" if pd.notna(x) and x<=90 else "⚪ Longo prazo")))
            df["categoria"] = df["nome"].apply(lambda x: "Pasta Carbon" if "Pasta" in str(x) else ("Blocos" if "Bloco" in str(x) else ("Tijolo Isolante" if "Isolante" in str(x) else ("Argamassa" if "Argamassa" in str(x) else ("Concreto" if "Concreto" in str(x) else ("Lã Rocha" if "Lã" in str(x) else ("Placas" if "Placa" in str(x) else "Tijolos")))))))
        return df, df_lock, df_hist
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_est, df_lock, df_hist = get_df()

# HEADER KPIs - GESTÃO
st.markdown(f"""
<div style='background: linear-gradient(90deg, #0F172A, #1E3A8A); padding:10px 20px; border-radius:12px; color:white; display:flex; justify-content:space-between; align-items:center;'>
    <span>📦 BUILD STOCK PRO | {st.session_state.usuario_email} {'👑 ADMIN' if st.session_state.is_admin else '👷'} | 21/08/2026 13:46</span>
    <span style='font-size:12px; opacity:0.8;'>Gavetas: 20 | Itens: {len(df_est)} | Total: {df_est['total'].sum() if not df_est.empty else 0:,.0f}</span>
</div>
""", unsafe_allow_html=True)

# KPIs
if not df_est.empty:
    total_kg = df_est["total"].sum()
    total_itens = len(df_est)
    total_gavetas_ocupadas = df_est["gaveta_id"].nunique()
    custo_total = df_est["custo_total"].sum() if "custo_total" in df_est.columns else 0
    vencidos = len(df_est[df_est["dias_vencer"]<0]) if "dias_vencer" in df_est.columns else 0
    vence_30d = len(df_est[(df_est["dias_vencer"]>=0) & (df_est["dias_vencer"]<=30)]) if "dias_vencer" in df_est.columns else 0
    zerados = len(df_est[df_est["qtd"]==0])

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    with k1: st.markdown(f"<div class='kpi-card ok'><small>📦 TOTAL ESTOQUE</small><h2>{total_kg:,.0f}</h2><small>KG/UN - {total_gavetas_ocupadas}/20 Gavetas</small></div>", unsafe_allow_html=True)
    with k2: st.markdown(f"<div class='kpi-card'><small>💰 VALOR ESTIMADO</small><h2>R$ {custo_total:,.0f}</h2><small>{total_itens} itens</small></div>", unsafe_allow_html=True)
    with k3: st.markdown(f"<div class='kpi-card {'alert' if vencidos>0 else 'ok'}'><small>🔴 VENCIDOS</small><h2>{vencidos}</h2><small>FEFO - Retirar</small></div>", unsafe_allow_html=True)
    with k4: st.markdown(f"<div class='kpi-card {'warn' if vence_30d>0 else 'ok'}'><small>🟡 VENCE 30 DIAS</small><h2>{vence_30d}</h2><small>Usar primeiro</small></div>", unsafe_allow_html=True)
    with k5: st.markdown(f"<div class='kpi-card {'alert' if zerados>0 else 'ok'}'><small>⚪ ZERADOS</small><h2>{zerados}</h2><small>Comprar</small></div>", unsafe_allow_html=True)
    with k6: st.markdown(f"<div class='kpi-card'><small>📊 GIRO</small><h2>{len(df_hist) if not df_hist.empty else 0}</h2><small>Movimentações</small></div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"👤 **{st.session_state.usuario_email}**")
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.logado=False
        st.rerun()
    st.divider()
    st.markdown("### 🎛️ Filtros Gestão")
    filtro_cat = st.selectbox("Categoria", ["TODAS"] + sorted(df_est["categoria"].unique().tolist()) if not df_est.empty else ["TODAS"])
    filtro_status = st.selectbox("Validade (FEFO)", ["TODOS", "🔴 VENCIDO", "🟡 Vence 30d", "🟢 OK", "⚪ Longo prazo", "⚪ ZERADO (qtd=0)"])
    if st.button("🔄 RESETAR DADOS REAIS 21/08", type="primary", use_container_width=True):
        if os.path.exists(DB): os.remove(DB)
        init_db(); carregar_dados_reais()
        st.session_state.gaveta_sel=None
        st.rerun()
    st.divider()
    st.markdown("### 📦 Legenda Gavetas")
    st.markdown("🟢 OK > mínimo\n🟡 Alerta < mínimo\n🔴 Zerado/Vencido\n⚪ Vazia\n🔒 Trancada")

tabs = st.tabs(["🗄️ GAVETAS VISUAIS (Clique abre tabela)", "📊 DASHBOARD GESTÃO (ABC, FEFO, Giro)", "📋 INVENTÁRIO COMPLETO", "📈 RELATÓRIOS", "👑 ADMIN" if st.session_state.is_admin else "👤 PERFIL"])

# ABA 1 - GAVETAS
with tabs[0]:
    df_filtro = df_est.copy()
    if filtro_cat!= "TODAS" and not df_filtro.empty:
        df_filtro = df_filtro[df_filtro["categoria"]==filtro_cat]
    if filtro_status!= "TODOS" and not df_filtro.empty:
        if "ZERADO" in filtro_status:
            df_filtro = df_filtro[df_filtro["qtd"]==0]
        else:
            df_filtro = df_filtro[df_filtro["status_validade"]==filtro_status]

    if st.session_state.gaveta_sel is None:
        st.markdown(f"### 🗄️ Arquivo de Aço - 20 Gavetas - Clique para abrir e ver tabela | Filtro: {filtro_cat} | {filtro_status}")

        # Grid gavetas com status inteligente
        for linha in range(0, 20, 4):
            cols = st.columns(4)
            for idx in range(4):
                gid = linha + idx + 1
                if gid>20: continue
                df_g = df_filtro[df_filtro["gaveta_id"]==gid] if not df_filtro.empty else pd.DataFrame()
                total_g = df_g["total"].sum() if not df_g.empty else 0
                qtd_g = len(df_g)
                custo_g = df_g["custo_total"].sum() if not df_g.empty and "custo_total" in df_g.columns else 0
                venc_g = len(df_g[df_g["dias_vencer"]<0]) if not df_g.empty and "dias_vencer" in df_g.columns else 0

                # Status inteligente
                status_class = "vazio"
                icon = "⚪"
                if not df_g.empty:
                    if venc_g>0 or (df_g["qtd"]==0).any(): status_class="perigo"; icon="🔴"
                    elif total_g < 100: status_class="alerta"; icon="🟡"
                    else: status_class="ok"; icon="🟢"

                trancada=False
                if not df_lock.empty:
                    r = df_lock[df_lock["gaveta_id"]==gid]
                    if not r.empty: trancada=bool(r.iloc[0]["trancada"])

                with cols[idx]:
                    st.markdown(f"""
                    <div class="gaveta-pro {status_class}">
                        <div class="etiqueta-pro">GAVETA {gid:02d} {icon} {'🔒' if trancada else ''}</div>
                        <div class="puxador-pro"></div>
                        <div style="font-size:11px;">{qtd_g} itens | {total_g:,.0f}</div>
                        <div style="font-size:10px; opacity:0.8;">R$ {custo_g:,.0f} {f'⚠️ {venc_g} venc' if venc_g>0 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"👆 ABRIR G{gid:02d} - Ver Tabela", key=f"open_{gid}", use_container_width=True, disabled=trancada and not st.session_state.is_admin):
                        st.session_state.gaveta_sel=gid
                        st.rerun()

        if not df_filtro.empty:
            st.divider()
            c1,c2 = st.columns(2)
            with c1:
                df_gav = df_filtro.groupby("gaveta_id")[["total","custo_total"]].sum().reset_index() if "custo_total" in df_filtro.columns else df_filtro.groupby("gaveta_id")[["total"]].sum().reset_index()
                fig = px.bar(df_gav, x="gaveta_id", y="total", color="total", title="📊 Ocupação por Gaveta (KG/UN)", text="total", color_continuous_scale="Blues")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                df_cat = df_filtro.groupby("categoria")[["total"]].sum().reset_index()
                fig2 = px.pie(df_cat, values="total", names="categoria", title="📦 Distribuição por Categoria (ABC)", hole=0.4)
                st.plotly_chart(fig2, use_container_width=True)

    else:
        sel = st.session_state.gaveta_sel
        if st.button("⬅️ FECHAR GAVETA E VOLTAR AO ARQUIVO", type="secondary", use_container_width=True):
            st.session_state.gaveta_sel=None
            st.rerun()

        st.markdown(f"<div class='tabela-pro'><h2>🗄️ GAVETA {sel:02d} ABERTA - {len(df_est[df_est.gaveta_id==sel]) if not df_est.empty else 0} itens - FEFO: Use vencimento mais próximo primeiro</h2></div>", unsafe_allow_html=True)

        con = sqlite3.connect(DB)
        try: df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE gaveta_id={sel} ORDER BY validade ASC", con)
        except: df_dentro = pd.DataFrame()

        if not df_dentro.empty:
            df_dentro["total"] = df_dentro.apply(lambda r: calc_total(r["qtd"], r["kg_unit"]), axis=1)
            df_dentro["validade"] = pd.to_datetime(df_dentro["validade"], errors='coerce')
            df_dentro["dias_vencer"] = (df_dentro["validade"] - pd.to_datetime(date.today())).dt.days
            df_dentro["status"] = df_dentro["dias_vencer"].apply(lambda x: "🔴 VENCIDO" if pd.notna(x) and x<0 else ("🟡 30d" if pd.notna(x) and x<=30 else "🟢 OK"))

            # TABELA QUE ABRE DIRETO
            st.markdown(f"### 📋 Tabela dentro da Gaveta {sel:02d} - Ordenada por FEFO (vence primeiro em cima) - Total: {df_dentro['total'].sum():,.0f}")

            df_show = df_dentro[["id","codigo","nome","marca","lote","qtd","unidade","total","validade","status","local","observacao","custo_total"]].copy()
            st.dataframe(df_show, use_container_width=True, height=300)

            # Edição intuitiva
            with st.expander(f"✏️ EDITAR TABELA DA GAVETA {sel:02d} - Clique para expandir", expanded=True):
                df_edit = st.data_editor(df_dentro, use_container_width=True, num_rows="dynamic", key=f"edit_{sel}")
                col1,col2,col3 = st.columns(3)
                if col1.button("💾 SALVAR ALTERAÇÕES", type="primary", use_container_width=True, key=f"save_{sel}"):
                    try:
                        con.execute("DELETE FROM estoque WHERE gaveta_id=?", (sel,))
                        df_save = df_edit.drop(columns=[c for c in ["total","dias_vencer","status"] if c in df_edit.columns], errors='ignore')
                        df_save.to_sql("estoque", con, if_exists="append", index=False)
                        con.commit()
                        st.success(f"✅ Gaveta {sel:02d} salva!")
                        st.rerun()
                    except Exception as e: st.error(str(e))
                if col2.button("🔄 FEFO - Reordenar por validade", use_container_width=True, key=f"fefo_{sel}"):
                    st.info("Tabela já ordenada por validade - use os vencidos primeiro!")
                if col3.button("🗑️ LIMPAR GAVETA", use_container_width=True, key=f"clear_{sel}"):
                    con.execute("DELETE FROM estoque WHERE gaveta_id=?", (sel,))
                    con.commit()
                    st.success("Limpa!")
                    st.rerun()

            # Movimentação rápida dentro da gaveta
            st.divider()
            c1,c2 = st.columns(2)
            with c1:
                with st.container(border=True):
                    st.markdown("#### 🟢 ENTRADA RÁPIDA nesta gaveta")
                    cod_e = st.text_input("Código", key=f"cod_e_{sel}")
                    nome_e = st.text_input("Nome", key=f"nome_e_{sel}")
                    qtd_e = st.number_input("Qtd", value=1.0, key=f"qtd_e_{sel}")
                    lote_e = st.text_input("Lote", key=f"lote_e_{sel}")
                    obs_e = st.text_input("Obs", key=f"obs_e_{sel}")
                    if st.button("➕ ENTRADA", type="primary", use_container_width=True, key=f"btn_e_{sel}"):
                        try:
                            con.execute("INSERT INTO estoque (gaveta_id, codigo, nome, marca, qtd, kg_unit, unidade, fab, validade, lote, local, observacao, data_entrada, custo_total) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                        (sel, cod_e, nome_e, "GERAL", qtd_e, 1, "UN", date.today().isoformat(), (date.today()+timedelta(days=90)).isoformat(), lote_e, "Barracão", obs_e, date.today().isoformat(), qtd_e*5))
                            con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, tipo, qtd, total_kg, usuario) VALUES (?,?,?,?,?,?,?,?)",
                                        (datetime.now().isoformat(), sel, cod_e, nome_e, "ENTRADA", qtd_e, qtd_e, st.session_state.usuario_email))
                            con.commit()
                            st.success("Entrada!")
                            st.rerun()
                        except Exception as e: st.error(str(e))
            with c2:
                with st.container(border=True):
                    st.markdown("#### 🔴 SAÍDA RÁPIDA desta gaveta")
                    if not df_dentro.empty:
                        id_s = st.selectbox("Item para saída:", df_dentro["id"].tolist(), format_func=lambda x: f"ID {x} - {df_dentro[df_dentro.id==x].iloc[0]['codigo']} - {df_dentro[df_dentro.id==x].iloc[0]['qtd']} {df_dentro[df_dentro.id==x].iloc[0]['status'] if 'status' in df_dentro.columns else ''}", key=f"saida_{sel}")
                        qtd_s = st.number_input("Qtd saída", value=1.0, key=f"qtd_s_{sel}")
                        obs_s = st.text_input("Motivo saída", key=f"obs_s_{sel}")
                        if st.button("➖ SAÍDA", type="primary", use_container_width=True, key=f"btn_s_{sel}"):
                            try:
                                row = df_dentro[df_dentro.id==id_s].iloc[0]
                                con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, tipo, qtd, total_kg, usuario, obs) VALUES (?,?,?,?,?,?,?,?,?)",
                                            (datetime.now().isoformat(), sel, row["codigo"], row["nome"], "SAIDA", qtd_s, qtd_s, st.session_state.usuario_email, obs_s))
                                if qtd_s >= row["qtd"]:
                                    con.execute("DELETE FROM estoque WHERE id=?", (int(id_s),))
                                else:
                                    con.execute("UPDATE estoque SET qtd = qtd -? WHERE id=?", (float(qtd_s), int(id_s)))
                                con.commit()
                                st.success("Saída!")
                                st.rerun()
                            except Exception as e: st.error(str(e))
        else:
            st.info(f"📭 Gaveta {sel:02d} vazia - Adicione material acima")
            with st.container(border=True):
                st.markdown("#### ➕ Primeiro item nesta gaveta")
                c1,c2,c3 = st.columns(3)
                cod_n = c1.text_input("Código", key=f"cod_new_{sel}")
                nome_n = c2.text_input("Nome", key=f"nome_new_{sel}")
                qtd_n = c3.number_input("Qtd", value=1.0, key=f"qtd_new_{sel}")
                if st.button("➕ ADICIONAR", type="primary", use_container_width=True, key=f"add_new_{sel}"):
                    try:
                        con.execute("INSERT INTO estoque (gaveta_id, codigo, nome, marca, qtd, kg_unit, unidade, fab, validade, local, data_entrada) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                                    (sel, cod_n, nome_n, "GERAL", qtd_n, 1, "UN", date.today().isoformat(), (date.today()+timedelta(days=90)).isoformat(), "Barracão", date.today().isoformat()))
                        con.commit()
                        st.success("Adicionado!")
                        st.rerun()
                    except Exception as e: st.error(str(e))
        con.close()
        if st.button("⬅️ FECHAR GAVETA", type="secondary", use_container_width=True, key=f"close2_{sel}"):
            st.session_state.gaveta_sel=None
            st.rerun()

# ABA 2 - DASHBOARD GESTÃO
with tabs[1]:
    if df_est.empty:
        st.warning("Sem dados")
    else:
        st.markdown("### 📊 Dashboard Gestão - Melhores práticas WMS")

        c1,c2 = st.columns(2)
        with c1:
            # ABC - Pareto
            df_abc = df_est.groupby("nome")[["total","custo_total"]].sum().reset_index().sort_values("total", ascending=False)
            df_abc["perc"] = df_abc["total"].cumsum() / df_abc["total"].sum() * 100
            df_abc["classe"] = df_abc["perc"].apply(lambda x: "A - 80% Giro" if x<=80 else ("B - 15% Giro" if x<=95 else "C - 5% Giro"))
            fig_abc = px.bar(df_abc, x="nome", y="total", color="classe", title="📈 Curva ABC - Pareto 80/20 - Foque na classe A", text="total")
            fig_abc.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_abc, use_container_width=True)
            st.dataframe(df_abc, use_container_width=True, height=200)

        with c2:
            # FEFO Validade
            df_fefo = df_est[df_est["dias_vencer"].notna()].copy()
            if not df_fefo.empty:
                fig_fefo = px.scatter(df_fefo, x="validade", y="total", color="status_validade", size="total", hover_data=["codigo","lote","gaveta_id"], title="⏰ FEFO - Validade x Quantidade - Use os vermelhos primeiro", color_discrete_map={"🔴 VENCIDO":"red","🟡 Vence 30d":"orange","🟢 OK":"green","⚪ Longo prazo":"gray"})
                st.plotly_chart(fig_fefo, use_container_width=True)

            # Giro por categoria
            df_cat_giro = df_est.groupby("categoria")[["total"]].sum().reset_index()
            fig_cat = px.treemap(df_cat_giro, path=["categoria"], values="total", title="📦 Ocupação por Categoria - Treemap")
            st.plotly_chart(fig_cat, use_container_width=True)

        c3,c4 = st.columns(2)
        with c3:
            # Estoque mínimo - Kanban
            df_gav = df_est.groupby("gaveta_id")[["total"]].sum().reset_index()
            df_gav = pd.merge(df_gav, df_lock[["gaveta_id","estoque_min"]], on="gaveta_id", how="left")
            df_gav["estoque_min"] = df_gav["estoque_min"].fillna(100)
            df_gav["status_kanban"] = df_gav.apply(lambda r: "🔴 Comprar" if r["total"] < r["estoque_min"] else ("🟡 Atenção" if r["total"] < r["estoque_min"]*1.5 else "🟢 OK"), axis=1)
            fig_kanban = px.bar(df_gav, x="gaveta_id", y="total", color="status_kanban", title="🚦 Kanban - Estoque Mínimo por Gaveta", color_discrete_map={"🔴 Comprar":"red","🟡 Atenção":"orange","🟢 OK":"green"})
            fig_kanban.add_trace(go.Scatter(x=df_gav["gaveta_id"], y=df_gav["estoque_min"], mode="lines", name="Mínimo", line=dict(color="red", dash="dash")))
            st.plotly_chart(fig_kanban, use_container_width=True)
            st.dataframe(df_gav[df_gav["status_kanban"]!="🟢 OK"].sort_values("total"), use_container_width=True)

        with c4:
            # Histórico giro
            if not df_hist.empty:
                df_hist["data"] = pd.to_datetime(df_hist["data"])
                df_hist["mes"] = df_hist["data"].dt.to_period("M").astype(str)
                df_mes = df_hist.groupby(["mes","tipo"])["qtd"].sum().reset_index()
                fig_giro = px.bar(df_mes, x="mes", y="qtd", color="tipo", barmode="group", title="🔄 Giro - Entradas x Saídas por Mês", color_discrete_map={"ENTRADA":"green","SAIDA":"red"})
                st.plotly_chart(fig_giro, use_container_width=True)
            else:
                st.info("Sem movimentações ainda - faça entradas e saídas nas gavetas")

        # Alertas gestão
        st.divider()
        st.markdown("### 🚨 Alertas Inteligentes - O que o gestor precisa fazer")
        col_a,col_b,col_c = st.columns(3)
        with col_a:
            st.markdown("#### 🔴 Comprar Urgente - Zerados")
            df_zero = df_est[df_est["qtd"]==0]
            if not df_zero.empty: st.dataframe(df_zero[["gaveta_id","codigo","nome","marca"]], use_container_width=True)
            else: st.success("Nenhum zerado")
        with col_b:
            st.markdown("#### 🟡 Vence em 30 dias - Usar primeiro (FEFO)")
            df_30 = df_est[(df_est["dias_vencer"]>=0) & (df_est["dias_vencer"]<=30)] if "dias_vencer" in df_est.columns else pd.DataFrame()
            if not df_30.empty: st.dataframe(df_30[["gaveta_id","codigo","nome","lote","validade","total"]].sort_values("validade"), use_container_width=True)
            else: st.success("Nenhum vence em 30 dias")
        with col_c:
            st.markdown("#### 🔴 Vencidos - Retirar")
            df_venc = df_est[df_est["dias_vencer"]<0] if "dias_vencer" in df_est.columns else pd.DataFrame()
            if not df_venc.empty: st.dataframe(df_venc[["gaveta_id","codigo","nome","lote","validade","total"]], use_container_width=True)
            else: st.success("Nenhum vencido")

# ABA 3 - INVENTÁRIO
with tabs[2]:
    st.markdown("### 📋 Inventário Completo - Todos os materiais - Edição em massa")
    if not df_est.empty:
        # Filtros
        c1,c2,c3 = st.columns(3)
        busca = c1.text_input("🔍 Buscar código, nome, lote")
        gav_f = c2.selectbox("Filtrar Gaveta", ["TODAS"] + sorted(df_est["gaveta_id"].unique().tolist()))
        cat_f = c3.selectbox("Filtrar Categoria", ["TODAS"] + sorted(df_est["categoria"].unique().tolist()))

        df_inv = df_est.copy()
        if busca: df_inv = df_inv[df_inv.apply(lambda r: busca.lower() in str(r["codigo"]).lower() or busca.lower() in str(r["nome"]).lower() or busca.lower() in str(r["lote"]).lower(), axis=1)]
        if gav_f!= "TODAS": df_inv = df_inv[df_inv["gaveta_id"]==gav_f]
        if cat_f!= "TODAS": df_inv = df_inv[df_inv["categoria"]==cat_f]

        st.markdown(f"**Mostrando {len(df_inv)} de {len(df_est)} itens - Total: {df_inv['total'].sum():,.0f} - Valor: R$ {df_inv['custo_total'].sum():,.0f}**")

        df_edit_full = st.data_editor(df_inv, use_container_width=True, height=500, num_rows="dynamic", key="edit_full")

        col1,col2,col3 = st.columns(3)
        if col1.button("💾 SALVAR INVENTÁRIO COMPLETO", type="primary", use_container_width=True):
            try:
                con = sqlite3.connect(DB)
                con.execute("DELETE FROM estoque")
                df_save = df_edit_full.drop(columns=[c for c in ["total","dias_vencer","status_validade","categoria","status"] if c in df_edit_full.columns], errors='ignore')
                df_save.to_sql("estoque", con, if_exists="append", index=False)
                con.commit(); con.close()
                st.success("Inventário salvo!")
                st.rerun()
            except Exception as e: st.error(str(e))

        if col2.button("📥 Exportar Excel", use_container_width=True):
            st.download_button("Baixar Excel", df_inv.to_csv(index=False).encode('utf-8'), "inventario_build_stock_21_08_2026.csv", "text/csv", use_container_width=True)

        if col3.button("🗑️ Limpar tudo", use_container_width=True):
            con = sqlite3.connect(DB)
            con.execute("DELETE FROM estoque")
            con.commit(); con.close()
            st.success("Limpo!")
            st.rerun()
    else: st.info("Sem estoque - clique RESETAR na sidebar")

# ABA 4 - RELATÓRIOS
with tabs[3]:
    st.markdown("### 📈 Relatórios Gestão")
    if not df_est.empty:
        c1,c2 = st.columns(2)
        with c1:
            df_rel_gav = df_est.groupby("gaveta_id").agg(Itens=("codigo","count"), Total_QTD=("total","sum"), Valor=("custo_total","sum"), Vencidos=("dias_vencer", lambda x: (x<0).sum())).reset_index()
            st.dataframe(df_rel_gav, use_container_width=True)
            st.plotly_chart(px.bar(df_rel_gav, x="gaveta_id", y="Valor", title="Valor por Gaveta"), use_container_width=True)
        with c2:
            if not df_hist.empty:
                df_hist["data"] = pd.to_datetime(df_hist["data"])
                st.dataframe(df_hist.head(100), use_container_width=True)
                st.plotly_chart(px.histogram(df_hist, x="data", y="qtd", color="tipo", title="Histórico movimentações"), use_container_width=True)
            else: st.info("Sem histórico - faça movimentações nas gavetas")

        st.divider()
        st.markdown("### 📄 Relatório para Impressão / PDF")
        st.markdown(f"""
        **BUILD STOCK - Relatório Gestão - {datetime.now().strftime('%d/%m/%Y %H:%M')}**

        - Total Itens: {len(df_est)}
        - Total KG/UN: {df_est['total'].sum():,.0f}
        - Valor Estimado: R$ {df_est['custo_total'].sum():,.0f}
        - Gavetas Ocupadas: {df_est['gaveta_id'].nunique()}/20
        - Itens Zerados: {len(df_est[df_est['qtd']==0])}
        - Vencidos: {len(df_est[df_est['dias_vencer']<0]) if 'dias_vencer' in df_est.columns else 0}
        - Vence 30 dias: {len(df_est[(df_est['dias_vencer']>=0) & (df_est['dias_vencer']<=30)]) if 'dias_vencer' in df_est.columns else 0}

        **Top 5 Materiais por Quantidade (ABC Classe A):**
        {df_est.groupby('nome')['total'].sum().sort_values(ascending=False).head(5).to_string()}

        **Por Categoria:**
        {df_est.groupby('categoria')['total'].sum().to_string()}
        """)

# ABA 5 ADMIN
if st.session_state.is_admin and len(tabs)>4:
    with tabs[4]:
        st.markdown("## 👑 ADMIN - Gestão Completa")
        con = sqlite3.connect(DB)

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("### 👥 Usuários")
            with st.form("cad_user", clear_on_submit=True):
                email_new = st.text_input("Email *")
                nome_new = st.text_input("Nome *")
                is_admin_new = st.checkbox("Admin?")
                ativo_new = st.checkbox("Ativo", value=True)
                if st.form_submit_button("💾 Salvar Usuário", type="primary", use_container_width=True):
                    try:
                        con.execute("INSERT OR REPLACE INTO usuarios (email, nome, is_admin, ativo) VALUES (?,?,?,?)", (email_new.strip().lower(), nome_new, int(is_admin_new), int(ativo_new)))
                        con.commit()
                        st.success("Salvo!")
                    except Exception as e: st.error(str(e))
            try: st.dataframe(pd.read_sql("SELECT * FROM usuarios", con), use_container_width=True)
            except: pass

        with c2:
            st.markdown("### 🔒 Gavetas - Travar e Estoque Mínimo (Kanban)")
            gav_tranca = st.selectbox("Gaveta", list(range(1,21)), key="gav_admin")
            col_a,col_b = st.columns(2)
            acao = col_a.selectbox("Ação", ["🔓 LIBERAR", "🔒 TRANCAR"], key="acao_admin")
            estoque_min = col_b.number_input("Estoque Mínimo (Kanban)", value=100.0, key="min_admin")
            motivo = st.text_input("Motivo", key="motivo_admin")
            if st.button("💾 SALVAR GAVETA", type="primary", use_container_width=True):
                val = 1 if "TRANCAR" in acao else 0
                try:
                    con.execute("UPDATE gaveta_lock SET trancada=?, motivo=?, estoque_min=? WHERE gaveta_id=?", (val, motivo, estoque_min, gav_tranca))
                    con.commit()
                    st.success(f"Gaveta {gav_tranca:02d} salva!")
                except Exception as e: st.error(str(e))
            try: st.dataframe(pd.read_sql("SELECT * FROM gaveta_lock", con), use_container_width=True)
            except: pass

        st.divider()
        st.markdown("### 📦 Cadastro Rápido Material")
        with st.form("cad_mat", clear_on_submit=True):
            c1,c2,c3,c4 = st.columns(4)
            cod = c1.text_input("Código *")
            nome = c2.text_input("Nome *")
            marca = c3.text_input("Marca *")
            cat = c4.selectbox("Categoria", ["Pasta Carbon","Blocos","Tijolo Isolante","Argamassa","Concreto","Lã Rocha","Placas","Tijolos","Outro"])
            c5,c6,c7 = st.columns(3)
            qtd = c5.number_input("Qtd", value=1.0)
            unidade = c6.selectbox("Unidade", LISTA_UNIDADES)
            gav = c7.selectbox("Gaveta Destino", list(range(1,21)))
            if st.form_submit_button("💾 Cadastrar no Estoque", type="primary", use_container_width=True):
                if cod and nome:
                    try:
                        con.execute("INSERT INTO estoque (gaveta_id, codigo, nome, marca, qtd, kg_unit, unidade, fab, validade, local, data_entrada, custo_total) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                                    (gav, cod, nome, marca, qtd, 1, unidade, date.today().isoformat(), (date.today()+timedelta(days=90)).isoformat(), "Barracão", date.today().isoformat(), qtd*5))
                        con.commit()
                        st.success("Cadastrado!")
                    except Exception as e: st.error(str(e))
        con.close()
else:
    if len(tabs)>4:
        with tabs[4]:
            st.markdown(f"### 👤 Perfil - {st.session_state.usuario_email}")
            st.info("Você não é ADMIN - solicite liberação para admin@buildstock.com")
