import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px

st.set_page_config(page_title="BUILD STOCK WMS FINAL", layout="wide", page_icon="📦")
st.title("📦 BUILD STOCK - FINAL | GALPÃO + SALA + OFICINA | FIFO + TRANSFER AUTO")

AREAS_REAIS = ["GALPÃO DE MATERIAIS REFRATÁRIOS", "SALA ANEXA", "OFICINA DE REVESTIMENTO"]

if "catalogo" not in st.session_state:
    st.session_state.catalogo = pd.DataFrame(columns=[
        "ID_RASTREADOR","DESCRICAO","MARCA","LOTE","FABRICACAO","VALIDADE_DIAS","VENCIMENTO",
        "TIPO_EMBALAGEM","QTD_POR_EMBALAGEM","UN_MEDIDA","AREA_ORIGEM_PADRAO","AREA_DESTINO_PADRAO"
    ])
if "mov" not in st.session_state:
    st.session_state.mov = pd.DataFrame(columns=[
        "ID_RASTREADOR","DESCRICAO","MARCA","LOTE","FABRICACAO","VENCIMENTO",
        "TIPO_EMBALAGEM","QTD_POR_EMBALAGEM","UN_MEDIDA","QTD_EMBALAGENS","TOTAL_KG_MEDIDA",
        "AREA_ORIGEM","AREA_DESTINO","MOV_TIPO","DATA_MOV","STATUS"
    ])

cat = st.session_state.catalogo
mov = st.session_state.mov

def get_lote_fifo(id_r, area_origem):
    if mov.empty:
        lotes = cat[cat["ID_RASTREADOR"]==id_r].sort_values("FABRICACAO")
        return lotes.iloc[0] if not lotes.empty else None
    estoque = mov.groupby(["ID_RASTREADOR","LOTE","FABRICACAO","AREA_DESTINO"]).agg(SALDO=("QTD_EMBALAGENS","sum")).reset_index()
    estoque = estoque[(estoque["ID_RASTREADOR"]==id_r) & (estoque["AREA_DESTINO"]==area_origem) & (estoque["SALDO"]>0)].sort_values("FABRICACAO")
    if not estoque.empty:
        lote_antigo = estoque.iloc[0]["LOTE"]
        cand = cat[(cat["ID_RASTREADOR"]==id_r) & (cat["LOTE"]==lote_antigo)]
        if not cand.empty:
            return cand.iloc[0]
    lotes = cat[cat["ID_RASTREADOR"]==id_r].sort_values("FABRICACAO")
    return lotes.iloc[0] if not lotes.empty else None

tab_cad, tab_transf, tab_est, tab_graf, tab_edit = st.tabs([
    "🆕 CADASTRO", "🔄 TRANSFER AUTO", "📋 ESTOQUE", "📊 GRÁFICOS LOTES", "✏️ EDITAR"
])

