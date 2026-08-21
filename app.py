import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3, os, json
from datetime import date, datetime, timedelta

DB = "estoque_fornos.db"

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS materiais (id INTEGER PRIMARY KEY, codigo TEXT UNIQUE, nome TEXT, categoria TEXT, unidade TEXT, peso_unit REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS gavetas (id INTEGER PRIMARY KEY, nome TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS estoque (id INTEGER PRIMARY KEY, gaveta_id INT, material_id INT, paletes INT, unit_por_palete INT, kilos_por_unit REAL, data_fab DATE, dias_validade INT, data_validade DATE, FOREIGN KEY(material_id) REFERENCES materiais(id))""")
    con.execute("""CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY, data TEXT, gaveta_id INT, material_id INT, tipo TEXT, paletes INT, total_kg REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS config (gaveta_id INT PRIMARY KEY, estoque_min REAL)""")
    # Cria 20 gavetas se não existir
    cur = con.execute("SELECT COUNT(*) FROM gavetas").fetchone()[0]
    if cur == 0:
        for i in range(1,21):
            con.execute("INSERT INTO gavetas (id, nome) VALUES (?,?)", (i, f"Gaveta {i:02d}"))
            con.execute("INSERT INTO config (gaveta_id, estoque_min) VALUES (?,?)", (i, 1000))
    con.commit()
    con.close()

init_db()

st.set_page_config(layout="wide", page_title="Reforma Fornos - Completo")
st.markdown("""
<style>
.gaveta-principal { background: linear-gradient(90deg, #5B8DEF, #3A6ED8); border: 3px solid #1E40AF; border-radius: 12px; padding: 20px; text-align: center; color: white; font-size: 26px; font-weight: 800; margin-bottom: 15px; }
.gaveta-aberta { background: #FFFFFF; border: 4px solid #16A34A; border-top: 12px solid #16A34A; border-radius: 0 0 15px 15px; padding: 20px; margin-top: -10px; }
</style>
""", unsafe_allow_html=True)

if 'selecionada' not in st.session_state: st.session_state.selecionada = None
if 'logado' not in st.session_state: st.session_state.logado = True # login simplificado

st.markdown('<div class="gaveta-principal">🔧 REFORMA DE FORNOS - SISTEMA COMPLETO COM CADASTRO</div>', unsafe_allow_html=True)

# --- ABA CADASTRO DE MATERIAIS ---
tab_materiais, tab_estoque, tab_alertas = st.tabs(["📦 CADASTRO DE MATERIAIS", "📂 GAVETAS - ESTOQUE DENTRO", "🚨 ALERTAS E HISTÓRICO"])

with tab_materiais:
    st.subheader("Cadastro de Materiais - fica salvo!")
    con = sqlite3.connect(DB)

    with st.form("form_material"):
        c1,c2,c3,c4 = st.columns(4)
        codigo = c1.text_input("Código", placeholder="Ex: TIJ-001")
        nome = c2.text_input("Nome Material", placeholder="Ex: Tijolo Refratário 25kg")
        categoria = c3.selectbox("Categoria", ["Refratário","Cimento","Isolante","Ferragem","Outro"])
        unidade = c4.selectbox("Unidade", ["KG","TON","UN","M","M²","LITROS"])
        peso = st.number_input("Peso padrão por unitário (KG)", min_value=0.1, value=25.0)
        if st.form_submit_button("💾 Cadastrar Material", type="primary"):
            try:
                con.execute("INSERT INTO materiais (codigo, nome, categoria, unidade, peso_unit) VALUES (?,?,?,?,?)", (codigo, nome, categoria, unidade, peso))
                con.commit()
                st.success(f"Material {codigo} - {nome} cadastrado!")
            except sqlite3.IntegrityError:
                st.error("Código já existe!")

    st.divider()
    df_materiais = pd.read_sql("SELECT * FROM materiais", con)
    st.dataframe(df_materiais, use_container_width=True)

    # Editar / Excluir
    if not df_materiais.empty:
        id_del = st.selectbox("Excluir material", df_materiais["id"].tolist(), format_func=lambda x: f"{x} - {df_materiais[df_materiais.id==x].iloc[0]['nome']}")
        if st.button("🗑️ Excluir"):
            con.execute("DELETE FROM materiais WHERE id=?", (id_del,))
            con.commit()
            st.rerun()
    con.close()

with tab_estoque:
    con = sqlite3.connect(DB)
    df_materiais = pd.read_sql("SELECT * FROM materiais", con)
    df_gavetas = pd.read_sql("SELECT * FROM gavetas", con)
    con.close()

    if df_materiais.empty:
        st.warning("⚠️ Cadastre um material primeiro na aba CADASTRO DE MATERIAIS")
        st.stop()

    # GRID GAVETAS - TUDO ARMAZENADO DENTRO
    cols = st.columns(5)
    for i in range(1,21):
        with cols[(i-1)%5]:
            # Mostra quantos materiais tem dentro
            con = sqlite3.connect(DB)
            qtd = con.execute("SELECT COUNT(*) FROM estoque WHERE gaveta_id=?", (i,)).fetchone()[0]
            total_kg = con.execute("SELECT SUM(paletes * unit_por_palete * kilos_por_unit) FROM estoque WHERE gaveta_id=?", (i,)).fetchone()[0] or 0
            con.close()
            label = f"📦 Gaveta {i:02d}\n{qtd} mat - {total_kg:.0f} KG"
            tipo = "primary" if st.session_state.selecionada == i else "secondary"
            if st.button(label, key=f"g_{i}", use_container_width=True, type=tipo):
                st.session_state.selecionada = None if st.session_state.selecionada == i else i
                st.rerun()

    if st.session_state.selecionada:
        sel = st.session_state.selecionada
        st.markdown('<div class="gaveta-aberta">', unsafe_allow_html=True)
        st.markdown(f"### 📂 DENTRO DA GAVETA {sel:02d} - Informações armazenadas aqui")

        # FORM PARA ADICIONAR MATERIAL DENTRO DA GAVETA
        con = sqlite3.connect(DB)
        with st.form(f"add_gaveta_{sel}"):
            st.write("Adicionar material dentro desta gaveta:")
            c1,c2,c3,c4,c5 = st.columns(5)
            mat_escolhido = c1.selectbox("Material cadastrado", df_materiais["id"].tolist(), format_func=lambda x: f"{df_materiais[df_materiais.id==x].iloc[0]['codigo']} - {df_materiais[df_materiais.id==x].iloc[0]['nome']}", key=f"mat_{sel}")
            paletes = c2.number_input("1️⃣ Paletes", min_value=1, value=1, key=f"pal_{sel}")
            unit_pal = c3.number_input("2️⃣ Unitários/Palete", min_value=1, value=56, key=f"unit_{sel}")
            kilos = c4.number_input("3️⃣ Kilos/Unit", min_value=0.1, value=25.0, key=f"kg_{sel}")
            data_fab = c5.date_input("📅 Fabricação", value=date.today(), key=f"fab_{sel}")
            dias_val = st.number_input("⏳ Validade em dias", min_value=1, value=90, key=f"val_{sel}")

            if st.form_submit_button("➕ Adicionar DENTRO da Gaveta", type="primary", use_container_width=True):
                data_validade = data_fab + timedelta(days=dias_val)
                con.execute("INSERT INTO estoque (gaveta_id, material_id, paletes, unit_por_palete, kilos_por_unit, data_fab, dias_validade, data_validade) VALUES (?,?,?,?,?,?,?,?)",
                            (sel, mat_escolhido, paletes, unit_pal, kilos, data_fab.isoformat(), dias_val, data_validade.isoformat()))
                # Histórico ENTRADA
                total_kg = paletes * unit_pal * kilos
                con.execute("INSERT INTO historico (data, gaveta_id, material_id, tipo, paletes, total_kg) VALUES (?,?,?,?,?,?)",
                            (datetime.now().isoformat(), sel, mat_escolhido, "ENTRADA", paletes, total_kg))
                con.commit()
                st.success(f"Adicionado DENTRO da gaveta {sel}: {total_kg:.0f} KG")
                st.rerun()

        st.divider()
        # MOSTRA TUDO QUE ESTÁ ARMAZENADO DENTRO DESSA GAVETA
        df_dentro = pd.read_sql(f"""
            SELECT e.id, m.codigo, m.nome, m.categoria, e.paletes, e.unit_por_palete, e.kilos_por_unit,
                   (e.paletes * e.unit_por_palete) as total_unit,
                   (e.paletes * e.unit_por_palete * e.kilos_por_unit) as total_kg,
                   e.data_fab, e.dias_validade, e.data_validade
            FROM estoque e JOIN materiais m ON e.material_id = m.id
            WHERE e.gaveta_id = {sel}
        """, con)

        if not df_dentro.empty:
            df_dentro["data_validade"] = pd.to_datetime(df_dentro["data_validade"])
            df_dentro["dias_vencer"] = (df_dentro["data_validade"] - pd.to_datetime(date.today())).dt.days
            df_dentro["status"] = df_dentro["dias_vencer"].apply(lambda x: "🔴 VENCIDO" if x<0 else ("🟡 ATENÇÃO" if x<=30 else "🟢 OK"))

            st.dataframe(df_dentro, use_container_width=True)

            # SAÍDA
            st.markdown("#### 🔄 Registrar SAÍDA desta gaveta")
            cs1, cs2 = st.columns(2)
            id_saida = cs1.selectbox("Qual item tirar?", df_dentro["id"].tolist(), format_func=lambda x: f"ID {x} - {df_dentro[df_dentro.id==x].iloc[0]['nome']} - {df_dentro[df_dentro.id==x].iloc[0]['total_kg']:.0f} KG")
            qtd_saida = cs2.number_input("Paletes para SAÍDA", min_value=1, value=1)
            if cs2.button("📤 Confirmar SAÍDA", type="primary"):
                # Baixa do estoque e registra histórico
                row = df_dentro[df_dentro.id==id_saida].iloc[0]
                total_kg_saida = qtd_saida * row["unit_por_palete"] * row["kilos_por_unit"]
                con.execute("INSERT INTO historico (data, gaveta_id, material_id, tipo, paletes, total_kg) VALUES (?,?,?,?,?,?)",
                            (datetime.now().isoformat(), sel, row["id"], "SAIDA", qtd_saida, total_kg_saida))
                # Atualiza ou remove
                if qtd_saida >= row["paletes"]:
                    con.execute("DELETE FROM estoque WHERE id=?", (int(id_saida),))
                else:
                    con.execute("UPDATE estoque SET paletes = paletes -? WHERE id=?", (int(qtd_saida), int(id_saida)))
                con.commit()
                st.success(f"Saída {total_kg_saida:.0f} KG registrada!"); st.rerun()
        else:
            st.info("Gaveta vazia - adicione material acima, fica armazenado aqui dentro")

        con.close()
        st.markdown('</div>', unsafe_allow_html=True)

with tab_alertas:
    con = sqlite3.connect(DB)
    df_hist = pd.read_sql("SELECT * FROM historico", con)
    df_est = pd.read_sql("SELECT gaveta_id, SUM(paletes * unit_por_palete * kilos_por_unit) as total FROM estoque GROUP BY gaveta_id", con)
    df_config = pd.read_sql("SELECT * FROM config", con)
    df_materiais = pd.read_sql("SELECT * FROM materiais", con)
    con.close()

    if not df_hist.empty:
        df_hist["data"] = pd.to_datetime(df_hist["data"])
        st.subheader("📊 Histórico Diário / Semanal / Mensal / Semestral / Anual")
        periodo = st.selectbox("Período", ["Diário","Semanal","Mensal","Semestral","Anual"])
        if periodo=="Diário": df_hist["periodo"] = df_hist["data"].dt.date
        elif periodo=="Semanal": df_hist["periodo"] = df_hist["data"].dt.isocalendar().week.astype(str) + "/" + df_hist["data"].dt.year.astype(str)
        elif periodo=="Mensal": df_hist["periodo"] = df_hist["data"].dt.to_period("M").astype(str)
        elif periodo=="Semestral": df_hist["periodo"] = df_hist["data"].dt.year.astype(str) + "-S" + ((df_hist["data"].dt.month-1)//6 +1).astype(str)
        else: df_hist["periodo"] = df_hist["data"].dt.year

        df_res = df_hist.groupby(["periodo","tipo"])["total_kg"].sum().reset_index()
        fig = px.bar(df_res, x="periodo", y="total_kg", color="tipo", barmode="group", color_discrete_map={"ENTRADA":"#16A34A","SAIDA":"#DC2626"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_hist.sort_values("data", ascending=False), use_container_width=True)
    else:
        st.info("Sem histórico ainda")

    st.divider()
    st.subheader("🚨 Alertas de Compra")
    alertas = []
    for _, cfg in df_config.iterrows():
        gid = cfg["gaveta_id"]
        estoque = df_est[df_est.gaveta_id==gid]["total"].sum() if not df_est.empty and gid in df_est.gaveta_id.values else 0
        minimo = cfg["estoque_min"]
        if estoque <= minimo:
            alertas.append({"Gaveta": gid, "Estoque": estoque, "Mínimo": minimo, "Comprar": minimo*2 - estoque, "Motivo": "ESTOQUE BAIXO"})

    if alertas:
        st.dataframe(pd.DataFrame(alertas), use_container_width=True)
    else:
        st.success("✅ Nenhum alerta - estoques OK")

st.sidebar.info("Tudo salvo em estoque_fornos.db - não perde ao fechar!")
