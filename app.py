import streamlit as st
import pandas as pd
import sqlite3, os
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="BUILD STOCK - APP UNICO FINAL", page_icon="🗄️")

DB = "build_stock_final.db"
for f in os.listdir("."):
    if f.endswith(".db"):
        try: os.remove(f)
        except: pass

def parse_date(s):
    try:
        s=str(s).strip()
        if s in ["00/00/0000","0","","nan","None"] or "XXXX" in s:
            return None
        if "/" in s:
            p=s.split("/")
            if len(p)>=3:
                return date(int(p[2]), int(p[1]), int(p[0]))
        return None
    except: return None

def init_db():
    con = sqlite3.connect(DB)
    con.execute("DROP TABLE IF EXISTS estoque")
    con.execute("DROP TABLE IF EXISTS gaveta_especial")
    con.execute("DROP TABLE IF EXISTS historico")
    con.execute("DROP TABLE IF EXISTS config")
    con.execute("CREATE TABLE config (chave TEXT PRIMARY KEY, valor REAL)")
    con.execute("INSERT INTO config VALUES ('galpao_m2', 1500)")
    con.execute("INSERT INTO config VALUES ('total_matriz', 0)")
    con.execute("CREATE TABLE estoque (produto_id INTEGER PRIMARY KEY AUTOINCREMENT, id_gaveta INTEGER, descricao TEXT, marca TEXT, lote TEXT, validade TEXT, qtd_por_palete REAL, unitario REAL, total_por_palete REAL, unidade TEXT, data_entrada TEXT, area_m2 REAL)")
    con.execute("CREATE TABLE gaveta_especial (id INTEGER PRIMARY KEY AUTOINCREMENT, id_original INTEGER, descricao TEXT, local TEXT, marca TEXT, entrada REAL, saida REAL, saldo REAL, unidade TEXT, data_hora TEXT)")
    con.execute("CREATE TABLE historico (id INTEGER PRIMARY KEY AUTOINCREMENT, data_hora TEXT, produto_id INTEGER, id_original INTEGER, descricao TEXT, local TEXT, local_origem TEXT, local_destino TEXT, marca TEXT, lote TEXT, tipo TEXT, qtd_mov REAL, saldo_antes REAL, saldo_depois REAL, saldo_anexa_antes REAL, saldo_anexa_depois REAL, saldo_barracao_antes REAL, saldo_barracao_depois REAL, total_geral_antes REAL, total_geral_depois REAL, usuario TEXT, gaveta_tipo TEXT, obs TEXT)")
    dados_geral = [
        (4, "ARGAMASSA REFRATARIA", "SHINAGAWA", "LOTE-SHIN-001", "00/00/0000", 1000, 25, 25000, "KILOS", "26/05/2026"),
        (16, "BARRAS CATODICAS", "IBAR", "LOTE-IBAR-1250", "00/00/0000", 1250, 25, 31250, "UNIDADES", "26/05/2026"),
        (15, "BLOCO DE FUNDO", "ALUBASE", "LOTE-ALU-FUNDO", "00/00/0000", 1, 25, 25, "UNIDADES", "26/05/2026"),
        (14, "BLOCO LATERAL", "CARBON", "LOTE-CARB-27", "00/00/0000", 27, 25, 675, "UNIDADES", "26/05/2026"),
        (12, "PASTA FRIA", "ELKEN", "LOTE-ELKEN-76030", "00/00/0000", 1000, 25, 25000, "KILOS", "26/05/2026"),
        (8, "TIJOLO REFRATARIO", "TOGNI", "LOTE-TOG-400", "00/00/0000", 400, 25, 10000, "UNIDADES", "26/05/2026"),
    ]
    for d in dados_geral:
        area = float(d[6])*1.3
        con.execute("INSERT INTO estoque (id_gaveta, descricao, marca, lote, validade, qtd_por_palete, unitario, total_por_palete, unidade, data_entrada, area_m2) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9], area))
    dados_especial = [
        (16, "BARRAS CATODICAS", "SALA ANEXA", "IBAR", 100, 13, 87, "UNIDADES", "26/05/2026"),
        (16, "BARRAS CATODICAS", "BARRACÃO", "CEMAÇO", 100, 13, 87, "UNIDADES", "26/05/2026"),
        (15, "BLOCOS DE FUNDO", "SALA ANEXA", "ALUBASE", 100, 13, 87, "UNIDADES", "26/05/2026"),
        (15, "BLOCOS DE FUNDO", "BARRACÃO", "ALUBASE", 100, 13, 87, "UNIDADES", "26/05/2026"),
    ]
    for d in dados_especial:
        con.execute("INSERT INTO gaveta_especial (id_original, descricao, local, marca, entrada, saida, saldo, unidade, data_hora) VALUES (?,?,?,?,?,?,?,?,?)", d)
    con.commit()
    con.close()

init_db()

USUARIOS = {
    "admin@buildstock.com": {"senha": "admin123", "nome": "Admin", "admin": 1},
    "operador@barracão.com": {"senha": "123", "nome": "Operador Barracão", "admin": 0},
    "operador@buildstock.com": {"senha": "operador123", "nome": "Operador", "admin": 0},
}

if 'logado' not in st.session_state: st.session_state.logado=False
if 'usuario' not in st.session_state: st.session_state.usuario=""
if 'is_admin' not in st.session_state: st.session_state.is_admin=False

#... resto do código igual arquivo baixável acima...

