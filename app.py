import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import date, datetime, timedelta

DB = "estoque_fornos.db"

def init_db():
    con = sqlite3.connect(DB)
    # Apaga tabela antiga com trava
    con.execute("DROP TABLE IF EXISTS materiais")
    con.execute("""CREATE TABLE IF NOT EXISTS materiais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nome TEXT,
        marca TEXT,
        categoria TEXT,
        unidade TEXT,
        peso_unit REAL,
        fornecedor TEXT,
        lote TEXT
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS gavetas (id INTEGER PRIMARY KEY, nome TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gaveta_id INT,
        material_id INT,
        codigo TEXT,
        nome TEXT,
        marca TEXT,
        paletes INT,
        unit_por_palete INT,
        kilos_por_unit REAL,
        data_fab DATE,
        dias_validade INT,
        data_validade DATE,
        lote TEXT,
        obs TEXT
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT, tipo TEXT, paletes INT, total_kg REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS config (gaveta_id INT PRIMARY KEY, estoque_min REAL)""")
    cur = con.execute("SELECT COUNT(*) FROM gavetas").fetchone()[0]
    if cur == 0:
        for i in range(1,21):
            con.execute("INSERT INTO gavetas (id, nome) VALUES (?,?)", (i, f"Gaveta {i:02d}"))
            con.execute("INSERT INTO config (gaveta_id, estoque_min) VALUES (?,?)", (i, 1000))
    con.commit()
    con.close()

init_db()

st.set_page_config(layout="wide", page_title="Reforma Fornos - Marca e ID Livre")
st.markdown("""
<style>
.gaveta-principal { background: linear-gradient(90deg, #5B8DEF, #3A6ED8); border: 3px solid #1E40AF; border-radius: 12px; padding: 20px; text-align: center; color: white; font-size: 26px; font-weight: 800; margin-bottom: 15px; }
.gaveta-aberta { background: #FFFFFF; border: 4px solid #16A34A; border-top: 12px solid #16A34A; border-radius: 0 0 15px 15px; padding: 20px; margin-top: -10px; }
</style>
""", unsafe_allow_html=True)

if 'selecionada' not in st.session_state: st.session_state.selecionada = None

st.markdown('<div class="gaveta-principal">🔧 REFORMA DE FORNOS - MARCA + ID LIVRE</div>', unsafe_allow_html=True)

tab_materiais, tab_estoque, tab_alertas = st.tabs(["📦 CADASTRO MATERIAIS (ID + MARCA)", "📂 GAVETAS - DENTRO", "🚨 ALERTAS + HISTÓRICO"])

with tab_materiais:
    st.subheader("Cadastro com ID LIVRE e MARCA - pode repetir mesmo material")
    con = sqlite3.connect(DB)

    with st.form("form_material", clear_on_submit=True):
        st.write("Pode cadastrar mesmo código várias vezes com marcas diferentes!")
        c1,c2,c3 = st.columns(3)
        codigo = c1.text_input("ID / Código (LIVRE - pode repetir)", placeholder="Ex: TIJ-001")
        nome = c2.text_input("Nome Material", placeholder="Ex: Tijolo Refratário")
        marca = c3.text_input("MARCA", placeholder="Ex: Santa Cruz, Refratek, Brasilit")

        c4,c5,c6,c7 = st.columns(4)
        categoria = c4.selectbox("Categoria", ["Refratário","Cimento","Isolante","Ferragem","Manta","Outro"])
        unidade = c5.selectbox("Unidade", ["KG","TON","UN","M","M²","LITROS"])
        peso = c6.number_input("Peso p/ unitário (KG)", min_value=0.1, value=25.0)
        fornecedor = c7.text_input("Fornecedor", placeholder="Ex: Leroy")

        lote = st.text_input("Lote / Referência", placeholder="Ex: LOTE-2025-001")

        if st.form_submit_button("💾 Cadastrar - ID NÃO TRAVA", type="primary", use_container_width=True):
            if not codigo or not nome:
                st.error("Preencha Código e Nome!")
            else:
                con.execute("INSERT INTO materiais (codigo, nome, marca, categoria, unidade, peso_unit, fornecedor, lote) VALUES (?,?,?,?,?,?,?,?)",
                            (codigo, nome, marca, categoria, unidade, peso, fornecedor, lote))
                con.commit()
                st.success(f"✅ Cadastrado: {codigo} - {nome} - MARCA: {marca} (pode repetir!)")

    st.divider()
    df_materiais = pd.read_sql("SELECT * FROM materiais ORDER BY id DESC", con)

    # FILTRO POR MARCA
    if not df_materiais.empty:
        filtro_marca = st.selectbox("Filtrar por Marca", ["TODAS"] + sorted(df_materiais["marca"].dropna().unique().tolist()))
        if filtro_marca!= "TODAS":
            df_materiais = df_materiais[df_materiais["marca"]==filtro_marca]

    st.dataframe(df_materiais, use_container_width=True, height=400)

    if not df_materiais.empty:
        c_del1, c_del2 = st.columns(2)
        id_del = c_del1.selectbox("Selecione ID para excluir", df_materiais["id"].tolist(), format_func=lambda x: f"ID {x} - {df_materiais[df_materiais.id==x].iloc[0]['codigo']} - {df_materiais[df_materiais.id==x].iloc[0]['nome']} - {df_materiais[df_materiais.id==x].iloc[0]['marca']}")
        if c_del2.button("🗑️ Excluir esse cadastro"):
            con.execute("DELETE FROM materiais WHERE id=?", (int(id_del),))
            con.commit()
            st.rerun()
    con.close()

