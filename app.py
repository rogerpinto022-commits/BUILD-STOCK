import streamlit as st
import pandas as pd
import sqlite3, os
from datetime import date, datetime, timedelta
import plotly.express as px

st.set_page_config(layout="wide", page_title="Controle Fornos", page_icon="🔧")

DB = "estoque_fornos.db"

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS materiais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT, nome TEXT, marca TEXT, categoria TEXT, peso REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT,
        paletes INT, unit_pal INT, kg_unit REAL, fab DATE, validade DATE, lote TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT, gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT,
        tipo TEXT, paletes INT, total_kg REAL)""")
    con.commit()
    con.close()

# TENTA INICIAR, SE DER ERRO DE SCHEMA, APAGA E RECRIA
try:
    init_db()
    con = sqlite3.connect(DB)
    con.execute("SELECT SUM(paletes * unit_pal * kg_unit) FROM estoque").fetchone()
    con.close()
except sqlite3.OperationalError:
    os.remove(DB) # apaga banco velho com erro
    init_db()
    st.warning("Banco antigo com erro foi corrigido automaticamente! Recarregando...")
    st.rerun()

if 'gaveta_sel' not in st.session_state: st.session_state.gaveta_sel = 1

st.markdown("""
<style>
.main-header { background: linear-gradient(90deg, #1E3A8A, #3B82F6); padding: 20px; border-radius: 15px; text-align: center; color: white; font-size: 28px; font-weight: 900; }
.box-entrada { background: #F0FDF4; border: 3px solid #16A34A; border-radius: 12px; padding: 15px; }
.box-saida { background: #FEF2F2; border: 3px solid #DC2626; border-radius: 12px; padding: 15px; }
</style>
<div class="main-header">🔧 REFORMA DE FORNOS - INTERFACE GRÁFICA</div>
""", unsafe_allow_html=True)

# SIDEBAR COM TRY
with st.sidebar:
    st.markdown("### 📊 RESUMO")
    try:
        con = sqlite3.connect(DB)
        total_kg = con.execute("SELECT SUM(paletes * unit_pal * kg_unit) FROM estoque").fetchone()[0] or 0
        total_itens = con.execute("SELECT COUNT(*) FROM estoque").fetchone()[0] or 0
        con.close()
    except:
        total_kg = 0
        total_itens = 0

    st.metric("Total Estoque", f"{total_kg:,.0f} KG")
    st.metric("Itens", total_itens)
    st.divider()
    for i in range(1,21):
        if st.button(f"Gaveta {i:02d}", key=f"side_{i}", use_container_width=True, type="primary" if st.session_state.gaveta_sel==i else "secondary"):
            st.session_state.gaveta_sel = i
            st.rerun()

tab_cad, tab_gavetas = st.tabs(["📝 CADASTRO", "📦 GAVETAS - ENTRADA / SAÍDA"])

with tab_cad:
    st.subheader("Cadastro ID LIVRE + MARCA - pode repetir mesmo código")
    con = sqlite3.connect(DB)
    with st.form("cad_mat", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        codigo = c1.text_input("CÓDIGO ID (LIVRE)")
        nome = c2.text_input("NOME")
        marca = c3.text_input("MARCA")
        c4,c5 = st.columns(2)
        categoria = c4.selectbox("Categoria", ["Refratário","Cimento","Manta","Isolante","Ferragem","Outro"])
        peso = c5.number_input("Peso KG", value=25.0)
        if st.form_submit_button("💾 SALVAR MATERIAL", type="primary", use_container_width=True):
            if codigo and nome and marca:
                con.execute("INSERT INTO materiais (codigo, nome, marca, categoria, peso) VALUES (?,?,?,?,?)", (codigo, nome, marca, categoria, peso))
                con.commit()
                st.success(f"SALVO: {codigo} - {marca}")
            else:
                st.error("Preencha Código, Nome e Marca")

    df_mat = pd.read_sql("SELECT * FROM materiais ORDER BY id DESC", con)
    st.dataframe(df_mat, use_container_width=True, height=300)
    con.close()

with tab_gavetas:
    st.markdown("### 📦 Clique na gaveta")
    cols = st.columns(5)
    con = sqlite3.connect(DB)
    for i in range(1,21):
        try:
            total_g = con.execute("SELECT SUM(paletes * unit_pal * kg_unit) FROM estoque WHERE gaveta_id=?", (i,)).fetchone()[0] or 0
        except:
            total_g = 0
        with cols[(i-1)%5]:
            if st.button(f"📦 Gaveta {i:02d}\n{total_g:.0f} KG", key=f"g_{i}", use_container_width=True, type="primary" if st.session_state.gaveta_sel==i else "secondary"):
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
    st.markdown(f"## 📂 GAVETA {sel:02d} - ABERTA")

    # ENTRADA
    with st.container(border=True):
        st.markdown("#### 🟢 ENTRADA - Adiciona DENTRO")
        ce1, ce2, ce3 = st.columns([2,1,1])
        mat_sel = ce1.selectbox("Material:", df_mat["id"].tolist(), format_func=lambda x: f"{df_mat[df_mat.id==x].iloc[0]['codigo']} - {df_mat[df_mat.id==x].iloc[0]['nome']} - MARCA {df_mat[df_mat.id==x].iloc[0]['marca']}")
        row_m = df_mat[df_mat.id==mat_sel].iloc[0]
        codigo_e = ce2.text_input("Código", value=row_m["codigo"], key=f"cod_e_{sel}")
        marca_e = ce3.text_input("Marca", value=row_m["marca"], key=f"marca_e_{sel}")

        ce4, ce5, ce6, ce7 = st.columns(4)
        pal_e = ce4.number_input("Paletes", min_value=1, value=1, key=f"pal_e_{sel}")
        unit_e = ce5.number_input("Unit/Palete", min_value=1, value=56, key=f"unit_e_{sel}")
        kg_e = ce6.number_input("Kg/Unit", min_value=0.1, value=float(row_m["peso"]), key=f"kg_e_{sel}")
        dias_e = ce7.number_input("Validade dias", min_value=1, value=90, key=f"dias_e_{sel}")
        fab_e = st.date_input("Fabricação", value=date.today(), key=f"fab_e_{sel}")

        if st.button("🟢 SALVAR ENTRADA", type="primary", use_container_width=True, key=f"btn_e_{sel}"):
            validade = fab_e + timedelta(days=dias_e)
            total = pal_e * unit_e * kg_e
            con.execute("INSERT INTO estoque (gaveta_id, codigo, nome, marca, paletes, unit_pal, kg_unit, fab, validade) VALUES (?,?,?,?,?,?,?,?,?)",
                        (sel, codigo_e, row_m["nome"], marca_e, pal_e, unit_e, kg_e, fab_e.isoformat(), validade.isoformat()))
            con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, total_kg) VALUES (?,?,?,?,?,?,?,?)",
                        (datetime.now().isoformat(), sel, codigo_e, row_m["nome"], marca_e, "ENTRADA", pal_e, total))
            con.commit()
            st.success(f"ENTRADA {total:.0f} KG salva na Gaveta {sel}!")
            st.balloons()
            st.rerun()

    # DENTRO DA GAVETA
    df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE gaveta_id={sel} ORDER BY id DESC", con)

    if not df_dentro.empty:
        df_dentro["total_kg"] = df_dentro["paletes"] * df_dentro["unit_pal"] * df_dentro["kg_unit"]
        st.markdown("#### 📋 DENTRO DA GAVETA - Edite e SALVE")

        df_edit = st.data_editor(df_dentro, use_container_width=True, key=f"edit_{sel}")

        if st.button("💾 SALVAR ALTERAÇÕES", type="primary", use_container_width=True, key=f"save_{sel}"):
            for _, r in df_edit.iterrows():
                con.execute("UPDATE estoque SET codigo=?, nome=?, marca=?, paletes=?, unit_pal=?, kg_unit=? WHERE id=?",
                            (r["codigo"], r["nome"], r["marca"], int(r["paletes"]), int(r["unit_pal"]), float(r["kg_unit"]), int(r["id"])))
            con.commit()
            st.success("Alterações salvas!")
            st.rerun()

        st.divider()
        # SAIDA
        with st.container(border=True):
            st.markdown("#### 🔴 SAÍDA - Retira da gaveta")
            cs1, cs2 = st.columns(2)
            id_saida = cs1.selectbox("Item para SAÍDA:", df_dentro["id"].tolist(), format_func=lambda x: f"ID {x} - {df_dentro[df_dentro.id==x].iloc[0]['codigo']} - MARCA {df_dentro[df_dentro.id==x].iloc[0]['marca']} - {df_dentro[df_dentro.id==x].iloc[0]['total_kg']:.0f}KG")
            qtd_saida = cs2.number_input("Qtd Paletes SAÍDA", min_value=1, value=1, key=f"qtd_s_{sel}")

            if st.button("🔴 SALVAR SAÍDA", type="primary", use_container_width=True, key=f"btn_s_{sel}"):
                row_s = df_dentro[df_dentro.id==id_saida].iloc[0]
                total_s = qtd_saida * row_s["unit_pal"] * row_s["kg_unit"]
                con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, total_kg) VALUES (?,?,?,?,?,?,?,?)",
                            (datetime.now().isoformat(), sel, row_s["codigo"], row_s["nome"], row_s["marca"], "SAIDA", qtd_saida, total_s))
                if qtd_saida >= row_s["paletes"]:
                    con.execute("DELETE FROM estoque WHERE id=?", (int(id_saida),))
                else:
                    con.execute("UPDATE estoque SET paletes = paletes -? WHERE id=?", (int(qtd_saida), int(id_saida)))
                con.commit()
                st.success(f"SAÍDA {total_s:.0f} KG salva!")
                st.rerun()

        # HISTORICO
        df_hist = pd.read_sql(f"SELECT * FROM historico WHERE gaveta_id={sel} ORDER BY data DESC", con)
        if not df_hist.empty:
            df_hist["data"] = pd.to_datetime(df_hist["data"])
            fig = px.bar(df_hist, x="data", y="total_kg", color="tipo", barmode="group", color_discrete_map={"ENTRADA":"#16A34A","SAIDA":"#DC2626"})
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("Gaveta vazia - faça ENTRADA acima")

    con.close()
