import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px

st.set_page_config(page_title="BUILD STOCK - WMS PRO", layout="wide", page_icon="📦")
st.title("📦 BUILD STOCK - WMS 3 ÁREAS | ID RASTREÁVEL")

if "estoque" not in st.session_state:
    st.session_state.estoque = pd.DataFrame(columns=[
        "ID_RASTREADOR","AREA","DESCRICAO","LOTE","FABRICACAO","VALIDADE_DIAS","VENCIMENTO",
        "TIPO_EMBALAGEM","QTD_POR_EMBALAGEM","UN_MEDIDA","QTD_EMBALAGENS","TOTAL_UNIDADES",
        "MOV_TIPO","DATA_MOV","STATUS"
    ])

df = st.session_state.estoque

st.sidebar.header("📝 Movimentação")
ids_existentes = ["+ NOVO ID"] + sorted(df["ID_RASTREADOR"].unique().tolist()) if not df.empty else ["+ NOVO ID"]
escolha_id = st.sidebar.selectbox("🔖 ID RASTREADOR", ids_existentes)

dados_auto = {}
if escolha_id!= "+ NOVO ID" and not df.empty:
    ultimo = df[df["ID_RASTREADOR"] == escolha_id].iloc[-1]
    dados_auto = ultimo.to_dict()
    st.sidebar.success(f"ID {escolha_id} encontrado - auto preenchido")
    id_final = escolha_id
else:
    id_final = st.sidebar.text_input("Digite o NOVO ID", placeholder="Ex: ID-001").upper()

mov_tipo = st.sidebar.selectbox("TIPO MOVIMENTAÇÃO", ["ENTRADA", "SAÍDA", "DEVOLUÇÃO"])

with st.sidebar.form("form_mov", clear_on_submit=False):
    area = st.selectbox("📍 ÁREA", ["ÁREA 1","ÁREA 2","ÁREA 3"])
    descricao = st.text_input("📝 DESCRIÇÃO", value=dados_auto.get("DESCRICAO",""))
    lote = st.text_input("🏷️ LOTE", value=dados_auto.get("LOTE",""))
    c1,c2 = st.columns(2)
    with c1:
        fab = st.date_input("🏭 FABRICAÇÃO", value=date.today())
    with c2:
        val_dias = st.number_input("⏳ VALIDADE DIAS", min_value=1, value=int(dados_auto.get("VALIDADE_DIAS",90)) if dados_auto.get("VALIDADE_DIAS") else 90)
    tipo_emb = st.selectbox("📦 TIPO EMBALAGEM", ["Saco","Caixa","Fardo","Palete","Rolo","Galão","Balde","Outro"])
    qtd_por_emb = st.number_input("QTD POR EMBALAGEM", min_value=0.01, value=float(dados_auto.get("QTD_POR_EMBALAGEM",1.0)) if dados_auto.get("QTD_POR_EMBALAGEM") else 1.0)
    un_med = st.selectbox("📏 UNIDADE (UND,M²,KG...)", ["UND","M²","M³","KG","LITROS","TON","PÇ","M"])
    qtd_emb = st.number_input("🔢 QTD EMBALAGENS", min_value=1, value=1, step=1)

    total_uni = qtd_por_emb * qtd_emb
    if mov_tipo == "SAÍDA":
        total_uni = -total_uni
        qtd_emb_calc = -qtd_emb
    else:
        qtd_emb_calc = qtd_emb

    st.info(f"Total: {total_uni:.2f} {un_med}")
    btn = st.form_submit_button(f"💾 SALVAR {mov_tipo}", use_container_width=True)

    if btn:
        if not id_final:
            st.sidebar.error("Digite o ID!")
        else:
            venc = fab + timedelta(days=int(val_dias))
            dias_rest = (venc - date.today()).days
            status = "✅ OK" if dias_rest > 30 else "⚠️ BREVE" if dias_rest > 0 else "❌ VENCIDO"
            nova = {
                "ID_RASTREADOR": id_final, "AREA": area, "DESCRICAO": descricao, "LOTE": lote,
                "FABRICACAO": fab, "VALIDADE_DIAS": val_dias, "VENCIMENTO": venc,
                "TIPO_EMBALAGEM": tipo_emb, "QTD_POR_EMBALAGEM": qtd_por_emb, "UN_MEDIDA": un_med,
                "QTD_EMBALAGENS": qtd_emb_calc, "TOTAL_UNIDADES": total_uni,
                "MOV_TIPO": mov_tipo, "DATA_MOV": date.today(), "STATUS": status
            }
            st.session_state.estoque = pd.concat([df, pd.DataFrame([nova])], ignore_index=True)
            st.sidebar.success(f"{mov_tipo} salva no {id_final}!")
            st.rerun()

