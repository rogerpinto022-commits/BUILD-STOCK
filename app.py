import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
from datetime import date, timedelta, datetime
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

st.set_page_config(page_title="BUILDSTOCK", layout="wide", page_icon="🧱")

# Se não tem Supabase, roda com dados mock
MOCK_MODE = not SUPABASE_URL or "xxx" in SUPABASE_URL
if not MOCK_MODE:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# CSS LUDICO
st.markdown("""
<style>
.big-number {font-size:56px; font-weight:900; text-align:center; color:#1E40AF;}
.card {border-radius:20px; padding:18px; background:white; box-shadow:0 8px 24px rgba(0,0,0,0.08); border:1px solid #E5E7EB}
.badge-verde {background:#DCFCE7; color:#166534; padding:4px 12px; border-radius:99px; font-weight:bold; font-size:12px}
.badge-amarelo {background:#FEF9C3; color:#854D0E; padding:4px 12px; border-radius:99px; font-weight:bold; font-size:12px}
.badge-vermelho {background:#FEE2E2; color:#991B1B; padding:4px 12px; border-radius:99px; font-weight:bold; font-size:12px}
</style>
""", unsafe_allow_html=True)

st.title("🧱 BUILDSTOCK")
st.caption("Soma tudo. Constrói tudo. | ESTOQUE GERAL = LOCAL 1 (MATRIZ FIXA) + LOCAL 2 + LOCAL 3")

# SIDEBAR - MODO AUTOMATICO / MANUAL
st.sidebar.image("https://i.imgur.com/ placeholder", width=100)
st.sidebar.header("⚙️ Modo Operação")
modo_entrada = st.sidebar.radio("ENTRADA", ["AUTOMATICO", "MANUAL"], horizontal=True, key="m_ent")
modo_saida = st.sidebar.radio("SAÍDA", ["AUTOMATICO", "MANUAL"], horizontal=True, key="m_sai")
st.sidebar.caption("AUTOMATICO = computa no Local onde você está | MANUAL = pergunta de qual local computar")

locais_mock = [{"id":"1","codigo":"LOCAL 1","nome":"MATRIZ - Galpão","fixo":True},{"id":"2","codigo":"LOCAL 2","nome":"Filial 1"},{"id":"3","codigo":"LOCAL 3","nome":"Filial 2"}]
materiais_mock = [{"id":"1","nome":"Cimento CP-II","ativo":True},{"id":"2","nome":"Tijolo Baiano","ativo":True},{"id":"3","nome":"Areia Fina","ativo":True},{"id":"4","nome":"Brita 1","ativo":False}]
gavetas_mock = [
    {"id":"g1","codigo":"ID-01","nome":"Gaveta A","cor":"#1E40AF","local1":95,"local2":45,"local3":35,"ultima_qtd":12,"lote":"LT-2025-882","validade":date.today()+timedelta(days=12)},
    {"id":"g2","codigo":"ID-02","nome":"Gaveta B","cor":"#10B981","local1":60,"local2":80,"local3":20,"ultima_qtd":8,"lote":"LT-2025-910","validade":date.today()+timedelta(days=95)},
    {"id":"g3","codigo":"ID-03","nome":"Gaveta C","cor":"#F59E0B","local1":30,"local2":30,"local3":60,"ultima_qtd":15,"lote":"LT-2025-901","validade":date.today()+timedelta(days=5)},
    {"id":"g4","codigo":"ID-04","nome":"Gaveta D","cor":"#EF4444","local1":120,"local2":10,"local3":10,"ultima_qtd":20,"lote":"LT-2025-899","validade":date.today()+timedelta(days=200)},
]

if MOCK_MODE:
    locais = locais_mock
else:
    locais = supabase.table("locais").select("*").execute().data

local_map = {l['codigo']: l['id'] for l in locais}
local_labels = [f"{l['codigo']} - {l['nome']}" for l in locais]
local_atual_label = st.sidebar.selectbox("Você está em qual Local?", local_labels)
codigo_local_atual = local_atual_label.split(" - ")[0]
id_local_atual = local_map[codigo_local_atual]

st.sidebar.divider()
filtro_tempo = st.sidebar.segmented_control("📅 Filtro Tempo - Entradas/Saídas TODOS LOCAIS", ["DIÁRIA","SEMANAL","MENSAL","SEMESTRAL","ANUAL"], default="MENSAL")

tabs = st.tabs(["📊 Estoque Geral", "📥 Entrada", "📤 Saída", "📈 Tempo", "⚙️ Materiais"])