with tab_cad:
    st.header("🆕 CADASTRO - Com MARCA e DESTINO PADRÃO (Sinaliza 1 vez)")
    with st.form("cad", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            id_r = st.text_input("🔖 ID RASTREADOR *").upper()
            desc = st.text_input("📝 DESCRIÇÃO *")
            marca = st.text_input("🏷️ MARCA *", placeholder="Votoran, Refratil")
        with c2:
            lote = st.text_input("🔢 LOTE *")
            fab = st.date_input("🏭 FABRICAÇÃO", value=date.today())
            val_d = st.number_input("VALIDADE DIAS", 1, value=90)
        with c3:
            tipo = st.selectbox("📦 EMBALAGEM", ["Palete","Saco","Caixa","Fardo","Rolo","Galão","Balde","Outro"])
            qtd_por = st.number_input("QTD POR EMB", 0.01, value=25.0)
            un = st.selectbox("UN", ["KG","UND","M²","M³","LITROS","TON","PÇ"])
            origem_padrao = st.selectbox("📍 ORIGEM PADRÃO", AREAS_REAIS, index=0)
            destino_padrao = st.selectbox("➡️ DESTINO PADRÃO", AREAS_REAIS, index=2)
        if st.form_submit_button("💾 CADASTRAR", type="primary", use_container_width=True):
            if id_r and desc and lote and marca:
                venc = fab + timedelta(days=int(val_d))
                novo = {"ID_RASTREADOR":id_r,"DESCRICAO":desc,"MARCA":marca,"LOTE":lote,"FABRICACAO":fab,"VALIDADE_DIAS":val_d,"VENCIMENTO":venc,"TIPO_EMBALAGEM":tipo,"QTD_POR_EMBALAGEM":qtd_por,"UN_MEDIDA":un,"AREA_ORIGEM_PADRAO":origem_padrao,"AREA_DESTINO_PADRAO":destino_padrao}
                st.session_state.catalogo = pd.concat([cat, pd.DataFrame([novo])], ignore_index=True)
                st.success(f"{id_r} | MARCA {marca} | LOTE {lote} -> {origem_padrao} -> {destino_padrao}"); st.rerun()
            else: st.error("Preencha ID, Descrição, Marca e Lote!")
    if not cat.empty:
        st.dataframe(cat, use_container_width=True)

with tab_transf:
    st.header("🔄 TRANSFERÊNCIA AUTOMÁTICA - SAÍDA GERA ENTRADA")
    if cat.empty:
        st.warning("Cadastre primeiro")
    else:
        st.subheader("⬇️ 1. ENTRADA INICIAL")
        with st.container(border=True):
            c1,c2 = st.columns(2)
            with c1:
                id_e = st.selectbox("ID Produto", sorted(cat["ID_RASTREADOR"].unique()), key="id_e")
                p_e = cat[cat["ID_RASTREADOR"]==id_e].sort_values("FABRICACAO").iloc[0] if not cat[cat["ID_RASTREADOR"]==id_e].empty else None
                if p_e is not None:
                    st.info(f"**{p_e['DESCRICAO']} | MARCA {p_e['MARCA']} | LOTE {p_e['LOTE']} | FAB {p_e['FABRICACAO']}**")
            with c2:
                area_e = st.selectbox("Área Entrada", AREAS_REAIS, key="area_e")
                q_e = st.number_input("Qtd Paletes", 1, value=1, key="q_e")
                if st.button("💾 ENTRADA", key="btn_eg", type="primary", use_container_width=True) and p_e is not None:
                    total = float(p_e["QTD_POR_EMBALAGEM"])*q_e
                    nova = {"ID_RASTREADOR":id_e,"DESCRICAO":p_e["DESCRICAO"],"MARCA":p_e["MARCA"],"LOTE":p_e["LOTE"],"FABRICACAO":p_e["FABRICACAO"],"VENCIMENTO":p_e["VENCIMENTO"],"TIPO_EMBALAGEM":p_e["TIPO_EMBALAGEM"],"QTD_POR_EMBALAGEM":p_e["QTD_POR_EMBALAGEM"],"UN_MEDIDA":p_e["UN_MEDIDA"],"QTD_EMBALAGENS":q_e,"TOTAL_KG_MEDIDA":total,"AREA_ORIGEM":"FORNECEDOR","AREA_DESTINO":area_e,"MOV_TIPO":"ENTRADA","DATA_MOV":date.today(),"STATUS":"✅ OK"}
                    st.session_state.mov = pd.concat([mov, pd.DataFrame([nova])], ignore_index=True)
                    st.success("Entrada OK"); st.rerun()

        st.divider()
        st.subheader("🔄 2. TRANSFERÊNCIA - Mostra LOTE por FABRICAÇÃO (FIFO)")
        with st.container(border=True):
            c1,c2,c3 = st.columns(3)
            with c1:
                id_t = st.selectbox("ID Produto", sorted(cat["ID_RASTREADOR"].unique()), key="id_t")
                origem = st.selectbox("📍 SAÍDA DE:", AREAS_REAIS, key="orig")
                destino = st.selectbox("➡️ ENTRADA EM:", AREAS_REAIS, key="dest", index=2)
            with c2:
                if not mov.empty:
                    saldo_lotes = mov[mov["ID_RASTREADOR"]==id_t].groupby(["LOTE","FABRICACAO","AREA_DESTINO","MARCA"]).agg(SALDO=("QTD_EMBALAGENS","sum")).reset_index()
                    saldo_lotes = saldo_lotes[(saldo_lotes["SALDO"]>0) & (saldo_lotes["AREA_DESTINO"]==origem)].sort_values("FABRICACAO")
                    if not saldo_lotes.empty:
                        st.write("**LOTES DISPONÍVEIS NESTA ÁREA (FIFO):**")
                        st.dataframe(saldo_lotes, use_container_width=True)
                    else:
                        st.warning(f"Sem estoque de {id_t} em {origem}")
            with c3:
                q_t = st.number_input("Qtd Transferir", 1, value=1, key="q_t")
                p_t = get_lote_fifo(id_t, origem)
                if p_t is not None:
                    st.success(f"**LOTE QUE VAI SAIR (MAIS ANTIGO):**\n\nLOTE: {p_t['LOTE']}\nFAB: {p_t['FABRICACAO']}\nMARCA: {p_t['MARCA']}\nVENC: {p_t['VENCIMENTO']}")

            if st.button("🔄 TRANSFERIR - SAÍDA + ENTRADA AUTO", type="primary", use_container_width=True):
                if origem==destino:
                    st.error("Origem e Destino iguais!")
                elif p_t is None:
                    st.error("Sem lote")
                else:
                    total = float(p_t["QTD_POR_EMBALAGEM"])*q_t
                    saida = {"ID_RASTREADOR":id_t,"DESCRICAO":p_t["DESCRICAO"],"MARCA":p_t["MARCA"],"LOTE":p_t["LOTE"],"FABRICACAO":p_t["FABRICACAO"],"VENCIMENTO":p_t["VENCIMENTO"],"TIPO_EMBALAGEM":p_t["TIPO_EMBALAGEM"],"QTD_POR_EMBALAGEM":p_t["QTD_POR_EMBALAGEM"],"UN_MEDIDA":p_t["UN_MEDIDA"],"QTD_EMBALAGENS":-q_t,"TOTAL_KG_MEDIDA":-total,"AREA_ORIGEM":origem,"AREA_DESTINO":destino,"MOV_TIPO":f"SAÍDA {origem} -> {destino}","DATA_MOV":date.today(),"STATUS":f"Transferido LOTE {p_t['LOTE']}"}
                    entrada = {"ID_RASTREADOR":id_t,"DESCRICAO":p_t["DESCRICAO"],"MARCA":p_t["MARCA"],"LOTE":p_t["LOTE"],"FABRICACAO":p_t["FABRICACAO"],"VENCIMENTO":p_t["VENCIMENTO"],"TIPO_EMBALAGEM":p_t["TIPO_EMBALAGEM"],"QTD_POR_EMBALAGEM":p_t["QTD_POR_EMBALAGEM"],"UN_MEDIDA":p_t["UN_MEDIDA"],"QTD_EMBALAGENS":q_t,"TOTAL_KG_MEDIDA":total,"AREA_ORIGEM":origem,"AREA_DESTINO":destino,"MOV_TIPO":f"ENTRADA em {destino}","DATA_MOV":date.today(),"STATUS":f"Recebido de {origem} LOTE {p_t['LOTE']}"}
                    st.session_state.mov = pd.concat([st.session_state.mov, pd.DataFrame([saida, entrada])], ignore_index=True)
                    st.success(f"✅ {q_t} x {id_t} LOTE {p_t['LOTE']} FAB {p_t['FABRICACAO']} | {origem} -> {destino} | ENTRADA AUTO OK!"); st.rerun()

with tab_est:
    if mov.empty:
        st.info("Sem movimentações")
    else:
        saldo = mov.groupby(["ID_RASTREADOR","DESCRICAO","MARCA","LOTE","FABRICACAO","AREA_DESTINO"]).agg(QTD_PALETES=("QTD_EMBALAGENS","sum"), SOMA_KG=("TOTAL_KG_MEDIDA","sum")).reset_index()
        saldo = saldo[saldo["QTD_PALETES"]>0].sort_values(["AREA_DESTINO","FABRICACAO"])
        st.subheader("📋 ESTOQUE ATUAL POR ÁREA + LOTE (FIFO)")
        st.dataframe(saldo, use_container_width=True)
        c1,c2,c3 = st.columns(3)
        c1.metric("TOTAL PALETES", f"{saldo['QTD_PALETES'].sum():.0f}")
        c2.metric("TOTAL KG", f"{saldo['SOMA_KG'].sum():.2f}")
        c3.metric("LOTES DIFERENTES", f"{saldo['LOTE'].nunique()}")
        st.divider()
        st.dataframe(mov.sort_values("DATA_MOV", ascending=False), use_container_width=True, height=400)

with tab_graf:
    if mov.empty:
        st.info("Sem dados")
    else:
        saldo_lote = mov.groupby(["ID_RASTREADOR","LOTE","MARCA","FABRICACAO","AREA_DESTINO"]).agg(QTD_PALETES=("QTD_EMBALAGENS","sum"), SOMA_KG=("TOTAL_KG_MEDIDA","sum")).reset_index()
        saldo_lote = saldo_lote[saldo_lote["QTD_PALETES"]>0].sort_values("FABRICACAO")
        saldo_lote["LABEL"] = saldo_lote["ID_RASTREADOR"] + " | LOTE: " + saldo_lote["LOTE"] + " | FAB: " + saldo_lote["FABRICACAO"].astype(str) + " | " + saldo_lote["AREA_DESTINO"]

        fig1 = px.bar(saldo_lote, x="QTD_PALETES", y="LABEL", orientation='h', color="LOTE", text="QTD_PALETES", title="📦 QTD ATUAL POR ID + LOTE (Cada LOTE uma cor) - FIFO", color_discrete_sequence=px.colors.qualitative.Bold, hover_data=["MARCA","FABRICACAO","SOMA_KG","AREA_DESTINO"])
        fig1.update_layout(height=900, showlegend=True)
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)

        st.divider()
        ultimas_saidas = mov[mov["QTD_EMBALAGENS"]<0].copy()
        if not ultimas_saidas.empty:
            ultimas_saidas["QTD_ABS"] = ultimas_saidas["QTD_EMBALAGENS"].abs()
            ultimas_saidas["LABEL_SAIDA"] = ultimas_saidas["ID_RASTREADOR"] + " | LOTE: " + ultimas_saidas["LOTE"] + " | FAB: " + ultimas_saidas["FABRICACAO"].astype(str) + " | " + ultimas_saidas["AREA_ORIGEM"] + " -> " + ultimas_saidas["AREA_DESTINO"]
            fig2 = px.bar(ultimas_saidas.sort_values("DATA_MOV", ascending=False).head(25), x="QTD_ABS", y="LABEL_SAIDA", orientation='h', color="ID_RASTREADOR", text="QTD_ABS", title="🔴 O QUE ESTÁ SAINDO AGORA - Últimas 25 Transferências", color_discrete_sequence=px.colors.qualitative.Vivid, hover_data=["MARCA","LOTE","FABRICACAO","DATA_MOV"])
            fig2.update_layout(height=800, showlegend=False)
            fig2.update_traces(textposition='outside')
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        fig3 = px.bar(saldo_lote, x="SOMA_KG", y="LABEL", orientation='h', color="MARCA", text="SOMA_KG", title="⚖️ SOMA KG POR LOTE E MARCA", color_discrete_sequence=px.colors.qualitative.Pastel)
        fig3.update_layout(height=900)
        st.plotly_chart(fig3, use_container_width=True)

        fig4 = px.bar(mov.groupby("AREA_DESTINO").agg(SOMA=("TOTAL_KG_MEDIDA","sum")).reset_index(), x="SOMA", y="AREA_DESTINO", orientation='h', color="AREA_DESTINO", text="SOMA", title="📍 SOMA POR ÁREA - Galpão x Sala Anexa x Oficina")
        st.plotly_chart(fig4, use_container_width=True)

with tab_edit:
    st.subheader("✏️ EDITAR CADASTRO")
    if not cat.empty:
        ce = st.data_editor(cat, num_rows="dynamic", use_container_width=True, key="ce")
        if st.button("💾 SALVAR CADASTRO"): st.session_state.catalogo=ce; st.success("Salvo!"); st.rerun()
    st.divider()
    if not mov.empty:
        me = st.data_editor(mov, num_rows="dynamic", use_container_width=True, key="me")
        if st.button("💾 SALVAR MOV"): st.session_state.mov=me; st.success("Salvo!"); st.rerun()
    if st.button("🔥 LIMPAR TUDO"):
        st.session_state.catalogo=pd.DataFrame(columns=cat.columns)
        st.session_state.mov=pd.DataFrame(columns=mov.columns)
        st.rerun()
