import streamlit as st
import pandas as pd
import sqlite3, os
from datetime import date, datetime, timedelta
import plotly.express as px

st.set_page_config(layout="wide", page_title="Reforma Fornos - Admin", page_icon="🔧", initial_sidebar_state="expanded")

DB = "estoque_fornos.db"
ADMIN_EMAIL = "admin@fornos.com" # TROQUE PELO SEU EMAIL DE ADMIN

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS materiais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT, nome TEXT, marca TEXT, categoria TEXT, peso REAL, fornecedor TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT,
        paletes INT, unit_pal INT, kg_unit REAL,
        fab DATE, validade DATE, lote TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT, gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT,
        tipo TEXT, paletes INT, unit_pal INT, kg_unit REAL, total_kg REAL, usuario TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS config (
        gaveta_id INT PRIMARY KEY, estoque_min REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE, nome TEXT, is_admin INTEGER DEFAULT 0, ativo INTEGER DEFAULT 1)""")
    con.execute("""CREATE TABLE IF NOT EXISTS gaveta_lock (
        gaveta_id INT PRIMARY KEY, trancada INTEGER DEFAULT 0, motivo TEXT)""")

    for i in range(1, 21):
        con.execute("INSERT OR IGNORE INTO config (gaveta_id, estoque_min) VALUES (?,?)", (i, 1000))
        con.execute("INSERT OR IGNORE INTO gaveta_lock (gaveta_id, trancada) VALUES (?,0)", (i,))

    # Cria admin padrão
    con.execute("INSERT OR IGNORE INTO usuarios (email, nome, is_admin, ativo) VALUES (?,?,1,1)", (ADMIN_EMAIL, "Administrador",))
    con.commit()
    con.close()

def reset_if_error():
    try:
        con = sqlite3.connect(DB)
        con.execute("SELECT paletes, unit_pal, kg_unit FROM estoque LIMIT 1").fetchall()
        con.execute("SELECT email FROM usuarios LIMIT 1").fetchall()
        con.execute("SELECT trancada FROM gaveta_lock LIMIT 1").fetchall()
        con.close()
        return False
    except:
        try: con.close()
        except: pass
        if os.path.exists(DB): os.remove(DB)
        init_db()
        return True

if not os.path.exists(DB):
    init_db()
else:
    if reset_if_error():
        st.rerun()

def calc_kg(p,u,k):
    try: return float(p or 0)*float(u or 0)*float(k or 0)
    except: return 0.0

if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario_email' not in st.session_state: st.session_state.usuario_email = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'gaveta_sel' not in st.session_state: st.session_state.gaveta_sel = 1

# ============== LOGIN COM EMAIL ==============
def check_login():
    if not st.session_state.logado:
        st.markdown("""
        <style>.login-box{background: linear-gradient(90deg, #1E3A8A, #3B82F6); padding:30px; border-radius:20px; color:white; text-align:center;}</style>
        <div class="login-box"><h1>🔒 LOGIN - REFORMA DE FORNOS</h1><p>Digite seu email cadastrado</p></div>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            email = st.text_input("📧 Seu Email", placeholder="seu@email.com")
            if st.button("🔓 ENTRAR", type="primary", use_container_width=True):
                con = sqlite3.connect(DB)
                user = con.execute("SELECT * FROM usuarios WHERE email=? AND ativo=1", (email.strip().lower(),)).fetchone()
                con.close()
                if user:
                    st.session_state.logado = True
                    st.session_state.usuario_email = email.strip().lower()
                    st.session_state.is_admin = bool(user[3]) # is_admin
                    st.success(f"Bem-vindo {user[2]}!")
                    st.rerun()
                else:
                    st.error("❌ Email não cadastrado ou desativado! Peça para o admin liberar.")
                    st.info(f"Admin padrão: {ADMIN_EMAIL}")

        # Cadastro rápido para teste
        with st.expander("🆕 Primeiro acesso? Solicitar cadastro"):
            with st.form("solicita"):
                nome_s = st.text_input("Nome")
                email_s = st.text_input("Email para liberação")
                if st.form_submit_button("Solicitar Acesso"):
                    con = sqlite3.connect(DB)
                    try:
                        con.execute("INSERT INTO usuarios (email, nome, is_admin, ativo) VALUES (?,?,0,0)", (email_s.strip().lower(), nome_s))
                        con.commit()
                        st.success("Solicitação enviada! Aguarde admin ativar.")
                    except:
                        st.warning("Email já existe, aguarde liberação")
                    con.close()
        st.stop()

check_login()

st.markdown(f"""
<style>.main-header {{ background: linear-gradient(90deg, #1E3A8A, #3B82F6); padding:15px; border-radius:12px; color:white; text-align:center; font-weight:900; }}</style>
<div class="main-header">🔧 FORNOS - Usuário: {st.session_state.usuario_email} {'👑 ADMIN' if st.session_state.is_admin else ''} | Gaveta {st.session_state.gaveta_sel:02d}</div>
""", unsafe_allow_html=True)

def get_df_estoque():
    try:
        con = sqlite3.connect(DB)
        df = pd.read_sql("SELECT * FROM estoque", con)
        con.close()
        if not df.empty:
            for c in ["paletes","unit_pal","kg_unit"]:
                if c not in df.columns: df[c]=0
            df["total_kg"] = df.apply(lambda r: calc_kg(r["paletes"], r["unit_pal"], r["kg_unit"]), axis=1)
            df["validade"] = pd.to_datetime(df["validade"], errors='coerce')
            df["dias_vencer"] = (df["validade"] - pd.to_datetime(date.today())).dt.days
        return df
    except: return pd.DataFrame()

def get_df_historico():
    try:
        con = sqlite3.connect(DB)
        df = pd.read_sql("SELECT * FROM historico ORDER BY data DESC", con)
        con.close()
        if not df.empty:
            df["data"] = pd.to_datetime(df["data"], errors='coerce')
            if "total_kg" not in df.columns or df["total_kg"].isna().all():
                for c in ["paletes","unit_pal","kg_unit"]:
                    if c not in df.columns: df[c]=0
                df["total_kg"] = df.apply(lambda r: calc_kg(r.get("paletes",0), r.get("unit_pal",0), r.get("kg_unit",0)), axis=1)
            df["total_kg"] = pd.to_numeric(df["total_kg"], errors='coerce').fillna(0)
        return df
    except: return pd.DataFrame()

def is_gaveta_trancada(gaveta_id):
    con = sqlite3.connect(DB)
    row = con.execute("SELECT trancada, motivo FROM gaveta_lock WHERE gaveta_id=?", (gaveta_id,)).fetchone()
    con.close()
    if row: return bool(row[0]), row[1]
    return False, ""

# SIDEBAR
with st.sidebar:
    st.markdown(f"👤 {st.session_state.usuario_email}")
    if st.session_state.is_admin: st.markdown("👑 **ADMINISTRADOR**")
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.logado = False
        st.session_state.usuario_email = ""
        st.rerun()

    df_est = get_df_estoque()
    total_kg = df_est["total_kg"].sum() if not df_est.empty else 0
    st.metric("Estoque Total", f"{total_kg:,.2f} KG")

    st.divider()
    st.markdown("### 📦 Gavetas")
    con = sqlite3.connect(DB)
    df_locks = pd.read_sql("SELECT * FROM gaveta_lock", con)
    con.close()

    c1,c2 = st.columns(2)
    for i in range(1,21):
        trancada = False
        if not df_locks.empty:
            r = df_locks[df_locks["gaveta_id"]==i]
            if not r.empty: trancada = bool(r.iloc[0]["trancada"])

        label = f"{'🔒' if trancada else '📦'} G{i:02d}"
        col = c1 if i%2==1 else c2
        if col.button(label, key=f"side_{i}", use_container_width=True, type="primary" if st.session_state.gaveta_sel==i else "secondary", disabled=trancada and not st.session_state.is_admin):
            st.session_state.gaveta_sel = i
            st.rerun()

# ABAS
abas = ["📈 DASHBOARD", "📝 CADASTRO", "📦 GAVETAS", "📊 RELATÓRIOS"]
if st.session_state.is_admin:
    abas.append("👑 ADMIN - USUÁRIOS E TRAVAS")

tabs = st.tabs(abas)
tab_dash = tabs[0]
tab_cad = tabs[1]
tab_gav = tabs[2]
tab_rel = tabs[3]
tab_admin = tabs[4] if st.session_state.is_admin else None

with tab_dash:
    st.markdown("## 📈 Dashboard")
    df_est = get_df_estoque()
    df_hist = get_df_historico()
    if not df_est.empty:
        c1,c2 = st.columns(2)
        with c1:
            df_gav = df_est.groupby("gaveta_id")["total_kg"].sum().reset_index()
            st.plotly_chart(px.bar(df_gav, x="gaveta_id", y="total_kg", title="Estoque por Gaveta", color="total_kg", text="total_kg"), use_container_width=True)
        with c2:
            df_marca = df_est.groupby("marca")["total_kg"].sum().reset_index()
            st.plotly_chart(px.pie(df_marca, values="total_kg", names="marca", title="Por Marca", hole=0.4), use_container_width=True)
    if not df_hist.empty:
        periodo = st.selectbox("Agrupar:", ["Diário","Semanal","Mensal","Semestral","Anual"], key="dash_per")
        df_hist["periodo"] = df_hist["data"]
        if periodo=="Diário": df_hist["periodo"] = df_hist["data"].dt.date
        elif periodo=="Semanal": df_hist["periodo"] = df_hist["data"].dt.strftime("%Y-W%U")
        elif periodo=="Mensal": df_hist["periodo"] = df_hist["data"].dt.to_period("M").astype(str)
        elif periodo=="Semestral": df_hist["periodo"] = df_hist["data"].dt.year.astype(str) + "-S" + ((df_hist["data"].dt.month-1)//6 +1).astype(str)
        else: df_hist["periodo"] = df_hist["data"].dt.year
        df_group = df_hist.groupby(["periodo","tipo"])["total_kg"].sum().reset_index()
        st.plotly_chart(px.bar(df_group, x="periodo", y="total_kg", color="tipo", barmode="group", color_discrete_map={"ENTRADA":"#16A34A","SAIDA":"#DC2626"}), use_container_width=True)

with tab_cad:
    st.markdown("## 📝 Cadastro ID LIVRE + MARCA")
    con = sqlite3.connect(DB)
    with st.form("cad_mat", clear_on_submit=True):
        c1,c2,c3,c4 = st.columns(4)
        codigo = c1.text_input("CÓDIGO *")
        nome = c2.text_input("NOME *")
        marca = c3.text_input("MARCA *")
        categoria = c4.selectbox("Categoria", ["Refratário","Cimento","Manta","Isolante","Ferragem","Outro"])
        c5,c6 = st.columns(2)
        peso = c5.number_input("Peso KG", value=25.0, format="%.2f")
        fornecedor = c6.text_input("Fornecedor")
        if st.form_submit_button("💾 SALVAR", type="primary", use_container_width=True):
            if codigo and nome and marca:
                con.execute("INSERT INTO materiais (codigo, nome, marca, categoria, peso, fornecedor) VALUES (?,?,?,?,?,?)", (codigo, nome, marca, categoria, peso, fornecedor))
                con.commit()
                st.success(f"Salvo: {codigo} - {marca}")
    df_mat = pd.read_sql("SELECT * FROM materiais ORDER BY id DESC", con)
    st.dataframe(df_mat, use_container_width=True)
    con.close()

with tab_gav:
    sel = st.session_state.gaveta_sel
    trancada, motivo = is_gaveta_trancada(sel)

    if trancada and not st.session_state.is_admin:
        st.error(f"🔒 GAVETA {sel:02d} TRANCADA PELO ADMIN - Motivo: {motivo} - Você não tem permissão")
        st.stop()
    elif trancada and st.session_state.is_admin:
        st.warning(f"🔒 Gaveta {sel:02d} está TRANCADA - Motivo: {motivo} - Como admin você pode usar")

    st.markdown(f"# 📂 GAVETA {sel:02d} {'🔒 TRANCADA' if trancada else '🔓 LIBERADA'}")

    con = sqlite3.connect(DB)
    df_mat = pd.read_sql("SELECT * FROM materiais", con)
    if df_mat.empty:
        st.warning("Cadastre material primeiro!")
        st.stop()

    # ENTRADA
    with st.container(border=True):
        st.markdown("#### 🟢 ENTRADA")
        ce1, ce2, ce3 = st.columns([2,1,1])
        mat_sel = ce1.selectbox("Material:", df_mat["id"].tolist(), format_func=lambda x: f"{df_mat[df_mat.id==x].iloc[0]['codigo']} - {df_mat[df_mat.id==x].iloc[0]['nome']} - {df_mat[df_mat.id==x].iloc[0]['marca']}", key=f"mat_e_{sel}")
        row_m = df_mat[df_mat.id==mat_sel].iloc[0]
        codigo_e = ce2.text_input("Código", value=row_m["codigo"], key=f"cod_e_{sel}")
        marca_e = ce3.text_input("Marca", value=row_m["marca"], key=f"marca_e_{sel}")

        ce4, ce5, ce6 = st.columns(3)
        pal_e = ce4.number_input("Paletes", min_value=1, value=1, key=f"pal_e_{sel}")
        unit_e = ce5.number_input("Unit/Palete", min_value=1, value=56, key=f"unit_e_{sel}")
        kg_e = ce6.number_input("Kg/Unit", min_value=0.1, value=float(row_m["peso"]), format="%.2f", key=f"kg_e_{sel}")

        total_preview = calc_kg(pal_e, unit_e, kg_e)
        st.markdown(f"**🧮 {pal_e} x {unit_e} x {kg_e} = {total_preview:,.2f} KG**")

        fab_e = st.date_input("Fabricação", value=date.today(), key=f"fab_e_{sel}")
        dias_e = st.number_input("Validade dias", value=90, key=f"dias_e_{sel}")
        lote_e = st.text_input("Lote/Obs", key=f"lote_e_{sel}")

        if st.button("🟢 SALVAR ENTRADA", type="primary", use_container_width=True, key=f"btn_e_{sel}"):
            validade = fab_e + timedelta(days=dias_e)
            con.execute("INSERT INTO estoque (gaveta_id, codigo, nome, marca, paletes, unit_pal, kg_unit, fab, validade, lote) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (sel, codigo_e, row_m["nome"], marca_e, pal_e, unit_e, kg_e, fab_e.isoformat(), validade.isoformat(), lote_e))
            con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, unit_pal, kg_unit, total_kg, usuario) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (datetime.now().isoformat(), sel, codigo_e, row_m["nome"], marca_e, "ENTRADA", pal_e, unit_e, kg_e, total_preview, st.session_state.usuario_email))
            con.commit()
            st.success(f"ENTRADA {total_preview:.2f} KG")
            st.rerun()

    df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE gaveta_id={sel} ORDER BY id DESC", con)
    if not df_dentro.empty:
        df_dentro["total_kg"] = df_dentro.apply(lambda r: calc_kg(r["paletes"], r["unit_pal"], r["kg_unit"]), axis=1)
        df_dentro["calc"] = df_dentro.apply(lambda r: f"{r['paletes']} x {r['unit_pal']} x {r['kg_unit']} = {r['total_kg']:.2f} KG", axis=1)
        st.dataframe(df_dentro[["id","codigo","marca","paletes","unit_pal","kg_unit","calc","total_kg"]], use_container_width=True)

        df_edit = st.data_editor(df_dentro[["id","codigo","nome","marca","paletes","unit_pal","kg_unit"]], use_container_width=True, key=f"edit_{sel}")

        if st.button("💾 SALVAR ALTERAÇÕES", type="primary", use_container_width=True, key=f"save_{sel}"):
            for _, r in df_edit.iterrows():
                con.execute("UPDATE estoque SET codigo=?, nome=?, marca=?, paletes=?, unit_pal=?, kg_unit=? WHERE id=?",
                            (r["codigo"], r["nome"], r["marca"], int(r["paletes"]), int(r["unit_pal"]), float(r["kg_unit"]), int(r["id"])))
            con.commit()
            st.success("✅ Atualizado!")
            st.rerun()

        st.divider()
        with st.container(border=True):
            st.markdown("#### 🔴 SAÍDA")
            id_saida = st.selectbox("Item SAÍDA:", df_dentro["id"].tolist(), format_func=lambda x: f"ID {x} - {df_dentro[df_dentro.id==x].iloc[0]['codigo']} - {df_dentro[df_dentro.id==x].iloc[0]['marca']} - {df_dentro[df_dentro.id==x].iloc[0]['calc']}", key=f"saida_{sel}")
            qtd_saida = st.number_input("Qtd Paletes SAÍDA", min_value=1, value=1, key=f"qtd_s_{sel}")
            row_s = df_dentro[df_dentro.id==id_saida].iloc[0]
            total_s_prev = calc_kg(qtd_saida, row_s["unit_pal"], row_s["kg_unit"])
            st.markdown(f"**🔴 SAÍDA: {qtd_saida} x {row_s['unit_pal']} x {row_s['kg_unit']} = {total_s_prev:,.2f} KG**")

            if st.button("🔴 SALVAR SAÍDA", type="primary", use_container_width=True, key=f"btn_s_{sel}"):
                con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, unit_pal, kg_unit, total_kg, usuario) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                            (datetime.now().isoformat(), sel, row_s["codigo"], row_s["nome"], row_s["marca"], "SAIDA", qtd_saida, row_s["unit_pal"], row_s["kg_unit"], total_s_prev, st.session_state.usuario_email))
                if qtd_saida >= row_s["paletes"]:
                    con.execute("DELETE FROM estoque WHERE id=?", (int(id_saida),))
                else:
                    con.execute("UPDATE estoque SET paletes = paletes -? WHERE id=?", (int(qtd_saida), int(id_saida)))
                con.commit()
                st.success(f"SAÍDA {total_s_prev:.2f} KG")
                st.rerun()
    else:
        st.info("Gaveta vazia")
    con.close()

