import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px

st.set_page_config(page_title="BUILD STOCK WMS", layout="wide", page_icon="📦")
st.title("📦 BUILD STOCK - CONTROLE REFRATÁRIOS | WMS PRO")

AREAS_REAIS = ["GALPÃO DE MATERIAIS REFRATÁRIOS", "SALA ANEXA", "OFICINA DE REVESTIMENTO"]

if "catalogo" not in st.session_state:
    st.session_state.catalogo = pd.DataFrame(columns=[
        "ID_RASTREADOR","DESCRICAO","MARCA","LOTE","FABRICACAO","VALIDADE_DIAS","VENCIMENTO",
        "TIPO_EMBALAGEM","QTD_POR_EMBALAGEM","UN_MEDIDA","AREA"
    ])
if "mov" not in st.session_state:
    st.session_state.mov = pd.DataFrame(columns=[
        "ID_RASTREADOR","DESCRICAO","MARCA","LOTE","FABRICACAO","VENCIMENTO",
        "TIPO_EMBALAGEM","QTD_POR_EMBALAGEM","UN_MEDIDA","QTD_EMBALAGENS","TOTAL_KG_MEDIDA","AREA","MOV_TIPO","DATA_MOV","STATUS"
    ])

cat = st.session_state.catalogo
mov = st.session_state.mov

tab_cad, tab_ent, tab_sai, tab_dev, tab_est, tab_graf, tab_edit = st.tabs([
    "🆕 CADASTRO MESTRE", "⬇️ ENTRADA", "⬆️ SAÍDA", "↩️ DEVOLUÇÃO", "📋 ESTOQUE", "📊 GRÁFICOS", "✏️ EDITAR"
])