with tab_estoque:
    con = sqlite3.connect(DB)
    df_materiais = pd.read_sql("SELECT * FROM materiais", con)
    con.close()

    if df_materiais.empty:
        st.warning("⚠️ Cadastre material primeiro com MARCA")
        st.stop()

    cols = st.columns(5)
    for i in range(1,21):
        con = sqlite3.connect(DB)
        qtd = con.execute("SELECT COUNT(*) FROM estoque WHERE gaveta_id=?", (i,)).fetchone()[0]
        total_kg = con.execute("SELECT SUM(paletes * unit_por_palete * kilos_por_unit) FROM estoque WHERE gaveta_id=?", (i,)).fetchone()[0] or 0
        con.close()
        tipo = "primary" if st.session_state.selecionada == i else "secondary"
        if st.button(f"📦 Gaveta {i:02d}\n{qtd} itens\n{total_kg:.0f} KG", key=f"g_{i}", use_container_width=True, type=tipo):
            st.session_state.selecionada = None if st.session_state.selecionada == i else i
            st.rerun()

    if st.session_state.selecionada:
        sel = st.session_state.selecionada
        st.markdown('<div class="gaveta-aberta">', unsafe_allow_html=True)
        st.markdown(f"### 📂 GAVETA {sel:02d} - Pode repetir mesmo material com marcas diferentes")

        con = sqlite3.connect(DB)
        with st.form(f"add_gaveta_{sel}", clear_on_submit=True):
            st.write("Adicionar DENTRO da gaveta - ID LIVRE, pode repetir:")
            c1,c2 = st.columns(2)
            # Select mostra CODIGO + NOME + MARCA + ID
            mat_escolhido_id = c1.selectbox("Escolha material cadastrado (mostra MARCA)", df_materiais["id"].tolist(),
                format_func=lambda x: f"ID:{x} | {df_materiais[df_materiais.id==x].iloc[0]['codigo']} - {df_materiais[df_materiais.id==x].iloc[0]['nome']} - MARCA:{df_materiais[df_materiais.id==x].iloc[0]['marca']}", key=f"mat_{sel}")

            # Campos editáveis para repetir com variação
            row_mat = df_materiais[df_materiais.id==mat_escolhido_id].iloc[0]
            c2a,c2b,c2c = st.columns(3)
            codigo_edit = c2a.text_input("Código (pode editar)", value=row_mat["codigo"], key=f"cod_{sel}")
            marca_edit = c2b.text_input("MARCA (pode editar)", value=row_mat["marca"], key=f"marca_{sel}")
            lote_edit = c2c.text_input("Lote", value=row_mat["lote"] or "", key=f"lote_{sel}")

            c3,c4,c5,c6,c7 = st.columns(5)
            paletes = c3.number_input("1️⃣ Paletes", min_value=1, value=1, key=f"pal_{sel}")
            unit_pal = c4.number_input("2️⃣ Unit/Palete", min_value=1, value=56, key=f"unit_{sel}")
            kilos = c5.number_input("3️⃣ Kg/Unit", min_value=0.1, value=float(row_mat["peso_unit"]), key=f"kg_{sel}")
            data_fab = c6.date_input("📅 Fabricação", value=date.today(), key=f"fab_{sel}")
            dias_val = c7.number_input("Validade dias", min_value=1, value=90, key=f"val_{sel}")

            obs = st.text_input("Observação", placeholder="Ex: Material com marca diferente mas mesmo código")

            if st.form_submit_button("➕ Adicionar DENTRO - REPETIR PERMITIDO", type="primary", use_container_width=True):
                data_validade = data_fab + timedelta(days=dias_val)
                # Salva COPIA com codigo/nome/marca editável - permite repetir
                con.execute("""INSERT INTO estoque (gaveta_id, material_id, codigo, nome, marca, paletes, unit_por_palete, kilos_por_unit, data_fab, dias_validade, data_validade, lote, obs)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (sel, int(mat_escolhido_id), codigo_edit, row_mat["nome"], marca_edit, paletes, unit_pal, kilos, data_fab.isoformat(), dias_val, data_validade.isoformat(), lote_edit, obs))
                total_kg = paletes * unit_pal * kilos
                con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, total_kg) VALUES (?,?,?,?,?,?,?,?)",
                            (datetime.now().isoformat(), sel, codigo_edit, row_mat["nome"], marca_edit, "ENTRADA", paletes, total_kg))
                con.commit()
                st.success(f"✅ Adicionado DENTRO gaveta {sel}: {codigo_edit} - {marca_edit} - {total_kg:.0f} KG - Pode repetir mesmo ID!")
                st.rerun()

        df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE gaveta_id={sel} ORDER BY id DESC", con)

        if not df_dentro.empty:
            df_dentro["data_validade"] = pd.to_datetime(df_dentro["data_validade"])
            df_dentro["dias_vencer"] = (df_dentro["data_validade"] - pd.to_datetime(date.today())).dt.days
            df_dentro["status"] = df_dentro["dias_vencer"].apply(lambda x: "🔴 VENCIDO" if x<0 else ("🟡 ATENÇÃO" if x<=30 else "🟢 OK"))
            df_dentro["total_kg"] = df_dentro["paletes"] * df_dentro["unit_por_palete"] * df_dentro["kilos_por_unit"]

            st.markdown("#### 📋 O que tem DENTRO desta gaveta (pode ter mesmo código repetido com marcas diferentes)")
            st.dataframe(df_dentro[["id","codigo","nome","marca","lote","paletes","unit_por_palete","kilos_por_unit","total_kg","data_fab","data_validade","dias_vencer","status","obs"]], use_container_width=True)

            # SAÍDA
            cs1, cs2 = st.columns(2)
            id_saida = cs1.selectbox("Tirar qual ID?", df_dentro["id"].tolist(), format_func=lambda x: f"ID Estoque {x} - {df_dentro[df_dentro.id==x].iloc[0]['codigo']} - MARCA {df_dentro[df_dentro.id==x].iloc[0]['marca']} - {df_dentro[df_dentro.id==x].iloc[0]['total_kg']:.0f}KG")
            qtd_saida = cs2.number_input("Paletes SAÍDA", min_value=1, value=1, key=f"qtd_s_{sel}")
            if cs2.button("📤 Registrar SAÍDA", type="primary", key=f"btn_s_{sel}"):
                row = df_dentro[df_dentro.id==id_saida].iloc[0]
                total_kg_saida = qtd_saida * row["unit_por_palete"] * row["kilos_por_unit"]
                con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, total_kg) VALUES (?,?,?,?,?,?,?,?)",
                            (datetime.now().isoformat(), sel, row["codigo"], row["nome"], row["marca"], "SAIDA", qtd_saida, total_kg_saida))
                if qtd_saida >= row["paletes"]:
                    con.execute("DELETE FROM estoque WHERE id=?", (int(id_saida),))
                else:
                    con.execute("UPDATE estoque SET paletes = paletes -? WHERE id=?", (int(qtd_saida), int(id_saida)))
                con.commit()
                st.success(f"Saída {total_kg_saida:.0f} KG"); st.rerun()
        else:
            st.info("Gaveta vazia")
        con.close()
        st.markdown('</div>', unsafe_allow_html=True)

with tab_alertas:
    con = sqlite3.connect(DB)
    df_hist = pd.read_sql("SELECT * FROM historico", con)
    con.close()
    if not df_hist.empty:
        df_hist["data"] = pd.to_datetime(df_hist["data"])
        df_hist["periodo"] = df_hist["data"].dt.to_period("M").astype(str)
        df_res = df_hist.groupby(["periodo","tipo"])["total_kg"].sum().reset_index()
        fig = px.bar(df_res, x="periodo", y="total_kg", color="tipo", barmode="group", color_discrete_map={"ENTRADA":"#16A34A","SAIDA":"#DC2626"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_hist.sort_values("data", ascending=False), use_container_width=True)
