import streamlit as st
import pandas as pd
import sqlite3, os
from datetime import datetime, date, timedelta
import plotly.express as px

st.set_page_config(layout="wide", page_title="BUILD STOCK - Completo", page_icon="📊")

DB = "/tmp/estoque_final.db"

# LIMPA QUALQUER BANCO ANTIGO QUE DAVA KeyError
for old in ["estoque_fornos.db", "estoque.db", "/tmp/estoque_fix.db", "/tmp/estoque_final.db"]:
    try:
        if os.path.exists(old):
            os.remove(old)
    except:
        pass

USUARIOS = {"admin@buildstock.com": "admin123", "gerente@buildstock.com": "admin123"}

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""
    CREATE TABLE estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_gaveta INTEGER DEFAULT 1,
        descricao TEXT DEFAULT '',
        marca TEXT DEFAULT '',
        lote TEXT DEFAULT '',
        validade TEXT DEFAULT '00/00/0000',
        fab TEXT DEFAULT '00/00/0000',
        qtd_palete REAL DEFAULT 1,
        entrada REAL DEFAULT 1,
        total REAL DEFAULT 0,
        unidade_medida TEXT DEFAULT 'KILOS',
        data_mov TEXT DEFAULT '26/05/2026',
        codigo TEXT DEFAULT ''
    )""")
    con.execute("""
    CREATE TABLE historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT, id_gaveta INTEGER, descricao TEXT, marca TEXT, lote TEXT,
        tipo TEXT, qtd_palete REAL, entrada REAL, total REAL, usuario TEXT
    )""")
    con.commit()

    c = con.execute("SELECT COUNT(*) FROM estoque").fetchone()[0]
    if c == 0:
        dados = [
            (1, "CIMENTO", "FONDU", "9999999999", "00/00/0000", "00/00/0000", 1250, 11, 13750, "KILOS", "26/05/2026", "CIM-1"),
            (2, "CARBETO DE SILICIO", "SHINAGAWA", "9999999999", "00/00/0000", "00/00/0000", 1000, 5, 5000, "KILOS", "26/05/2026", "CARB-1"),
            (3, "ARGAMASSA", "TECNOFIRE", "221027970", "07/05/2023", "07/05/2023", 1, 1, 1, "KILOS", "26/05/2026", "ARG-1"),
            (4, "PLACIBAR SG", "IBAR", "9999999999", "00/00/0000", "00/00/0000", 1000, 15, 15000, "KILOS", "26/05/2026", "PLACIBAR"),
            (4, "CONCRETO CASTIBAR", "IBAR", "9999999999", "00/00/0000", "00/00/0000", 1250, 4, 5000, "KILOS", "26/05/2026", "CONC-1"),
            (5, "LÃ DE ROCHA", "BIOLÃ", "9999999999", "00/00/0000", "00/00/0000", 1, 103, 103, "PACOTES", "26/05/2026", "LA-1"),
            (12, "PASTA FRIA", "ELKEN", "76030_76037", "20/01/2027", "20/07/2026", 1000, 78, 78000, "KILOS", "26/05/2026", "PASTA-1"),
            (13, "PASTA FRIA CARBON", "CARBON", "772/773", "23/01/2027", "23/07/2026", 1000, 40, 40000, "KILOS", "20/08/2026", "PASTA-CARBON"),
            (14, "BLOCO LATERAL M", "CARBON", "CARBON-46", "20/08/2027", "20/08/2026", 27, 92, 2484, "UNIDADES", "20/08/2026", "BLOCO-M"),
            (7, "TIJOLO ISOLANTE", "SKAMOL", "1140", "21/08/2027", "21/08/2026", 1173, 3, 3519, "UNIDADES", "21/08/2026", "TIJ-1140"),
            (15, "TIJOLO 15A", "MOSCONI", "15A", "20/08/2027", "20/08/2026", 1, 94, 94, "UNIDADES", "20/08/2026", "TIJ-15A"),
        ]
        for d in dados:
            con.execute("INSERT INTO estoque (id_gaveta, descricao, marca, lote, validade, fab, qtd_palete, entrada, total, unidade_medida, data_mov, codigo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", d)
        con.commit()
    con.close()

init_db()

if 'logado' not in st.session_state: st.session_state.logado=False
if 'usuario' not in st.session_state: st.session_state.usuario=""
if 'gaveta_sel' not in st.session_state: st.session_state.gaveta_sel=None

if not st.session_state.logado:
    st.markdown("<div style='background: linear-gradient(90deg, #111827, #3B82F6); padding:25px; border-radius:15px; color:white; text-align:center;'><h1>📊 BUILD STOCK - COMPLETO</h1><p>EDITAR + EXCLUIR + DASHBOARD Entradas Saídas Saldo Vencidos A Vencer</p></div>", unsafe_allow_html=True)
    with st.container(border=True):
        email = st.text_input("Email", value="admin@buildstock.com")
        senha = st.text_input("Senha", type="password", value="admin123")
        if st.button("ENTRAR", type="primary", use_container_width=True):
            if email.lower() in USUARIOS and senha == USUARIOS[email.lower()]:
                st.session_state.logado=True
                st.session_state.usuario=email.lower()
                st.rerun()
            else:
                st.error("admin@buildstock.com / admin123")
    st.stop()

def parse_validade(v):
    try:
        if not v or v == "00/00/0000" or v == "9999999999" or "XXXX" in str(v):
            return None
        if "/" in str(v):
            d,m,y = str(v).split("/")[:3]
            return date(int(y), int(m), int(d))
        else:
            return datetime.fromisoformat(str(v)).date()
    except:
        return None

def get_df():
    con = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM estoque", con)
    df_hist = pd.read_sql("SELECT * FROM historico ORDER BY id DESC", con)
    con.close()
    if not df.empty:
        df["qtd_palete"] = pd.to_numeric(df["qtd_palete"], errors='coerce').fillna(1)
        df["entrada"] = pd.to_numeric(df["entrada"], errors='coerce').fillna(1)
        df["total"] = df["qtd_palete"] * df["entrada"]
        df["validade_date"] = df["validade"].apply(parse_validade)
        hoje = date.today()
        def status_venc(row):
            vd = row["validade_date"]
            if vd is None:
                return "⚪ SEM VALIDADE"
            diff = (vd - hoje).days
            if diff < 0: return "🔴 VENCIDO"
            elif diff <= 30: return "🟡 VENCE 30 DIAS"
            elif diff <= 90: return "🟠 VENCE 90 DIAS"
            else: return "🟢 OK"
        df["status_validade"] = df.apply(status_venc, axis=1)
        df["dias_vencer"] = df["validade_date"].apply(lambda x: (x - hoje).days if x else 9999)
    return df, df_hist

df_est, df_hist = get_df()

# KPIs HEADER
total_saldo = df_est["total"].sum() if not df_est.empty else 0
total_entradas = df_hist[df_hist["tipo"]=="ENTRADA"]["total"].sum() if not df_hist.empty else 0
total_saidas = df_hist[df_hist["tipo"]=="SAIDA"]["total"].sum() if not df_hist.empty else 0
vencidos = len(df_est[df_est["status_validade"]=="🔴 VENCIDO"]) if not df_est.empty else 0
a_vencer_30 = len(df_est[df_est["status_validade"]=="🟡 VENCE 30 DIAS"]) if not df_est.empty else 0
a_vencer_90 = len(df_est[df_est["status_validade"]=="🟠 VENCE 90 DIAS"]) if not df_est.empty else 0

st.markdown(f"""
<div style='background:#111827; color:white; padding:12px 15px; border-radius:10px; display:flex; justify-content:space-between;'>
<span>📊 {st.session_state.usuario} | SALDO: {total_saldo:,.0f} | ENTRADAS: {total_entradas:,.0f} | SAÍDAS: {total_saidas:,.0f}</span>
<span>🔴 VENCIDOS: {vencidos} | 🟡 30D: {a_vencer_30} | 🟠 90D: {a_vencer_90}</span>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"👤 {st.session_state.usuario}")
    if st.button("Sair", use_container_width=True):
        st.session_state.logado=False
        st.rerun()
    if st.button("🗑️ RESETAR BANCO", type="primary", use_container_width=True):
        try: os.remove(DB)
        except: pass
        init_db()
        st.rerun()
    st.divider()
    st.metric("💰 SALDO ESTOQUE", f"{total_saldo:,.0f}")
    st.metric("🟢 ENTRADAS", f"{total_entradas:,.0f}")
    st.metric("🔴 SAÍDAS", f"{total_saidas:,.0f}")
    st.metric("🔴 VENCIDOS", vencidos)
    st.metric("🟡 A VENCER 30D", a_vencer_30)

