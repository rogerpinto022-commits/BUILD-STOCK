import streamlit as st
import pandas as pd
import sqlite3, os, base64
from datetime import date, datetime, timedelta
import plotly.express as px

st.set_page_config(layout="wide", page_title="Fornos - Gavetas Visuais", page_icon="🗄️")

DB = "estoque_fornos.db"
ADMIN_EMAIL = "admin@fornos.com"

UNIDADES_MEDIDA = {
    "MASSA": ["KG - Quilograma", "G - Grama", "T - Tonelada", "UN - Unidade"],
    "VOLUME": ["L - Litro", "ML - Mililitro", "M³ - Metro cúbico"],
    "COMPRIMENTO": ["M - Metro", "CM - Centímetro", "MM - Milímetro"],
    "GERAL": ["PC - Peça", "CX - Caixa", "SC - Saco", "PL - Palete", "RL - Rolo", "PCT - Pacote", "DZ - Dúzia", "PAR - Par"]
}
LISTA_UNIDADES = []
for cat, lista in UNIDADES_MEDIDA.items():
    for u in lista: LISTA_UNIDADES.append(f"{cat} | {u}")

def get_sigla(u):
    try: return u.split("|")[-1].split(" - ")[0].strip()
    except: return "UN"

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS materiais (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT, nome TEXT, marca TEXT, categoria TEXT, peso REAL, unidade_medida TEXT, unidade_sigla TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS estoque (id INTEGER PRIMARY KEY AUTOINCREMENT, gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT, paletes INT, unit_pal INT, kg_unit REAL, unidade_medida TEXT, unidade_sigla TEXT, fab DATE, validade DATE, lote TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT, tipo TEXT, paletes INT, unit_pal INT, kg_unit REAL, total_kg REAL, usuario TEXT, unidade_medida TEXT, unidade_sigla TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS config (gaveta_id INT PRIMARY KEY, estoque_min REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, nome TEXT, is_admin INTEGER DEFAULT 0, ativo INTEGER DEFAULT 1)""")
    con.execute("""CREATE TABLE IF NOT EXISTS gaveta_lock (gaveta_id INT PRIMARY KEY, trancada INTEGER DEFAULT 0, motivo TEXT)""")
    for i in range(1,21):
        con.execute("INSERT OR IGNORE INTO config (gaveta_id, estoque_min) VALUES (?,?)", (i, 1000))
        con.execute("INSERT OR IGNORE INTO gaveta_lock (gaveta_id, trancada) VALUES (?,0)", (i,))
    con.execute("INSERT OR IGNORE INTO usuarios (email, nome, is_admin, ativo) VALUES (?,?,1,1)", (ADMIN_EMAIL, "Admin"))
    con.commit(); con.close()

if not os.path.exists(DB): init_db()

def calc_kg(p,u,k):
    try: return float(p or 0)*float(u or 0)*float(k or 0)
    except: return 0.0

def get_cols(table):
    con = sqlite3.connect(DB)
    c = con.execute(f"PRAGMA table_info({table})").fetchall()
    con.close()
    return c

def add_col(table, name, typ):
    name = name.strip().lower().replace(" ","_")
    name = ''.join(x for x in name if x.isalnum() or x=='_')
    if not name: return False, "Nome inválido"
    if name in [x[1] for x in get_cols(table)]: return False, "Já existe"
    try:
        con = sqlite3.connect(DB)
        con.execute(f"ALTER TABLE {table} ADD COLUMN {name} {typ}")
        con.commit(); con.close()
        return True, f"Campo {name} criado!"
    except Exception as e: return False, str(e)

if 'logado' not in st.session_state: st.session_state.logado=False
if 'usuario_email' not in st.session_state: st.session_state.usuario_email=""
if 'is_admin' not in st.session_state: st.session_state.is_admin=False
if 'gaveta_sel' not in st.session_state: st.session_state.gaveta_sel=None
if 'filtro_unidade' not in st.session_state: st.session_state.filtro_unidade="TODAS"

def check_login():
    if not st.session_state.logado:
        st.markdown("<div style='background: linear-gradient(90deg, #1E3A8A, #3B82F6); padding:30px; border-radius:20px; color:white; text-align:center;'><h1>🗄️ LOGIN - ARQUIVO DE GAVETAS</h1></div>", unsafe_allow_html=True)
        with st.container(border=True):
            email = st.text_input("📧 Email")
            if st.button("🔓 ENTRAR", type="primary", use_container_width=True):
                con = sqlite3.connect(DB)
                user = con.execute("SELECT * FROM usuarios WHERE email=? AND ativo=1", (email.strip().lower(),)).fetchone()
                con.close()
                if user:
                    st.session_state.logado=True
                    st.session_state.usuario_email=email.strip().lower()
                    st.session_state.is_admin=bool(user[3])
                    st.rerun()
                else: st.error("Email não cadastrado!")
        st.stop()
check_login()

# ===== CSS GAVETAS VISUAIS =====
st.markdown("""
<style>
.main-header { background: linear-gradient(90deg, #1E3A8A, #3B82F6); padding:15px; border-radius:12px; color:white; text-align:center; font-weight:900; font-size:22px; }
.gaveta-fechada {
    background: linear-gradient(180deg, #8A8A8A 0%, #6B6B6B 10%, #5A5A5A 50%, #6B6B6B 90%, #8A8A8A 100%);
    border: 3px solid #3A3A3A;
    border-radius: 6px;
    height: 140px;
    position: relative;
    box-shadow: inset 0 2px 3px rgba(255,255,255,0.3), 0 4px 8px rgba(0,0,0,0.4);
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: white;
    font-weight: 800;
}
.gaveta-fechada:hover { transform: translateY(-3px); box-shadow: inset 0 2px 3px rgba(255,255,255,0.4), 0 8px 16px rgba(0,0,0,0.5); border-color: #3B82F6; }
.gaveta-puxador {
    width: 90px; height: 14px; background: linear-gradient(90deg, #1A1A1A, #3A3A3A, #1A1A1A);
    border-radius: 7px; margin: 8px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.5); border: 1px solid #000;
}
.gaveta-etiqueta {
    background: white; color: black; padding: 2px 8px; border-radius: 3px; font-size: 10px; font-weight: 900;
    border: 1px solid #999; min-width: 60px; text-align: center;
}
.gaveta-trancada { background: linear-gradient(180deg, #DC2626 0%, #991B1B 100%)!important; border-color: #7F1D1D!important; }
.gaveta-aberta-visual {
    background: #F8FAFC; border: 4px solid #16A34A; border-top: 12px solid #16A34A;
    border-radius: 0 0 20px 20px; padding: 25px; margin-top: 15px;
    box-shadow: inset 0 10px 20px rgba(0,0,0,0.1), 0 10px 30px rgba(0,0,0,0.2);
    min-height: 400px;
}
.gaveta-vazia { background: #111827; color: #6B7280; padding: 40px; border-radius: 10px; text-align: center; border: 3px dashed #374151; }
</style>
""", unsafe_allow_html=True)

def get_df_estoque():
    con = sqlite3.connect(DB)
    try: df = pd.read_sql("SELECT * FROM estoque", con)
    except: df = pd.DataFrame()
    con.close()
    if not df.empty:
        for c in ["paletes","unit_pal","kg_unit"]:
            if c not in df.columns: df[c]=0
        df["total_kg"] = df.apply(lambda r: calc_kg(r["paletes"], r["unit_pal"], r["kg_unit"]), axis=1)
        if "unidade_sigla" not in df.columns: df["unidade_sigla"]="KG"
        df["validade"] = pd.to_datetime(df["validade"], errors='coerce')
        df["dias_vencer"] = (df["validade"] - pd.to_datetime(date.today())).dt.days
    return df

def get_df_historico():
    con = sqlite3.connect(DB)
    try: df = pd.read_sql("SELECT * FROM historico ORDER BY data DESC", con)
    except: df = pd.DataFrame()
    con.close()
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"], errors='coerce')
    return df

# HEADER
st.markdown(f"<div class='main-header'>🗄️ ARQUIVO DE AÇO - 20 GAVETAS | Usuário: {st.session_state.usuario_email} {'👑 ADMIN' if st.session_state.is_admin else ''}</div>", unsafe_allow_html=True)

# SIDEBAR FILTRO UNIDADE
with st.sidebar:
    st.markdown(f"👤 {st.session_state.usuario_email}")
    if st.button("🚪 Sair"):
        st.session_state.logado=False
        st.rerun()
    st.divider()
    st.markdown("### 📏 Filtro Unidade")
    filtro_un = st.selectbox("Filtrar por", ["TODAS"] + LISTA_UNIDADES, key="filtro_side")
    if st.button("🔍 Aplicar Filtro", use_container_width=True, type="primary"):
        st.session_state.filtro_unidade = filtro_un
        st.session_state.gaveta_sel = None
        st.rerun()
    if st.button("🧹 Limpar", use_container_width=True):
        st.session_state.filtro_unidade="TODAS"
        st.session_state.gaveta_sel=None
        st.rerun()

    df_est = get_df_estoque()
    if st.session_state.filtro_unidade!="TODAS" and not df_est.empty:
        df_f = df_est[df_est["unidade_medida"]==st.session_state.filtro_unidade] if "unidade_medida" in df_est.columns else df_est
        st.metric(f"Filtrado {get_sigla(st.session_state.filtro_unidade)}", f"{df_f['total_kg'].sum():,.2f}")
    else:
        st.metric("Estoque Total", f"{df_est['total_kg'].sum() if not df_est.empty else 0:,.2f}")

abas = ["🗄️ GAVETAS VISUAIS", "📝 CADASTRO", "📈 DASHBOARD", "📊 RELATÓRIOS"]
if st.session_state.is_admin: abas.append("👑 ADMIN")
tabs = st.tabs(abas)

# ===== ABA GAVETAS VISUAIS - INTERFACE PRINCIPAL =====
with tabs[0]:
    df_est = get_df_estoque()
    con = sqlite3.connect(DB)
    df_locks = pd.read_sql("SELECT * FROM gaveta_lock", con)
    con.close()

    # SE NENHUMA GAVETA SELECIONADA -> MOSTRA ARQUIVO DE GAVETAS
    if st.session_state.gaveta_sel is None:
        st.markdown(f"### 🗄️ Clique na gaveta para ABRIR - Filtro atual: **{st.session_state.filtro_unidade}**")
        st.markdown("**Como funciona:** Clique na gaveta → Ela abre → Faça Entrada/Saída/Verificação dentro dela")

        # GRID 4x5 GAVETAS VISUAIS
        for linha in range(0, 20, 4):
            cols = st.columns(4)
            for idx in range(4):
                gid = linha + idx + 1
                if gid > 20: continue

                # Dados da gaveta
                df_g = df_est[df_est["gaveta_id"]==gid] if not df_est.empty else pd.DataFrame()
                if st.session_state.filtro_unidade!="TODAS" and not df_g.empty and "unidade_medida" in df_g.columns:
                    df_g = df_g[df_g["unidade_medida"]==st.session_state.filtro_unidade]

                total_g = df_g["total_kg"].sum() if not df_g.empty else 0
                qtd_g = len(df_g)

                trancada=False
                motivo=""
                if not df_locks.empty:
                    r = df_locks[df_locks["gaveta_id"]==gid]
                    if not r.empty:
                        trancada=bool(r.iloc[0]["trancada"])
                        motivo=r.iloc[0]["motivo"]

                with cols[idx]:
                    # HTML da gaveta visual
                    classe_extra = "gaveta-trancada" if trancada else ""
                    status_icon = "🔒" if trancada else ("🟢" if total_g>0 else "⚪")

                    st.markdown(f"""
                    <div class="gaveta-fechada {classe_extra}">
                        <div class="gaveta-etiqueta">GAVETA {gid:02d}</div>
                        <div class="gaveta-puxador"></div>
                        <div style="font-size:11px; margin-top:4px;">{status_icon} {qtd_g} itens</div>
                        <div style="font-size:12px; font-weight:900;">{total_g:,.0f} {df_g.iloc[0]['unidade_sigla'] if not df_g.empty and 'unidade_sigla' in df_g.columns else 'KG' if total_g>0 else ''}</div>
                        <div style="font-size:9px; opacity:0.8;">{motivo[:15] if trancada else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Botão invisível para clicar
                    disabled = trancada and not st.session_state.is_admin
                    if st.button(f"{'🔒 TRANCADA' if trancada else '👆 CLICAR PARA ABRIR'} - Gaveta {gid:02d}", key=f"open_{gid}", use_container_width=True, disabled=disabled, type="secondary"):
                        st.session_state.gaveta_sel = gid
                        st.rerun()

        # Resumo visual
        if not df_est.empty:
            st.divider()
            c1,c2 = st.columns(2)
            with c1:
                df_gav = df_est.groupby("gaveta_id")["total_kg"].sum().reset_index()
                st.plotly_chart(px.bar(df_gav, x="gaveta_id", y="total_kg", title="Ocupação por Gaveta", color="total_kg", text="total_kg"), use_container_width=True)
            with c2:
                if "unidade_sigla" in df_est.columns:
                    df_un = df_est.groupby("unidade_sigla")["total_kg"].sum().reset_index()
                    st.plotly_chart(px.pie(df_un, values="total_kg", names="unidade_sigla", title="Por Unidade de Medida", hole=0.4), use_container_width=True)

    # SE GAVETA SELECIONADA -> MOSTRA CONTEÚDO ABERTO
    else:
        sel = st.session_state.gaveta_sel
        trancada=False
        motivo=""
        if not df_locks.empty:
            r = df_locks[df_locks["gaveta_id"]==sel]
            if not r.empty:
                trancada=bool(r.iloc[0]["trancada"])
                motivo=r.iloc[0]["motivo"]

        if trancada and not st.session_state.is_admin:
            st.error(f"🔒 Gaveta {sel:02d} TRANCADA: {motivo}")
            if st.button("⬅️ Voltar para arquivo"):
                st.session_state.gaveta_sel=None
                st.rerun()
            st.stop()

        # Botão voltar
        if st.button("⬅️ FECHAR GAVETA E VOLTAR PARA ARQUIVO", type="secondary", use_container_width=True):
            st.session_state.gaveta_sel=None
            st.rerun()

        st.markdown(f"""
        <div class="gaveta-aberta-visual">
            <h1>🗄️ GAVETA {sel:02d} ABERTA {'🔒 TRANCADA' if trancada else '🔓 LIBERADA'} - {st.session_state.filtro_unidade if st.session_state.filtro_unidade!='TODAS' else 'Todas Unidades'}</h1>
            <p>📦 Tudo que está aqui dentro fica armazenado nesta gaveta. Faça entrada, saída e verificação.</p>
        </div>
        """, unsafe_allow_html=True)

        con = sqlite3.connect(DB)
        df_mat = pd.read_sql("SELECT * FROM materiais", con)
        if df_mat.empty:
            st.warning("Cadastre material na aba CADASTRO primeiro!")
            if st.button("Ir para Cadastro"):
                st.session_state.gaveta_sel=None
                st.rerun()
            st.stop()

        # Filtra materiais pela unidade
        if st.session_state.filtro_unidade!="TODAS":
            df_mat_f = df_mat[df_mat["unidade_medida"]==st.session_state.filtro_unidade] if "unidade_medida" in df_mat.columns else pd.DataFrame()
            if not df_mat_f.empty:
                df_mat = df_mat_f

        # ENTRADA DENTRO DA GAVETA ABERTA
        with st.container(border=True):
            st.markdown("### 🟢 1. ENTRADA - Colocar material DENTRO desta gaveta")
            ce1, ce2, ce3, ce4 = st.columns([2,1,1,1])
            mat_sel = ce1.selectbox("Material cadastrado:", df_mat["id"].tolist(), format_func=lambda x: f"{df_mat[df_mat.id==x].iloc[0]['codigo']} - {df_mat[df_mat.id==x].iloc[0]['nome']} - {df_mat[df_mat.id==x].iloc[0]['marca']} ({df_mat[df_mat.id==x].iloc[0]['unidade_sigla'] if 'unidade_sigla' in df_mat.columns else 'KG'})", key=f"mat_e_{sel}")
            row_m = df_mat[df_mat.id==mat_sel].iloc[0]
            codigo_e = ce2.text_input("Código", value=str(row_m["codigo"]), key=f"cod_e_{sel}")
            marca_e = ce3.text_input("Marca", value=str(row_m["marca"]), key=f"marca_e_{sel}")
            unidade_e = ce4.selectbox("📏 Unidade", LISTA_UNIDADES, index=LISTA_UNIDADES.index(row_m["unidade_medida"]) if "unidade_medida" in row_m and row_m["unidade_medida"] in LISTA_UNIDADES else 0, key=f"uni_e_{sel}")

            ce5, ce6, ce7 = st.columns(3)
            pal_e = ce5.number_input("1️⃣ Paletes", min_value=1, value=1, key=f"pal_e_{sel}")
            unit_e = ce6.number_input("2️⃣ Unit/Palete", min_value=1, value=56, key=f"unit_e_{sel}")
            kg_e = ce7.number_input(f"3️⃣ Kg/Unit ({get_sigla(unidade_e)})", min_value=0.0001, value=float(row_m["peso"]) if "peso" in df_mat.columns else 25.0, format="%.4f", key=f"kg_e_{sel}")

            total_preview = calc_kg(pal_e, unit_e, kg_e)
            st.success(f"🧮 CÁLCULO CORRETO: {pal_e} x {unit_e} x {kg_e} = {total_preview:,.4f} {get_sigla(unidade_e)} - Vai entrar na Gaveta {sel:02d}")

            fab_e = st.date_input("Fabricação", value=date.today(), key=f"fab_e_{sel}")
            dias_e = st.number_input("Validade dias", value=90, key=f"dias_e_{sel}")
            lote_e = st.text_input("Lote/Obs", key=f"lote_e_{sel}")

            if st.button("🟢 SALVAR ENTRADA - GRAVA DENTRO DA GAVETA", type="primary", use_container_width=True, key=f"btn_e_{sel}"):
                validade = fab_e + timedelta(days=dias_e)
                sigla = get_sigla(unidade_e)
                con.execute("INSERT INTO estoque (gaveta_id, codigo, nome, marca, paletes, unit_pal, kg_unit, unidade_medida, unidade_sigla, fab, validade, lote) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            (sel, codigo_e, row_m["nome"], marca_e, pal_e, unit_e, kg_e, unidade_e, sigla, fab_e.isoformat(), validade.isoformat(), lote_e))
                con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, unit_pal, kg_unit, total_kg, usuario, unidade_medida, unidade_sigla) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (datetime.now().isoformat(), sel, codigo_e, row_m["nome"], marca_e, "ENTRADA", pal_e, unit_e, kg_e, total_preview, st.session_state.usuario_email, unidade_e, sigla))
                con.commit()
                st.success(f"✅ Entrou {total_preview:.4f} {sigla} na Gaveta {sel:02d}!")
                st.balloons()
                st.rerun()

        # CONTEÚDO DENTRO DA GAVETA - VERIFICAÇÃO E ATUALIZAÇÃO
        df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE gaveta_id={sel} ORDER BY id DESC", con)

        if st.session_state.filtro_unidade!="TODAS" and not df_dentro.empty and "unidade_medida" in df_dentro.columns:
            df_dentro = df_dentro[df_dentro["unidade_medida"]==st.session_state.filtro_unidade]

        if not df_dentro.empty:
            df_dentro["total_kg"] = df_dentro.apply(lambda r: calc_kg(r["paletes"], r["unit_pal"], r["kg_unit"]), axis=1)
            df_dentro["calc"] = df_dentro.apply(lambda r: f"{r['paletes']} x {r['unit_pal']} x {r['kg_unit']} = {r['total_kg']:.4f} {r.get('unidade_sigla','')}", axis=1)
            df_dentro["validade"] = pd.to_datetime(df_dentro["validade"], errors='coerce')
            df_dentro["dias_vencer"] = (df_dentro["validade"] - pd.to_datetime(date.today())).dt.days
            df_dentro["status"] = df_dentro["dias_vencer"].apply(lambda x: "🔴 VENCIDO" if pd.notna(x) and x<0 else ("🟡 30d" if pd.notna(x) and x<=30 else "🟢 OK"))

            st.markdown("### 📋 2. VERIFICAÇÃO - O que tem DENTRO desta gaveta")
            st.markdown(f"**Total dentro da Gaveta {sel:02d}: {df_dentro['total_kg'].sum():,.4f} - {len(df_dentro)} itens**")

            # Tabela visual de dentro
            st.dataframe(df_dentro[["id","codigo","nome","marca","unidade_sigla","paletes","unit_pal","kg_unit","calc","status","lote"]], use_container_width=True, height=250)

            # EDIÇÃO TOTAL - ATUALIZAÇÃO DE ESTOQUE
            st.markdown("### ✏️ 3. ATUALIZAÇÃO DE ESTOQUE - Edite tudo e salve")
            df_edit = st.data_editor(df_dentro, use_container_width=True, num_rows="dynamic", key=f"edit_{sel}",
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "total_kg": st.column_config.NumberColumn("Total", disabled=True),
                    "calc": st.column_config.TextColumn("Cálculo", disabled=True),
                })

            if st.button("💾 SALVAR ALTERAÇÕES - ATUALIZA ESTOQUE DA GAVETA", type="primary", use_container_width=True, key=f"save_{sel}"):
                try:
                    con.execute("DELETE FROM estoque WHERE gaveta_id=?", (sel,))
                    df_save = df_edit.copy()
                    for c in ["total_kg","calc","dias_vencer","status"]:
                        if c in df_save.columns: df_save = df_save.drop(columns=[c], errors='ignore')
                    df_save.to_sql("estoque", con, if_exists="append", index=False)
                    con.commit()
                    st.success(f"✅ Gaveta {sel:02d} atualizada!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

            # SAÍDA DENTRO DA GAVETA
            st.divider()
            with st.container(border=True):
                st.markdown("### 🔴 4. SAÍDA - Retirar material desta gaveta")
                cs1, cs2 = st.columns(2)
                id_saida = cs1.selectbox("Escolha item para SAÍDA:", df_dentro["id"].tolist(), format_func=lambda x: f"ID {x} - {df_dentro[df_dentro.id==x].iloc[0]['codigo']} - {df_dentro[df_dentro.id==x].iloc[0]['marca']} - {df_dentro[df_dentro.id==x].iloc[0]['calc']} - {df_dentro[df_dentro.id==x].iloc[0]['status']}", key=f"saida_{sel}")
                qtd_saida = cs2.number_input("Qtd Paletes SAÍDA", min_value=1, value=1, key=f"qtd_s_{sel}")
                row_s = df_dentro[df_dentro.id==id_saida].iloc[0]
                total_s_prev = calc_kg(qtd_saida, row_s["unit_pal"], row_s["kg_unit"])
                st.warning(f"🔴 SAÍDA: {qtd_saida} x {row_s['unit_pal']} x {row_s['kg_unit']} = {total_s_prev:.4f} {row_s.get('unidade_sigla','')} - Vai sair da Gaveta {sel:02d}")

                if st.button("🔴 SALVAR SAÍDA - RETIRA DA GAVETA", type="primary", use_container_width=True, key=f"btn_s_{sel}"):
                    con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, unit_pal, kg_unit, total_kg, usuario, unidade_medida, unidade_sigla) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                (datetime.now().isoformat(), sel, row_s["codigo"], row_s["nome"], row_s["marca"], "SAIDA", qtd_saida, row_s["unit_pal"], row_s["kg_unit"], total_s_prev, st.session_state.usuario_email, row_s.get("unidade_medida",""), row_s.get("unidade_sigla","")))
                    if qtd_saida >= row_s["paletes"]:
                        con.execute("DELETE FROM estoque WHERE id=?", (int(id_saida),))
                    else:
                        con.execute("UPDATE estoque SET paletes = paletes -? WHERE id=?", (int(qtd_saida), int(id_saida)))
                    con.commit()
                    st.success(f"✅ SAÍDA {total_s_prev:.4f} {row_s.get('unidade_sigla','')} da Gaveta {sel:02d}")
                    st.rerun()

            # Gráfico da gaveta aberta
            st.divider()
            df_hist_gav = pd.read_sql(f"SELECT * FROM historico WHERE gaveta_id={sel} ORDER BY data", con)
            if not df_hist_gav.empty:
                df_hist_gav["data"] = pd.to_datetime(df_hist_gav["data"])
                st.plotly_chart(px.bar(df_hist_gav, x="data", y="total_kg", color="tipo", title=f"Histórico Gaveta {sel:02d} - Entradas x Saídas", color_discrete_map={"ENTRADA":"#16A34A","SAIDA":"#DC2626"}), use_container_width=True)

        else:
            st.markdown(f"""
            <div class="gaveta-vazia">
                <h2>📭 Gaveta {sel:02d} Vazia</h2>
                <p>Nenhum material dentro. Filtro atual: {st.session_state.filtro_unidade}</p>
                <p>Faça uma ENTRADA acima para armazenar material aqui dentro.</p>
            </div>
            """, unsafe_allow_html=True)

        con.close()

        # Botão fechar no final também
        if st.button("⬅️ FECHAR GAVETA", type="secondary", use_container_width=True, key=f"close_{sel}"):
            st.session_state.gaveta_sel=None
            st.rerun()

with tabs[1]:
    con = sqlite3.connect(DB)
    st.markdown("### 📝 Cadastro - ID Livre + Marca + Unidade")
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
                con.execute("INSERT INTO materiais (codigo, nome, marca, categoria, peso, unidade_medida, unidade_sigla) VALUES (?,?,?,?,?,?,?)", (codigo, nome, marca, categoria, peso, unidade_sel, get_sigla(unidade_sel)))
                con.commit()
                st.success(f"Salvo: {codigo} - {marca} - {unidade_sel}")
    df_mat = pd.read_sql("SELECT * FROM materiais ORDER BY id DESC", con)
    st.dataframe(df_mat, use_container_width=True)
    con.close()

with tabs[2]:
    df_est = get_df_estoque()
    df_hist = get_df_historico()
    if not df_est.empty:
        st.plotly_chart(px.bar(df_est.groupby("gaveta_id")["total_kg"].sum().reset_index(), x="gaveta_id", y="total_kg", title="Estoque por Gaveta", color="total_kg"), use_container_width=True)
    if not df_hist.empty:
        df_hist["periodo"] = df_hist["data"].dt.to_period("M").astype(str)
        st.plotly_chart(px.bar(df_hist.groupby(["periodo","tipo"])["total_kg"].sum().reset_index(), x="periodo", y="total_kg", color="tipo", barmode="group"), use_container_width=True)

with tabs[3]:
    df_hist = get_df_historico()
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True)
    else: st.info("Sem histórico")

if st.session_state.is_admin and len(tabs)>4:
    with tabs[4]:
        st.markdown("## 👑 ADMIN - TUDO EDITÁVEL")
        st.markdown("### 🛠️ Criar Campo na Tabela")
        with st.container(border=True):
            c1,c2,c3 = st.columns(3)
            tabela_alvo = c1.selectbox("Tabela", ["estoque","materiais","historico"])
            nome_campo = c2.text_input("Nome campo", placeholder="Ex: cor, tamanho")
            tipo_campo = c3.selectbox("Tipo", ["TEXT","INTEGER","REAL","DATE"])
            st.caption(f"Campos atuais: {', '.join([c[1] for c in get_cols(tabela_alvo)])}")
            if st.button("➕ CRIAR CAMPO", type="primary", use_container_width=True):
                if nome_campo:
                    ok, msg = add_col(tabela_alvo, nome_campo, tipo_campo)
                    if ok: st.success(msg); st.rerun()
                    else: st.error(msg)

        st.divider()
        st.markdown("### 🔒 Trancar/Liberar Gavetas")
        con = sqlite3.connect(DB)
        c1,c2,c3 = st.columns(3)
        gav_tranca = c1.selectbox("Gaveta", list(range(1,21)))
        acao = c2.selectbox("Ação", ["🔓 LIBERAR", "🔒 TRANCAR"])
        motivo = c3.text_input("Motivo")
        if st.button("💾 SALVAR TRAVA", type="primary"):
            val = 1 if "TRANCAR" in acao else 0
            con.execute("UPDATE gaveta_lock SET trancada=?, motivo=? WHERE gaveta_id=?", (val, motivo, gav_tranca))
            con.commit()
            st.success(f"Gaveta {gav_tranca:02d} {'TRANCADA' if val else 'LIBERADA'}!")
        st.dataframe(pd.read_sql("SELECT * FROM gaveta_lock", con), use_container_width=True)

        st.divider()
        st.markdown("### 👥 Usuários - Cadastro Email")
        with st.form("cad_user", clear_on_submit=True):
            c1,c2,c3 = st.columns(3)
            email_new = c1.text_input("Email *")
            nome_new = c2.text_input("Nome *")
            is_admin_new = c3.checkbox("Admin?")
            ativo_new = st.checkbox("Ativo", value=True)
            if st.form_submit_button("💾 CADASTRAR EMAIL", type="primary", use_container_width=True):
                try:
                    con.execute("INSERT INTO usuarios (email, nome, is_admin, ativo) VALUES (?,?,?,?) ON CONFLICT(email) DO UPDATE SET nome=?, is_admin=?, ativo=?",
                                (email_new.strip().lower(), nome_new, int(is_admin_new), int(ativo_new), nome_new, int(is_admin_new), int(ativo_new)))
                    con.commit()
                    st.success("Salvo!")
                except Exception as e: st.error(str(e))
        st.dataframe(pd.read_sql("SELECT * FROM usuarios", con), use_container_width=True)
        con.close()
