import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(layout="wide", page_title="GAVETA ESPECIAL", page_icon="🗄️")

# LOGIN SIMPLES
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🗄️ GAVETA ESPECIAL - LOGIN")
    email = st.text_input("Email", value="admin@buildstock.com")
    senha = st.text_input("Senha", type="password", value="admin123")
    if st.button("ENTRAR", type="primary"):
        if email == "admin@buildstock.com" and senha == "admin123":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Login: admin@buildstock.com / admin123")
    st.stop()

# BANCO SIMPLES - NÃO DELETA ARQUIVOS
con = sqlite3.connect("gaveta.db", check_same_thread=False)
con.execute("CREATE TABLE IF NOT EXISTS gaveta (id INTEGER PRIMARY KEY, id_original INTEGER, descricao TEXT, local TEXT, marca TEXT, entrada REAL, saida REAL, saldo REAL, unidade TEXT, data_hora TEXT)")
con.execute("CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY, data_hora TEXT, id_original INTEGER, descricao TEXT, local_origem TEXT, local_destino TEXT, tipo TEXT, qtd REAL, total_geral_antes REAL, total_geral_depois REAL, usuario TEXT)")

# SE VAZIO, INSERE DADOS DA FOTO
cur = con.execute("SELECT COUNT(*) FROM gaveta").fetchone()[0]
if cur == 0:
    dados = [
        (16, "BARRAS CATODICAS", "SALA ANEXA", "IBAR", 100, 13, 87, "UNIDADES", "26/05/2026"),
        (16, "BARRAS CATODICAS", "BARRACÃO", "CEMAÇO", 100, 13, 87, "UNIDADES", "26/05/2026"),
        (15, "BLOCOS DE FUNDO", "SALA ANEXA", "ALUBASE", 100, 13, 87, "UNIDADES", "26/05/2026"),
        (15, "BLOCOS DE FUNDO", "BARRACÃO", "ALUBASE", 100, 13, 87, "UNIDADES", "26/05/2026"),
    ]
    for d in dados:
        con.execute("INSERT INTO gaveta (id_original, descricao, local, marca, entrada, saida, saldo, unidade, data_hora) VALUES (?,?,?,?,?,?,?,?,?)", d)
    con.commit()

# DADOS
df = pd.read_sql("SELECT * FROM gaveta", con)
df["saldo"] = df["entrada"] - df["saida"]

total_geral = df["saldo"].sum()
saldo_anexa = df[df.local=="SALA ANEXA"]["saldo"].sum()
saldo_barracao = df[df.local=="BARRACÃO"]["saldo"].sum()