with tab_cad:
    st.header("🆕 CADASTRO MESTRE - Com MARCA, LOTE, FABRICAÇÃO")
    st.write("Cadastre aqui para auto preenchimento nas movimentações")
    with st.form("cad", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            id_r = st.text_input("🔖 ID RASTREADOR *", placeholder="ID-001").upper()
            desc = st.text_input("📝 DESCRIÇÃO *", placeholder="Ex: Cimento Refratário")
            marca = st.text_input("🏷️ MARCA *", placeholder="Ex: Votoran, Refratil, Magnesita")
        with c2:
            lote = st.text_input("🔢 LOTE *")
            fab = st.date_input("🏭 DATA FABRICAÇÃO", value=date.today())
            val_d = st.number_input("⏳ VALIDADE DIAS", 1, value=90)
        with c3:
            tipo = st.selectbox("📦 TIPO EMBALAGEM", ["Palete","Saco","Caixa","Fardo","Rolo","Galão","Balde","Outro"])
            qtd_por = st.number_input("QTD POR EMBALAGEM", 0.01, value=25.0)
            un = st.selectbox("📏 UNIDADE", ["KG","UND","M²","M³","LITROS","TON","PÇ","M"])
            area = st.selectbox("📍 ÁREA", AREAS_REAIS)
        if st.form_submit_button("💾 CADASTRAR MATERIAL", type="primary", use_container_width=True):
            if id_r and desc and lote and marca:
                venc = fab + timedelta(days=int(val_d))
                novo = {"ID_RASTREADOR":id_r,"DESCRICAO":desc,"MARCA":marca,"LOTE":lote,"FABRICACAO":fab,"VALIDADE_DIAS":val_d,"VENCIMENTO":venc,"TIPO_EMBALAGEM":tipo,"QTD_POR_EMBALAGEM":qtd_por,"UN_MEDIDA":un,"AREA":area}
                st.session_state.catalogo = pd.concat([cat, pd.DataFrame([novo])], ignore_index=True)
                st.success(f"{id_r} - {marca} cadastrado!"); st.rerun()
            else: st.error("Preencha ID, Descrição, Marca e Lote!")
    if not cat.empty:
        st.subheader(f"{len(cat)} Materiais Cadastrados")
        st.dataframe(cat, use_container_width=True)

def get_p(id_b):
    r = cat[cat["ID_RASTREADOR"]==id_b]
    return r.iloc[0] if not r.empty else None

def salvar(id_r, area, tipo_mov, qtd):
    p = get_p(id_r)
    if p is None: return False
    total = float(p["QTD_POR_EMBALAGEM"])*int(qtd)
    if tipo_mov=="SAÍDA": total=-total; qtd=-int(qtd)
    dias = (p["VENCIMENTO"]-date.today()).days if isinstance(p["VENCIMENTO"], date) else 99
    status = "✅ OK" if dias>30 else "⚠️ BREVE" if dias>0 else "❌ VENCIDO"
    nova = {"ID_RASTREADOR":id_r,"DESCRICAO":p["DESCRICAO"],"MARCA":p["MARCA"],"LOTE":p["LOTE"],"FABRICACAO":p["FABRICACAO"],"VENCIMENTO":p["VENCIMENTO"],"TIPO_EMBALAGEM":p["TIPO_EMBALAGEM"],"QTD_POR_EMBALAGEM":p["QTD_POR_EMBALAGEM"],"UN_MEDIDA":p["UN_MEDIDA"],"QTD_EMBALAGENS":qtd,"TOTAL_KG_MEDIDA":total,"AREA":area,"MOV_TIPO":tipo_mov,"DATA_MOV":date.today(),"STATUS":status}
    st.session_state.mov = pd.concat([mov, pd.DataFrame([nova])], ignore_index=True)
    return True

with tab_ent:
    st.header("⬇️ ENTRADA - Digite o ID e auto preenche MARCA/LOTE")
    if cat.empty: st.warning("Cadastre materiais primeiro na aba CADASTRO MESTRE")
    else:
        id_s = st.selectbox("🔖 ID RASTREADOR", sorted(cat["ID_RASTREADOR"].unique()), key="e_id")
        p = get_p(id_s)
        if p is not None:
            st.success(f"**{p['DESCRICAO']} | MARCA: {p['MARCA']} | LOTE: {p['LOTE']} | FAB: {p['FABRICACAO']} | {p['TIPO_EMBALAGEM']} {p['QTD_POR_EMBALAGEM']} {p['UN_MEDIDA']}**")
            c1,c2 = st.columns(2)
            with c1:
                a = st.selectbox("📍 Área Destino", AREAS_REAIS, key="e_area")
                q = st.number_input("🔢 QTD PALETES/EMBALAGENS", 1, value=1, key="e_qtd")
            with c2:
                st.metric("TOTAL KG/MEDIDA", f"{float(p['QTD_POR_EMBALAGEM'])*q:.2f} {p['UN_MEDIDA']}")
                if st.button("💾 CONFIRMAR ENTRADA", key="btn_e", type="primary", use_container_width=True):
                    salvar(id_s,a,"ENTRADA",q); st.success("Entrada OK!"); st.rerun()

with tab_sai:
    st.header("⬆️ SAÍDA - Auto preenchimento")
    if not cat.empty:
        id_s = st.selectbox("🔖 ID", sorted(cat["ID_RASTREADOR"].unique()), key="s_id")
        p = get_p(id_s)
        saldo = mov[mov["ID_RASTREADOR"]==id_s]["QTD_EMBALAGENS"].sum() if not mov.empty else 0
        if p is not None: st.warning(f"Saldo atual: {saldo:.0f} {p['TIPO_EMBALAGEM']} = {saldo*float(p['QTD_POR_EMBALAGEM']):.2f} {p['UN_MEDIDA']} | MARCA: {p['MARCA']}")
        a = st.selectbox("📍 Área Origem", AREAS_REAIS, key="s_area")
        q = st.number_input("Qtd Saída", 1, value=1, key="s_qtd")
        if st.button("💾 CONFIRMAR SAÍDA", key="btn_s", type="primary", use_container_width=True):
            salvar(id_s,a,"SAÍDA",q); st.success("Saída OK!"); st.rerun()

with tab_dev:
    st.header("↩️ DEVOLUÇÃO")
    if not cat.empty:
        id_s = st.selectbox("🔖 ID", sorted(cat["ID_RASTREADOR"].unique()), key="d_id")
        a = st.selectbox("📍 Área", AREAS_REAIS, key="d_area")
        q = st.number_input("Qtd Devolução", 1, value=1, key="d_qtd")
        if st.button("💾 CONFIRMAR DEVOLUÇÃO", key="btn_d", type="primary", use_container_width=True):
            salvar(id_s,a,"DEVOLUÇÃO",q); st.success("Devolução OK!"); st.rerun()

with tab_est:
    if mov.empty: st.info("Sem movimentações ainda")
    else:
        saldo = mov.groupby(["ID_RASTREADOR","DESCRICAO","MARCA","LOTE","TIPO_EMBALAGEM","UN_MEDIDA","AREA"]).agg(QTD_PALETES=("QTD_EMBALAGENS","sum"), SOMA_KG=("TOTAL_KG_MEDIDA","sum")).reset_index()
        saldo = saldo[saldo["QTD_PALETES"]>0]
        st.subheader("📋 Estoque Atual - Qtd Paletes + Soma KG/Medida por Produto")
        st.dataframe(saldo, use_container_width=True)
        c1,c2 = st.columns(2)
        c1.metric("TOTAL PALETES", f"{saldo['QTD_PALETES'].sum():.0f}")
        c2.metric("TOTAL KG/MEDIDA", f"{saldo['SOMA_KG'].sum():.2f} KG")
        st.subheader("Histórico Completo")
        st.dataframe(mov.sort_values("DATA_MOV", ascending=False), use_container_width=True, height=350)

with tab_graf:
    if mov.empty: st.info("Sem dados")
    else:
        sg = mov.groupby(["ID_RASTREADOR","MARCA"]).agg(QTD_PALETES=("QTD_EMBALAGENS","sum"), SOMA_KG=("TOTAL_KG_MEDIDA","sum")).reset_index()
        sg = sg[sg["QTD_PALETES"]>0]
        fig1 = px.bar(sg.sort_values("QTD_PALETES"), x="QTD_PALETES", y="ID_RASTREADOR", orientation='h', color="ID_RASTREADOR", text="QTD_PALETES", title="QTD PALETES POR ID (cada barra uma cor)", color_discrete_sequence=px.colors.qualitative.Bold)
        fig1.update_layout(showlegend=False, height=600)
        st.plotly_chart(fig1, use_container_width=True)
        fig2 = px.bar(sg.sort_values("SOMA_KG"), x="SOMA_KG", y="ID_RASTREADOR", orientation='h', color="MARCA", text="SOMA_KG", title="SOMA KG/MEDIDA POR ID - POR MARCA", color_discrete_sequence=px.colors.qualitative.Vivid)
        fig2.update_layout(height=600)
        st.plotly_chart(fig2, use_container_width=True)
        sp = mov.groupby("DESCRICAO").agg(SOMA=("TOTAL_KG_MEDIDA","sum"), QTD=("QTD_EMBALAGENS","sum")).reset_index()
        sp = sp[sp["SOMA"]>0]
        fig3 = px.bar(sp.sort_values("SOMA"), x="SOMA", y="DESCRICAO", orientation='h', color="DESCRICAO", text="SOMA", title="SOMA TOTAL POR PRODUTO (KG/MEDIDA)")
        fig3.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig3, use_container_width=True)
        fig4 = px.bar(mov.groupby("AREA").agg(SOMA=("TOTAL_KG_MEDIDA","sum")).reset_index(), x="SOMA", y="AREA", orientation='h', color="AREA", text="SOMA", title="SOMA POR ÁREA")
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