with tab_rel:
    st.markdown("## 📊 Histórico")
    df_hist = get_df_historico()
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("Sem histórico")

# ============== ABA ADMIN ==============
if st.session_state.is_admin and tab_admin is not None:
    with tab_admin:
        st.markdown("## 👑 PAINEL ADMINISTRADOR")

        st.markdown("### 🔒 Trancar / Liberar Gavetas")
        con = sqlite3.connect(DB)
        df_locks = pd.read_sql("SELECT * FROM gaveta_lock", con)

        c1,c2,c3 = st.columns(3)
        gav_tranca = c1.selectbox("Gaveta para trancar/liberar", list(range(1,21)), format_func=lambda x: f"Gaveta {x:02d}")
        acao = c2.selectbox("Ação", ["🔓 LIBERAR", "🔒 TRANCAR"])
        motivo = c3.text_input("Motivo da trava", placeholder="Ex: Inventário")

        if st.button("💾 SALVAR TRAVA", type="primary", use_container_width=True):
            trancada_val = 1 if "TRANCAR" in acao else 0
            con.execute("UPDATE gaveta_lock SET trancada=?, motivo=? WHERE gaveta_id=?", (trancada_val, motivo, gav_tranca))
            con.commit()
            st.success(f"Gaveta {gav_tranca:02d} {'TRANCADA' if trancada_val else 'LIBERADA'}!")

        st.dataframe(df_locks, use_container_width=True)
        st.divider()

        st.markdown("### 👥 Cadastro de Emails - Permissão de Uso")
        with st.form("cad_user", clear_on_submit=True):
            c1,c2,c3 = st.columns(3)
            email_new = c1.text_input("Email *")
            nome_new = c2.text_input("Nome *")
            is_admin_new = c3.checkbox("É Administrador?")
            ativo_new = st.checkbox("Ativo / Liberado", value=True)
            if st.form_submit_button("💾 CADASTRAR/LIBERAR EMAIL", type="primary", use_container_width=True):
                try:
                    con.execute("INSERT INTO usuarios (email, nome, is_admin, ativo) VALUES (?,?,?,?) ON CONFLICT(email) DO UPDATE SET nome=?, is_admin=?, ativo=?",
                                (email_new.strip().lower(), nome_new, int(is_admin_new), int(ativo_new), nome_new, int(is_admin_new), int(ativo_new)))
                    con.commit()
                    st.success(f"Email {email_new} cadastrado/liberado!")
                except Exception as e:
                    st.error(f"Erro: {e}")

        df_users = pd.read_sql("SELECT * FROM usuarios ORDER BY is_admin DESC, email", con)
        st.markdown(f"### Usuários Cadastrados ({len(df_users)})")
        st.dataframe(df_users, use_container_width=True)

        st.divider()
        st.markdown("### Editar / Desativar Usuário")
        if not df_users.empty:
            email_edit = st.selectbox("Selecione email:", df_users["email"].tolist(), format_func=lambda x: f"{x} - {'ADMIN' if df_users[df_users.email==x].iloc[0]['is_admin'] else 'USER'} - {'ATIVO' if df_users[df_users.email==x].iloc[0]['ativo'] else 'BLOQUEADO'}")
            user_row = df_users[df_users["email"]==email_edit].iloc[0]

            c1,c2,c3 = st.columns(3)
            novo_nome = c1.text_input("Nome", value=user_row["nome"], key="edit_nome")
            novo_admin = c2.checkbox("Admin", value=bool(user_row["is_admin"]), key="edit_admin")
            novo_ativo = c3.checkbox("Ativo", value=bool(user_row["ativo"]), key="edit_ativo")

            col_a, col_b = st.columns(2)
            if col_a.button("💾 SALVAR ALTERAÇÕES USUÁRIO", use_container_width=True, type="primary"):
                con.execute("UPDATE usuarios SET nome=?, is_admin=?, ativo=? WHERE email=?", (novo_nome, int(novo_admin), int(novo_ativo), email_edit))
                con.commit()
                st.success("Usuário atualizado!")
                st.rerun()
            if col_b.button("🗑️ EXCLUIR EMAIL", use_container_width=True):
                con.execute("DELETE FROM usuarios WHERE email=?", (email_edit,))
                con.commit()
                st.success("Email excluído!")
                st.rerun()

        con.close()