# HEADER
st.markdown(f"### 🗄️ GAVETA ESPECIAL | TOTAL GERAL {total_geral:.0f} = ANEXA {saldo_anexa:.0f} + BARRACÃO {saldo_barracao:.0f} | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# TABELA
st.markdown("#### 📋 Tabela - ID | DESCRIÇÃO | LOCAL | MARCA | ENTRADA | SAIDA | UNIDADE | DATA/HORA")
st.dataframe(df[["id_original","descricao","local","marca","entrada","saida","unidade","data_hora"]], use_container_width=True)

# TOTAIS
c1,c2,c3 = st.columns(3)
with c1: st.metric("SALA ANEXA TOTAL ENTRADA", f"{df[df.local=='SALA ANEXA']['entrada'].sum():.0f}")
with c2: st.metric("BARRACÃO TOTAL ENTRADA", f"{df[df.local=='BARRACÃO']['entrada'].sum():.0f}")
with c3: st.metric("TOTAL GERAL EM ESTOQUE", f"{total_geral:.0f}", f"ANEXA {saldo_anexa:.0f} + BARR {saldo_barracao:.0f}")

# TOTAL POR ITEM
df_total = df.groupby(["id_original","descricao"])["saldo"].sum().reset_index()
df_total["ITEM"] = df_total["descricao"].apply(lambda x: "BARRAS" if "BARRAS" in x else "BLOCOS DE FUNDO")
st.dataframe(df_total[["id_original","ITEM","saldo"]].rename(columns={"id_original":"ID","saldo":"TOTAL EM ESTOQUE"}), use_container_width=True)

st.divider()

# MOVIMENTAÇÃO - TRANSFERÊNCIA
st.markdown("### 🔄 Movimentação - ENTRADA ANEXA → RETIRA BARRACÃO | NOVA ENTRADA BARRACÃO → Atualiza TOTAL GERAL")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📍 SALA ANEXA - ENTRADA = RETIRA BARRACÃO")
    df_anexa = df[df.local=="SALA ANEXA"]
    id_anexa = st.selectbox("Material ANEXA", df_anexa["id"].tolist(), format_func=lambda x: f"ID {df_anexa[df_anexa.id==x].iloc[0]['id_original']} - {df_anexa[df_anexa.id==x].iloc[0]['descricao']} - Saldo {df_anexa[df_anexa.id==x].iloc[0]['saldo']:.0f}", key="id_anexa")
    prod_anexa = df_anexa[df_anexa.id==id_anexa].iloc[0]
    df_bar_match = df[(df.local=="BARRACÃO") & (df.id_original==prod_anexa["id_original"])]
    prod_bar = df_bar_match.iloc[0] if not df_bar_match.empty else None

    qtd_ent = st.number_input("Qtd ENTRADA ANEXA", min_value=0.0, value=10.0, key="qtd_ent_anexa")
    if st.button(f"ENTRADA +{qtd_ent:.0f} ANEXA → RETIRA BARRACÃO", type="primary", use_container_width=True):
        if prod_bar is None or qtd_ent > float(prod_bar["saldo"]):
            st.error(f"BARRACÃO só tem {prod_bar['saldo']:.0f}" if prod_bar is not None else "Sem material")
        else:
            saldo_anexa_antes = float(prod_anexa["saldo"])
            saldo_bar_antes = float(prod_bar["saldo"])
            total_antes = saldo_anexa_antes + saldo_bar_antes
            nova_ent = float(prod_anexa["entrada"]) + qtd_ent
            novo_saldo_anexa = nova_ent - float(prod_anexa["saida"])
            nova_sai_bar = float(prod_bar["saida"]) + qtd_ent
            novo_saldo_bar = float(prod_bar["entrada"]) - nova_sai_bar
            total_depois = novo_saldo_anexa + novo_saldo_bar
            con.execute("UPDATE gaveta SET entrada=?, saldo=? WHERE id=?", (nova_ent, novo_saldo_anexa, int(id_anexa)))
            con.execute("UPDATE gaveta SET saida=?, saldo=? WHERE id=?", (nova_sai_bar, novo_saldo_bar, int(prod_bar["id"])))
            con.execute("INSERT INTO historico (data_hora, id_original, descricao, local_origem, local_destino, tipo, qtd, total_geral_antes, total_geral_depois, usuario) VALUES (?,?,?,?,?,?,?,?,?,?)", (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), int(prod_anexa["id_original"]), prod_anexa["descricao"], "BARRACÃO", "SALA ANEXA", "TRANSFERENCIA", qtd_ent, total_antes, total_depois, "admin"))
            con.commit()
            st.success(f"ID {prod_anexa['id_original']} | ANEXA {saldo_anexa_antes:.0f}→{novo_saldo_anexa:.0f} | BARRACÃO {saldo_bar_antes:.0f}→{novo_saldo_bar:.0f} | TOTAL GERAL {total_antes:.0f}→{total_depois:.0f} | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            st.rerun()

with col2:
    st.markdown("#### 📍 BARRACÃO - NOVA ENTRADA = Atualiza TOTAL GERAL")
    df_bar = df[df.local=="BARRACÃO"]
    id_bar = st.selectbox("Material BARRACÃO", df_bar["id"].tolist(), format_func=lambda x: f"ID {df_bar[df_bar.id==x].iloc[0]['id_original']} - {df_bar[df_bar.id==x].iloc[0]['descricao']} - Saldo {df_bar[df_bar.id==x].iloc[0]['saldo']:.0f}", key="id_bar")
    prod_bar2 = df_bar[df_bar.id==id_bar].iloc[0]
    df_anexa_match = df[(df.local=="SALA ANEXA") & (df.id_original==prod_bar2["id_original"])]
    saldo_anexa_atual = float(df_anexa_match.iloc[0]["saldo"]) if not df_anexa_match.empty else 0
    total_geral_antes = float(prod_bar2["saldo"]) + saldo_anexa_atual

    qtd_nova = st.number_input("Qtd NOVA ENTRADA BARRACÃO", min_value=0.0, value=50.0, key="qtd_nova_bar")
    if st.button(f"NOVA ENTRADA +{qtd_nova:.0f} BARRACÃO", type="primary", use_container_width=True):
        saldo_bar_antes = float(prod_bar2["saldo"])
        nova_ent = float(prod_bar2["entrada"]) + qtd_nova
        novo_saldo = nova_ent - float(prod_bar2["saida"])
        total_depois = saldo_anexa_atual + novo_saldo
        con.execute("UPDATE gaveta SET entrada=?, saldo=? WHERE id=?", (nova_ent, novo_saldo, int(id_bar)))
        con.execute("INSERT INTO historico (data_hora, id_original, descricao, local_origem, local_destino, tipo, qtd, total_geral_antes, total_geral_depois, usuario) VALUES (?,?,?,?,?,?,?,?,?,?)", (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), int(prod_bar2["id_original"]), prod_bar2["descricao"], "FORNECEDOR", "BARRACÃO", "NOVA ENTRADA", qtd_nova, total_geral_antes, total_depois, "admin"))
        con.commit()
        st.success(f"ID {prod_bar2['id_original']} | BARRACÃO {saldo_bar_antes:.0f}→{novo_saldo:.0f} | ANEXA {saldo_anexa_atual:.0f} | TOTAL GERAL {total_geral_antes:.0f}→{total_depois:.0f}")
        st.rerun()

# HISTÓRICO
st.divider()
st.markdown("#### 🔍 Histórico - Informações a cada movimentação")
df_h = pd.read_sql("SELECT * FROM historico ORDER BY id DESC", con)
st.dataframe(df_h, use_container_width=True, height=300)

st.markdown(f"<div style='background:#111827; color:white; padding:8px; border-radius:8px; text-align:center; font-size:10px;'>TOTAL GERAL {total_geral:.0f} = ANEXA {saldo_anexa:.0f} + BARRACÃO {saldo_barracao:.0f} | ENTRADA ANEXA → RETIRA BARRACÃO | NOVA ENTRADA BARRACÃO → Atualiza TOTAL GERAL</div>", unsafe_allow_html=True)
