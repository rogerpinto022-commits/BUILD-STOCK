import streamlit as st
import pandas as pd
import sqlite3, os
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ================= CONFIGURAÇÃO =================
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
    # Cria config mínima
    for i in range(1, 21):
        con.execute("INSERT OR IGNORE INTO config (gaveta_id, estoque_min) VALUES (?,?)", (i, 1000))
    con.commit()
    con.close()

# CORREÇÃO AUTOMÁTICA SE BANCO ESTIVER COM ERRO
try:
    init_db()
    con = sqlite3.connect(DB)
    con.execute("SELECT paletes, unit_pal, kg_unit FROM estoque LIMIT 1").fetchall()
    con.close()
except sqlite3.OperationalError:
    if os.path.exists(DB): os.remove(DB)
    init_db()

def calc_kg(paletes, unit_pal, kg_unit):
    """CÁLCULO CORRETO: 1 x 56 x 25 = 1400 KG"""
    try:
        return float(paletes) * float(unit_pal) * float(kg_unit)
    except:
        return 0.0

if 'gaveta_sel' not in st.session_state: st.session_state.gaveta_sel = 1

# CSS
st.markdown("""
<style>
.main-header { background: linear-gradient(90deg, #1E3A8A, #3B82F6); padding: 22px; border-radius: 15px; text-align: center; color: white; font-size: 28px; font-weight: 900; box-shadow: 0 8px 20px rgba(0,0,0,0.2); }
.metric-card { background: white; border-radius: 12px; padding: 15px; border-left: 6px solid #3B82F6; }
.calc-box { background: #EFF6FF; border: 2px dashed #3B82F6; padding: 12px; border-radius: 10px; font-weight: 800; text-align: center; font-size: 18px; color: #1E3A8A; }
.alert-box { background: #DC2626; color: white; padding: 15px; border-radius: 12px; font-weight: 900; animation: pulse 2s infinite; }
</style>
<div class="main-header">🔧 REFORMA DE FORNOS - CONTROLE DE ESTOQUE COMPLETO</div>
""", unsafe_allow_html=True)

# ================= FUNÇÕES DE DADOS =================
def get_df_estoque():
    con = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM estoque", con)
    con.close()
    if not df.empty:
        df["total_kg"] = df.apply(lambda r: calc_kg(r["paletes"], r["unit_pal"], r["kg_unit"]), axis=1)
        df["validade"] = pd.to_datetime(df["validade"], errors='coerce')
        df["dias_vencer"] = (df["validade"] - pd.to_datetime(date.today())).dt.days
    return df

def get_df_historico():
    con = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM historico ORDER BY data DESC", con)
    con.close()
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
        df["total_kg"] = df.apply(lambda r: calc_kg(r["paletes"], r["unit_pal"], r["kg_unit"]), axis=1)
    return df

# ================= SIDEBAR - DASHBOARD RÁPIDO =================
with st.sidebar:
    st.markdown("## 📊 DASHBOARD")
    df_est = get_df_estoque()
    df_hist = get_df_historico()

    total_kg = df_est["total_kg"].sum() if not df_est.empty else 0
    total_itens = len(df_est)
    entradas_hoje = df_hist[df_hist["tipo"]=="ENTRADA"]["total_kg"].sum() if not df_hist.empty else 0
    saidas_hoje = df_hist[df_hist["tipo"]=="SAIDA"]["total_kg"].sum() if not df_hist.empty else 0

    st.metric("📦 Estoque Total", f"{total_kg:,.2f} KG")
    st.metric("📋 Itens", total_itens)
    st.metric("🟢 Total Entradas", f"{entradas_hoje:,.2f} KG")
    st.metric("🔴 Total Saídas", f"{saidas_hoje:,.2f} KG")
    st.metric("⚖️ Saldo", f"{entradas_hoje-saidas_hoje:,.2f} KG")

    st.divider()
    st.markdown("### 🚨 ALERTAS")
    con = sqlite3.connect(DB)
    df_config = pd.read_sql("SELECT * FROM config", con)
    con.close()
    alertas = 0
    for _, cfg in df_config.iterrows():
        gid = cfg["gaveta_id"]
        estoque_g = df_est[df_est["gaveta_id"]==gid]["total_kg"].sum() if not df_est.empty else 0
        if estoque_g <= cfg["estoque_min"]:
            st.error(f"Gaveta {gid:02d}: {estoque_g:.0f} KG < Mín {cfg['estoque_min']:.0f}")
            alertas+=1
    if alertas==0:
        st.success("✅ Nenhum alerta")

    st.divider()
    st.markdown("### 📦 GAVETAS")
    cols_side = st.columns(2)
    for i in range(1,21):
        with cols_side[(i-1)%2]:
            if st.button(f"G{i:02d}", key=f"side_{i}", use_container_width=True, type="primary" if st.session_state.gaveta_sel==i else "secondary"):
                st.session_state.gaveta_sel = i
                st.rerun()