tabs = st.tabs(["📊 DASHBOARD", "🗄️ GAVETAS - Editar e Excluir", "🔄 MOVIMENTAÇÃO", "📋 PLANILHA COMPLETA"])

with tabs[0]:
    st.markdown("## 📊 DASHBOARD GESTÃO - Entradas Saídas Saldo Vencidos A Vencer")

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    with k1: st.markdown(f"<div style='background:white; padding:15px; border-radius:12px; border-left:5px solid #3B82F6; box-shadow:0 4px 10px rgba(0,0,0,0.1);'><small>SALDO ESTOQUE</small><h2>{total_saldo:,.0f}</h2><small>TOTAL = QTD/PALETE × ENTRADA</small></div>", unsafe_allow_html=True)
    with k2: st.markdown(f"<div style='background:white; padding:15px; border-radius:12px; border-left:5px solid #10B981; box-shadow:0 4px 10px rgba(0,0,0,0.1);'><small>🟢 ENTRADAS</small><h2>{total_entradas:,.0f}</h2><small>{len(df_hist[df_hist['tipo']=='ENTRADA']) if not df_hist.empty else 0} mov.</small></div>", unsafe_allow_html=True)
    with k3: st.markdown(f"<div style='background:white; padding:15px; border-radius:12px; border-left:5px solid #EF4444; box-shadow:0 4px 10px rgba(0,0,0,0.1);'><small>🔴 SAÍDAS</small><h2>{total_saidas:,.0f}</h2><small>{len(df_hist[df_hist['tipo']=='SAIDA']) if not df_hist.empty else 0} mov.</small></div>", unsafe_allow_html=True)
    with k4: st.markdown(f"<div style='background:white; padding:15px; border-radius:12px; border-left:5px solid #DC2626; box-shadow:0 4px 10px rgba(0,0,0,0.1);'><small>🔴 VENCIDOS</small><h2>{vencidos}</h2><small>Retirar</small></div>", unsafe_allow_html=True)
    with k5: st.markdown(f"<div style='background:white; padding:15px; border-radius:12px; border-left:5px solid #F59E0B; box-shadow:0 4px 10px rgba(0,0,0,0.1);'><small>🟡 VENCE 30D</small><h2>{a_vencer_30}</h2><small>Usar primeiro</small></div>", unsafe_allow_html=True)
    with k6: st.markdown(f"<div style='background:white; padding:15px; border-radius:12px; border-left:5px solid #F97316; box-shadow:0 4px 10px rgba(0,0,0,0.1);'><small>🟠 VENCE 90D</small><h2>{a_vencer_90}</h2><small>Atenção</small></div>", unsafe_allow_html=True)

    st.divider()
    if not df_est.empty:
        c1,c2 = st.columns(2)
        with c1:
            df_gav = df_est.groupby("id_gaveta")["total"].sum().reset_index()
            fig = px.bar(df_gav, x="id_gaveta", y="total", title="💰 Saldo por Gaveta - TOTAL = QTD/PALETE × ENTRADA", text="total", color="total", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)

            df_status = df_est.groupby("status_validade")["total"].sum().reset_index()
            fig2 = px.pie(df_status, values="total", names="status_validade", title="⏰ Saldo por Validade - Vencidos e A Vencer", color="status_validade",
                         color_discrete_map={"🔴 VENCIDO":"red","🟡 VENCE 30 DIAS":"orange","🟠 VENCE 90 DIAS":"#F97316","🟢 OK":"green","⚪ SEM VALIDADE":"gray"})
            st.plotly_chart(fig2, use_container_width=True)

        with c2:
            if not df_hist.empty:
                df_hist["data"] = pd.to_datetime(df_hist["data"])
                df_hist["mes"] = df_hist["data"].dt.strftime("%Y-%m")
                df_mes = df_hist.groupby(["mes","tipo"])["total"].sum().reset_index()
                fig3 = px.bar(df_mes, x="mes", y="total", color="tipo", barmode="group", title="🔄 Entradas x Saídas por Mês", color_discrete_map={"ENTRADA":"#10B981","SAIDA":"#EF4444"})
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("Sem movimentações - faça entradas e saídas")

            df_marca = df_est.groupby("marca")["total"].sum().reset_index().sort_values("total", ascending=False).head(10)
            fig4 = px.bar(df_marca, x="marca", y="total", title="Top 10 Marcas por Saldo", color="total")
            st.plotly_chart(fig4, use_container_width=True)

        st.divider()
        c3,c4,c5 = st.columns(3)
        with c3:
            st.markdown("#### 🔴 VENCIDOS - Retirar do estoque")
            df_venc = df_est[df_est["status_validade"]=="🔴 VENCIDO"]
            if not df_venc.empty:
                st.dataframe(df_venc[["id_gaveta","descricao","marca","lote","validade","total","dias_vencer"]].sort_values("dias_vencer"), use_container_width=True)
                if st.button("🗑️ EXCLUIR TODOS VENCIDOS", type="primary", use_container_width=True):
                    con = sqlite3.connect(DB)
                    con.execute("DELETE FROM estoque WHERE id IN ({})".format(",".join(map(str, df_venc["id"].tolist()))))
                    con.commit(); con.close()
                    st.success(f"{len(df_venc)} vencidos excluídos!"); st.rerun()
            else: st.success("Nenhum vencido")
        with c4:
            st.markdown("#### 🟡 VENCE EM 30 DIAS - Usar primeiro FEFO")
            df_30 = df_est[df_est["status_validade"]=="🟡 VENCE 30 DIAS"]
            if not df_30.empty:
                st.dataframe(df_30[["id_gaveta","descricao","marca","lote","validade","total","dias_vencer"]].sort_values("dias_vencer"), use_container_width=True)
            else: st.success("Nenhum vence em 30 dias")
        with c5:
            st.markdown("#### 🟠 VENCE EM 90 DIAS")
            df_90 = df_est[df_est["status_validade"]=="🟠 VENCE 90 DIAS"]
            if not df_90.empty:
                st.dataframe(df_90[["id_gaveta","descricao","marca","lote","validade","total","dias_vencer"]].sort_values("dias_vencer"), use_container_width=True)
            else: st.success("Nenhum vence em 90 dias")

