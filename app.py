import streamlit as st
import pandas as pd
import sqlite3, os
from datetime import date, datetime, timedelta
import plotly.express as px

st.set_page_config(layout="wide", page_title="Reforma Fornos - Controle Total", page_icon="🔧", initial_sidebar_state="expanded")

DB = "estoque_fornos.db"

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS materiais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT, nome TEXT, marca TEXT, categoria TEXT, peso REAL, fornecedor TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT,
        paletes INT, unit_pal INT, kg_unit REAL,
        fab DATE, validade DATE, lote TEXT, obs TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT, gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT,
        tipo TEXT, paletes INT, unit_pal INT, kg_unit REAL, total_kg REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS config (
        gaveta_id INT PRIMARY KEY, estoque_min REAL)""")
    for i in range(1, 21):
        con.execute("INSERT OR IGNORE INTO config (gaveta_id, estoque_min) VALUES (?,?)", (i, 1000))
    con.commit()
    con.close()

# RESET AUTOMÁTICO SE BANCO VELHO DER ERRO
def reset_if_error():
    try:
        con = sqlite3.connect(DB)
        # Testa todas as colunas necessárias
        con.execute("SELECT paletes, unit_pal, kg_unit FROM estoque LIMIT 1").fetchall()
        con.execute("SELECT paletes, unit_pal, kg_unit, total_kg FROM historico LIMIT 1").fetchall()
        con.close()
        return False
    except Exception as e:
        con.close()
        if os.path.exists(DB):
            os.remove(DB)
        init_db()
        return True

if not os.path.exists(DB):
    init_db()
else:
    if reset_if_error():
        st.warning("⚠️ Banco antigo detectado e corrigido! Recarregando...")
        st.rerun()

def calc_kg(paletes, unit_pal, kg_unit):
    try:
        return float(paletes or 0) * float(unit_pal or 0) * float(kg_unit or 0)
    except:
        return 0.0

if 'gaveta_sel' not in st.session_state: st.session_state.gaveta_sel = 1

st.markdown("""
<style>
.main-header { background: linear-gradient(90deg, #1E3A8A, #3B82F6); padding: 22px; border-radius: 15px; text-align: center; color: white; font-size: 28px; font-weight: 900; }
.calc-box { background: #EFF6FF; border: 2px dashed #3B82F6; padding: 12px; border-radius: 10px; font-weight: 800; text-align: center; font-size: 18px; color: #1E3A8A; }
</style>
<div class="main-header">🔧 REFORMA DE FORNOS - CONTROLE TOTAL - CÁLCULO CORRIGIDO</div>
""", unsafe_allow_html=True)

def get_df_estoque():
    try:
        con = sqlite3.connect(DB)
        df = pd.read_sql("SELECT * FROM estoque", con)
        con.close()
        if not df.empty:
            # Garante colunas
            for col in ["paletes","unit_pal","kg_unit"]:
                if col not in df.columns:
                    df[col] = 0
            df["total_kg"] = df.apply(lambda r: calc_kg(r["paletes"], r["unit_pal"], r["kg_unit"]), axis=1)
            df["validade"] = pd.to_datetime(df["validade"], errors='coerce')
            df["dias_vencer"] = (df["validade"] - pd.to_datetime(date.today())).dt.days
        return df
    except:
        return pd.DataFrame()

def get_df_historico():
    try:
        con = sqlite3.connect(DB)
        df = pd.read_sql("SELECT * FROM historico ORDER BY data DESC", con)
        con.close()
        if not df.empty:
            df["data"] = pd.to_datetime(df["data"], errors='coerce')
            # Se já tem total_kg salvo, usa ele, senão calcula
            if "total_kg" not in df.columns or df["total_kg"].isna().all():
                for col in ["paletes","unit_pal","kg_unit"]:
                    if col not in df.columns:
                        df[col] = 0
                df["total_kg"] = df.apply(lambda r: calc_kg(r.get("paletes",0), r.get("unit_pal",0), r.get("kg_unit",0)), axis=1)
            df["total_kg"] = pd.to_numeric(df["total_kg"], errors='coerce').fillna(0)
        return df
    except Exception as e:
        # st.error(f"Erro histórico: {e}")
        return pd.DataFrame()

# SIDEBAR
with st.sidebar:
    df_est = get_df_estoque()
    df_hist = get_df_historico()

    total_kg = df_est["total_kg"].sum() if not df_est.empty else 0
    total_itens = len(df_est)

    st.metric("📦 Estoque Total", f"{total_kg:,.2f} KG")
    st.metric("📋 Itens", total_itens)

    if not df_hist.empty:
        entradas = df_hist[df_hist["tipo"]=="ENTRADA"]["total_kg"].sum()
        saidas = df_hist[df_hist["tipo"]=="SAIDA"]["total_kg"].sum()
        st.metric("🟢 Entradas", f"{entradas:,.2f} KG")
        st.metric("🔴 Saídas", f"{saidas:,.2f} KG")

    st.divider()
    st.markdown("### 📦 GAVETAS")
    c1, c2 = st.columns(2)
    for i in range(1,21):
        col = c1 if i%2==1 else c2
        if col.button(f"G{i:02d}", key=f"side_{i}", use_container_width=True, type="primary" if st.session_state.gaveta_sel==i else "secondary"):
            st.session_state.gaveta_sel = i
            st.rerun()

    if st.button("🗑️ RESETAR BANCO (se der erro)", use_container_width=True):
        if os.path.exists(DB):
            os.remove(DB)
        st.rerun()

tab_dash, tab_cad, tab_gavetas, tab_rel = st.tabs(["📈 DASHBOARD", "📝 CADASTRO", "📦 GAVETAS - ENTRADA/SAÍDA/SALVAR", "📊 RELATÓRIOS"])

with tab_dash:
    st.markdown("## 📈 Dashboard")
    df_est = get_df_estoque()
    df_hist = get_df_historico()

    c1,c2,c3 = st.columns(3)
    c1.metric("Estoque Total", f"{total_kg:,.2f} KG")
    c2.metric("Itens", total_itens)
    c3.metric("Saldo Entrada-Saída", f"{(df_hist[df_hist['tipo']=='ENTRADA']['total_kg'].sum() - df_hist[df_hist['tipo']=='SAIDA']['total_kg'].sum()) if not df_hist.empty else 0:,.2f} KG")

    if not df_est.empty:
        col1, col2 = st.columns(2)
        with col1:
            df_gav = df_est.groupby("gaveta_id")["total_kg"].sum().reset_index()
            fig1 = px.bar(df_gav, x="gaveta_id", y="total_kg", title="Estoque por Gaveta", color="total_kg", text="total_kg")
            fig1.update_traces(texttemplate='%{text:.0f} KG', textposition='outside')
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            df_marca = df_est.groupby("marca")["total_kg"].sum().reset_index()
            fig2 = px.pie(df_marca, values="total_kg", names="marca", title="Por Marca", hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)

        # Validade
        df_est["status"] = df_est["dias_vencer"].apply(lambda x: "🔴 Vencido" if pd.notna(x) and x<0 else ("🟡 30d" if pd.notna(x) and x<=30 else "🟢 OK"))
        fig3 = px.bar(df_est, x="status", y="total_kg", color="status", title="Validade", color_discrete_map={"🔴 Vencido":"#DC2626","🟡 30d":"#F59E0B","🟢 OK":"#16A34A"})
        st.plotly_chart(fig3, use_container_width=True)

    if not df_hist.empty:
        st.divider()
        periodo = st.selectbox("Agrupar por:", ["Diário","Semanal","Mensal","Semestral","Anual"], key="dash_per")
        df_hist["periodo"] = df_hist["data"]
        if periodo=="Diário": df_hist["periodo"] = df_hist["data"].dt.date
        elif periodo=="Semanal": df_hist["periodo"] = df_hist["data"].dt.strftime("%Y-W%U")
        elif periodo=="Mensal": df_hist["periodo"] = df_hist["data"].dt.to_period("M").astype(str)
        elif periodo=="Semestral": df_hist["periodo"] = df_hist["data"].dt.year.astype(str) + "-S" + ((df_hist["data"].dt.month-1)//6 +1).astype(str)
        else: df_hist["periodo"] = df_hist["data"].dt.year

        df_group = df_hist.groupby(["periodo","tipo"])["total_kg"].sum().reset_index()
        fig_h = px.bar(df_group, x="periodo", y="total_kg", color="tipo", barmode="group", title=f"Entradas x Saídas - {periodo}", color_discrete_map={"ENTRADA":"#16A34A","SAIDA":"#DC2626"})
        st.plotly_chart(fig_h, use_container_width=True)

with tab_cad:
    st.markdown("## 📝 Cadastro ID LIVRE + MARCA - pode repetir")
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
        if st.form_submit_button("💾 SALVAR MATERIAL", type="primary", use_container_width=True):
            if codigo and nome and marca:
                con.execute("INSERT INTO materiais (codigo, nome, marca, categoria, peso, fornecedor) VALUES (?,?,?,?,?,?)", (codigo, nome, marca, categoria, peso, fornecedor))
                con.commit()
                st.success(f"Salvo: {codigo} - {marca}")
            else:
                st.error("Preencha Código, Nome e Marca")
    df_mat = pd.read_sql("SELECT * FROM materiais ORDER BY id DESC", con)
    st.dataframe(df_mat, use_container_width=True)
    con.close()

with tab_gavetas:
    st.markdown("### 📦 Gavetas - Clique para abrir")
    cols = st.columns(5)
    con = sqlite3.connect(DB)
    for i in range(1,21):
        try:
            df_g = pd.read_sql(f"SELECT paletes, unit_pal, kg_unit FROM estoque WHERE gaveta_id={i}", con)
            total_g = df_g.apply(lambda r: calc_kg(r["paletes"], r["unit_pal"], r["kg_unit"]), axis=1).sum() if not df_g.empty else 0
        except:
            total_g = 0
        with cols[(i-1)%5]:
            if st.button(f"📦 Gaveta {i:02d}\n{total_g:,.0f} KG", key=f"g_{i}", use_container_width=True, type="primary" if st.session_state.gaveta_sel==i else "secondary"):
                st.session_state.gaveta_sel = i
                st.rerun()
    con.close()

    sel = st.session_state.gaveta_sel
    con = sqlite3.connect(DB)
    df_mat = pd.read_sql("SELECT * FROM materiais", con)
    if df_mat.empty:
        st.warning("Cadastre material primeiro!")
        st.stop()

    st.divider()
    st.markdown(f"# 📂 GAVETA {sel:02d}")

    # Config mínimo
    df_config = pd.read_sql(f"SELECT * FROM config WHERE gaveta_id={sel}", con)
    min_atual = float(df_config.iloc[0]["estoque_min"]) if not df_config.empty else 1000.0
    c_min1, c_min2 = st.columns(2)
    novo_min = c_min1.number_input(f"Estoque Mínimo Gaveta {sel} KG", value=min_atual, step=100.0, key=f"min_{sel}")
    if c_min1.button("💾 SALVAR MÍNIMO", key=f"btn_min_{sel}"):
        con.execute("UPDATE config SET estoque_min=? WHERE gaveta_id=?", (novo_min, sel))
        con.commit()
        st.success(f"Mínimo {novo_min} KG salvo")

    # ENTRADA
    with st.container(border=True):
        st.markdown("#### 🟢 ENTRADA")
        ce1, ce2, ce3 = st.columns([2,1,1])
        mat_sel = ce1.selectbox("Material:", df_mat["id"].tolist(), format_func=lambda x: f"{df_mat[df_mat.id==x].iloc[0]['codigo']} - {df_mat[df_mat.id==x].iloc[0]['nome']} - {df_mat[df_mat.id==x].iloc[0]['marca']}", key=f"mat_e_{sel}")
        row_m = df_mat[df_mat.id==mat_sel].iloc[0]
        codigo_e = ce2.text_input("Código", value=row_m["codigo"], key=f"cod_e_{sel}")
        marca_e = ce3.text_input("Marca", value=row_m["marca"], key=f"marca_e_{sel}")

        ce4, ce5, ce6 = st.columns(3)
        pal_e = ce4.number_input("1️⃣ Paletes", min_value=1, value=1, key=f"pal_e_{sel}")
        unit_e = ce5.number_input("2️⃣ Unit/Palete", min_value=1, value=56, key=f"unit_e_{sel}")
        kg_e = ce6.number_input("3️⃣ Kg/Unit", min_value=0.1, value=float(row_m["peso"]), format="%.2f", key=f"kg_e_{sel}")

        total_preview = calc_kg(pal_e, unit_e, kg_e)
        st.markdown(f'<div class="calc-box">🧮 CÁLCULO CORRETO: {pal_e} x {unit_e} x {kg_e} = {total_preview:,.2f} KG</div>', unsafe_allow_html=True)

        fab_e = st.date_input("Fabricação", value=date.today(), key=f"fab_e_{sel}")
        dias_e = st.number_input("Validade dias", value=90, key=f"dias_e_{sel}")
        lote_e = st.text_input("Lote/Obs", key=f"lote_e_{sel}")

        if st.button("🟢 SALVAR ENTRADA - ATUALIZA ESTOQUE", type="primary", use_container_width=True, key=f"btn_e_{sel}"):
            validade = fab_e + timedelta(days=dias_e)
            con.execute("INSERT INTO estoque (gaveta_id, codigo, nome, marca, paletes, unit_pal, kg_unit, fab, validade, lote) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (sel, codigo_e, row_m["nome"], marca_e, pal_e, unit_e, kg_e, fab_e.isoformat(), validade.isoformat(), lote_e))
            con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, unit_pal, kg_unit, total_kg) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (datetime.now().isoformat(), sel, codigo_e, row_m["nome"], marca_e, "ENTRADA", pal_e, unit_e, kg_e, total_preview))
            con.commit()
            st.success(f"✅ ENTRADA {total_preview:.2f} KG - Cálculo: {pal_e} x {unit_e} x {kg_e}")
            st.balloons()
            st.rerun()

    df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE gaveta_id={sel} ORDER BY id DESC", con)
    if not df_dentro.empty:
        df_dentro["total_kg"] = df_dentro.apply(lambda r: calc_kg(r["paletes"], r["unit_pal"], r["kg_unit"]), axis=1)
        df_dentro["calc"] = df_dentro.apply(lambda r: f"{r['paletes']} x {r['unit_pal']} x {r['kg_unit']} = {r['total_kg']:.2f} KG", axis=1)

        st.markdown("#### 📋 DENTRO DA GAVETA")
        st.dataframe(df_dentro[["id","codigo","marca","paletes","unit_pal","kg_unit","calc","total_kg"]], use_container_width=True)

        df_edit = st.data_editor(df_dentro[["id","codigo","nome","marca","paletes","unit_pal","kg_unit"]], use_container_width=True, key=f"edit_{sel}")

        if st.button("💾 SALVAR ALTERAÇÕES DA TABELA", type="primary", use_container_width=True, key=f"save_{sel}"):
            for _, r in df_edit.iterrows():
                con.execute("UPDATE estoque SET codigo=?, nome=?, marca=?, paletes=?, unit_pal=?, kg_unit=? WHERE id=?",
                            (r["codigo"], r["nome"], r["marca"], int(r["paletes"]), int(r["unit_pal"]), float(r["kg_unit"]), int(r["id"])))
            con.commit()
            st.success("✅ Estoque atualizado!")
            st.rerun()

        total_gaveta = df_dentro["total_kg"].sum()
        c_min2.metric(f"Total Gaveta {sel:02d}", f"{total_gaveta:,.2f} KG")

        st.divider()
        with st.container(border=True):
            st.markdown("#### 🔴 SAÍDA")
            id_saida = st.selectbox("Item SAÍDA:", df_dentro["id"].tolist(), format_func=lambda x: f"ID {x} - {df_dentro[df_dentro.id==x].iloc[0]['codigo']} - {df_dentro[df_dentro.id==x].iloc[0]['marca']} - {df_dentro[df_dentro.id==x].iloc[0]['calc']}", key=f"saida_{sel}")
            qtd_saida = st.number_input("Qtd Paletes SAÍDA", min_value=1, value=1, key=f"qtd_s_{sel}")
            row_s = df_dentro[df_dentro.id==id_saida].iloc[0]
            total_s_prev = calc_kg(qtd_saida, row_s["unit_pal"], row_s["kg_unit"])
            st.markdown(f'<div class="calc-box" style="border-color:#DC2626; background:#FEF2F2;">🔴 {qtd_saida} x {row_s["unit_pal"]} x {row_s["kg_unit"]} = {total_s_prev:,.2f} KG</div>', unsafe_allow_html=True)

            if st.button("🔴 SALVAR SAÍDA - ATUALIZA ESTOQUE", type="primary", use_container_width=True, key=f"btn_s_{sel}"):
                con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, unit_pal, kg_unit, total_kg) VALUES (?,?,?,?,?,?,?,?,?,?)",
                            (datetime.now().isoformat(), sel, row_s["codigo"], row_s["nome"], row_s["marca"], "SAIDA", qtd_saida, row_s["unit_pal"], row_s["kg_unit"], total_s_prev))
                if qtd_saida >= row_s["paletes"]:
                    con.execute("DELETE FROM estoque WHERE id=?", (int(id_saida),))
                else:
                    con.execute("UPDATE estoque SET paletes = paletes -? WHERE id=?", (int(qtd_saida), int(id_saida)))
                con.commit()
                st.success(f"✅ SAÍDA {total_s_prev:.2f} KG")
                st.rerun()
    else:
        st.info("Gaveta vazia - faça ENTRADA")

    con.close()

with tab_rel:
    st.markdown("## 📊 Histórico e Alerta de Compra")
    df_hist = get_df_historico()
    df_est = get_df_estoque()
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True, height=350)
        periodo = st.selectbox("Agrupar por:", ["Diário","Semanal","Mensal","Semestral","Anual"], key="rel_per")
        df_hist["periodo"] = df_hist["data"]
        if periodo=="Diário": df_hist["periodo"] = df_hist["data"].dt.date
        elif periodo=="Semanal": df_hist["periodo"] = df_hist["data"].dt.strftime("%Y-W%U")
        elif periodo=="Mensal": df_hist["periodo"] = df_hist["data"].dt.to_period("M").astype(str)
        elif periodo=="Semestral": df_hist["periodo"] = df_hist["data"].dt.year.astype(str) + "-S" + ((df_hist["data"].dt.month-1)//6 +1).astype(str)
        else: df_hist["periodo"] = df_hist["data"].dt.year
        df_group = df_hist.groupby(["periodo","tipo"])["total_kg"].sum().reset_index()
        fig = px.bar(df_group, x="periodo", y="total_kg", color="tipo", barmode="group", color_discrete_map={"ENTRADA":"#16A34A","SAIDA":"#DC2626"})
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.markdown("### 🚨 Alerta de Compra")
        con = sqlite3.connect(DB)
        df_config = pd.read_sql("SELECT * FROM config", con)
        con.close()
        alertas = []
        for _, cfg in df_config.iterrows():
            gid = cfg["gaveta_id"]
            estoque_g = df_est[df_est["gaveta_id"]==gid]["total_kg"].sum() if not df_est.empty else 0
            if estoque_g <= cfg["estoque_min"]:
                alertas.append({"Gaveta": gid, "Estoque": estoque_g, "Mínimo": cfg["estoque_min"], "Comprar": cfg["estoque_min"]*2 - estoque_g})
        if alertas:
            df_alertas = pd.DataFrame(alertas)
            st.dataframe(df_alertas, use_container_width=True)
            st.error(f"Total para comprar: {df_alertas['Comprar'].sum():,.2f} KG")
        else:
            st.success("✅ Sem alertas")
    else:
        st.info("Sem histórico")