# ================= ABAS PRINCIPAIS =================
tab_dash, tab_cad, tab_gavetas, tab_rel = st.tabs(["📈 DASHBOARD + GRÁFICOS", "📝 CADASTRO MATERIAIS (ID LIVRE + MARCA)", "📦 GAVETAS - ENTRADA / SAÍDA / SALVAR", "📊 RELATÓRIOS E HISTÓRICO"])

with tab_dash:
    st.markdown("## 📈 Dashboard Completo - Entrada x Saída x Estoque")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Estoque Total", f"{total_kg:,.2f} KG")
    c2.metric("Itens Únicos", total_itens)
    c3.metric("Entradas", f"{entradas_hoje:,.2f} KG", delta="Total histórico")
    c4.metric("Saídas", f"{saidas_hoje:,.2f} KG", delta="Total histórico", delta_color="inverse")

    if not df_est.empty:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            # Gráfico Estoque por Gaveta
            df_por_gaveta = df_est.groupby("gaveta_id")["total_kg"].sum().reset_index()
            fig1 = px.bar(df_por_gaveta, x="gaveta_id", y="total_kg", title="Estoque por Gaveta (KG)", color="total_kg", color_continuous_scale="Blues", text="total_kg")
            fig1.update_traces(texttemplate='%{text:.0f} KG', textposition='outside')
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            # Gráfico por Marca
            df_por_marca = df_est.groupby("marca")["total_kg"].sum().reset_index()
            fig2 = px.pie(df_por_marca, values="total_kg", names="marca", title="Estoque por Marca", hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)

        col_g3, col_g4 = st.columns(2)
        with col_g3:
            # Validade
            df_est["status"] = df_est["dias_vencer"].apply(lambda x: "🔴 Vencido" if x<0 else ("🟡 Vence 30d" if x<=30 else "🟢 OK"))
            fig3 = px.histogram(df_est, x="status", y="total_kg", color="status", title="Validade do Estoque", color_discrete_map={"🔴 Vencido":"#DC2626","🟡 Vence 30d":"#F59E0B","🟢 OK":"#16A34A"})
            st.plotly_chart(fig3, use_container_width=True)

        with col_g4:
            # Estoque por Código
            df_por_codigo = df_est.groupby("codigo")["total_kg"].sum().reset_index().sort_values("total_kg", ascending=False).head(10)
            fig4 = px.bar(df_por_codigo, x="codigo", y="total_kg", title="Top 10 Materiais por KG", color="total_kg")
            st.plotly_chart(fig4, use_container_width=True)

    if not df_hist.empty:
        st.divider()
        st.markdown("### 📊 Histórico de Entrada e Saída")
        periodo = st.selectbox("Agrupar por:", ["Diário","Semanal","Mensal","Semestral","Anual"], key="periodo_dash")

        df_hist["periodo"] = df_hist["data"]
        if periodo=="Diário": df_hist["periodo"] = df_hist["data"].dt.date
        elif periodo=="Semanal": df_hist["periodo"] = df_hist["data"].dt.strftime("%Y-W%U")
        elif periodo=="Mensal": df_hist["periodo"] = df_hist["data"].dt.to_period("M").astype(str)
        elif periodo=="Semestral": df_hist["periodo"] = df_hist["data"].dt.year.astype(str) + "-S" + ((df_hist["data"].dt.month-1)//6 +1).astype(str)
        else: df_hist["periodo"] = df_hist["data"].dt.year

        df_group = df_hist.groupby(["periodo","tipo"])["total_kg"].sum().reset_index()
        fig_hist = px.bar(df_group, x="periodo", y="total_kg", color="tipo", barmode="group", title=f"Entradas x Saídas - {periodo}", color_discrete_map={"ENTRADA":"#16A34A","SAIDA":"#DC2626"})
        st.plotly_chart(fig_hist, use_container_width=True)

        # Linha de saldo acumulado
        df_saldo = df_hist.sort_values("data")
        df_saldo["saldo_acum"] = df_saldo.apply(lambda r: r["total_kg"] if r["tipo"]=="ENTRADA" else -r["total_kg"], axis=1).cumsum()
        fig_saldo = px.line(df_saldo, x="data", y="saldo_acum", title="Saldo Acumulado de Estoque (KG) ao longo do tempo")
        st.plotly_chart(fig_saldo, use_container_width=True)

with tab_cad:
    st.markdown("## 📝 Cadastro - ID LIVRE pode repetir mesmo código com marcas diferentes")
    con = sqlite3.connect(DB)
    with st.container(border=True):
        c1,c2,c3,c4 = st.columns(4)
        codigo = c1.text_input("CÓDIGO / ID LIVRE *", placeholder="Ex: TIJ-001")
        nome = c2.text_input("NOME MATERIAL *", placeholder="Ex: Tijolo Refratário")
        marca = c3.text_input("MARCA *", placeholder="Ex: Santa Cruz")
        categoria = c4.selectbox("Categoria", ["Refratário","Cimento","Manta","Isolante","Ferragem","Outro"])

        c5,c6,c7 = st.columns(3)
        peso = c5.number_input("Peso padrão KG", value=25.0, format="%.2f")
        fornecedor = c6.text_input("Fornecedor")
        obs_cad = c7.text_input("Obs")

        if st.button("💾 SALVAR MATERIAL - ID NÃO TRAVA", type="primary", use_container_width=True):
            if codigo and nome and marca:
                con.execute("INSERT INTO materiais (codigo, nome, marca, categoria, peso, fornecedor) VALUES (?,?,?,?,?,?)", (codigo, nome, marca, categoria, peso, fornecedor))
                con.commit()
                st.success(f"✅ Salvo: {codigo} - {nome} - MARCA {marca} - Pode repetir!")
            else:
                st.error("Preencha Código, Nome e Marca obrigatórios!")

    df_mat = pd.read_sql("SELECT * FROM materiais ORDER BY id DESC", con)
    st.markdown(f"### Materiais Cadastrados ({len(df_mat)}) - Pode ter mesmo código com marcas diferentes")
    st.dataframe(df_mat, use_container_width=True, height=350)

    if not df_mat.empty:
        filtro_marca = st.selectbox("Filtrar por Marca", ["TODAS"] + sorted(df_mat["marca"].dropna().unique().tolist()))
        if filtro_marca!="TODAS":
            st.dataframe(df_mat[df_mat["marca"]==filtro_marca], use_container_width=True)

        c_del1, c_del2 = st.columns([3,1])
        id_del = c_del1.selectbox("Excluir:", df_mat["id"].tolist(), format_func=lambda x: f"ID {x} - {df_mat[df_mat.id==x].iloc[0]['codigo']} | {df_mat[df_mat.id==x].iloc[0]['nome']} | MARCA {df_mat[df_mat.id==x].iloc[0]['marca']}")
        if c_del2.button("🗑️ EXCLUIR", use_container_width=True):
            con.execute("DELETE FROM materiais WHERE id=?", (int(id_del),))
            con.commit()
            st.rerun()
    con.close()

with tab_gavetas:
    st.markdown("### 📦 Clique na Gaveta para abrir - Informações ficam armazenadas DENTRO")
    cols = st.columns(5)
    con = sqlite3.connect(DB)
    for i in range(1,21):
        df_g = pd.read_sql(f"SELECT paletes, unit_pal, kg_unit FROM estoque WHERE gaveta_id={i}", con)
        total_g = df_g.apply(lambda r: calc_kg(r["paletes"], r["unit_pal"], r["kg_unit"]), axis=1).sum() if not df_g.empty else 0
        qtd_g = len(df_g)
        with cols[(i-1)%5]:
            if st.button(f"📦 Gaveta {i:02d}\n{qtd_g} itens\n{total_g:,.0f} KG", key=f"g_{i}", use_container_width=True, type="primary" if st.session_state.gaveta_sel==i else "secondary"):
                st.session_state.gaveta_sel = i
                st.rerun()
    con.close()

    sel = st.session_state.gaveta_sel
    con = sqlite3.connect(DB)
    df_mat = pd.read_sql("SELECT * FROM materiais", con)
    if df_mat.empty:
        st.warning("Cadastre material na aba CADASTRO primeiro!")
        st.stop()

    st.divider()
    st.markdown(f"# 📂 GAVETA {sel:02d} ABERTA - Estoque armazenado aqui dentro")

    # CONFIG ESTOQUE MÍNIMO
    df_config = pd.read_sql(f"SELECT * FROM config WHERE gaveta_id={sel}", con)
    estoque_min_atual = float(df_config.iloc[0]["estoque_min"]) if not df_config.empty else 1000.0
    c_min1, c_min2 = st.columns(2)
    novo_min = c_min1.number_input(f"Estoque Mínimo Gaveta {sel} (KG) - para alerta de compra", value=estoque_min_atual, step=100.0, key=f"min_{sel}")
    if c_min1.button("💾 SALVAR ESTOQUE MÍNIMO", key=f"btn_min_{sel}"):
        con.execute("UPDATE config SET estoque_min=? WHERE gaveta_id=?", (novo_min, sel))
        con.commit()
        st.success(f"Estoque mínimo Gaveta {sel} salvo: {novo_min} KG")

    # ENTRADA
    with st.container(border=True):
        st.markdown("#### 🟢 ENTRADA DE MATERIAL")
        ce1, ce2, ce3 = st.columns([2,1,1])
        mat_sel = ce1.selectbox("Material cadastrado:", df_mat["id"].tolist(), format_func=lambda x: f"{df_mat[df_mat.id==x].iloc[0]['codigo']} - {df_mat[df_mat.id==x].iloc[0]['nome']} - MARCA {df_mat[df_mat.id==x].iloc[0]['marca']}", key=f"mat_e_{sel}")
        row_m = df_mat[df_mat.id==mat_sel].iloc[0]
        codigo_e = ce2.text_input("Código", value=row_m["codigo"], key=f"cod_e_{sel}")
        marca_e = ce3.text_input("Marca", value=row_m["marca"], key=f"marca_e_{sel}")

        ce4, ce5, ce6, ce7 = st.columns(4)
        pal_e = ce4.number_input("1️⃣ Paletes", min_value=1, value=1, key=f"pal_e_{sel}")
        unit_e = ce5.number_input("2️⃣ Unit/Palete", min_value=1, value=56, key=f"unit_e_{sel}")
        kg_e = ce6.number_input("3️⃣ Kg/Unit", min_value=0.1, value=float(row_m["peso"]), format="%.2f", key=f"kg_e_{sel}")
        dias_e = ce7.number_input("⏳ Validade dias", min_value=1, value=90, key=f"dias_e_{sel}")

        total_preview = calc_kg(pal_e, unit_e, kg_e)
        st.markdown(f'<div class="calc-box">🧮 {pal_e} x {unit_e} x {kg_e} = {total_preview:,.2f} KG</div>', unsafe_allow_html=True)

        fab_e = st.date_input("Fabricação", value=date.today(), key=f"fab_e_{sel}")
        lote_e = st.text_input("Lote / Obs", key=f"lote_e_{sel}")

        if st.button("🟢 SALVAR ENTRADA - ATUALIZA ESTOQUE", type="primary", use_container_width=True, key=f"btn_e_{sel}"):
            validade = fab_e + timedelta(days=dias_e)
            con.execute("INSERT INTO estoque (gaveta_id, codigo, nome, marca, paletes, unit_pal, kg_unit, fab, validade, lote) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (sel, codigo_e, row_m["nome"], marca_e, pal_e, unit_e, kg_e, fab_e.isoformat(), validade.isoformat(), lote_e))
            con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, unit_pal, kg_unit, total_kg) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (datetime.now().isoformat(), sel, codigo_e, row_m["nome"], marca_e, "ENTRADA", pal_e, unit_e, kg_e, total_preview))
            con.commit()
            st.success(f"✅ ENTRADA: {total_preview:.2f} KG na Gaveta {sel}")
            st.balloons()
            st.rerun()

    # DENTRO
    df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE gaveta_id={sel} ORDER BY id DESC", con)
    if not df_dentro.empty:
        df_dentro["total_kg"] = df_dentro.apply(lambda r: calc_kg(r["paletes"], r["unit_pal"], r["kg_unit"]), axis=1)
        df_dentro["validade"] = pd.to_datetime(df_dentro["validade"], errors='coerce')
        df_dentro["dias_vencer"] = (df_dentro["validade"] - pd.to_datetime(date.today())).dt.days
        df_dentro["status"] = df_dentro["dias_vencer"].apply(lambda x: "🔴 VENCIDO" if x<0 else ("🟡 30d" if x<=30 else "🟢 OK"))
        df_dentro["calc"] = df_dentro.apply(lambda r: f"{r['paletes']} x {r['unit_pal']} x {r['kg_unit']} = {r['total_kg']:.2f} KG", axis=1)

        st.markdown("#### 📋 ESTOQUE DENTRO - Editável + Botão SALVAR")
        df_edit = st.data_editor(df_dentro[["id","codigo","nome","marca","paletes","unit_pal","kg_unit","total_kg","status","calc"]], use_container_width=True, key=f"edit_{sel}", disabled=["id","total_kg","status","calc"])

        if st.button("💾 SALVAR ALTERAÇÕES DA TABELA - ATUALIZA ESTOQUE", type="primary", use_container_width=True, key=f"save_{sel}"):
            for _, r in df_edit.iterrows():
                con.execute("UPDATE estoque SET codigo=?, nome=?, marca=?, paletes=?, unit_pal=?, kg_unit=? WHERE id=?",
                            (r["codigo"], r["nome"], r["marca"], int(r["paletes"]), int(r["unit_pal"]), float(r["kg_unit"]), int(r["id"])))
            con.commit()
            st.success("✅ Estoque atualizado!")
            st.rerun()

        total_gaveta = df_dentro["total_kg"].sum()
        c_min2.metric(f"Total Gaveta {sel:02d}", f"{total_gaveta:,.2f} KG")

        # SAÍDA
        st.divider()
        with st.container(border=True):
            st.markdown("#### 🔴 SAÍDA DE MATERIAL")
            cs1, cs2 = st.columns(2)
            id_saida = cs1.selectbox("Item para SAÍDA:", df_dentro["id"].tolist(), format_func=lambda x: f"ID {x} - {df_dentro[df_dentro.id==x].iloc[0]['codigo']} - {df_dentro[df_dentro.id==x].iloc[0]['marca']} - {df_dentro[df_dentro.id==x].iloc[0]['calc']}", key=f"saida_sel_{sel}")
            qtd_saida = cs2.number_input("Qtd Paletes SAÍDA", min_value=1, value=1, key=f"qtd_s_{sel}")

            row_s = df_dentro[df_dentro.id==id_saida].iloc[0]
            total_s_preview = calc_kg(qtd_saida, row_s["unit_pal"], row_s["kg_unit"])
            st.markdown(f'<div class="calc-box" style="border-color:#DC2626; background:#FEF2F2;">🔴 SAÍDA: {qtd_saida} x {row_s["unit_pal"]} x {row_s["kg_unit"]} = {total_s_preview:,.2f} KG</div>', unsafe_allow_html=True)

            if st.button("🔴 SALVAR SAÍDA - ATUALIZA ESTOQUE", type="primary", use_container_width=True, key=f"btn_s_{sel}"):
                con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, unit_pal, kg_unit, total_kg) VALUES (?,?,?,?,?,?,?,?,?,?)",
                            (datetime.now().isoformat(), sel, row_s["codigo"], row_s["nome"], row_s["marca"], "SAIDA", qtd_saida, row_s["unit_pal"], row_s["kg_unit"], total_s_preview))
                if qtd_saida >= row_s["paletes"]:
                    con.execute("DELETE FROM estoque WHERE id=?", (int(id_saida),))
                else:
                    con.execute("UPDATE estoque SET paletes = paletes -? WHERE id=?", (int(qtd_saida), int(id_saida)))
                con.commit()
                st.success(f"✅ SAÍDA: {total_s_preview:.2f} KG retirada")
                st.rerun()
    else:
        st.info("Gaveta vazia - faça ENTRADA acima, fica armazenado aqui")

    con.close()

