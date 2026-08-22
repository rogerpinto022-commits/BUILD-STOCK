import streamlit as st
import pandas as pd
import sqlite3, os
from datetime import date, datetime
import plotly.express as px

st.set_page_config(layout="wide", page_title="BUILD STOCK - Automação Planilha", page_icon="📋")

DB = "estoque_fornos.db"

USUARIOS = {
    "admin@buildstock.com": {"nome": "Admin", "senha": "admin123", "admin": 1},
    "gerente@buildstock.com": {"nome": "Gerente", "senha": "admin123", "admin": 1},
}

def init_db():
    con = sqlite3.connect(DB)
    # TABELA EXATA DA SUA FOTO
    con.execute("""
    CREATE TABLE IF NOT EXISTS estoque (
        id_gaveta INTEGER,
        descricao TEXT,
        marca TEXT,
        lote TEXT,
        validade TEXT,
        qtd_palete REAL,
        entrada REAL,
        total REAL,
        unidade_medida TEXT,
        data_mov TEXT,
        fab TEXT,
        codigo TEXT,
        custo_unit REAL DEFAULT 0
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS historico (
        data TEXT, id_gaveta INTEGER, descricao TEXT, marca TEXT, lote TEXT,
        tipo TEXT, qtd_palete REAL, entrada REAL, total REAL, usuario TEXT
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS usuarios (email TEXT UNIQUE, nome TEXT, is_admin INTEGER, ativo INTEGER)""")
    for email, d in USUARIOS.items():
        con.execute("INSERT OR IGNORE INTO usuarios (email, nome, is_admin, ativo) VALUES (?,?,?,1)", (email, d["nome"], d["admin"]))
    con.commit(); con.close()

