import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import os
import pytz

# FUSO BRASÍLIA
BR_TZ = pytz.timezone("America/Sao_Paulo")
def agora_br():
    return datetime.now(BR_TZ)

st.set_page_config(page_title="BUILD STOCK BR", layout="wide", page_icon="📦")
st.title(f"📦 BUILD STOCK - BRASÍLIA | {agora_br().strftime('%d/%m/%Y %H:%M:%S')}")

AREAS_REAIS = ["GALPÃO DE MATERIAIS REFRATÁRIOS", "SALA ANEXA", "OFICINA DE REVESTIMENTO"]
CAT_FILE = "catalogo.csv"
MOV_FILE = "movimentacoes.csv"

def carregar():
    cat = pd.read_csv(CAT_FILE) if os.path.exists(CAT_FILE) else pd.DataFrame(columns=[
        "ID_RASTREADOR","DESCRICAO","MARCA","LOTE","FABRICACAO","VENCIMENTO",
        "EMB_EXTERNA","EMB_INTERNA","QTD_INTERNA_POR_EXTERNA","MEDIDA_POR_INTERNA","UN_MEDIDA","TOTAL_POR_EXTERNA"
    ])
    mov = pd.read_csv(MOV_FILE) if os.path.exists(MOV_FILE) else pd.DataFrame(columns=[
        "ID_RASTREADOR","DESCRICAO","MARCA","LOTE","FABRICACAO","VENCIMENTO",
        "EMB_EXTERNA","EMB_INTERNA","QTD_INTERNA_POR_EXTERNA","MEDIDA_POR_INTERNA","UN_MEDIDA","TOTAL_POR_EXTERNA",
        "QTD_EXTERNA","QTD_INTERNA_TOTAL","MEDIDA_TOTAL","AREA_ORIGEM","AREA_DESTINO","MOV_TIPO","DATA_MOV","HORA_MOV","DATA_HORA_BR","STATUS"
    ])
    return cat, mov

def salvar():
    st.session_state.catalogo.to_csv(CAT_FILE, index=False)
    st.session_state.mov.to_csv(MOV_FILE, index=False)

if "catalogo" not in st.session_state:
    c, m = carregar()
    st.session_state.catalogo = c
    st.session_state.mov = m

cat = st.session_state.catalogo
mov = st.session_state.mov

def get_p(id_b, lote=None):
    if cat.empty: return None
    r = cat[cat["ID_RASTREADOR"]==id_b]
    if lote: r = r[r["LOTE"]==lote]
    return r.sort_values("FABRICACAO").iloc[0] if not r.empty else None

def get_fifo(id_r, area):
    if cat.empty: return None
    if mov.empty:
        l = cat[cat["ID_RASTREADOR"]==id_r].sort_values("FABRICACAO")
        return l.iloc[0] if not l.empty else None
    est = mov.groupby(["ID_RASTREADOR","LOTE","FABRICACAO","AREA_DESTINO"]).agg(SALDO=("QTD_EXTERNA","sum")).reset_index()
    est = est[(est["ID_RASTREADOR"]==id_r) & (est["AREA_DESTINO"]==area) & (est["SALDO"]>0)].sort_values("FABRICACAO")
    if not est.empty:
        lote = est.iloc[0]["LOTE"]
        cand = cat[(cat["ID_RASTREADOR"]==id_r) & (cat["LOTE"]==lote)]
        if not cand.empty: return cand.iloc[0]
    l = cat[cat["ID_RASTREADOR"]==id_r].sort_values("FABRICACAO")
    return l.iloc[0] if not l.empty else None

tab_cad, tab_mov, tab_est, tab_graf = st.tabs(["🆕 CADASTRO", "🔄 MOVIMENTAÇÕES", "📋 ESTOQUE", "📊 GRÁFICOS ID x DATA/HORA BR"])