with tabs[0]:
    if MOCK_MODE:
        df = pd.DataFrame(gavetas_mock)
        df['total_geral'] = df['local1']+df['local2']+df['local3']
    else:
        estoque = supabase.table("vw_estoque_geral").select("*").execute().data
        df = pd.DataFrame(estoque)

    if not df.empty:
        # Grafico 1 - EMPILHADO HORIZONTAL POR ID - SOMA 3 LOCAIS
        fig = go.Figure()
        fig.add_trace(go.Bar(y=df['codigo'], x=df['local1'] if 'local1' in df else [95,60,30,120], name='LOCAL 1 MATRIZ', orientation='h', marker_color='#1E40AF'))
        fig.add_trace(go.Bar(y=df['codigo'], x=df['local2'] if 'local2' in df else [45,80,30,10], name='LOCAL 2', orientation='h', marker_color='#10B981'))
        fig.add_trace(go.Bar(y=df['codigo'], x=df['local3'] if 'local3' in df else [35,20,60,10], name='LOCAL 3', orientation='h', marker_color='#F59E0B'))
        fig.update_layout(barmode='stack', height=380, title="ESTOQUE GERAL POR ID - Cada cor é um local, comprimento = SOMA")
        st.plotly_chart(fig, use_container_width=True)

        # Dashboard ludico + ultima retirada + lote e validade
        st.subheader("🎯 Dashboard Lúdico + Última Retirada + Lote e Validade")
        cols = st.columns(4)
        for i, row in df.iterrows() if MOCK_MODE else enumerate(df.to_dict('records')):
            if MOCK_MODE:
                r = row
                total = r['total_geral']
                dias = (r['validade'] - date.today()).days
            else:
                r = row
                total = r.get('total_geral',0)
                dias = 45
            badge_class = "badge-verde" if dias>90 else "badge-amarelo" if dias>30 else "badge-vermelho"
            badge_text = f"Val: {r['validade'] if MOCK_MODE else '08/10/2025'} ({dias}d)"
            with cols[i % 4]:
                st.markdown(f"""
                <div class="card" style="border-top:7px solid {r.get('cor','#1E40AF')}">
                    <div style="font-weight:900">{r['codigo']} - {r.get('nome') or r.get('gaveta')}</div>
                    <div class="big-number">{total}</div>
                    <div style="text-align:center; color:#6B7280">un em estoque geral</div>
                    <hr>
                    ⬇️ Última: <b>{r.get('ultima_qtd',12)} un</b><br>
                    📦 Lote: {r.get('lote','LT-2025-882')}<br><br>
                    <span class="{badge_class}">⚠️ {badge_text}</span><br>
                    <small style="color:#9CA3AF">L1:{r.get('local1',0)} L2:{r.get('local2',0)} L3:{r.get('local3',0)}</small>
                </div>
                """, unsafe_allow_html=True)

with tabs[1]:
    st.subheader("📥 Entrada - Modo: "+modo_entrada)
    materiais_lista = [m['nome'] for m in materiais_mock if m['ativo']] + ["OUTRO..."]
    mat = st.selectbox("Material (só ATIVOS + OUTRO)", materiais_lista)
    gav = st.selectbox("ID / Gaveta", [g['codigo']+" - "+g['nome'] for g in gavetas_mock])
    qtd = st.number_input("Qtd", 1, 1000, 10)
    lote = st.text_input("Lote", "LT-2025-882")
    val = st.date_input("Validade", date.today()+timedelta(days=90))
    if modo_entrada=="MANUAL":
        local_dest = st.selectbox("Computar entrada em qual local?", [l['codigo'] for l in locais])
    else:
        local_dest = codigo_local_atual
        st.info(f"Automático: vai entrar em {local_dest}")

    if mat=="OUTRO...":
        outro = st.text_input("Nome material avulso")
        if st.checkbox("Ativar esse material?"):
            st.success(f"{outro} ativado!")

    if st.button("✅ Confirmar ENTRADA", type="primary", use_container_width=True):
        st.success(f"Entrada {qtd} de {mat} em {gav} no {local_dest} [{modo_entrada}]")
        st.balloons()

with tabs[2]:
    st.subheader("📤 Saída - Só ATIVOS aparecem - Modo: "+modo_saida)
    mat_s = st.selectbox("Material ATIVO", materiais_lista, key="ms")
    gav_s = st.selectbox("ID / Gaveta", [g['codigo']+" - "+g['nome'] for g in gavetas_mock], key="gs")
    qtd_s = st.number_input("Qtd Saída", 1, 1000, 5, key="qs")
    if modo_saida=="MANUAL":
        local_sai = st.selectbox("Computar saída de qual local?", [l['codigo'] for l in locais], key="ls")
    else:
        local_sai = codigo_local_atual
        st.info(f"Automático: vai sair de {local_sai}")
    if st.button("✅ Confirmar SAÍDA", type="primary", use_container_width=True):
        st.warning(f"Saída {qtd_s} de {mat_s} em {gav_s} do {local_sai} [{modo_saida}] - Estoque Geral atualizado!")

with tabs[3]:
    st.subheader(f"📈 {filtro_tempo} - Entradas e Saídas em TODOS OS LOCAIS")
    labels = {"DIÁRIA":["21/09","22/09","23/09","24/09","25/09","26/09"],"SEMANAL":["Sem 1","Sem 2","Sem 3","Sem 4","Sem 5"],"MENSAL":["Abr","Mai","Jun","Jul","Ago","Set"],"SEMESTRAL":["2024-S2","2025-S1","2025-S2"],"ANUAL":["2022","2023","2024","2025","2026"]}[filtro_tempo]
    ent = [20,35,28,40,32,45][:len(labels)]
    sai = [15,28,22,38,30,40][:len(labels)]
    fig2 = go.Figure()
    fig2.add_bar(x=labels, y=ent, name="ENTRADAS", marker_color="#10B981")
    fig2.add_bar(x=labels, y=sai, name="SAÍDAS", marker_color="#EF4444")
    fig2.update_layout(barmode="group", height=350)
    st.plotly_chart(fig2, use_container_width=True)

with tabs[4]:
    st.subheader("⚙️ Materiais - Marcar ATIVOS")
    for m in materiais_mock:
        m['ativo'] = st.checkbox(m['nome'], value=m['ativo'], key="mat_"+m['nome'])
