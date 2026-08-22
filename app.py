import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime, timedelta
import plotly.express as px

# CONFIGURAÇÃO VISUAL
st.set_page_config(layout="wide", page_title="Controle Fornos", page_icon="🔧")
st.markdown("""
<style>
   .main-header { background: linear-gradient(90deg, #1E3A8A, #3B82F6); padding: 25px; border-radius: 15px; text-align: center; color: white; font-size: 32px; font-weight: 900; margin-bottom: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.2); }
   .gaveta-card { background: white; border: 2px solid #E5E7EB; border-radius: 12px; padding: 15px; text-align: center; transition: 0.3s; }
   .gaveta-card:hover { border-color: #3B82F6; box-shadow: 0 5px 15px rgba(59,130,246,0.3); }
   .box-entrada { background: #F0FDF4; border: 3px solid #16A34A; border-radius: 12px; padding: 20px; }
   .box-saida { background: #FEF2F2; border: 3px solid #DC2626; border-radius: 12px; padding: 20px; }
   .box-dentro { background: #FFFFFF; border: 3px solid #3B82F6; border-radius: 12px; padding: 20px; margin-top: 15px; }
    div.stButton > button[kind="primary"] { font-weight: 800; font-size: 16px; height: 50px; }
</style>
""", unsafe_allow_html=True)