if df.empty:
    st.info("👈 Cadastre o primeiro material na lateral")
else:
    saldo = df.groupby("ID_RASTREADOR").agg(
        SALDO_EMB=("QTD_EMBALAGENS","sum"), SALDO_UNI=("TOTAL_UNIDADES","sum"),
        DESCRICAO=("DESCRICAO","last"), AREA=("AREA","last")
    ).reset_index()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("IDs Ativos", len(saldo[saldo["SALDO_EMB"]>0]))
    c2.metric("Total Embalagens", f"{saldo[saldo['SALDO_EMB']>0]['SALDO_EMB'].sum():.0f}")
    c3.metric("Total Unidades", f"{saldo[saldo['SALDO_UNI']>0]['SALDO_UNI'].sum():.2f}")
    c4.metric("Mov Hoje", len(df[df["DATA_MOV"]==date.today()]))

    tab_graf, tab_tabela, tab_edit = st.tabs(["📊 GRÁFICOS", "📋 ESTOQUE", "✏️ EDITAR / EXCLUIR"])

    with tab_graf:
        cg1,cg2 = st.columns(2)
        with cg1:
            fig_area = px.bar(df.groupby("AREA")["TOTAL_UNIDADES"].sum().reset_index(), x="AREA", y="TOTAL_UNIDADES", color="AREA", title="Movimentação por Área", text_auto=True)
            st.plotly_chart(fig_area, use_container_width=True)
            fig_mov = px.pie(df, names="MOV_TIPO", values="QTD_EMBALAGENS", title="Entrada x Saída x Devolução", hole=0.4)
            st.plotly_chart(fig_mov, use_container_width=True)
        with cg2:
            fig_id = px.bar(saldo.sort_values("SALDO_UNI", ascending=False).head(10), x="ID_RASTREADOR", y="SALDO_UNI", title="Top 10 IDs - Saldo Unidades", text_auto=True, color="SALDO_UNI")
            st.plotly_chart(fig_id, use_container_width=True)
            fig_val = px.histogram(df, x="VENCIMENTO", color="STATUS", title="Vencimentos por Data")
            st.plotly_chart(fig_val, use_container_width=True)

    with tab_tabela:
        st.subheader("Saldo Atual por ID Rastreador")
        st.dataframe(saldo[saldo["SALDO_EMB"]>0], use_container_width=True)
        st.subheader("Histórico Completo")
        filtro_id2 = st.selectbox("Filtrar ID", ["TODOS"] + sorted(df["ID_RASTREADOR"].unique().tolist()), key="filtro2")
        df_show = df if filtro_id2=="TODOS" else df[df["ID_RASTREADOR"]==filtro_id2]
        st.dataframe(df_show.sort_values("DATA_MOV", ascending=False), use_container_width=True, height=400)
        c_s1,c_s2 = st.columns(2)
        c_s1.success(f"SOMA TOTAL EMBALAGENS: {df_show['QTD_EMBALAGENS'].sum():.0f}")
        c_s2.success(f"SOMA TOTAL UNIDADES: {df_show['TOTAL_UNIDADES'].sum():.2f}")

    with tab_edit:
        st.subheader("✏️ Editar e Excluir Registros")
        df_edit = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="editor")
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            if st.button("💾 SALVAR EDIÇÕES", use_container_width=True):
                st.session_state.estoque = df_edit
                st.success("Alterações salvas!")
                st.rerun()
        with col_e2:
            id_del = st.selectbox("ID para excluir", [""] + sorted(df["ID_RASTREADOR"].unique().tolist()))
            if st.button("🗑️ EXCLUIR ID INTEIRO", use_container_width=True):
                if id_del:
                    st.session_state.estoque = df[df["ID_RASTREADOR"]!= id_del]
                    st.success(f"ID {id_del} excluído!")
                    st.rerun()
        with col_e3:
            if st.button("🔥 LIMPAR TUDO", use_container_width=True):
                st.session_state.estoque = pd.DataFrame(columns=df.columns)
                st.rerun()