with tab_rel:
    st.markdown("## 📊 Relatórios - Histórico Completo")
    df_hist = get_df_historico()
    df_est = get_df_estoque()

    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True, height=400)

        # Filtros de período
        periodo = st.selectbox("Agrupar gráfico por:", ["Diário","Semanal","Mensal","Semestral","Anual"], key="periodo_rel")
        df_hist["periodo"] = df_hist["data"]
        if periodo=="Diário": df_hist["periodo"] = df_hist["data"].dt.date
        elif periodo=="Semanal": df_hist["periodo"] = df_hist["data"].dt.strftime("%Y-W%U")
        elif periodo=="Mensal": df_hist["periodo"] = df_hist["data"].dt.to_period("M").astype(str)
        elif periodo=="Semestral": df_hist["periodo"] = df_hist["data"].dt.year.astype(str) + "-S" + ((df_hist["data"].dt.month-1)//6 +1).astype(str)
        else: df_hist["periodo"] = df_hist["data"].dt.year

        df_group = df_hist.groupby(["periodo","tipo"])["total_kg"].sum().reset_index()
        fig = px.bar(df_group, x="periodo", y="total_kg", color="tipo", barmode="group", title=f"Entradas x Saídas - {periodo}", color_discrete_map={"ENTRADA":"#16A34A","SAIDA":"#DC2626"})
        st.plotly_chart(fig, use_container_width=True)

        # Alerta de compra
        st.divider()
        st.markdown("### 🚨 ALERTA DE COMPRA AUTOMÁTICO")
        con = sqlite3.connect(DB)
        df_config = pd.read_sql("SELECT * FROM config", con)
        con.close()
        alertas = []
        for _, cfg in df_config.iterrows():
            gid = cfg["gaveta_id"]
            estoque_g = df_est[df_est["gaveta_id"]==gid]["total_kg"].sum() if not df_est.empty else 0
            if estoque_g <= cfg["estoque_min"]:
                falta = cfg["estoque_min"]*2 - estoque_g
                alertas.append({"Gaveta": gid, "Estoque Atual": estoque_g, "Mínimo": cfg["estoque_min"], "Comprar": falta, "Urgência": "🔴 ALTA"})

        if alertas:
            df_alertas = pd.DataFrame(alertas)
            st.dataframe(df_alertas, use_container_width=True)
            st.error(f"📦 Total para comprar: {df_alertas['Comprar'].sum():,.2f} KG")
            if st.button("📧 Gerar Pedido de Compra"):
                txt = "\n".join([f"Gaveta {r['Gaveta']:02d}: {r['Comprar']:.0f} KG" for _, r in df_alertas.iterrows()])
                st.text_area("Pedido", f"PEDIDO {date.today()}\n{txt}\nTOTAL: {df_alertas['Comprar'].sum():.0f} KG", height=200)
        else:
            st.success("✅ Estoques OK")

        # Exportar
        if st.button("📥 Exportar Histórico CSV"):
            st.download_button("Baixar CSV", df_hist.to_csv(index=False), "historico_fornos.csv", "text/csv")

    else:
        st.info("Sem histórico ainda - faça Entradas e Saídas")
