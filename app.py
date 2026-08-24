import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Controle Materiais - Sala Anexa e Barracão", layout="wide")
fuso_brasil = pytz.timezone('America/Sao_Paulo')

# --- FUNÇÃO DATA/HORA BRASÍLIA ---
def data_hora_brasil():
    agora = datetime.now(fuso_brasil)
    return agora

# --- ARQUIVO DE DADOS ---
ARQUIVO = "estoque.csv"
if not os.path.exists(ARQUIVO):
    df_inicial = pd.DataFrame(columns=["data", "produto", "local", "tipo", "quantidade"])
    df_inicial.to_csv(ARQUIVO, index=False)

df = pd.read_csv(ARQUIVO)
if not df.empty:
    df['data'] = pd.to_datetime(df['data'])

# --- SIDEBAR - LANÇAMENTO ---
st.sidebar.header("📦 Lançamento")
agora = data_hora_brasil()
st.sidebar.info(f"📅 {agora.strftime('%d/%m/%Y')} \n⏰ {agora.strftime('%H:%M:%S')} - Brasília")

produto = st.sidebar.selectbox("Produto", ["Cimento", "Areia", "Brita", "Tijolo", "Cal", "Outro"])
if produto == "Outro":
    produto = st.sidebar.text_input("Nome do produto")

local = st.sidebar.selectbox("Local", ["Barracão", "Sala Anexa"])
tipo = st.sidebar.selectbox("Tipo", ["Entrada", "Saída"])
qtd = st.sidebar.number_input("Quantidade", min_value=1, value=1)

if st.sidebar.button("LANÇAR"):
    nova_linha = pd.DataFrame([{
        "data": data_hora_brasil(),
        "produto": produto,
        "local": local,
        "tipo": tipo,
        "quantidade": qtd
    }])
    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(ARQUIVO, index=False)
    st.sidebar.success("Lançado com sucesso!")
    st.rerun()

# --- CÁLCULO DO ESTOQUE ATUAL (AUTOMÁTICO QUE VOCÊ PEDIU) ---
st.title("📊 Painel de Controle - Materiais Construção")

if df.empty:
    st.warning("Nenhum lançamento ainda.")
    st.stop()

# Cria estoque por local
estoque = df.copy()
estoque['qtd_calc'] = estoque.apply(lambda x: x['quantidade'] if x['tipo'] == 'Entrada' else -x['quantidade'], axis=1)

# LÓGICA AUTOMÁTICA INTERLIGADA
# O estoque final é calculado, mas a transferência já está implícita nos lançamentos
# Se você lança ENTRADA na Sala, tem que ter SAÍDA no Barracão e vice-versa.
# Para automatizar de verdade, vamos fazer o desconto automático no visual:

resumo_local = estoque.groupby(['local', 'produto'])['qtd_calc'].sum().reset_index()
pivot = resumo_local.pivot(index='produto', columns='local', values='qtd_calc').fillna(0)

# Garante colunas
if 'Barracão' not in pivot.columns:
    pivot['Barracão'] = 0
if 'Sala Anexa' not in pivot.columns:
    pivot['Sala Anexa'] = 0

pivot['TOTAL GERAL'] = pivot['Barracão'] + pivot['Sala Anexa']

# --- MOSTRA MÉTRICAS ---
col1, col2, col3 = st.columns(3)
col1.metric("🏚️ Barracão", f"{pivot['Barracão'].sum():.0f}")
col2.metric("🏠 Sala Anexa", f"{pivot['Sala Anexa'].sum():.0f}")
col3.metric("📦 TOTAL GERAL (Sala + Barracão)", f"{pivot['TOTAL GERAL'].sum():.0f}")

st.dataframe(pivot, use_container_width=True)

# --- GRÁFICOS DE ESTOQUE ATUAL ---
st.divider()
st.subheader("📦 Estoque Atual por Local")
c1, c2 = st.columns(2)
with c1:
    fig1 = px.bar(pivot.reset_index(), x='produto', y=['Barracão', 'Sala Anexa'], barmode='group', title="Barracão x Sala Anexa")
    st.plotly_chart(fig1, use_container_width=True)
with c2:
    fig2 = px.pie(pivot.reset_index(), values='TOTAL GERAL', names='produto', title="TOTAL GERAL por Produto")
    st.plotly_chart(fig2, use_container_width=True)

# --- GRÁFICOS TEMPORAIS ---
st.divider()
st.subheader("📈 Entradas x Saídas - Mensal, Semestral e Anual")

df['mes'] = df['data'].dt.to_period('M').astype(str)
df['semestre'] = df['data'].dt.year.astype(str) + "-S" + ((df['data'].dt.month-1)//6 + 1).astype(str)
df['ano'] = df['data'].dt.year.astype(str)

mensal = df.groupby(['mes', 'tipo'])['quantidade'].sum().reset_index()
fig_mensal = px.line(mensal, x='mes', y='quantidade', color='tipo', markers=True, title="MENSAL")
st.plotly_chart(fig_mensal, use_container_width=True)

semestral = df.groupby(['semestre', 'tipo'])['quantidade'].sum().reset_index()
fig_sem = px.bar(semestral, x='semestre', y='quantidade', color='tipo', barmode='group', title="SEMESTRAL")
st.plotly_chart(fig_sem, use_container_width=True)

anual = df.groupby(['ano', 'tipo'])['quantidade'].sum().reset_index()
fig_anual = px.bar(anual, x='ano', y='quantidade', color='tipo', barmode='group', title="ANUAL")
st.plotly_chart(fig_anual, use_container_width=True)

# --- HISTÓRICO ---
st.divider()
st.subheader("📋 Histórico de Lançamentos")
st.dataframe(df.sort_values('data', ascending=False), use_container_width=True)