with tabs[1]:
    if st.session_state.gaveta_sel is None:
        st.markdown("### 🗄️ Gavetas - Clique para EDITAR e EXCLUIR registros")
        cols = st.columns(4)
        for gid in range(1, 21):
            df_g = df_est[df_est["id_gaveta"]==gid] if not df_est.empty else pd.DataFrame()
            total_g = df_g["total"].sum() if not df_g.empty else 0
            venc_g = len(df_g[df_g["status_validade"]=="🔴 VENCIDO"]) if not df_g.empty else 0
            with cols[(gid-1)%4]:
                color = "red" if venc_g>0 else "#E5E7EB"
                st.markdown(f"<div style='background:{color}; border:3px solid #111; border-radius:10px; height:90px; display:flex; flex-direction:column; justify-content:center; align-items:center; font-weight:800;'><div>ID {gid:02d} {'🔴' if venc_g>0 else ''}</div><div>{len(df_g)} itens</div><div>{total_g:,.0f}</div></div>", unsafe_allow_html=True)
                if st.button(f"ABRIR ID {gid:02d}", key=f"open_{gid}", use_container_width=True):
                    st.session_state.gaveta_sel=gid
                    st.rerun()
    else:
        sel = st.session_state.gaveta_sel
        if st.button("⬅️ VOLTAR", use_container_width=True):
            st.session_state.gaveta_sel=None
            st.rerun()

        st.markdown(f"## ID {sel:02d} - EDITAR E EXCLUIR REGISTROS")
        con = sqlite3.connect(DB)
        df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE id_gaveta={sel} ORDER BY validade", con)

        if not df_dentro.empty:
            df_dentro["qtd_palete"] = pd.to_numeric(df_dentro["qtd_palete"], errors='coerce').fillna(1)
            df_dentro["entrada"] = pd.to_numeric(df_dentro["entrada"], errors='coerce').fillna(1)
            df_dentro["total"] = df_dentro["qtd_palete"] * df_dentro["entrada"]

            st.markdown(f"**{len(df_dentro)} registros | Total: {df_dentro['total'].sum():,.0f} | Edite QTD/PALETE e ENTRADA - TOTAL calcula sozinho**")

            # TABELA COM EDITAR E EXCLUIR
            df_edit = st.data_editor(
                df_dentro,
                use_container_width=True,
                height=350,
                num_rows="dynamic",
                key=f"edit_{sel}",
                column_config={
                    "id": st.column_config.NumberColumn("ID Registro", disabled=True),
                    "id_gaveta": st.column_config.NumberColumn("ID Gaveta"),
                    "descricao": st.column_config.TextColumn("DESCRIÇÃO *"),
                    "marca": st.column_config.TextColumn("MARCA *"),
                    "lote": st.column_config.TextColumn("LOTE *"),
                    "validade": st.column_config.TextColumn("VALIDADE * (dd/mm/aaaa)"),
                    "qtd_palete": st.column_config.NumberColumn("QTD/PALETE *", format="%.2f"),
                    "entrada": st.column_config.NumberColumn("ENTRADA *", format="%.2f"),
                    "total": st.column_config.NumberColumn("TOTAL = QTD/PALETE × ENTRADA", disabled=True, format="%.0f"),
                    "unidade_medida": st.column_config.SelectboxColumn("UNIDADE", options=["KILOS","UNIDADES","PACOTES","ROLOS"]),
                    "data_mov": st.column_config.TextColumn("DATA"),
                }
            )

            df_edit["total"] = pd.to_numeric(df_edit["qtd_palete"], errors='coerce').fillna(0) * pd.to_numeric(df_edit["entrada"], errors='coerce').fillna(0)

            col1,col2,col3 = st.columns(3)
            if col1.button("💾 SALVAR EDIÇÕES", type="primary", use_container_width=True, key=f"save_{sel}"):
                try:
                    con.execute("DELETE FROM estoque WHERE id_gaveta=?", (sel,))
                    df_edit.to_sql("estoque", con, if_exists="append", index=False)
                    con.commit()
                    st.success(f"Gaveta {sel:02d} salva! Total: {df_edit['total'].sum():,.0f}")
                    st.rerun()
                except Exception as e: st.error(str(e))

            if col2.button("🗑️ EXCLUIR REGISTROS SELECIONADOS - Selecione linhas e clique", use_container_width=True, key=f"del_{sel}"):
                # Pega IDs que foram removidos do editor vs original
                ids_originais = set(df_dentro["id"].tolist())
                ids_editados = set(df_edit["id"].dropna().tolist()) if "id" in df_edit.columns else set()
                ids_removidos = ids_originais - ids_editados
                if ids_removidos:
                    con.execute(f"DELETE FROM estoque WHERE id IN ({','.join(map(str, ids_removidos))})")
                    con.commit()
                    st.success(f"{len(ids_removidos)} registros excluídos!")
                    st.rerun()
                else:
                    st.warning("Para excluir: selecione a linha na tabela (clique no checkbox da linha) e aperte DELETE no teclado, depois clique SALVAR")

            if col3.button("🗑️ LIMPAR GAVETA TODA", use_container_width=True, key=f"clear_{sel}"):
                con.execute("DELETE FROM estoque WHERE id_gaveta=?", (sel,))
                con.commit()
                st.success(f"Gaveta {sel:02d} limpa!"); st.rerun()

            st.divider()
            # EXCLUIR INDIVIDUAL
            st.markdown("#### 🗑️ EXCLUIR REGISTRO INDIVIDUAL")
            if not df_dentro.empty:
                id_del = st.selectbox("Selecione registro para EXCLUIR:", df_dentro["id"].tolist(), format_func=lambda x: f"ID {x} - {df_dentro[df_dentro.id==x].iloc[0]['descricao']} - {df_dentro[df_dentro.id==x].iloc[0]['marca']} - {df_dentro[df_dentro.id==x].iloc[0]['total']:.0f}", key=f"sel_del_{sel}")
                col_del1, col_del2 = st.columns(2)
                if col_del1.button("🗑️ EXCLUIR ESSE REGISTRO", type="primary", use_container_width=True, key=f"btn_del_{sel}"):
                    con.execute("DELETE FROM estoque WHERE id=?", (int(id_del),))
                    con.commit()
                    st.success(f"Registro ID {id_del} excluído!"); st.rerun()
                if col_del2.button("✏️ EDITAR ESSE REGISTRO", use_container_width=True, key=f"btn_edit_{sel}"):
                    row = df_dentro[df_dentro.id==id_del].iloc[0]
                    st.session_state[f"edit_row_{sel}"] = row.to_dict()
                    st.info(f"Editando ID {id_del} - altere abaixo e salve")

                # Formulário de edição individual
                if f"edit_row_{sel}" in st.session_state:
                    st.markdown("#### ✏️ Editar Registro")
                    r = st.session_state[f"edit_row_{sel}"]
                    c1,c2,c3,c4 = st.columns(4)
                    desc_e = c1.text_input("DESCRIÇÃO", value=r["descricao"], key=f"e_desc_{sel}")
                    marca_e = c2.text_input("MARCA", value=r["marca"], key=f"e_marca_{sel}")
                    lote_e = c3.text_input("LOTE", value=r["lote"], key=f"e_lote_{sel}")
                    val_e = c4.text_input("VALIDADE", value=r["validade"], key=f"e_val_{sel}")
                    c5,c6,c7,c8 = st.columns(4)
                    qtd_e = c5.number_input("QTD/PALETE", value=float(r["qtd_palete"]), key=f"e_qtd_{sel}")
                    ent_e = c6.number_input("ENTRADA", value=float(r["entrada"]), key=f"e_ent_{sel}")
                    uni_e = c7.selectbox("UNIDADE", ["KILOS","UNIDADES","PACOTES","ROLOS"], index=0, key=f"e_uni_{sel}")
                    data_e = c8.text_input("DATA", value=r["data_mov"], key=f"e_data_{sel}")
                    total_e = qtd_e * ent_e
                    st.success(f"TOTAL = {qtd_e} × {ent_e} = {total_e:,.0f} {uni_e}")
                    if st.button("💾 SALVAR EDIÇÃO INDIVIDUAL", type="primary", use_container_width=True, key=f"save_ind_{sel}"):
                        con.execute("UPDATE estoque SET descricao=?, marca=?, lote=?, validade=?, qtd_palete=?, entrada=?, total=?, unidade_medida=?, data_mov=? WHERE id=?",
                                    (desc_e, marca_e, lote_e, val_e, qtd_e, ent_e, total_e, uni_e, data_e, int(id_del)))
                        con.commit()
                        st.success("Editado!");
                        if f"edit_row_{sel}" in st.session_state: del st.session_state[f"edit_row_{sel}"]
                        st.rerun()

        else:
            st.info(f"ID {sel:02d} vazia")

        # ADICIONAR NOVO
        with st.container(border=True):
            st.markdown("#### ➕ ADICIONAR NOVO REGISTRO")
            c1,c2,c3,c4 = st.columns(4)
            desc_n = c1.text_input("DESCRIÇÃO", key=f"n_desc_{sel}")
            marca_n = c2.text_input("MARCA", key=f"n_marca_{sel}")
            lote_n = c3.text_input("LOTE", value="9999999999", key=f"n_lote_{sel}")
            val_n = c4.text_input("VALIDADE (dd/mm/aaaa)", value="00/00/0000", key=f"n_val_{sel}")
            c5,c6,c7,c8 = st.columns(4)
            qtd_n = c5.number_input("QTD/PALETE", value=1000.0, key=f"n_qtd_{sel}")
            ent_n = c6.number_input("ENTRADA", value=1.0, key=f"n_ent_{sel}")
            uni_n = c7.selectbox("UNIDADE", ["KILOS","UNIDADES","PACOTES","ROLOS"], key=f"n_uni_{sel}")
            data_n = c8.text_input("DATA", value="26/05/2026", key=f"n_data_{sel}")
            total_n = qtd_n * ent_n
            st.success(f"TOTAL = {qtd_n} × {ent_n} = {total_n:,.0f} {uni_n}")
            if st.button("💾 ADICIONAR", type="primary", use_container_width=True, key=f"n_add_{sel}"):
                con.execute("INSERT INTO estoque (id_gaveta, descricao, marca, lote, validade, fab, qtd_palete, entrada, total, unidade_medida, data_mov, codigo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            (sel, desc_n, marca_n, lote_n, val_n, val_n, qtd_n, ent_n, total_n, uni_n, data_n, f"{desc_n[:3]}-{marca_n[:3]}"))
                con.execute("INSERT INTO historico (data, id_gaveta, descricao, marca, lote, tipo, qtd_palete, entrada, total, usuario) VALUES (?,?,?,?,?,?,?,?,?,?)",
                            (datetime.now().isoformat(), sel, desc_n, marca_n, lote_n, "ENTRADA", qtd_n, ent_n, total_n, st.session_state.usuario))
                con.commit()
                st.success("Adicionado!"); st.rerun()
        con.close()
        if st.button("⬅️ VOLTAR", use_container_width=True, key=f"back_{sel}"):
            st.session_state.gaveta_sel=None
            st.rerun()

with tabs[2]:
    st.markdown("### 🔄 MOVIMENTAÇÃO - Entradas e Saídas - Saldo atualiza sozinho")
    if not df_est.empty:
        busca = st.text_input("🔍 Buscar DESCRIÇÃO, MARCA, LOTE")
        df_busca = df_est.copy()
        if busca:
            df_busca = df_busca[df_busca.apply(lambda r: busca.lower() in str(r["descricao"]).lower() or busca.lower() in str(r["marca"]).lower(), axis=1)]
        st.dataframe(df_busca[["id","id_gaveta","descricao","marca","lote","validade","qtd_palete","entrada","total","unidade_medida","status_validade"]], use_container_width=True, height=300)

        if not df_busca.empty:
            sel_idx = st.selectbox("Material para movimentar:", df_busca.index.tolist(), format_func=lambda x: f"ID {df_busca.loc[x,'id']} - G{df_busca.loc[x,'id_gaveta']:02d} - {df_busca.loc[x,'descricao']} - {df_busca.loc[x,'total']:.0f} {df_busca.loc[x,'status_validade']}", key="sel_mov")
            row = df_busca.loc[sel_idx]

            c1,c2 = st.columns(2)
            with c1:
                st.markdown("#### 🟢 ENTRADA - Aumenta saldo")
                ent_e = st.number_input("ENTRADA +", value=1.0, min_value=0.0, key="mov_e")
                tot_e = float(row["qtd_palete"]) * ent_e
                st.success(f"Saldo atual {row['total']:.0f} + {tot_e:.0f} = {row['total']+tot_e:.0f}")
                if st.button("➕ ENTRADA", type="primary", use_container_width=True):
                    con = sqlite3.connect(DB)
                    nova_ent = float(row["entrada"]) + ent_e
                    novo_tot = float(row["qtd_palete"]) * nova_ent
                    con.execute("UPDATE estoque SET entrada=?, total=? WHERE id=?", (nova_ent, novo_tot, int(row["id"])))
                    con.execute("INSERT INTO historico (data, id_gaveta, descricao, marca, lote, tipo, qtd_palete, entrada, total, usuario) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                (datetime.now().isoformat(), int(row["id_gaveta"]), row["descricao"], row["marca"], row["lote"], "ENTRADA", float(row["qtd_palete"]), ent_e, tot_e, st.session_state.usuario))
                    con.commit(); con.close()
                    st.success("Entrada registrada!"); st.rerun()

            with c2:
                st.markdown("#### 🔴 SAÍDA - Diminui saldo")
                ent_s = st.number_input("SAÍDA -", value=1.0, min_value=0.0, key="mov_s")
                tot_s = float(row["qtd_palete"]) * ent_s
                st.error(f"Saldo atual {row['total']:.0f} - {tot_s:.0f} = {row['total']-tot_s:.0f}")
                if st.button("➖ SAÍDA", type="primary", use_container_width=True):
                    con = sqlite3.connect(DB)
                    if ent_s > float(row["entrada"]):
                        st.error(f"Saída {ent_s} maior que entrada {row['entrada']}!")
                    else:
                        nova_ent = float(row["entrada"]) - ent_s
                        novo_tot = float(row["qtd_palete"]) * nova_ent
                        con.execute("UPDATE estoque SET entrada=?, total=? WHERE id=?", (nova_ent, novo_tot, int(row["id"])))
                        con.execute("INSERT INTO historico (data, id_gaveta, descricao, marca, lote, tipo, qtd_palete, entrada, total, usuario) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                    (datetime.now().isoformat(), int(row["id_gaveta"]), row["descricao"], row["marca"], row["lote"], "SAIDA", float(row["qtd_palete"]), ent_s, tot_s, st.session_state.usuario))
                        con.commit()
                        st.success("Saída registrada!"); st.rerun()
                    con.close()

with tabs[3]:
    if not df_est.empty:
        df_show = df_est[["id_gaveta","descricao","marca","lote","validade","qtd_palete","entrada","total","unidade_medida","data_mov","status_validade","dias_vencer"]].copy()
        df_show.columns = ["ID","DESCRIÇÃO","MARCA","LOTE","VALIDADE","QTD/PALETE","ENTRADA","TOTAL","UNIDADE","DATA","STATUS VALIDADE","DIAS VENCER"]
        st.dataframe(df_show, use_container_width=True, height=600)
        st.download_button("📥 Baixar Planilha CSV", df_show.to_csv(index=False).encode('utf-8'), "planilha_completa.csv", "text/csv", type="primary", use_container_width=True)
        st.download_button("📥 Baixar Histórico Entradas Saídas", df_hist.to_csv(index=False).encode('utf-8'), "historico_entradas_saidas.csv", "text/csv", use_container_width=True)

        st.markdown(f"""
        ### Resumo Dashboard
        - **SALDO ESTOQUE:** {total_saldo:,.0f} = SOMA(QTD/PALETE × ENTRADA)
        - **ENTRADAS:** {total_entradas:,.0f} - Total de entradas no histórico
        - **SAÍDAS:** {total_saidas:,.0f} - Total de saídas no histórico
        - **VENCIDOS:** {vencidos} itens - Status 🔴 VENCIDO
        - **A VENCER 30 DIAS:** {a_vencer_30} itens - Status 🟡 VENCE 30 DIAS
        - **A VENCER 90 DIAS:** {a_vencer_90} itens - Status 🟠 VENCE 90 DIAS
        """)