with tab_cad:
    with st.form("cad", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            id_r = st.text_input("🔖 ID *").upper()
            desc = st.text_input("DESCRIÇÃO *")
            marca = st.text_input("MARCA *")
            lote = st.text_input("LOTE *")
        with c2:
            fab = st.date_input("FABRICAÇÃO", value=date.today())
            val_d = st.number_input("VALIDADE DIAS", 1, value=90)
            emb_ext = st.selectbox("EMB EXTERNA", ["Palete","Caixa","Fardo","Container"])
            emb_int = st.selectbox("EMB INTERNA", ["Saco","Rolo","M²","M","UND","PÇ"])
        with c3:
            qtd_int = st.number_input(f"QTD {emb_int} POR {emb_ext}", 1.0, value=40.0)
            med_int = st.number_input(f"MEDIDA POR {emb_int}", 0.01, value=25.0)
            un = st.selectbox("UN FINAL", ["KG","M","M²","M³","LITROS","UND","TON"])
            total_ext = qtd_int * med_int
            st.metric(f"TOTAL POR {emb_ext}", f"{total_ext:.2f} {un}")
        if st.form_submit_button("💾 CADASTRAR", type="primary", use_container_width=True):
            if id_r and desc and marca and lote:
                venc = fab + timedelta(days=int(val_d))
                novo = {"ID_RASTREADOR":id_r,"DESCRICAO":desc,"MARCA":marca,"LOTE":lote,"FABRICACAO":fab,"VENCIMENTO":venc,"EMB_EXTERNA":emb_ext,"EMB_INTERNA":emb_int,"QTD_INTERNA_POR_EXTERNA":qtd_int,"MEDIDA_POR_INTERNA":med_int,"UN_MEDIDA":un,"TOTAL_POR_EXTERNA":total_ext}
                st.session_state.catalogo = pd.concat([cat, pd.DataFrame([novo])], ignore_index=True)
                salvar(); st.success("Salvo!"); st.rerun()
    if not cat.empty: st.dataframe(cat, use_container_width=True)

with tab_mov:
    if cat.empty: st.warning("Cadastre")
    else:
        c1,c2,c3 = st.columns(3)
        with c1:
            id_e = st.selectbox("ID", sorted(cat["ID_RASTREADOR"].unique()), key="id_e")
            lotes = cat[cat["ID_RASTREADOR"]==id_e].sort_values("FABRICACAO")
            lote_sel = st.selectbox("LOTE", lotes["LOTE"].tolist(), key="lote_e")
            p_e = get_p(id_e, lote_sel)
            area_e = st.selectbox("Área", AREAS_REAIS, key="area_e")
        with c2:
            q_ext = st.number_input("QTD EXTERNA", 1.0, value=1.0, key="q_e")
            if p_e is not None:
                q_int_tot = q_ext * float(p_e["QTD_INTERNA_POR_EXTERNA"])
                med_tot = q_int_tot * float(p_e["MEDIDA_POR_INTERNA"])
                st.write(f"{q_ext} {p_e['EMB_EXTERNA']} = {q_int_tot} {p_e['EMB_INTERNA']} = {med_tot} {p_e['UN_MEDIDA']}")
        with c3:
            if st.button("💾 ENTRADA", type="primary", use_container_width=True) and p_e is not None:
                dt = agora_br()
                nova = {"ID_RASTREADOR":id_e,"DESCRICAO":p_e["DESCRICAO"],"MARCA":p_e["MARCA"],"LOTE":p_e["LOTE"],"FABRICACAO":p_e["FABRICACAO"],"VENCIMENTO":p_e["VENCIMENTO"],"EMB_EXTERNA":p_e["EMB_EXTERNA"],"EMB_INTERNA":p_e["EMB_INTERNA"],"QTD_INTERNA_POR_EXTERNA":p_e["QTD_INTERNA_POR_EXTERNA"],"MEDIDA_POR_INTERNA":p_e["MEDIDA_POR_INTERNA"],"UN_MEDIDA":p_e["UN_MEDIDA"],"TOTAL_POR_EXTERNA":p_e["TOTAL_POR_EXTERNA"],"QTD_EXTERNA":q_ext,"QTD_INTERNA_TOTAL":q_int_tot,"MEDIDA_TOTAL":med_tot,"AREA_ORIGEM":"FORNECEDOR","AREA_DESTINO":area_e,"MOV_TIPO":"ENTRADA","DATA_MOV":dt.date(),"HORA_MOV":dt.strftime("%H:%M:%S"),"DATA_HORA_BR":dt.strftime("%d/%m/%Y %H:%M:%S"),"STATUS":"OK"}
                st.session_state.mov = pd.concat([mov, pd.DataFrame([nova])], ignore_index=True)
                salvar(); st.rerun()
        st.divider()
        c1,c2 = st.columns(2)
        with c1:
            id_t = st.selectbox("ID Transf", sorted(cat["ID_RASTREADOR"].unique()), key="id_t")
            origem = st.selectbox("SAÍDA DE:", AREAS_REAIS, index=0, key="orig")
            destino = st.selectbox("ENTRADA EM:", AREAS_REAIS, index=2, key="dest")
            q_t = st.number_input("QTD", 1.0, value=1.0, key="q_t")
            if st.button("🔄 TRANSFER AUTO FIFO", type="primary", use_container_width=True):
                p_t = get_fifo(id_t, origem)
                if origem!=destino and p_t is not None:
                    dt = agora_br()
                    q_int = q_t * float(p_t["QTD_INTERNA_POR_EXTERNA"])
                    m_tot = q_int * float(p_t["MEDIDA_POR_INTERNA"])
                    saida = {"ID_RASTREADOR":id_t,"DESCRICAO":p_t["DESCRICAO"],"MARCA":p_t["MARCA"],"LOTE":p_t["LOTE"],"FABRICACAO":p_t["FABRICACAO"],"VENCIMENTO":p_t["VENCIMENTO"],"EMB_EXTERNA":p_t["EMB_EXTERNA"],"EMB_INTERNA":p_t["EMB_INTERNA"],"QTD_INTERNA_POR_EXTERNA":p_t["QTD_INTERNA_POR_EXTERNA"],"MEDIDA_POR_INTERNA":p_t["MEDIDA_POR_INTERNA"],"UN_MEDIDA":p_t["UN_MEDIDA"],"TOTAL_POR_EXTERNA":p_t["TOTAL_POR_EXTERNA"],"QTD_EXTERNA":-q_t,"QTD_INTERNA_TOTAL":-q_int,"MEDIDA_TOTAL":-m_tot,"AREA_ORIGEM":origem,"AREA_DESTINO":destino,"MOV_TIPO":f"SAÍDA {origem}->{destino}","DATA_MOV":dt.date(),"HORA_MOV":dt.strftime("%H:%M:%S"),"DATA_HORA_BR":dt.strftime("%d/%m/%Y %H:%M:%S"),"STATUS":f"LOTE {p_t['LOTE']}"}
                    entrada = {"ID_RASTREADOR":id_t,"DESCRICAO":p_t["DESCRICAO"],"MARCA":p_t["MARCA"],"LOTE":p_t["LOTE"],"FABRICACAO":p_t["FABRICACAO"],"VENCIMENTO":p_t["VENCIMENTO"],"EMB_EXTERNA":p_t["EMB_EXTERNA"],"EMB_INTERNA":p_t["EMB_INTERNA"],"QTD_INTERNA_POR_EXTERNA":p_t["QTD_INTERNA_POR_EXTERNA"],"MEDIDA_POR_INTERNA":p_t["MEDIDA_POR_INTERNA"],"UN_MEDIDA":p_t["UN_MEDIDA"],"TOTAL_POR_EXTERNA":p_t["TOTAL_POR_EXTERNA"],"QTD_EXTERNA":q_t,"QTD_INTERNA_TOTAL":q_int,"MEDIDA_TOTAL":m_tot,"AREA_ORIGEM":origem,"AREA_DESTINO":destino,"MOV_TIPO":f"ENTRADA em {destino}","DATA_MOV":dt.date(),"HORA_MOV":dt.strftime("%H:%M:%S"),"DATA_HORA_BR":dt.strftime("%d/%m/%Y %H:%M:%S"),"STATUS":f"Recebido LOTE {p_t['LOTE']}"}
                    st.session_state.mov = pd.concat([st.session_state.mov, pd.DataFrame([saida, entrada])], ignore_index=True)
                    salvar(); st.rerun()
        with c2:
            if not mov.empty:
                st.write("Estoque por área (FIFO)")
                saldo = mov.groupby(["ID_RASTREADOR","LOTE","AREA_DESTINO"]).agg(SALDO=("QTD_EXTERNA","sum")).reset_index()
                saldo = saldo[saldo["SALDO"]>0].sort_values("LOTE")
                st.dataframe(saldo, use_container_width=True, height=300)

with tab_est:
    if not mov.empty:
        st.dataframe(mov.sort_values("DATA_HORA_BR", ascending=False), use_container_width=True, height=500)

with tab_graf:
    if mov.empty: st.info("Sem dados")
    else:
        mov["DATA_HORA_BR_DT"] = pd.to_datetime(mov["DATA_HORA_BR"], format="%d/%m/%Y %H:%M:%S", errors='coerce')
        mov["TIPO_ENT_SAI"] = mov["QTD_EXTERNA"].apply(lambda x: "ENTRADA" if x>0 else "SAÍDA")
        mov["QTD_ABS"] = mov["QTD_EXTERNA"].abs()

        # GRÁFICO 1 - POR ID RASTREADOR - ENTRADA x SAÍDA
        fig1 = px.bar(mov.groupby(["ID_RASTREADOR","TIPO_ENT_SAI"]).agg(QTD=("QTD_ABS","sum"), MEDIDA=("MEDIDA_TOTAL","sum")).reset_index().assign(MEDIDA=lambda d: d["MEDIDA"].abs()), x="ID_RASTREADOR", y="QTD", color="TIPO_ENT_SAI", barmode="group", text="QTD", title="📊 POR ID RASTREADOR: ENTRADA x SAÍDA (QTD Externa) - Horário Brasília", color_discrete_map={"ENTRADA":"green","SAÍDA":"red"})
        fig1.update_layout(height=500); st.plotly_chart(fig1, use_container_width=True)

        # GRÁFICO 2 - ENTRADA E SAÍDA COM DATA/HORA
        fig2 = px.bar(mov, x="DATA_HORA_BR", y="QTD_ABS", color="TIPO_ENT_SAI", facet_col="ID_RASTREADOR", facet_col_wrap=2, hover_data=["LOTE","MARCA","AREA_ORIGEM","AREA_DESTINO","MEDIDA_TOTAL"], title="📅 ENTRADA E SAÍDA POR ID COM DATA/HORA BRASÍLIA", color_discrete_map={"ENTRADA":"green","SAÍDA":"red"})
        fig2.update_layout(height=800); st.plotly_chart(fig2, use_container_width=True)

        # GRÁFICO 3 - LINHA DO TEMPO POR ID
        fig3 = px.line(mov.sort_values("DATA_HORA_BR_DT"), x="DATA_HORA_BR_DT", y="QTD_EXTERNA", color="ID_RASTREADOR", markers=True, title="📈 LINHA DO TEMPO: Movimentação por ID ao longo do tempo (Brasília)", hover_data=["LOTE","MOV_TIPO","AREA_DESTINO"])
        fig3.update_layout(height=600); st.plotly_chart(fig3, use_container_width=True)

        # GRÁFICO 4 - HORIZONTAL POR LOTE (O QUE PEDIU ANTES)
        sl = mov.groupby(["ID_RASTREADOR","LOTE","FABRICACAO","AREA_DESTINO"]).agg(EXTERNA=("QTD_EXTERNA","sum")).reset_index()
        sl = sl[sl["EXTERNA"]>0].sort_values("FABRICACAO")
        sl["LABEL"] = sl["ID_RASTREADOR"] + " | LOTE: " + sl["LOTE"] + " | " + sl["AREA_DESTINO"] + " | " + sl["FABRICACAO"].astype(str)
        fig4 = px.bar(sl, x="EXTERNA", y="LABEL", orientation='h', color="LOTE", text="EXTERNA", title="📦 ESTOQUE ATUAL POR ID + LOTE (FIFO) - Cada lote uma cor")
        fig4.update_layout(height=900); st.plotly_chart(fig4, use_container_width=True)

        # GRÁFICO 5 - O QUE ESTÁ SAINDO AGORA
        ult = mov[mov["QTD_EXTERNA"]<0].sort_values("DATA_HORA_BR_DT", ascending=False).head(20).copy()
        if not ult.empty:
            ult["LAB"] = ult["ID_RASTREADOR"] + " | LOTE: " + ult["LOTE"] + " | " + ult["DATA_HORA_BR"] + " | " + ult["AREA_ORIGEM"] + "->" + ult["AREA_DESTINO"]
            fig5 = px.bar(ult, x="QTD_ABS", y="LAB", orientation='h', color="ID_RASTREADOR", text="QTD_ABS", title="🔴 O QUE ESTÁ SAINDO AGORA - Com Data/Hora Brasília")
            fig5.update_layout(height=700); st.plotly_chart(fig5, use_container_width=True)
