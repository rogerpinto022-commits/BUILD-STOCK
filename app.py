import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime, timedelta
import plotly.express as px

DB = "estoque_fornos.db"

def init_db():
    con = sqlite3.connect(DB)
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
    con.execute("""CREATE TABLE IF NOT EXISTS estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gaveta_id INT,
        codigo TEXT,
        nome TEXT,
        marca TEXT,
        paletes INT,
        unit_por_palete INT,
        kilos_por_unit REAL,
        data_fab DATE,
        data_validade DATE,
        lote TEXT,
        obs TEXT
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        gaveta_id INT,
        codigo TEXT,
        nome TEXT,
        marca TEXT,
        tipo TEXT,
        paletes INT,
        total_kg REAL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS config (gaveta_id INT PRIMARY KEY, estoque_min REAL)""")
    cur = con.execute("SELECT COUNT(*) FROM config").fetchone()[0]
    if cur == 0:
        for i in range(1,21):
            con.execute("INSERT OR IGNORE INTO config (gaveta_id, estoque_min) VALUES (?,?)", (i, 1000))
    con.commit()
    con.close()

init_db()

st.set_page_config(layout="wide")
st.markdown("""
<style>
.gaveta-principal { background: linear-gradient(90deg, #5B8DEF, #3A6ED8); border: 3px solid #1E40AF; border-radius: 12px; padding: 20px; text-align: center; color: white; font-size: 26px; font-weight: 800; }
.gaveta-aberta { background: #FFFFFF; border: 4px solid #16A34A; border-top: 12px solid #16A34A; border-radius: 0 0 15px 15px; padding: 20px; margin-top: 10px; }
.btn-entrada { background: #16A34A; color: white; padding: 10px; border-radius: 8px; font-weight: 800; }
.btn-saida { background: #DC2626; color: white; padding: 10px; border-radius: 8px; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

if 'selecionada' not in st.session_state: st.session_state.selecionada = 1

st.markdown('<div class="gaveta-principal">🔧 REFORMA DE FORNOS - ENTRADA / SAÍDA / SALVAR</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📦 1- CADASTRO MATERIAIS", "📂 2- GAVETAS (ENTRADA E SAÍDA)"])

with tab1:
    st.subheader("Cadastro - ID LIVRE + MARCA - pode repetir")
    con = sqlite3.connect(DB)
    with st.form("cad_mat", clear_on_submit=True):
        c1,c2,c3,c4 = st.columns(4)
        codigo = c1.text_input("ID / Código (LIVRE)")
        nome = c2.text_input("Nome")
        marca = c3.text_input("MARCA *")
        categoria = c4.text_input("Categoria")
        c5,c6 = st.columns(2)
        peso = c5.number_input("Peso por unitário KG", value=25.0)
        fornecedor = c6.text_input("Fornecedor")
        if st.form_submit_button("💾 SALVAR MATERIAL", type="primary", use_container_width=True):
            con.execute("INSERT INTO materiais (codigo, nome, marca, categoria, peso_unit, fornecedor) VALUES (?,?,?,?,?,?)", (codigo, nome, marca, categoria, peso, fornecedor))
            con.commit()
            st.success(f"Salvo: {codigo} - {nome} - {marca}")

    df_mat = pd.read_sql("SELECT * FROM materiais ORDER BY id DESC", con)
    st.dataframe(df_mat, use_container_width=True)
    con.close()

with tab2:
    # GRID GAVETAS
    cols = st.columns(5)
    for i in range(1,21):
        con = sqlite3.connect(DB)
        total = con.execute("SELECT SUM(paletes * unit_por_palete * kilos_por_unit) FROM estoque WHERE gaveta_id=?", (i,)).fetchone()[0] or 0
        con.close()
        if cols[(i-1)%5].button(f"📦 Gaveta {i:02d}\n{total:.0f} KG", key=f"g_{i}", use_container_width=True, type="primary" if st.session_state.selecionada==i else "secondary"):
            st.session_state.selecionada = i
            st.rerun()

    sel = st.session_state.selecionada
    st.markdown('<div class="gaveta-aberta">', unsafe_allow_html=True)
    st.markdown(f"### 📂 GAVETA {sel:02d} - FUNÇÕES DE ENTRADA E SAÍDA")

    con = sqlite3.connect(DB)
    df_mat = pd.read_sql("SELECT * FROM materiais", con)

    if df_mat.empty:
        st.warning("Cadastre material na aba 1 primeiro!")
        st.stop()

    # ----- BLOCO ENTRADA -----
    st.markdown("#### 🟢 REGISTRAR ENTRADA")
    with st.form(f"form_entrada_{sel}", clear_on_submit=True):
        ce1,ce2,ce3 = st.columns(3)
        mat_id = ce1.selectbox("Material cadastrado", df_mat["id"].tolist(), format_func=lambda x: f"{df_mat[df_mat.id==x].iloc[0]['codigo']} - {df_mat[df_mat.id==x].iloc[0]['nome']} - MARCA {df_mat[df_mat.id==x].iloc[0]['marca']}")
        row = df_mat[df_mat.id==mat_id].iloc[0]
        codigo_e = ce2.text_input("Código (pode editar)", value=row["codigo"])
        marca_e = ce3.text_input("Marca", value=row["marca"])

        ce4,ce5,ce6,ce7,ce8 = st.columns(5)
        pal_e = ce4.number_input("Paletes ENTRADA", min_value=1, value=1, key=f"pal_e_{sel}")
        unit_e = ce5.number_input("Unit/Palete", min_value=1, value=56, key=f"unit_e_{sel}")
        kg_e = ce6.number_input("Kg/Unit", min_value=0.1, value=float(row["peso_unit"]), key=f"kg_e_{sel}")
        fab_e = ce7.date_input("Fabricação", value=date.today(), key=f"fab_e_{sel}")
        val_e = ce8.number_input("Validade dias", min_value=1, value=90, key=f"val_e_{sel}")
        lote_e = st.text_input("Lote", key=f"lote_e_{sel}")

        if st.form_submit_button("🟢 SALVAR ENTRADA - ATUALIZA ESTOQUE", type="primary", use_container_width=True):
            data_validade = fab_e + timedelta(days=val_e)
            total_kg = pal_e * unit_e * kg_e
            con.execute("INSERT INTO estoque (gaveta_id, codigo, nome, marca, paletes, unit_por_palete, kilos_por_unit, data_fab, data_validade, lote) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (sel, codigo_e, row["nome"], marca_e, pal_e, unit_e, kg_e, fab_e.isoformat(), data_validade.isoformat(), lote_e))
            con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, total_kg) VALUES (?,?,?,?,?,?,?,?)",
                        (datetime.now().isoformat(), sel, codigo_e, row["nome"], marca_e, "ENTRADA", pal_e, total_kg))
            con.commit()
            st.success(f"✅ ENTRADA salva: {total_kg:.0f} KG dentro da gaveta {sel}")
            st.rerun()

    st.divider()

    # ----- MOSTRA ESTOQUE DENTRO -----
    df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE gaveta_id={sel} ORDER BY id DESC", con)

    if not df_dentro.empty:
        df_dentro["total_kg"] = df_dentro["paletes"] * df_dentro["unit_por_palete"] * df_dentro["kilos_por_unit"]
        df_dentro["data_validade"] = pd.to_datetime(df_dentro["data_validade"])
        df_dentro["dias_vencer"] = (df_dentro["data_validade"] - pd.to_datetime(date.today())).dt.days
        df_dentro["status"] = df_dentro["dias_vencer"].apply(lambda x: "🔴 VENCIDO" if x<0 else "🟢 OK")

        st.markdown("#### 📋 ESTOQUE DENTRO DA GAVETA - Edite e clique SALVAR")

        # TABELA EDITÁVEL COM BOTÃO SALVAR
        df_edit = st.data_editor(
            df_dentro[["id","codigo","nome","marca","paletes","unit_por_palete","kilos_por_unit","total_kg","lote","status"]],
            use_container_width=True,
            key=f"editor_{sel}",
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "codigo": st.column_config.TextColumn("Código"),
                "marca": st.column_config.TextColumn("MARCA"),
                "paletes": st.column_config.NumberColumn("Paletes", min_value=0),
                "total_kg": st.column_config.NumberColumn("Total KG", disabled=True),
            }
        )

        if st.button("💾 SALVAR ALTERAÇÕES DA TABELA", type="primary", use_container_width=True, key=f"salvar_tab_{sel}"):
            for _, r in df_edit.iterrows():
                con.execute("UPDATE estoque SET codigo=?, nome=?, marca=?, paletes=?, unit_por_palete=?, kilos_por_unit=?, lote=? WHERE id=?",
                            (r["codigo"], r["nome"], r["marca"], int(r["paletes"]), int(r["unit_por_palete"]), float(r["kilos_por_unit"]), r["lote"], int(r["id"])))
            con.commit()
            st.success("✅ Alterações salvas! Estoque atualizado.")
            st.rerun()

        st.divider()

        # ----- BLOCO SAÍDA -----
        st.markdown("#### 🔴 REGISTRAR SAÍDA")
        with st.form(f"form_saida_{sel}", clear_on_submit=True):
            cs1,cs2 = st.columns(2)
            id_saida = cs1.selectbox("Escolha o item para SAÍDA", df_dentro["id"].tolist(), format_func=lambda x: f"ID {x} - {df_dentro[df_dentro.id==x].iloc[0]['codigo']} - {df_dentro[df_dentro.id==x].iloc[0]['marca']} - {df_dentro[df_dentro.id==x].iloc[0]['total_kg']:.0f} KG")
            qtd_saida = cs2.number_input("Qtd Paletes SAÍDA", min_value=1, value=1)

            if st.form_submit_button("🔴 SALVAR SAÍDA - ATUALIZA ESTOQUE", type="primary", use_container_width=True):
                row_s = df_dentro[df_dentro.id==id_saida].iloc[0]
                total_saida = qtd_saida * row_s["unit_por_palete"] * row_s["kilos_por_unit"]
                con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, total_kg) VALUES (?,?,?,?,?,?,?,?)",
                            (datetime.now().isoformat(), sel, row_s["codigo"], row_s["nome"], row_s["marca"], "SAIDA", qtd_saida, total_saida))
                if qtd_saida >= row_s["paletes"]:
                    con.execute("DELETE FROM estoque WHERE id=?", (int(id_saida),))
                else:
                    con.execute("UPDATE estoque SET paletes = paletes -? WHERE id=?", (int(qtd_saida), int(id_saida)))
                con.commit()
                st.success(f"✅ SAÍDA salva: {total_saida:.0f} KG - estoque atualizado!")
                st.rerun()

        # HISTÓRICO DA GAVETA
        st.divider()
        st.markdown("#### 📊 Histórico desta gaveta")
        df_hist = pd.read_sql(f"SELECT * FROM historico WHERE gaveta_id={sel} ORDER BY data DESC", con)
        if not df_hist.empty:
            df_hist["data"] = pd.to_datetime(df_hist["data"])
            st.dataframe(df_hist, use_container_width=True)
            fig = px.bar(df_hist, x="data", y="total_kg", color="tipo", barmode="group", color_discrete_map={"ENTRADA":"#16A34A","SAIDA":"#DC2626"}, title="Entradas x Saídas")
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Gaveta vazia - faça uma ENTRADA acima")

    con.close()
    st.markdown('</div>', unsafe_allow_html=True)