DB = "estoque_fornos.db"

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS materiais (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT, nome TEXT, marca TEXT, categoria TEXT, peso REAL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS estoque (id INTEGER PRIMARY KEY AUTOINCREMENT, gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT, paletes INT, unit_pal INT, kg_unit REAL, fab DATE, validade DATE, lote TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, gaveta_id INT, codigo TEXT, nome TEXT, marca TEXT, tipo TEXT, paletes INT, total_kg REAL)""")
    con.commit()
    con.close()

init_db()

if 'gaveta_sel' not in st.session_state: st.session_state.gaveta_sel = 1

st.markdown('<div class="main-header">🔧 REFORMA DE FORNOS - CONTROLE TOTAL</div>', unsafe_allow_html=True)

# MENU LATERAL COM GRÁFICO
with st.sidebar:
    st.markdown("### 📊 RESUMO GERAL")
    con = sqlite3.connect(DB)
    total_kg = con.execute("SELECT SUM(paletes * unit_pal * kg_unit) FROM estoque").fetchone()[0] or 0
    total_itens = con.execute("SELECT COUNT(*) FROM estoque").fetchone()[0] or 0
    con.close()
    st.metric("Total em Estoque", f"{total_kg:,.0f} KG")
    st.metric("Itens Armazenados", total_itens)
    st.divider()
    st.markdown("### 📦 GAVETAS")
    for i in range(1,21):
        if st.button(f"Gaveta {i:02d}", key=f"side_{i}", use_container_width=True, type="primary" if st.session_state.gaveta_sel==i else "secondary"):
            st.session_state.gaveta_sel = i
            st.rerun()

# ABAS PRINCIPAIS
tab_cad, tab_gavetas = st.tabs(["📝 CADASTRO DE MATERIAIS", "📦 GAVETAS - ENTRADA / SAÍDA / SALVAR"])

with tab_cad:
    st.markdown("## 📝 Cadastro de Materiais com MARCA")
    st.info("✅ Aqui o ID é LIVRE - pode cadastrar mesmo código com marcas diferentes!")

    con = sqlite3.connect(DB)
    with st.container(border=True):
        c1,c2,c3 = st.columns(3)
        codigo = c1.text_input("CÓDIGO / ID", placeholder="Ex: TIJ-001")
        nome = c2.text_input("NOME DO MATERIAL", placeholder="Ex: Tijolo Refratário")
        marca = c3.text_input("MARCA", placeholder="Ex: Santa Cruz")

        c4,c5,c6 = st.columns(3)
        categoria = c4.selectbox("Categoria", ["Refratário","Cimento","Manta","Isolante","Ferragem"])
        peso = c5.number_input("Peso por Unidade KG", value=25.0, step=0.5)
        fornecedor = c6.text_input("Fornecedor")

        if st.button("💾 SALVAR MATERIAL", type="primary", use_container_width=True):
            if codigo and nome and marca:
                con.execute("INSERT INTO materiais (codigo, nome, marca, categoria, peso) VALUES (?,?,?,?,?)", (codigo, nome, marca, categoria, peso))
                con.commit()
                st.success(f"✅ SALVO: {codigo} - {nome} - MARCA {marca}")
            else:
                st.error("Preencha Código, Nome e Marca!")

    st.divider()
    df_mat = pd.read_sql("SELECT * FROM materiais ORDER BY id DESC", con)
    st.markdown(f"### Materiais Cadastrados ({len(df_mat)})")
    st.dataframe(df_mat, use_container_width=True, height=350)

    if not df_mat.empty:
        col_del1, col_del2 = st.columns([3,1])
        id_del = col_del1.selectbox("Excluir material:", df_mat["id"].tolist(), format_func=lambda x: f"ID {x} - {df_mat[df_mat.id==x].iloc[0]['codigo']} | {df_mat[df_mat.id==x].iloc[0]['nome']} | MARCA {df_mat[df_mat.id==x].iloc[0]['marca']}")
        if col_del2.button("🗑️ EXCLUIR", use_container_width=True):
            con.execute("DELETE FROM materiais WHERE id=?", (int(id_del),))
            con.commit()
            st.rerun()
    con.close()

with tab_gavetas:
    # BARRA DE GAVETAS COM VISUAL
    st.markdown("### 📦 CLIQUE NA GAVETA PARA ABRIR")
    cols = st.columns(5)
    con = sqlite3.connect(DB)
    for i in range(1,21):
        total_g = con.execute("SELECT SUM(paletes * unit_pal * kg_unit) FROM estoque WHERE gaveta_id=?", (i,)).fetchone()[0] or 0
        qtd_g = con.execute("SELECT COUNT(*) FROM estoque WHERE gaveta_id=?", (i,)).fetchone()[0] or 0
        cor = "🔴" if total_g==0 else "🟢"
        with cols[(i-1)%5]:
            if st.button(f"{cor} Gaveta {i:02d}\n{qtd_g} itens\n{total_g:.0f} KG", key=f"g_{i}", use_container_width=True, type="primary" if st.session_state.gaveta_sel==i else "secondary"):
                st.session_state.gaveta_sel = i
                st.rerun()
    con.close()

    sel = st.session_state.gaveta_sel
    con = sqlite3.connect(DB)
    df_mat = pd.read_sql("SELECT * FROM materiais", con)

    if df_mat.empty:
        st.warning("⚠️ Cadastre um material primeiro na aba CADASTRO!")
        st.stop()

    st.divider()
    st.markdown(f"# 📂 GAVETA {sel:02d} ABERTA")

    # CAIXA DE ENTRADA
    with st.container(border=True):
        st.markdown('<div class="box-entrada"><h3>🟢 1. ENTRADA DE MATERIAL - ADICIONA DENTRO DA GAVETA</h3></div>', unsafe_allow_html=True)
        ce1, ce2, ce3 = st.columns([2,1,1])
        mat_sel = ce1.selectbox("Selecione material cadastrado:", df_mat["id"].tolist(), format_func=lambda x: f"{df_mat[df_mat.id==x].iloc[0]['codigo']} - {df_mat[df_mat.id==x].iloc[0]['nome']} - MARCA: {df_mat[df_mat.id==x].iloc[0]['marca']}", key=f"mat_e_{sel}")
        row_m = df_mat[df_mat.id==mat_sel].iloc[0]

        codigo_e = ce2.text_input("Código", value=row_m["codigo"], key=f"cod_e_{sel}")
        marca_e = ce3.text_input("Marca", value=row_m["marca"], key=f"marca_e_{sel}")

        ce4, ce5, ce6, ce7, ce8 = st.columns(5)
        pal_e = ce4.number_input("Paletes", min_value=1, value=1, key=f"pal_e_{sel}")
        unit_e = ce5.number_input("Unit/Palete", min_value=1, value=56, key=f"unit_e_{sel}")
        kg_e = ce6.number_input("Kg/Unit", min_value=0.1, value=float(row_m["peso"]), key=f"kg_e_{sel}")
        fab_e = ce7.date_input("Fabricação", value=date.today(), key=f"fab_e_{sel}")
        dias_e = ce8.number_input("Validade dias", min_value=1, value=90, key=f"dias_e_{sel}")

        lote_e = st.text_input("Lote / Obs", key=f"lote_e_{sel}", placeholder="Ex: LOTE 123 - Marca diferente")

        if st.button("🟢 SALVAR ENTRADA - GRAVA DENTRO DA GAVETA", type="primary", use_container_width=True, key=f"btn_e_{sel}"):
            validade = fab_e + timedelta(days=dias_e)
            total = pal_e * unit_e * kg_e
            con.execute("INSERT INTO estoque (gaveta_id, codigo, nome, marca, paletes, unit_pal, kg_unit, fab, validade, lote) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (sel, codigo_e, row_m["nome"], marca_e, pal_e, unit_e, kg_e, fab_e.isoformat(), validade.isoformat(), lote_e))
            con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, total_kg) VALUES (?,?,?,?,?,?,?,?)",
                        (datetime.now().isoformat(), sel, codigo_e, row_m["nome"], marca_e, "ENTRADA", pal_e, total))
            con.commit()
            st.success(f"✅ ENTRADA GRAVADA: {total:.0f} KG dentro da Gaveta {sel}")
            st.balloons()
            st.rerun()

    # O QUE TEM DENTRO
    df_dentro = pd.read_sql(f"SELECT * FROM estoque WHERE gaveta_id={sel} ORDER BY id DESC", con)

    if not df_dentro.empty:
        df_dentro["total_kg"] = df_dentro["paletes"] * df_dentro["unit_pal"] * df_dentro["kg_unit"]

        with st.container(border=True):
            st.markdown('<div class="box-dentro"><h3>📋 O QUE ESTÁ DENTRO DESSA GAVETA - EDITÁVEL</h3></div>', unsafe_allow_html=True)

            df_edit = st.data_editor(
                df_dentro,
                use_container_width=True,
                num_rows="dynamic",
                key=f"editor_{sel}",
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "gaveta_id": st.column_config.NumberColumn("Gaveta", disabled=True),
                    "codigo": st.column_config.TextColumn("CÓDIGO (editável)"),
                    "nome": st.column_config.TextColumn("Nome"),
                    "marca": st.column_config.TextColumn("MARCA (editável)"),
                    "paletes": st.column_config.NumberColumn("Paletes", min_value=0),
                    "total_kg": st.column_config.NumberColumn("Total KG", disabled=True),
                }
            )

            if st.button("💾 SALVAR ALTERAÇÕES DA TABELA", type="primary", use_container_width=True, key=f"save_tab_{sel}"):
                for _, r in df_edit.iterrows():
                    con.execute("UPDATE estoque SET codigo=?, nome=?, marca=?, paletes=?, unit_pal=?, kg_unit=?, lote=? WHERE id=?",
                                (r["codigo"], r["nome"], r["marca"], int(r["paletes"]), int(r["unit_pal"]), float(r["kg_unit"]), r["lote"], int(r["id"])))
                con.commit()
                st.success("✅ TABELA SALVA E ATUALIZADA!")
                st.rerun()

        # CAIXA DE SAÍDA
        with st.container(border=True):
            st.markdown('<div class="box-saida"><h3>🔴 2. SAÍDA DE MATERIAL - RETIRA DA GAVETA</h3></div>', unsafe_allow_html=True)
            cs1, cs2 = st.columns(2)
            id_saida = cs1.selectbox("Escolha qual item tirar:", df_dentro["id"].tolist(), format_func=lambda x: f"ID {x} - {df_dentro[df_dentro.id==x].iloc[0]['codigo']} - {df_dentro[df_dentro.id==x].iloc[0]['marca']} - {df_dentro[df_dentro.id==x].iloc[0]['total_kg']:.0f}KG", key=f"saida_sel_{sel}")
            qtd_saida = cs2.number_input("Quantos paletes tirar?", min_value=1, value=1, key=f"qtd_s_{sel}")

            if st.button("🔴 SALVAR SAÍDA - ATUALIZA ESTOQUE", type="primary", use_container_width=True, key=f"btn_s_{sel}"):
                row_s = df_dentro[df_dentro.id==id_saida].iloc[0]
                total_s = qtd_saida * row_s["unit_pal"] * row_s["kg_unit"]
                con.execute("INSERT INTO historico (data, gaveta_id, codigo, nome, marca, tipo, paletes, total_kg) VALUES (?,?,?,?,?,?,?,?)",
                            (datetime.now().isoformat(), sel, row_s["codigo"], row_s["nome"], row_s["marca"], "SAIDA", qtd_saida, total_s))
                if qtd_saida >= row_s["paletes"]:
                    con.execute("DELETE FROM estoque WHERE id=?", (int(id_saida),))
                else:
                    con.execute("UPDATE estoque SET paletes = paletes -? WHERE id=?", (int(qtd_saida), int(id_saida)))
                con.commit()
                st.success(f"✅ SAÍDA GRAVADA: {total_s:.0f} KG retirados da Gaveta {sel}")
                st.rerun()

        # HISTÓRICO GRÁFICO
        st.divider()
        df_hist = pd.read_sql(f"SELECT * FROM historico WHERE gaveta_id={sel} ORDER BY data DESC", con)
        if not df_hist.empty:
            df_hist["data"] = pd.to_datetime(df_hist["data"])
            c_hist1, c_hist2 = st.columns([2,1])
            with c_hist1:
                fig = px.bar(df_hist, x="data", y="total_kg", color="tipo", barmode="group", title=f"Histórico Gaveta {sel}", color_discrete_map={"ENTRADA":"#16A34A","SAIDA":"#DC2626"})
                st.plotly_chart(fig, use_container_width=True)
            with c_hist2:
                st.dataframe(df_hist[["data","codigo","marca","tipo","total_kg"]], use_container_width=True)
    else:
        st.info("📭 Gaveta vazia - faça uma ENTRADA acima, vai ficar gravado dentro dela")

    con.close()