def carregar_planilha_foto():
    con = sqlite3.connect(DB)
    c = con.execute("SELECT COUNT(*) FROM estoque").fetchone()[0]
    if c>0: con.close(); return

    # DADOS EXATOS DA SUA FOTO - 26/05/2026
    dados_foto = [
        (1, "CIMENTO", "FONDU", "9999999999", "00/00/0000", 1250, 11, 13750, "KILOS", "26/05/2026", "00/00/0000", "CIM-FONDU-1250"),
        (1, "CIMENTO", "FONDU", "9999999999", "00/00/0000", 200, 1, 200, "KILOS", "26/05/2026", "00/00/0000", "CIM-FONDU-200"),
        (2, "CARBETO DE SILICIO", "SHINAGAWA", "9999999999", "00/00/0000", 1000, 5, 5000, "KILOS", "26/05/2026", "00/00/0000", "CARB-SHINA"),
        (3, "ARGAMASSA REFRATARIA", "TECNOFIRE", "9999999999", "00/00/0000", 0, 0, 0, "KILOS", "26/05/2026", "00/00/0000", "ARG-TECNOFIRE"),
        (3, "ARGAMASSA REFRATARIA", "CABOFRAX", "221027970", "07/05/2023", 1, 1, 1, "KILOS", "26/05/2026", "07/05/2023", "ARG-CABO-970"),
        (3, "ARGAMASSA REFRATARIA", "CABOFRAX", "231000196", "02/07/2023", 1, 1, 1, "KILOS", "26/05/2026", "02/07/2023", "ARG-CABO-196"),
        (3, "ARGAMASSA REFRATARIA", "CABOFRAX", "231000194", "02/07/2023", 1, 1, 1, "KILOS", "26/05/2026", "02/07/2023", "ARG-CABO-194"),
        (4, "PLACIBAR SG", "IBAR", "9999999999", "00/00/0000", 1000, 15, 15000, "KILOS", "26/05/2026", "00/00/0000", "PLACIBAR-SG"),
        (4, "CONCRETO CASTIBAR PSI UG", "IBAR", "9999999999", "00/00/0000", 1250, 4, 5000, "KILOS", "26/05/2026", "00/00/0000", "CONC-CAST-UG"),
        (5, "LÃ DE ROCHA", "BIOLÃ", "9999999999", "00/00/0000", 1, 103, 103, "PACOTES", "26/05/2026", "00/00/0000", "LA-ROCHA-BIOLA"),
        (6, "TIJOLO SEMI ISOLANTE SUPRA", "SKAMOL ALUPORO", "9999999999", "00/00/0000", 912, 10, 9120, "UNIDADES", "26/05/2026", "00/00/0000", "TIJ-SUPRA-SKAMOL"),
        (6, "TIJOLO SEMI ISOLANTE SUPRA", "MOSCONI AB70", "9999999999", "00/00/0000", 1020, 31, 31620, "UNIDADES", "26/05/2026", "00/00/0000", "TIJ-SUPRA-MOSCONI"),
        (7, "TIJOLO ISOLANTE", "SKAMOL ALUPORO", "9999999999", "00/00/0000", 912, 141, 128592, "UNIDADES", "26/05/2026", "00/00/0000", "TIJ-ISOL-SKAMOL-912"),
        (7, "TIJOLO ISOLANTE", "MOSCONI AB 55", "9999999999", "00/00/0000", 680, 256, 174080, "UNIDADES", "26/05/2026", "00/00/0000", "TIJ-ISOL-MOSCONI-680"),
        (8, "TIJOLO REFRATARIO", "IBAR SA ALUM", "9999999999", "00/00/0000", 512, 313, 160256, "KILOS", "26/05/2026", "00/00/0000", "TIJ-REFR-IBAR-512"),
        (8, "TIJOLO REFRATARIO", "TOGNI", "9999999999", "00/00/0000", 400, 1, 400, "KILOS", "26/05/2026", "00/00/0000", "TIJ-REFR-TOGNI"),
        (8, "TIJOLO REFRATARIO", "MAGNESITA", "9999999999", "00/00/0000", 310, 37, 11470, "KILOS", "26/05/2026", "00/00/0000", "TIJ-REFR-MAG-310"),
        (8, "TIJOLO REFRATARIO", "ADVANCAL", "9999999999", "00/00/0000", 300, 22, 6600, "KILOS", "26/05/2026", "00/00/0000", "TIJ-REFR-ADV-300"),
        (12, "PASTA FRIA", "ELKEN", "75074_75075", "00/00/0000", 1000, 4, 4000, "KILOS", "26/05/2026", "00/00/0000", "PASTA-ELKEN-75074"),
        (12, "PASTA FRIA", "ELKEN", "74630RM74631", "00/00/0000", 1000, 2, 2000, "KILOS", "26/05/2026", "00/00/0000", "PASTA-ELKEN-74630"),
        (12, "PASTA FRIA", "ELKEN", "75949RM75952", "00/00/0000", 1000, 8, 8000, "KILOS", "26/05/2026", "00/00/0000", "PASTA-ELKEN-75949"),
        (12, "PASTA FRIA", "ELKEN", "76007RM76010", "00/00/0000", 1000, 12, 12000, "KILOS", "26/05/2026", "00/00/0000", "PASTA-ELKEN-76007"),
        (12, "PASTA FRIA", "ELKEN", "76030_76037/76062_76067", "00/00/0000", 1000, 78, 78000, "KILOS", "26/05/2026", "00/00/0000", "PASTA-ELKEN-76030"),
        (14, "BLOCO LATERAL M", "CARBON", "9999999999", "00/00/0000", 27, 92, 2484, "KILOS", "26/05/2026", "00/00/0000", "BLOCO-M-CARBON-27"),
        (14, "BLOCO LATERAL P", "CARBON", "9999999999", "00/00/0000", 2, 92, 184, "KILOS", "26/05/2026", "00/00/0000", "BLOCO-P-CARBON-2"),
        (14, "BLOCO LATERAL O", "CARBON", "9999999999", "00/00/0000", 2, 92, 184, "KILOS", "26/05/2026", "00/00/0000", "BLOCO-O-CARBON-2"),
        (14, "BLOCO LATERAL O'", "CARBON", "9999999999", "00/00/0000", 4, 92, 368, "KILOS", "26/05/2026", "00/00/0000", "BLOCO-O'-CARBON-4"),
        (15, "BLOCO DE FUNDO", "TOKAY", "25/05/2026", "00/00/0000", 1, 2, 2, "UNIDADES", "26/05/2026", "25/05/2026", "BLOCO-FUNDO-TOKAY"),
        (15, "BLOCO DE FUNDO", "SEC", "25/05/2026", "00/00/0000", 1, 1, 1, "UNIDADES", "26/05/2026", "25/05/2026", "BLOCO-FUNDO-SEC"),
        (15, "BLOCO DE FUNDO", "ENERGOPROM", "25/05/2026", "00/00/0000", 1, 1, 1, "UNIDADES", "26/05/2026", "25/05/2026", "BLOCO-FUNDO-ENERGO"),
        (15, "GRD- SALA ANEXA", "ENGUSADOS", "9999999999", "00/00/0000", 1, 113, 113, "KILOS", "26/05/2026", "00/00/0000", "GRD-ENGUSADOS"),
        (16, "BARRAS CATODICAS", "CEMAÇO", "9999999999", "00/00/0000", 1, 587, 587, "KILOS", "26/05/2026", "00/00/0000", "BARRA-CAT-CEMACO"),
        (16, "BARRAS CATODICAS", "ALUBASE", "9999999999", "00/00/0000", 1, 9, 9, "KILOS", "26/05/2026", "00/00/0000", "BARRA-CAT-ALUBASE"),
        (17, "BLOCOS DE FUNDO", "SEC", "9999999999", "00/00/0000", 2, 253, 506, "KILOS", "26/05/2026", "00/00/0000", "BLOCO-FUNDO-SEC-2"),
        (7, "TIJOLO ISOLANTE 57", "SKAMOL ALUPORO", "XXXXXXX", "00/00/0000", 1824, 3, 5472, "KILOS", "26/05/2026", "00/00/0000", "TIJ-57-SKAMOL-1824"),
        (7, "TIJOLO ISOLANTE 90", "SKAMOL ALUPORO", "XXXXXXX", "00/00/0000", 1140, 8, 9120, "KILOS", "26/05/2026", "00/00/0000", "TIJ-90-SKAMOL-1140"),
        (7, "TIJOLO ISOLANTE 57", "SKAMOL ALUPORO", "XXXXXXX", "00/00/0000", 760, 1, 760, "KILOS", "26/05/2026", "00/00/0000", "TIJ-57-SKAMOL-760"),
        (7, "TIJOLO ISOLANTE 57", "MOSCONI", "XXXXXXX", "00/00/0000", 1360, 10, 13600, "KILOS", "26/05/2026", "00/00/0000", "TIJ-57-MOSCONI-1360"),
        (7, "TIJOLO ISOLANTE 90", "MOSCONI", "XXXXXXX", "00/00/0000", 850, 17, 14450, "KILOS", "26/05/2026", "00/00/0000", "TIJ-90-MOSCONI-850"),
        (8, "TIJOLO REFRATARIO 57", "IBAR", "XXXXXXX", "00/00/0000", 1008, 7, 7056, "KILOS", "26/05/2026", "00/00/0000", "TIJ-REFR-57-IBAR-1008"),
        (8, "TIJOLO REFRATARIO 57", "BONY", "XXXXXXX", "00/00/0000", 864, 10, 8640, "KILOS", "26/05/2026", "00/00/0000", "TIJ-REFR-57-BONY-864"),
    ]
    for d in dados_foto:
        con.execute("INSERT INTO estoque (id_gaveta, descricao, marca, lote, validade, qtd_palete, entrada, total, unidade_medida, data_mov, fab, codigo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", d)
    con.commit(); con.close()

