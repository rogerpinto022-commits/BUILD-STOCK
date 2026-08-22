import streamlit as st
import pandas as pd
import sqlite3, os
from datetime import date, datetime, timedelta
import plotly.express as px

st.set_page_config(layout="wide", page_title="Fornos - Gavetas Visuais", page_icon="🗄️")

DB = "estoque_fornos.db"
ADMIN_EMAIL = "admin@fornos.com"

LISTA_UNIDADES = ["MASSA | KG - Quilograma", "MASSA | G - Grama", "MASSA | T - Tonelada", "GERAL | UN - Unidade", "GERAL | PC - Peça", "GERAL | CX - Caixa", "GERAL | SC - Saco", "GERAL | PL - Palete", "VOLUME | L - Litro", "VOLUME | M³ - Metro cúbico"]

def get_sigla(u):
    try: return u.split("|")[-1].split(" - ")[0].strip()
    except: return "KG"

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS materiais (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT, nome TEXT, marca TEXT, categoria TEXT, peso REAL, unidade_medida TEXT, unidade_sigla TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS estoque (id INTEGER PRIMARY KEY AUTOINCREMENT, gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT, paletes INT, unit_pal INT, kg_unit REAL, unidade_medida TEXT, unidade_sigla TEXT, fab DATE, validade DATE, lote TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT, tipo TEXT, paletes INT, unit_pal INT, kg_unit REAL, total_kg REAL, usuario TEXT, unidade_medida TEXT, unidade_sigla TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS config (gaveta_id INT PRIMARY KEY, estoque_min REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, nome TEXT, is_admin INTEGER DEFAULT 1, ativo INTEGER DEFAULT 1)""")
    con.execute("""CREATE TABLE IF NOT EXISTS gaveta_lock (gaveta_id INT PRIMARY KEY, trancada INTEGER DEFAULT 0, motivo TEXT)""")
    for i in range(1,21):
        con.execute("INSERT OR IGNORE INTO config (gaveta_id, estoque_min) VALUES (?,?)", (i, 1000))
        con.execute("INSERT OR IGNORE INTO gaveta_lock (gaveta_id, trancada) VALUES (?,0)", (i,))
    # Admin sempre ativo
    con.execute("INSERT OR REPLACE INTO usuarios (id, email, nome, is_admin, ativo) VALUES (1,?,?,1,1)", (ADMIN_EMAIL, "Admin"))
    con.commit(); con.close()

# FORÇA RESET SE ESTIVER TRAVADO - DESCOMENTE SE PRECISAR
# if os.path.exists(DB): os.remove(DB)

if not os.path.exists(DB):
    init_db()
else:
    # Tenta corrigir colunas sem apagar
    try:
        con = sqlite3.connect(DB)
        con.execute("PRAGMA table_info(usuarios)")
        cols = [c[1] for c in con.execute("PRAGMA table_info(usuarios)").fetchall()]
        if "ativo" not in cols:
            con.execute("ALTER TABLE usuarios ADD COLUMN ativo INTEGER DEFAULT 1")
        if "is_admin" not in cols:
            con.execute("ALTER TABLE usuarios ADD COLUMN is_admin INTEGER DEFAULT 0")
        con.execute("UPDATE usuarios SET ativo=1 WHERE ativo IS NULL")
        con.commit()
        # Garante admin existe e ativo
        con.execute("INSERT OR IGNORE INTO usuarios (email, nome, is_admin, ativo) VALUES (?,?,1,1)", (ADMIN_EMAIL, "Admin"))
        con.execute("UPDATE usuarios SET ativo=1, is_admin=1 WHERE email=?", (ADMIN_EMAIL,))
        con.commit()
        con.close()
    except:
        try: con.close()
        except: pass
        if os.path.exists(DB): os.remove(DB)
        init_db()

def calc_kg(p,u,k):
    try: return float(p or 0)*float(u or 0)*float(k or 0)
    except: return 0.0

if 'logado' not in st.session_state: st.session_state.logado=False
if 'usuario_email' not in st.session_state: st.session_state.usuario_email=""
if 'is_admin' not in st.session_state: st.session_state.is_admin=False
if 'gaveta_sel' not in st.session_state: st.session_state.gaveta_sel=None
if 'filtro_unidade' not in st.session_state: st.session_state.filtro_unidade="TODAS"

# LOGIN LIBERADO - ENTRA COM QUALQUER EMAIL
def check_login():
    if not st.session_state.logado:
        st.markdown("""
        <div style='background: linear-gradient(90deg, #1E3A8A, #3B82F6); padding:30px; border-radius:20px; color:white; text-align:center;'>
            <h1>🗄️ LOGIN LIBERADO - ARQUIVO DE GAVETAS</h1>
            <p>Digite qualquer email para entrar. admin@fornos.com entra como ADMIN</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            email = st.text_input("📧 Digite seu Email para entrar", value="admin@fornos.com", key="login_email_final")
            nome = st.text_input("👤 Seu Nome", value="Administrador", key="login_nome")

            col1, col2 = st.columns(2)
            if col1.button("🔓 ENTRAR DIRETO (Sem senha)", type="primary", use_container_width=True, key="btn_login_final"):
                try:
                    con = sqlite3.connect(DB)
                    email_low = email.strip().lower()
                    # Se for admin, garante admin
                    is_admin = 1 if email_low == ADMIN_EMAIL.lower() else 0
                    # Se for primeiro acesso, libera como admin também
                    total_users = con.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
                    if total_users <= 1: is_admin = 1

                    con.execute("INSERT OR IGNORE INTO usuarios (email, nome, is_admin, ativo) VALUES (?,?,?,1)", (email_low, nome, is_admin))
                    con.execute("UPDATE usuarios SET nome=?, ativo=1, is_admin=? WHERE email=?", (nome, is_admin, email_low))
                    # Se for admin email, força admin=1
                    if email_low == ADMIN_EMAIL.lower():
                        con.execute("UPDATE usuarios SET is_admin=1, ativo=1 WHERE email=?", (email_low,))
                        is_admin = 1
                    con.commit()
                    con.close()

                    st.session_state.logado=True
                    st.session_state.usuario_email=email_low
                    st.session_state.is_admin=bool(is_admin)
                    st.success(f"Entrando como {email_low} {'ADMIN' if is_admin else ''}")
                    st.rerun()
                except Exception as e:
                    # Se der erro, entra mesmo assim como admin
                    st.session_state.logado=True
                    st.session_state.usuario_email=email.strip().lower()
                    st.session_state.is_admin=True
                    st.warning(f"Entrou modo emergência (erro banco corrigido): {e}")
                    st.rerun()

            if col2.button("🗑️ RESETAR BANCO AGORA (se travou)", use_container_width=True, key="btn_reset_login"):
                if os.path.exists(DB): os.remove(DB)
                init_db()
                st.success("Banco resetado! Agora entre com admin@fornos.com")
                st.rerun()

        st.info(f"""
        **Para entrar agora:**
        - Email: `admin@fornos.com`
        - Nome: `Admin`
        - Clique em ENTRAR DIRETO

        Esse email entra automaticamente como 👑 ADMIN e pode cadastrar outros emails depois na aba ADMIN.
        """)
        st.stop()

check_login()

# CSS GAVETAS
st.markdown("""
<style>
.main-header { background: linear-gradient(90deg, #1E3A8A, #3B82F6); padding:12px; border-radius:12px; color:white; text-align:center; font-weight:900; }
.gaveta-fechada { background: linear-gradient(180deg, #8A8A8A 0%, #5A5A5A 50%, #6B6B6B 100%); border: 3px solid #3A3A3A; border-radius: 6px; height: 120px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; font-weight: 800; box-shadow: 0 4px 8px rgba(0,0,0,0.4); }
.gaveta-puxador { width: 70px; height: 10px; background: #1A1A1A; border-radius: 5px; margin: 5px 0; }
.gaveta-etiqueta { background: white; color: black; padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: 900; }
.gaveta-trancada { background: linear-gradient(180deg, #DC2626 0%, #991B1B 100%)!important; }
.gaveta-aberta-visual { background: #F8FAFC; border: 4px solid #16A34A; border-top: 12px solid #16A34A; border-radius: 0 0 15px 15px; padding: 15px; margin-top: 10px; }
</style>
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
            if "unidade_sigla" not in df.columns: df["unidade_sigla"]="KG"
            df["validade"] = pd.to_datetime(df["validade"], errors='coerce')
        return df
    except: return pd.DataFrame()

st.markdown(f"<div class='main-header'>🗄️ ARQUIVO 20 GAVETAS | {st.session_state.usuario_email} {'👑 ADMIN' if st.session_state.is_admin else ''}</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"👤 {st.session_state.usuario_email}")
    if st.session_state.is_admin: st.markdown("👑 ADMIN")
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.logado=False
        st.rerun()
    if st.button("🗑️ RESET BANCO", use_container_width=True, type="primary"):
        if os.path.exists(DB): os.remove(DB)
        st.session_state.logado=False
        st.rerun()
    st.divider()
    filtro_un = st.selectbox("Filtro Unidade", ["TODAS"] + LISTA_UNIDADES, key="filtro_side_final2")
    if st.button("🔍 Aplicar Filtro", use_container_width=True, type="primary"):
        st.session_state.filtro_unidade = filtro_un
        st.session_state.gaveta_sel = None
        st.rerun()
    if st.button("🧹 Limpar", use_container_width=True):
        st.session_state.filtro_unidade="TODAS"
        st.session_state.gaveta_sel=None
        st.rerun()
    df_est = get_df_estoque()
    st.metric("Estoque Total", f"{df_est['total_kg'].sum() if not df_est.empty else 0:,.2f}")

abas = ["🗄️ GAVETAS VISUAIS", "📝 CADASTRO", "📈 DASHBOARD", "📊 RELATÓRIOS"]
if st.session_state.is_admin: abas.append("👑 ADMIN")
tabs = st.tabs(abas)

with tabs[0]:
    df_est = get_df_estoque()
    try:
        con = sqlite3.connect(DB)
        df_locks = pd.read_sql("SELECT * FROM gaveta_lock", con)
        con.close()
    except: df_locks = pd.DataFrame()

    if st.session_state.gaveta_sel is None:
        st.markdown(f"### 🗄️ Clique para ABRIR - Filtro: {st.session_state.filtro_unidade}")
        for linha in range(0, 20, 4):
            cols = st.columns(4)
            for idx in range(4):
                gid = linha + idx + 1
                if gid>20: continue
                df_g = df_est[df_est["gaveta_id"]==gid] if not df_est.empty else pd.DataFrame()
                total_g = df_g["total_kg"].sum() if not df_g.empty else 0
                qtd_g = len(df_g)
                trancada=False
                if not df_locks.empty:
                    r = df_locks[df_locks["gaveta_id"]==gid]
                    if not r.empty: trancada=bool(r.iloc[0]["trancada"])
                with cols[idx]:
                    classe_extra = "gaveta-trancada" if trancada else ""
                    status_icon = "🔒" if trancada else ("🟢" if total_g>0 else "⚪")
                    st.markdown(f"""<div class="gaveta-fechada {classe_extra}"><div class="gaveta-etiqueta">GAVETA {gid:02d}</div><div class="gaveta-puxador"></div><div style="font-size:10px;">{status_icon} {qtd_g} itens</div><div style="font-size:11px;">{total_g:,.0f}</div></div>""", unsafe_allow_html=True)
                    disabled = trancada and not st.session_state.is_admin
                    if st.button(f"{'🔒' if trancada else '👆 ABRIR'} G{gid:02d}", key=f"open_{gid}", use_container_width=True, disabled=disabled):
                        st.session_state.gaveta_sel = gid
                        st.rerun()
    else:
        sel = st.session_state.gaveta_sel
        if st.button("⬅️ FECHAR GAVETA", type="secondary", use_container_width=True):
            st.session_state.gaveta_sel=None
            st.rerun()
        st.markdown(f"<div class='gaveta-aberta-visual'><h2>🗄️ GAVETA {sel:02d} ABERTA</h2></div>", unsafe_allow_html=True)
        con = sqlite3.connect(DB)
        try: df_mat = pd.read_sql("SELECT * FROM materiais", con)
        except: df_mat = pd.DataFrame()
        if df_mat.empty:
            st.warning("Cadastre material primeiro na aba CADASTRO!")
        else:
            with st.container(border=True):
                st.markdown("#### 🟢 ENTRADA - Dentro da gaveta")
                ce1, ce2, ce3, ce4 = st.columns([2,1,1,1])
                mat_sel = ce1.selectbox("Material:", df_mat["id"].tolist(), format_func=lambda x: f"{df_mat[df_mat.id==x].iloc[0]['codigo']} - {df_mat[df_mat.id==x].iloc[0]['nome']}", key=f"mat_e_{sel}")
                row_m = df_mat[df_mat.id==mat_sel].iloc[0]
                codigo_e = ce2.text_input("Código", value=str(row_m["codigo"]), key=f"cod_e_{sel}")
                marca_e = ce3.text_input("Marca", value=str(row_m["marca"]), key=f"marca_e_{sel}")
                unidade_e = ce4.selectbox("📏 Unidade", LISTA_UNIDADES, key=f"uni_e_{sel}")
                ce5, ce6, ce7 = st.columns(3)
                pal_e = ce5.number_input("Paletes", min_value=1, value=1, key=f"pal_e_{sel}")
                unit_e = ce6.number_input("Unit/Palete", min_value=1, value=56, key=f"unit_e_{sel}")
                kg_e = ce7.number_input(f"Kg/Unit ({get_sigla(unidade_e)})", min_value=0.0001, value=25.0, format="%.4f", key=f"kg_e_{sel}")
                total_preview = calc_kg(pal_e, unit_e, kg_e)
                st.success(f"🧮 {pal_e} x {unit_e} x {kg_e} = {total_preview:,.4f} {get_sigla(unidade_e)}")
                fab_e = st.date_input("Fabricação", value=date.today(), key=f"fab_e_{sel}")
                dias_e = st.number_input("Validade dias", value=90, key=f"dias_e_{sel}")
                lote_e = st.text_input("Lote", key=f"lote_e_{sel}")
                if st.button("🟢 SALVAR ENTRADA DENTRO DA GAVETA", type="primary", use_container_width=True, key=f"btn_e_{sel}"):
                    validade = fab_e + timedelta(days=dias_e)
                    sigla = get_sigla(unidade_e)
                    try:
                        con.execute("INSERT INTO estoque (gaveta_id, codigo, nome, marca, paletes, unit_pal, kg_unit, unidade_medida, unidade_sigla, fab, validade, lote) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                                    (sel, codigo_e, row_m["nome"], marca_e, pal_e, unit_e, kg_e, unidade_e, sigla, fab_e.isoformat(), validade.isoformat(), lote_e))
                        con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, unit_pal, kg_unit, total_kg, usuario, unidade_medida, unidade_sigla) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                    (datetime.now().isoformat(), sel, codigo_e, row_m["nome"], marca_e, "ENTRADA", pal_e, unit_e, kg_e, total_preview, st.session_state.usuario_email, unidade_e, sigla))
                        con.commit()
                        st.success(f"✅ Entrou {total_preview:.4f} {sigla}!")
                        st.balloons()
                        st.rerun()
                    except Exception as e: st.error(f"Erro: {e}")
            try: df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE gaveta_id={sel} ORDER BY id DESC", con)
            except: df_dentro = pd.DataFrame()
            if not df_dentro.empty:
                df_dentro["total_kg"] = df_dentro.apply(lambda r: calc_kg(r["paletes"], r["unit_pal"], r["kg_unit"]), axis=1)
                df_dentro["calc"] = df_dentro.apply(lambda r: f"{r['paletes']} x {r['unit_pal']} x {r['kg_unit']} = {r['total_kg']:.4f} {r.get('unidade_sigla','')}", axis=1)
                st.markdown(f"### 📋 Dentro da Gaveta {sel:02d} - Total: {df_dentro['total_kg'].sum():,.4f}")
                st.dataframe(df_dentro[["id","codigo","marca","unidade_sigla","paletes","unit_pal","kg_unit","calc"]], use_container_width=True)
                st.markdown("### ✏️ ATUALIZAÇÃO")
                try:
                    df_edit = st.data_editor(df_dentro, use_container_width=True, num_rows="dynamic", key=f"edit_{sel}")
                    if st.button("💾 SALVAR ALTERAÇÕES", type="primary", use_container_width=True, key=f"save_{sel}"):
                        con.execute("DELETE FROM estoque WHERE gaveta_id=?", (sel,))
                        df_save = df_edit.drop(columns=[c for c in ["total_kg","calc"] if c in df_edit.columns], errors='ignore')
                        df_save.to_sql("estoque", con, if_exists="append", index=False)
                        con.commit()
                        st.success("Atualizado!")
                        st.rerun()
                except Exception as e: st.error(str(e))
                with st.container(border=True):
                    st.markdown("### 🔴 SAÍDA")
                    id_saida = st.selectbox("Item SAÍDA:", df_dentro["id"].tolist(), format_func=lambda x: f"ID {x} - {df_dentro[df_dentro.id==x].iloc[0]['codigo']} - {df_dentro[df_dentro.id==x].iloc[0]['calc']}", key=f"saida_{sel}")
                    qtd_saida = st.number_input("Qtd Paletes SAÍDA", min_value=1, value=1, key=f"qtd_s_{sel}")
                    row_s = df_dentro[df_dentro.id==id_saida].iloc[0]
                    total_s_prev = calc_kg(qtd_saida, row_s["unit_pal"], row_s["kg_unit"])
                    st.warning(f"🔴 {qtd_saida} x {row_s['unit_pal']} x {row_s['kg_unit']} = {total_s_prev:.4f}")
                    if st.button("🔴 SALVAR SAÍDA", type="primary", use_container_width=True, key=f"btn_s_{sel}"):
                        con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, unit_pal, kg_unit, total_kg, usuario) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                                    (datetime.now().isoformat(), sel, row_s["codigo"], row_s["nome"], row_s["marca"], "SAIDA", qtd_saida, row_s["unit_pal"], row_s["kg_unit"], total_s_prev, st.session_state.usuario_email))
                        if qtd_saida >= row_s["paletes"]:
                            con.execute("DELETE FROM estoque WHERE id=?", (int(id_saida),))
                        else:
                            con.execute("UPDATE estoque SET paletes = paletes -? WHERE id=?", (int(qtd_saida), int(id_saida)))
                        con.commit()
                        st.success("SAÍDA OK")
                        st.rerun()
            else: st.info(f"📭 Gaveta {sel:02d} vazia")
        con.close()
        if st.button("⬅️ FECHAR GAVETA", type="secondary", use_container_width=True, key=f"close_bottom_{sel}"):
            st.session_state.gaveta_sel=None
            st.rerun()

with tabs[1]:
    con = sqlite3.connect(DB)
    try: df_mat = pd.read_sql("SELECT * FROM materiais ORDER BY id DESC", con)
    except: df_mat = pd.DataFrame()
    with st.form("cad_mat", clear_on_submit=True):
        c1,c2,c3,c4 = st.columns(4)
        codigo = c1.text_input("CÓDIGO *")
        nome = c2.text_input("NOME *")
        marca = c3.text_input("MARCA *")
        unidade_sel = c4.selectbox("📏 UNIDADE *", LISTA_UNIDADES)
        c5,c6 = st.columns(2)
        peso = c5.number_input(f"Peso por {get_sigla(unidade_sel)}", value=25.0, format="%.4f")
        categoria = c6.selectbox("Categoria", ["Refratário","Cimento","Manta","Isolante","Ferragem","Outro"])
        if st.form_submit_button("💾 SALVAR", type="primary", use_container_width=True):
            if codigo and nome and marca:
                try:
                    con.execute("INSERT INTO materiais (codigo, nome, marca, categoria, peso, unidade_medida, unidade_sigla) VALUES (?,?,?,?,?,?,?)", (codigo, nome, marca, categoria, peso, unidade_sel, get_sigla(unidade_sel)))
                    con.commit()
                    st.success(f"Salvo: {codigo}")
                except Exception as e: st.error(str(e))
    st.dataframe(df_mat, use_container_width=True)
    con.close()

with tabs[2]:
    df_est = get_df_estoque()
    if not df_est.empty:
        st.plotly_chart(px.bar(df_est.groupby("gaveta_id")["total_kg"].sum().reset_index(), x="gaveta_id", y="total_kg", title="Estoque por Gaveta"), use_container_width=True)

with tabs[3]:
    try:
        con = sqlite3.connect(DB)
        df_hist = pd.read_sql("SELECT * FROM historico ORDER BY data DESC", con)
        con.close()
        st.dataframe(df_hist, use_container_width=True)
    except: st.info("Sem histórico")

if st.session_state.is_admin and len(tabs)>4:
    with tabs[4]:
        st.markdown("## 👑 ADMIN")
        con = sqlite3.connect(DB)
        try: df_users = pd.read_sql("SELECT * FROM usuarios", con)
        except: df_users = pd.DataFrame()
        with st.form("cad_user", clear_on_submit=True):
            c1,c2,c3 = st.columns(3)
            email_new = c1.text_input("Email *")
            nome_new = c2.text_input("Nome *")
            is_admin_new = c3.checkbox("Admin?")
            ativo_new = st.checkbox("Ativo", value=True)
            if st.form_submit_button("💾 CADASTRAR/LIBERAR EMAIL", type="primary", use_container_width=True):
                try:
                    con.execute("INSERT OR REPLACE INTO usuarios (email, nome, is_admin, ativo) VALUES (?,?,?,?)", (email_new.strip().lower(), nome_new, int(is_admin_new), int(ativo_new)))
                    con.commit()
                    st.success("Salvo!")
                except Exception as e: st.error(str(e))
        try: st.dataframe(pd.read_sql("SELECT * FROM usuarios", con), use_container_width=True)
        except: st.error("Erro listar")
        con.close()