with tab_edit:
    st.subheader("✏️ Editar Cadastro (MARCA, LOTE...)")
    if not cat.empty:
        ce = st.data_editor(cat, num_rows="dynamic", use_container_width=True, key="ce")
        if st.button("💾 SALVAR CADASTRO"): st.session_state.catalogo=ce; st.success("Salvo!"); st.rerun()
    st.divider()
    st.subheader("✏️ Editar Movimentações")
    if not mov.empty:
        me = st.data_editor(mov, num_rows="dynamic", use_container_width=True, key="me")
        if st.button("💾 SALVAR MOV"): st.session_state.mov=me; st.success("Salvo!"); st.rerun()
    c1,c2 = st.columns(2)
    with c1:
        id_del = st.selectbox("Excluir ID", [""] + sorted(cat["ID_RASTREADOR"].unique().tolist()) if not cat.empty else [""])
        if st.button("🗑️ EXCLUIR ID"):
            if id_del:
                st.session_state.catalogo = cat[cat["ID_RASTREADOR"]!=id_del]
                st.session_state.mov = mov[mov["ID_RASTREADOR"]!=id_del]
                st.success(f"{id_del} excluído!"); st.rerun()
    with c2:
        if st.button("🔥 LIMPAR TUDO"):
            st.session_state.catalogo=pd.DataFrame(columns=cat.columns)
            st.session_state.mov=pd.DataFrame(columns=mov.columns)
            st.rerun()