if not os.path.exists(DB):
    init_db(); carregar_planilha_foto()
else:
    try: init_db(); carregar_planilha_foto()
    except:
        if os.path.exists(DB): os.remove(DB)
        init_db(); carregar_planilha_foto()

if 'logado' not in st.session_state: st.session_state.logado=False
if 'usuario' not in st.session_state: st.session_state.usuario=""
if 'gaveta_sel' not in st.session_state: st.session_state.gaveta_sel=None

def check_login():
    if not st.session_state.logado:
        st.markdown("<div style='background: linear-gradient(90deg, #1F2937, #3B82F6); padding:25px; border-radius:15px; color:white; text-align:center;'><h1>📋 BUILD STOCK - AUTOMAÇÃO PLANILHA</h1><p>Sua tabela automatizada - TOTAL = QTD/PALETE × ENTRADA - Só faça movimentação</p></div>", unsafe_allow_html=True)
        with st.container(border=True):
            email = st.text_input("Email", value="admin@buildstock.com")
            senha = st.text_input("Senha", type="password", value="admin123")
            if st.button("ENTRAR", type="primary", use_container_width=True):
                if email.lower() in USUARIOS and senha == USUARIOS[email.lower()]["senha"]:
                    st.session_state.logado=True
                    st.session_state.usuario=email.lower()
                    st.rerun()
                else: st.error("admin@buildstock.com / admin123")
            if st.button("RESETAR E CARREGAR PLANILHA DA FOTO 26/05/2026", use_container_width=True):
                if os.path.exists(DB): os.remove(DB)
                init_db(); carregar_planilha_foto()
                st.success("Planilha da foto carregada!")
        st.stop()
