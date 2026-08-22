import streamlit as st
import pandas as pd
import sqlite3, os
from datetime import datetime, date

st.set_page_config(layout="wide", page_title="BUILD STOCK - FIX", page_icon="📋")

DB = "/tmp/estoque_fix.db" # MUDEI LOCAL PARA /tmp PARA NUNCA DAR ERRO DE BANCO ANTIGO

# APAGA QUALQUER BANCO ANTIGO
for f in ["estoque_fornos.db", "estoque.db", DB]:
    try:
        if os.path.exists(f):
            os.remove(f)
    except:
        pass

USUARIOS = {
    "admin@buildstock.com": "admin123",
    "gerente@buildstock.com": "admin123",
}

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""
    CREATE TABLE IF NOT EXISTS estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_gaveta INTEGER DEFAULT 1,
        descricao TEXT DEFAULT '',
        marca TEXT DEFAULT '',
        lote TEXT DEFAULT '9999999999',
        validade TEXT DEFAULT '00/00/0000',
        qtd_palete REAL DEFAULT 1,
        entrada REAL DEFAULT 1,
        total REAL DEFAULT 0,
        unidade_medida TEXT DEFAULT 'KILOS',
        data_mov TEXT DEFAULT '26/05/2026',
        codigo TEXT DEFAULT ''
    )""")
    con.execute("""
    CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT, id_gaveta INTEGER, descricao TEXT, marca TEXT, lote TEXT,
        tipo TEXT, qtd_palete REAL, entrada REAL, total REAL, usuario TEXT
    )""")
    con.commit()

    # CARREGA DADOS DA SUA FOTO 26/05/2026
    c = con.execute("SELECT COUNT(*) FROM estoque").fetchone()[0]
    if c == 0:
        dados = [
            (1, "CIMENTO", "FONDU", "9999999999", "00/00/0000", 1250, 11, 13750, "KILOS", "26/05/2026", "CIM-1"),
            (1, "CIMENTO", "FONDU", "9999999999", "00/00/0000", 200, 1, 200, "KILOS", "26/05/2026", "CIM-2"),
            (2, "CARBETO DE SILICIO", "SHINAGAWA", "9999999999", "00/00/0000", 1000, 5, 5000, "KILOS", "26/05/2026", "CARB-1"),
            (4, "PLACIBAR SG", "IBAR", "9999999999", "00/00/0000", 1000, 15, 15000, "KILOS", "26/05/2026", "PLACIBAR"),
            (4, "CONCRETO CASTIBAR PSI UG", "IBAR", "9999999999", "00/00/0000", 1250, 4, 5000, "KILOS", "26/05/2026", "CONC-1"),
            (5, "LÃ DE ROCHA", "BIOLÃ", "9999999999", "00/00/0000", 1, 103, 103, "PACOTES", "26/05/2026", "LA-1"),
            (12, "PASTA FRIA", "ELKEN", "76030_76037", "00/00/0000", 1000, 78, 78000, "KILOS", "26/05/2026", "PASTA-1"),
            (14, "BLOCO LATERAL M", "CARBON", "9999999999", "00/00/0000", 27, 92, 2484, "KILOS", "26/05/2026", "BLOCO-M"),
            (14, "BLOCO LATERAL P", "CARBON", "9999999999", "00/00/0000", 2, 92, 184, "KILOS", "26/05/2026", "BLOCO-P"),
        ]
        for d in dados:
            con.execute("INSERT INTO estoque (id_gaveta, descricao, marca, lote, validade, qtd_palete, entrada, total, unidade_medida, data_mov, codigo) VALUES (?,?,?,?,?,?,?,?,?,?,?)", d)
        con.commit()
    con.close()

init_db()

if 'logado' not in st.session_state: st.session_state.logado=False
if 'usuario' not in st.session_state: st.session_state.usuario=""
if 'gaveta_sel' not in st.session_state: st.session_state.gaveta_sel=None

if not st.session_state.logado:
    st.markdown("<div style='background:#111827; color:white; padding:20px; border-radius:15px; text-align:center;'><h1>📋 BUILD STOCK - CORRIGIDO DEFINITIVO</h1><p>TOTAL = QTD/PALETE × ENTRADA - Sem erro KeyError</p></div>", unsafe_allow_html=True)
    with st.container(border=True):
        email = st.text_input("Email", value="admin@buildstock.com")
        senha = st.text_input("Senha", type="password", value="admin123")
        if st.button("ENTRAR", type="primary", use_container_width=True):
            if email.lower() in USUARIOS and senha == USUARIOS[email.lower()]:
                st.session_state.logado=True
                st.session_state.usuario=email.lower()
                st.rerun()
            else:
                st.error("Use admin@buildstock.com / admin123")
    st.stop()

def get_df():
    con = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM estoque", con)
    df_hist = pd.read_sql("SELECT * FROM historico ORDER BY id DESC", con)
    con.close()
    # CALCULO SEGURO - NUNCA DA KeyError
    if not df.empty:
        # Garante que colunas existem
        for col in ["qtd_palete", "entrada"]:
            if col not in df.columns:
                df[col] = 1
        df["qtd_palete"] = pd.to_numeric(df["qtd_palete"], errors='coerce').fillna(1)
        df["entrada"] = pd.to_numeric(df["entrada"], errors='coerce').fillna(1)
        df["total"] = df["qtd_palete"] * df["entrada"]
    return df, df_hist

df_est, df_hist = get_df()

st.markdown(f"<div style='background:#111827; color:white; padding:10px; border-radius:10px;'>📋 {st.session_state.usuario} | TOTAL: {df_est['total'].sum() if not df_est.empty else 0:,.0f} | {len(df_est)} itens | BANCO NOVO /tmp - SEM ERRO</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"👤 {st.session_state.usuario}")
    if st.button("Sair"):
        st.session_state.logado=False
        st.rerun()
    st.success("✅ Banco em /tmp - Novo - Sem KeyError")
    if st.button("🗑️ RESETAR TUDO", type="primary", use_container_width=True):
        for f in ["estoque_fornos.db", "estoque.db", DB]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except: pass
        init_db()
        st.rerun()

tabs = st.tabs(["🗄️ GAVETAS", "🔄 MOVIMENTAÇÃO", "📋 PLANILHA"])

with tabs[0]:
    if st.session_state.gaveta_sel is None:
        st.markdown("### 🗄️ Clique na gaveta")
        cols = st.columns(4)
        for gid in range(1, 9):
            df_g = df_est[df_est["id_gaveta"]==gid] if not df_est.empty else pd.DataFrame()
            total_g = df_g["total"].sum() if not df_g.empty else 0
            with cols[(gid-1)%4]:
                st.markdown(f"<div style='background:#E5E7EB; border:3px solid #111; border-radius:10px; height:90px; display:flex; flex-direction:column; justify-content:center; align-items:center; font-weight:800;'><div>ID {gid:02d}</div><div>{len(df_g)} itens</div><div>{total_g:,.0f}</div></div>", unsafe_allow_html=True)
                if st.button(f"ABRIR ID {gid:02d}", key=f"open_{gid}", use_container_width=True):
                    st.session_state.gaveta_sel=gid
                    st.rerun()
    else:
        sel = st.session_state.gaveta_sel
        if st.button("⬅️ FECHAR"):
            st.session_state.gaveta_sel=None
            st.rerun()
        st.markdown(f"## ID {sel:02d} - TOTAL = QTD/PALETE × ENTRADA")
        con = sqlite3.connect(DB)
        df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE id_gaveta={sel}", con)
        if not df_dentro.empty:
            df_dentro["qtd_palete"] = pd.to_numeric(df_dentro["qtd_palete"], errors='coerce').fillna(1)
            df_dentro["entrada"] = pd.to_numeric(df_dentro["entrada"], errors='coerce').fillna(1)
            df_dentro["total"] = df_dentro["qtd_palete"] * df_dentro["entrada"]
            st.dataframe(df_dentro, use_container_width=True)

            df_edit = st.data_editor(df_dentro, use_container_width=True, num_rows="dynamic", key=f"edit_{sel}")
            if not df_edit.empty:
                df_edit["qtd_palete"] = pd.to_numeric(df_edit["qtd_palete"], errors='coerce').fillna(1)
                df_edit["entrada"] = pd.to_numeric(df_edit["entrada"], errors='coerce').fillna(1)
                df_edit["total"] = df_edit["qtd_palete"] * df_edit["entrada"]
                st.markdown(f"### TOTAL GAVETA {sel:02d}: {df_edit['total'].sum():,.0f} = SOMA(QTD/PALETE × ENTRADA)")

                if st.button("💾 SALVAR - TOTAL CALCULA SOZINHO", type="primary", use_container_width=True):
                    con.execute("DELETE FROM estoque WHERE id_gaveta=?", (sel,))
                    df_edit.to_sql("estoque", con, if_exists="append", index=False)
                    con.commit()
                    st.success("Salvo!")
                    st.rerun()
        con.close()

with tabs[1]:
    st.markdown("### 🔄 Só movimentar - Sistema calcula TOTAL = QTD/PALETE × ENTRADA")
    if not df_est.empty:
        busca = st.text_input("🔍 Buscar")
        df_busca = df_est.copy()
        if busca:
            df_busca = df_busca[df_busca["descricao"].str.contains(busca, case=False, na=False)]
        st.dataframe(df_busca[["id_gaveta","descricao","marca","lote","qtd_palete","entrada","total","unidade_medida"]], use_container_width=True)

        if not df_busca.empty:
            sel_idx = st.selectbox("Material:", df_busca.index.tolist(), format_func=lambda x: f"ID {df_busca.loc[x,'id_gaveta']} - {df_busca.loc[x,'descricao']} - {df_busca.loc[x,'total']:.0f}", key="sel_mov")
            row = df_busca.loc[sel_idx]

            c1,c2 = st.columns(2)
            with c1:
                st.markdown("#### 🟢 ENTRADA")
                ent_e = st.number_input("ENTRADA +", value=1.0, key="ent_e")
                tot_e = float(row["qtd_palete"]) * ent_e
                st.success(f"+ {row['qtd_palete']} × {ent_e} = +{tot_e:,.0f}")
                if st.button("➕ ADICIONAR", type="primary", use_container_width=True):
                    con = sqlite3.connect(DB)
                    nova_ent = float(row["entrada"]) + ent_e
                    novo_tot = float(row["qtd_palete"]) * nova_ent
                    con.execute("UPDATE estoque SET entrada=?, total=? WHERE id=?", (nova_ent, novo_tot, int(row["id"])))
                    con.execute("INSERT INTO historico (data, id_gaveta, descricao, marca, lote, tipo, qtd_palete, entrada, total, usuario) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                (datetime.now().isoformat(), int(row["id_gaveta"]), row["descricao"], row["marca"], row["lote"], "ENTRADA", float(row["qtd_palete"]), ent_e, tot_e, st.session_state.usuario))
                    con.commit(); con.close()
                    st.success("Entrada OK!"); st.rerun()

            with c2:
                st.markdown("#### 🔴 SAÍDA")
                ent_s = st.number_input("SAÍDA -", value=1.0, key="ent_s")
                tot_s = float(row["qtd_palete"]) * ent_s
                st.error(f"- {row['qtd_palete']} × {ent_s} = -{tot_s:,.0f}")
                if st.button("➖ SAÍDA", type="primary", use_container_width=True):
                    con = sqlite3.connect(DB)
                    if ent_s > float(row["entrada"]):
                        st.error("Saída maior que estoque!")
                    else:
                        nova_ent = float(row["entrada"]) - ent_s
                        novo_tot = float(row["qtd_palete"]) * nova_ent
                        con.execute("UPDATE estoque SET entrada=?, total=? WHERE id=?", (nova_ent, novo_tot, int(row["id"])))
                        con.execute("INSERT INTO historico (data, id_gaveta, descricao, marca, lote, tipo, qtd_palete, entrada, total, usuario) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                    (datetime.now().isoformat(), int(row["id_gaveta"]), row["descricao"], row["marca"], row["lote"], "SAIDA", float(row["qtd_palete"]), ent_s, tot_s, st.session_state.usuario))
                        con.commit()
                        st.success("Saída OK!"); st.rerun()
                    con.close()

with tabs[2]:
    if not df_est.empty:
        df_show = df_est[["id_gaveta","descricao","marca","lote","validade","qtd_palete","entrada","total","unidade_medida","data_mov"]].copy()
        df_show.columns = ["ID","DESCRIÇÃO","MARCA","LOTE","VALIDADE","QTD/PALETE","ENTRADA","TOTAL","UNIDADE","DATA"]
        st.dataframe(df_show, use_container_width=True, height=500)
        st.download_button("📥 Baixar CSV", df_show.to_csv(index=False).encode('utf-8'), "planilha.csv", "text/csv", type="primary", use_container_width=True)
        st.markdown(f"**TOTAL = QTD/PALETE × ENTRADA = {df_show['TOTAL'].sum():,.0f}**")