check_login()

st.markdown("""
<style>
.formula { background: linear-gradient(90deg, #059669, #10B981); color:white; padding:12px; border-radius:10px; text-align:center; font-weight:900; font-size:18px; }
.campo { background:#FEF3C7; border:2px solid #F59E0B; border-radius:8px; padding:8px; }
.tabela-auto { background:white; border-radius:12px; padding:15px; box-shadow:0 5px 15px rgba(0,0,0,0.1); border-top:6px solid #3B82F6; }
</style>
""", unsafe_allow_html=True)

def get_df():
    con = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM estoque", con)
    df_hist = pd.read_sql("SELECT * FROM historico ORDER BY data DESC", con)
    con.close()
    if not df.empty:
        df["total"] = df["qtd_palete"] * df["entrada"]
        df["formula"] = df["qtd_palete"].astype(str) + " × " + df["entrada"].astype(str) + " = " + df["total"].astype(str) + " " + df["unidade_medida"]
    return df, df_hist

df_est, df_hist = get_df()

# HEADER
st.markdown(f"<div style='background:#111827; color:white; padding:10px 15px; border-radius:10px; display:flex; justify-content:space-between;'><span>📋 {st.session_state.usuario} | TOTAL: {df_est['total'].sum() if not df_est.empty else 0:,.0f} | {len(df_est)} itens | 26/05/2026</span><span>GAVETAS 20</span></div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"👤 {st.session_state.usuario}")
    if st.button("Sair", use_container_width=True):
        st.session_state.logado=False
        st.rerun()
    if st.button("RESET PLANILHA FOTO", type="primary", use_container_width=True):
        if os.path.exists(DB): os.remove(DB)
        init_db(); carregar_planilha_foto()
        st.session_state.gaveta_sel=None
        st.rerun()
    st.divider()
    st.metric("Total Geral", f"{df_est['total'].sum() if not df_est.empty else 0:,.0f}")
    st.metric("Itens", len(df_est))

tabs = st.tabs(["🗄️ GAVETAS - Tabela Automática", "🔄 MOVIMENTAÇÃO RÁPIDA - Só movimentar", "📊 DASHBOARD", "📋 PLANILHA COMPLETA"])

with tabs[0]:
    if st.session_state.gaveta_sel is None:
        st.markdown("### 🗄️ Clique na gaveta - Abre tabela exata da sua foto com cálculo automático")
        st.info("Fórmula da sua planilha: TOTAL = QTD/PALETE × ENTRADA - Sistema calcula sozinho")

        for linha in range(0, 20, 4):
            cols = st.columns(4)
            for idx in range(4):
                gid = linha+idx+1
                if gid>20: continue
                df_g = df_est[df_est["id_gaveta"]==gid] if not df_est.empty else pd.DataFrame()
                total_g = df_g["total"].sum() if not df_g.empty else 0
                with cols[idx]:
                    st.markdown(f"<div style='background: linear-gradient(180deg, #E5E7EB, #9CA3AF); border:3px solid #374151; border-radius:10px; height:100px; display:flex; flex-direction:column; justify-content:center; align-items:center; font-weight:800;'><div style='background:white; padding:2px 8px; border-radius:4px; font-size:11px;'>ID {gid:02d}</div><div style='font-size:11px;'>{len(df_g)} itens</div><div style='font-size:12px;'>{total_g:,.0f}</div></div>", unsafe_allow_html=True)
                    if st.button(f"ABRIR ID {gid:02d}", key=f"open_{gid}", use_container_width=True):
                        st.session_state.gaveta_sel=gid
                        st.rerun()

        if not df_est.empty:
            st.divider()
            df_gav = df_est.groupby("id_gaveta")["total"].sum().reset_index()
            st.plotly_chart(px.bar(df_gav, x="id_gaveta", y="total", title="Total por Gaveta ID - QTD/PALETE × ENTRADA", text="total"), use_container_width=True)

    else:
        sel = st.session_state.gaveta_sel
        if st.button("⬅️ FECHAR GAVETA", use_container_width=True):
            st.session_state.gaveta_sel=None
            st.rerun()

        st.markdown(f"<div class='tabela-auto'><h2>📋 ID {sel:02d} - Tabela Automática - TOTAL = QTD/PALETE × ENTRADA</h2><p>Só edite QTD/PALETE e ENTRADA - TOTAL calcula sozinho</p></div>", unsafe_allow_html=True)

        con = sqlite3.connect(DB)
        try: df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE id_gaveta={sel} ORDER BY descricao", con)
        except: df_dentro = pd.DataFrame()

        if not df_dentro.empty:
            df_dentro["total"] = df_dentro["qtd_palete"] * df_dentro["entrada"]
            st.markdown(f"### ID {sel:02d} - {len(df_dentro)} materiais - Total: {df_dentro['total'].sum():,.0f} - Fórmula: QTD/PALETE × ENTRADA")

            # TABELA EXATA DA FOTO COM MULTIPLICAÇÃO AUTOMÁTICA
            df_edit = st.data_editor(
                df_dentro,
                use_container_width=True,
                height=400,
                num_rows="dynamic",
                key=f"edit_{sel}",
                column_config={
                    "id_gaveta": st.column_config.NumberColumn("ID", disabled=False),
                    "descricao": st.column_config.TextColumn("DESCRIÇÃO"),
                    "marca": st.column_config.TextColumn("MARCA"),
                    "lote": st.column_config.TextColumn("LOTE"),
                    "validade": st.column_config.TextColumn("VALIDADE"),
                    "qtd_palete": st.column_config.NumberColumn("QTD/PALETE *", format="%.2f", help="Quantidade por palete - Ex: 1000, 1250, 27, 2"),
                    "entrada": st.column_config.NumberColumn("ENTRADA *", format="%.2f", help="Quantidade entrada - Ex: 11, 1, 5"),
                    "total": st.column_config.NumberColumn("TOTAL = QTD/PALETE × ENTRADA", disabled=True, format="%.0f", help="Calculado automaticamente"),
                    "unidade_medida": st.column_config.SelectboxColumn("UNIDADE DE MEDIDA", options=["KILOS", "UNIDADES", "PACOTES", "ROLOS", "PALETES"]),
                    "data_mov": st.column_config.TextColumn("DATA"),
                }
            )

            # Recalcula
            df_edit["total"] = df_edit["qtd_palete"] * df_edit["entrada"]
            total_gav = df_edit["total"].sum()
            st.markdown(f"<div class='formula'>TOTAL GAVETA {sel:02d} = SOMA(QTD/PALETE × ENTRADA) = {total_gav:,.0f}</div>", unsafe_allow_html=True)

            col1,col2 = st.columns(2)
            if col1.button("💾 SALVAR - Sistema atualiza TOTAL automaticamente", type="primary", use_container_width=True, key=f"save_{sel}"):
                try:
                    con.execute("DELETE FROM estoque WHERE id_gaveta=?", (sel,))
                    df_edit.to_sql("estoque", con, if_exists="append", index=False)
                    con.commit()
                    st.success(f"✅ Gaveta {sel:02d} salva! Total: {total_gav:,.0f}")
                    st.rerun()
                except Exception as e: st.error(str(e))

            if col2.button("🗑️ Limpar Gaveta", use_container_width=True, key=f"clear_{sel}"):
                con.execute("DELETE FROM estoque WHERE id_gaveta=?", (sel,))
                con.commit()
                st.success("Limpa!")
                st.rerun()
        else:
            st.info(f"ID {sel:02d} vazia - Adicione abaixo")

        # Adicionar com multiplicação
        with st.container(border=True):
            st.markdown(f"#### ➕ Adicionar material no ID {sel:02d} - Preencha QTD/PALETE e ENTRADA")
            c1,c2,c3,c4 = st.columns(4)
            desc_n = c1.text_input("DESCRIÇÃO *", key=f"desc_n_{sel}")
            marca_n = c2.text_input("MARCA *", key=f"marca_n_{sel}")
            lote_n = c3.text_input("LOTE *", value="9999999999", key=f"lote_n_{sel}")
            validade_n = c4.text_input("VALIDADE", value="00/00/0000", key=f"val_n_{sel}")

            c5,c6,c7,c8 = st.columns(4)
            qtd_pal_n = c5.number_input("QTD/PALETE *", value=1000.0, key=f"qtd_pal_n_{sel}", help="Ex: 1000, 1250, 27")
            entrada_n = c6.number_input("ENTRADA *", value=1.0, key=f"entrada_n_{sel}", help="Ex: 11, 5, 92")
            unidade_n = c7.selectbox("UNIDADE DE MEDIDA", ["KILOS", "UNIDADES", "PACOTES", "ROLOS"], key=f"uni_n_{sel}")
            data_n = c8.text_input("DATA", value="26/05/2026", key=f"data_n_{sel}")

            total_preview = qtd_pal_n * entrada_n
            st.markdown(f"<div class='formula'>{qtd_pal_n} (QTD/PALETE) × {entrada_n} (ENTRADA) = {total_preview:,.0f} {unidade_n}</div>", unsafe_allow_html=True)

            if st.button(f"💾 SALVAR {total_preview:,.0f} {unidade_n} NO ID {sel:02d}", type="primary", use_container_width=True, key=f"add_n_{sel}"):
                try:
                    con.execute("INSERT INTO estoque (id_gaveta, descricao, marca, lote, validade, qtd_palete, entrada, total, unidade_medida, data_mov, fab, codigo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                                (sel, desc_n, marca_n, lote_n, validade_n, qtd_pal_n, entrada_n, total_preview, unidade_n, data_n, validade_n, f"{desc_n[:3]}-{marca_n[:3]}-{qtd_pal_n:.0f}"))
                    con.execute("INSERT INTO historico (data, id_gaveta, descricao, marca, lote, tipo, qtd_palete, entrada, total, usuario) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                (datetime.now().isoformat(), sel, desc_n, marca_n, lote_n, "ENTRADA", qtd_pal_n, entrada_n, total_preview, st.session_state.usuario))
                    con.commit()
                    st.success(f"Salvo! {qtd_pal_n} × {entrada_n} = {total_preview:,.0f}")
                    st.rerun()
                except Exception as e: st.error(str(e))
        con.close()
        if st.button("⬅️ FECHAR", use_container_width=True, key=f"close2_{sel}"):
            st.session_state.gaveta_sel=None
            st.rerun()

with tabs[1]:
    st.markdown("### 🔄 MOVIMENTAÇÃO RÁPIDA - Você só movimenta, sistema atualiza")
    st.info("Escolha o material, digite ENTRADA ou SAÍDA - TOTAL = QTD/PALETE × ENTRADA calcula sozinho")

    if not df_est.empty:
        # Busca material
        busca = st.text_input("🔍 Buscar material (DESCRIÇÃO, MARCA, LOTE)", key="busca_mov")
        df_busca = df_est.copy()
        if busca:
            df_busca = df_busca[df_busca.apply(lambda r: busca.lower() in str(r["descricao"]).lower() or busca.lower() in str(r["marca"]).lower() or busca.lower() in str(r["lote"]).lower(), axis=1)]

        if not df_busca.empty:
            st.dataframe(df_busca[["id_gaveta","descricao","marca","lote","qtd_palete","entrada","total","unidade_medida"]], use_container_width=True, height=250)

            sel_idx = st.selectbox("Selecione material para movimentar:", df_busca.index.tolist(), format_func=lambda x: f"ID {df_busca.loc[x,'id_gaveta']} - {df_busca.loc[x,'descricao']} - {df_busca.loc[x,'marca']} - Lote {df_busca.loc[x,'lote']} - TOTAL {df_busca.loc[x,'total']:.0f}", key="sel_mov")

            if sel_idx is not None:
                row = df_busca.loc[sel_idx]
                st.markdown(f"<div class='tabela-auto'><b>Material:</b> {row['descricao']} | <b>Marca:</b> {row['marca']} | <b>Lote:</b> {row['lote']} | <b>Atual:</b> {row['qtd_palete']} × {row['entrada']} = {row['total']:.0f} {row['unidade_medida']}</div>", unsafe_allow_html=True)

                c1,c2,c3 = st.columns(3)
                with c1:
                    st.markdown("#### 🟢 ENTRADA")
                    qtd_pal_e = st.number_input("QTD/PALETE", value=float(row["qtd_palete"]), key="mov_qtd_pal_e")
                    entrada_e = st.number_input("ENTRADA (+)", value=1.0, key="mov_entrada_e")
                    total_e = qtd_pal_e * entrada_e
                    st.markdown(f"<div class='formula'>+ {qtd_pal_e} × {entrada_e} = +{total_e:,.0f}</div>", unsafe_allow_html=True)
                    if st.button("➕ ADICIONAR ENTRADA", type="primary", use_container_width=True, key="btn_entrada"):
                        try:
                            con = sqlite3.connect(DB)
                            # Atualiza entrada
                            nova_entrada = row["entrada"] + entrada_e
                            novo_total = row["qtd_palete"] * nova_entrada
                            con.execute("UPDATE estoque SET entrada=?, total=?, qtd_palete=? WHERE rowid=?", (nova_entrada, novo_total, qtd_pal_e, sel_idx+1))
                            con.execute("INSERT INTO historico (data, id_gaveta, descricao, marca, lote, tipo, qtd_palete, entrada, total, usuario) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                        (datetime.now().isoformat(), int(row["id_gaveta"]), row["descricao"], row["marca"], row["lote"], "ENTRADA", qtd_pal_e, entrada_e, total_e, st.session_state.usuario))
                            con.commit(); con.close()
                            st.success(f"Entrada +{total_e:,.0f} | Novo total: {novo_total:,.0f}")
                            st.rerun()
                        except Exception as e: st.error(str(e))

                with c2:
                    st.markdown("#### 🔴 SAÍDA")
                    entrada_s = st.number_input("SAÍDA (-)", value=1.0, min_value=0.0, key="mov_entrada_s")
                    total_s = row["qtd_palete"] * entrada_s
                    st.markdown(f"<div class='formula' style='background: linear-gradient(90deg, #DC2626, #EF4444);'>- {row['qtd_palete']} × {entrada_s} = -{total_s:,.0f}</div>", unsafe_allow_html=True)
                    if st.button("➖ REGISTRAR SAÍDA", type="primary", use_container_width=True, key="btn_saida"):
                        try:
                            con = sqlite3.connect(DB)
                            if entrada_s > row["entrada"]:
                                st.error(f"Saída {entrada_s} maior que entrada {row['entrada']}! Não pode.")
                            else:
                                nova_entrada = row["entrada"] - entrada_s
                                novo_total = row["qtd_palete"] * nova_entrada
                                con.execute("UPDATE estoque SET entrada=?, total=? WHERE rowid=?", (nova_entrada, novo_total, sel_idx+1))
                                con.execute("INSERT INTO historico (data, id_gaveta, descricao, marca, lote, tipo, qtd_palete, entrada, total, usuario) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                            (datetime.now().isoformat(), int(row["id_gaveta"]), row["descricao"], row["marca"], row["lote"], "SAIDA", row["qtd_palete"], entrada_s, total_s, st.session_state.usuario))
                                con.commit()
                                st.success(f"Saída -{total_s:,.0f} | Novo total: {novo_total:,.0f}")
                                st.rerun()
                            con.close()
                        except Exception as e: st.error(str(e))

                with c3:
                    st.markdown("#### 📊 Saldo Atualizado")
                    st.metric("QTD/PALETE", f"{row['qtd_palete']:.0f}")
                    st.metric("ENTRADA Atual", f"{row['entrada']:.0f}")
                    st.metric("TOTAL Atual", f"{row['total']:,.0f} {row['unidade_medida']}")

with tabs[2]:
    if not df_est.empty:
        c1,c2 = st.columns(2)
        with c1:
            df_gav = df_est.groupby("id_gaveta")["total"].sum().reset_index()
            st.plotly_chart(px.bar(df_gav, x="id_gaveta", y="total", title="Total por ID Gaveta - QTD/PALETE × ENTRADA", text="total"), use_container_width=True)
        with c2:
            df_marca = df_est.groupby("marca")["total"].sum().reset_index().sort_values("total", ascending=False).head(10)
            st.plotly_chart(px.pie(df_marca, values="total", names="marca", title="Top 10 Marcas por Total"), use_container_width=True)

        st.plotly_chart(px.treemap(df_est, path=["id_gaveta","descricao"], values="total", title="Treemap - Ocupação por Gaveta e Descrição"), use_container_width=True)

        if not df_hist.empty:
            st.dataframe(df_hist.head(50), use_container_width=True)
            df_hist["data"] = pd.to_datetime(df_hist["data"])
            st.plotly_chart(px.bar(df_hist, x="data", y="total", color="tipo", title="Histórico Entrada x Saída"), use_container_width=True)

with tabs[3]:
    st.markdown("### 📋 Planilha Completa - Exata da sua foto - Automatizada")
    if not df_est.empty:
        df_show = df_est.copy()
        df_show = df_show[["id_gaveta","descricao","marca","lote","validade","qtd_palete","entrada","total","unidade_medida","data_mov"]]
        df_show.columns = ["ID","DESCRIÇÃO","MARCA","LOTE","VALIDADE","QTD/PALETE","ENTRADA","TOTAL","UNIDADE DE MEDIDA","DATA"]

        st.dataframe(df_show, use_container_width=True, height=600)

        st.download_button("📥 Baixar Planilha Automatizada (CSV)", df_show.to_csv(index=False).encode('utf-8'), f"planilha_automatizada_{date.today()}.csv", "text/csv", type="primary", use_container_width=True)

        st.markdown(f"**Resumo:** {len(df_show)} linhas | Total Geral: {df_show['TOTAL'].sum():,.0f} | Fórmula: TOTAL = QTD/PALETE × ENTRADA")
    
