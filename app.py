import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
import os

st.set_page_config(page_title="BUILD STOCK FINAL PERSISTENTE", layout="wide", page_icon="📦")
st.title("📦 BUILD STOCK - FINAL PERSISTENTE | AUTO PREENCHIMENTO")

AREAS_REAIS = ["GALPÃO DE MATERIAIS REFRATÁRIOS", "SALA ANEXA", "OFICINA DE REVESTIMENTO"]
CAT_FILE = "catalogo.csv"
MOV_FILE = "movimentacoes.csv"

def carregar():
    cat = pd.read_csv(CAT_FILE) if os.path.exists(CAT_FILE) else pd.DataFrame(columns=[
        "ID_RASTREADOR","DESCRICAO","MARCA","LOTE","FABRICACAO","VALIDADE_DIAS","VENCIMENTO",
        "TIPO_EMBALAGEM","QTD_POR_EMBALAGEM","UN_MEDIDA","AREA_ORIGEM_PADRAO","AREA_DESTINO_PADRAO"
    ])
    mov = pd.read_csv(MOV_FILE) if os.path.exists(MOV_FILE) else pd.DataFrame(columns=[
        "ID_RASTREADOR","DESCRICAO","MARCA","LOTE","FABRICACAO","VENCIMENTO",
        "TIPO_EMBALAGEM","QTD_POR_EMBALAGEM","UN_MEDIDA","QTD_EMBALAGENS","TOTAL_KG_MEDIDA",
        "AREA_ORIGEM","AREA_DESTINO","MOV_TIPO","DATA_MOV","STATUS"
    ])
    if not cat.empty:
        try:
            cat["FABRICACAO"] = pd.to_datetime(cat["FABRICACAO"]).dt.date
            cat["VENCIMENTO"] = pd.to_datetime(cat["VENCIMENTO"]).dt.date
        except: pass
    if not mov.empty:
        try:
            mov["FABRICACAO"] = pd.to_datetime(mov["FABRICACAO"]).dt.date
            mov["VENCIMENTO"] = pd.to_datetime(mov["VENCIMENTO"]).dt.date
            mov["DATA_MOV"] = pd.to_datetime(mov["DATA_MOV"]).dt.date
        except: pass
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

def get_p(id_b):
    if cat.empty: return None
    r = cat[cat["ID_RASTREADOR"]==id_b]
    return r.sort_values("FABRICACAO").iloc[0] if not r.empty else None

def get_lote_fifo(id_r, area_origem):
    if cat.empty: return None
    if mov.empty:
        lotes = cat[cat["ID_RASTREADOR"]==id_r].sort_values("FABRICACAO")
        return lotes.iloc[0] if not lotes.empty else None
    estoque = mov.groupby(["ID_RASTREADOR","LOTE","FABRICACAO","AREA_DESTINO"]).agg(SALDO=("QTD_EMBALAGENS","sum")).reset_index()
    estoque = estoque[(estoque["ID_RASTREADOR"]==id_r) & (estoque["AREA_DESTINO"]==area_origem) & (estoque["SALDO"]>0)].sort_values("FABRICACAO")
    if not estoque.empty:
        lote_antigo = estoque.iloc[0]["LOTE"]
        cand = cat[(cat["ID_RASTREADOR"]==id_r) & (cat["LOTE"]==lote_antigo)]
        if not cand.empty: return cand.iloc[0]
    lotes = cat[cat["ID_RASTREADOR"]==id_r].sort_values("FABRICACAO")
    return lotes.iloc[0] if not lotes.empty else None

tab_cad, tab_mov, tab_est, tab_graf, tab_edit = st.tabs([
    "🆕 CADASTRO (Auto Preenchimento)", "🔄 MOVIMENTAÇÕES", "📋 ESTOQUE", "📊 GRÁFICOS POR LOTE", "✏️ EDITAR / BACKUP"
])

with tab_cad:
    st.header("🆕 CADASTRO MESTRE - Só pra auto preencher na movimentação")
    st.info("Cadastre aqui 1 vez: ID, Descrição, Marca, Lote, Fabricação. Na movimentação é só digitar o ID que preenche tudo!")
    with st.form("cad", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        with c1:
            id_r = st.text_input("🔖 ID RASTREADOR *").upper()
            desc = st.text_input("📝 DESCRIÇÃO *")
            marca = st.text_input("🏷️ MARCA *", placeholder="Votoran, Refratil, Magnesita")
        with c2:
            lote = st.text_input("🔢 LOTE *")
            fab = st.date_input("🏭 FABRICAÇÃO", value=date.today())
            val_d = st.number_input("⏳ VALIDADE DIAS", 1, value=90)
        with c3:
            tipo = st.selectbox("📦 EMBALAGEM", ["Palete","Saco","Caixa","Fardo","Rolo","Galão","Balde","Outro"])
            qtd_por = st.number_input("QTD POR EMB", 0.01, value=25.0)
            un = st.selectbox("UN", ["KG","UND","M²","M³","LITROS","TON","PÇ"])
            origem_padrao = st.selectbox("📍 ORIGEM PADRÃO", AREAS_REAIS, index=0)
            destino_padrao = st.selectbox("➡️ DESTINO PADRÃO (Sinaliza 1x)", AREAS_REAIS, index=2)
        if st.form_submit_button("💾 CADASTRAR E SALVAR", type="primary", use_container_width=True):
            if id_r and desc and lote and marca:
                if not cat.empty and ((cat["ID_RASTREADOR"]==id_r) & (cat["LOTE"]==lote)).any():
                    st.error(f"ID {id_r} com LOTE {lote} já existe!")
                else:
                    venc = fab + timedelta(days=int(val_d))
                    novo = {"ID_RASTREADOR":id_r,"DESCRICAO":desc,"MARCA":marca,"LOTE":lote,"FABRICACAO":fab,"VALIDADE_DIAS":val_d,"VENCIMENTO":venc,"TIPO_EMBALAGEM":tipo,"QTD_POR_EMBALAGEM":qtd_por,"UN_MEDIDA":un,"AREA_ORIGEM_PADRAO":origem_padrao,"AREA_DESTINO_PADRAO":destino_padrao}
                    st.session_state.catalogo = pd.concat([cat, pd.DataFrame([novo])], ignore_index=True)
                    salvar()
                    st.success(f"✅ {id_r} | {marca} | LOTE {lote} SALVO! NUNCA MAIS APAGA!"); st.rerun()
            else: st.error("Preencha ID, Descrição, Marca e Lote!")
    st.divider()
    st.subheader(f"📚 {len(cat)} Materiais Cadastrados (Persistente)")
    if not cat.empty:
        st.dataframe(cat.sort_values(["ID_RASTREADOR","FABRICACAO"]), use_container_width=True)
    else:
        st.info("Nenhum cadastro ainda")

with tab_mov:
    st.header("🔄 MOVIMENTAÇÕES INDEPENDENTES - Auto Preenchimento por ID")
    if cat.empty:
        st.warning("⚠️ Cadastre primeiro na aba CADASTRO")
    else:
        # --- ENTRADA ---
        st.subheader("⬇️ ENTRADA")
        with st.container(border=True):
            col1,col2,col3 = st.columns(3)
            with col1:
                id_e = st.selectbox("🔖 ID RASTREADOR", sorted(cat["ID_RASTREADOR"].unique()), key="id_e")
                p_e = get_p(id_e)
                if p_e is not None:
                    st.success(f"**{p_e['DESCRICAO']}**\n\nMARCA: {p_e['MARCA']}\nLOTE: {p_e['LOTE']}\nFAB: {p_e['FABRICACAO']}")
                    # Se tiver vários lotes do mesmo ID, deixa escolher
                    lotes_do_id = cat[cat["ID_RASTREADOR"]==id_e][["LOTE","FABRICACAO","MARCA"]].sort_values("FABRICACAO")
                    lote_sel = st.selectbox("Escolha o LOTE", lotes_do_id["LOTE"].tolist(), key="lote_e")
                    p_e = cat[(cat["ID_RASTREADOR"]==id_e) & (cat["LOTE"]==lote_sel)].iloc[0]
            with col2:
                area_e = st.selectbox("📍 Área Destino", AREAS_REAIS, key="area_e")
                q_e = st.number_input("Qtd Paletes/Emb", 1, value=1, key="q_e")
            with col3:
                if p_e is not None:
                    st.metric("Total KG", f"{float(p_e['QTD_POR_EMBALAGEM'])*q_e:.2f} {p_e['UN_MEDIDA']}")
                    st.write(f"Venc: {p_e['VENCIMENTO']}")
                    if st.button("💾 CONFIRMAR ENTRADA", type="primary", use_container_width=True, key="btn_e"):
                        total = float(p_e["QTD_POR_EMBALAGEM"])*q_e
                        nova = {"ID_RASTREADOR":id_e,"DESCRICAO":p_e["DESCRICAO"],"MARCA":p_e["MARCA"],"LOTE":p_e["LOTE"],"FABRICACAO":p_e["FABRICACAO"],"VENCIMENTO":p_e["VENCIMENTO"],"TIPO_EMBALAGEM":p_e["TIPO_EMBALAGEM"],"QTD_POR_EMBALAGEM":p_e["QTD_POR_EMBALAGEM"],"UN_MEDIDA":p_e["UN_MEDIDA"],"QTD_EMBALAGENS":q_e,"TOTAL_KG_MEDIDA":total,"AREA_ORIGEM":"FORNECEDOR","AREA_DESTINO":area_e,"MOV_TIPO":"ENTRADA","DATA_MOV":date.today(),"STATUS":"✅ OK"}
                        st.session_state.mov = pd.concat([mov, pd.DataFrame([nova])], ignore_index=True)
                        salvar()
                        st.success(f"Entrada {q_e} no {area_e} LOTE {p_e['LOTE']}"); st.rerun()

        st.divider()
        # --- TRANSFERÊNCIA AUTOMÁTICA ---
        st.subheader("🔄 TRANSFERÊNCIA AUTOMÁTICA - SAÍDA GERA ENTRADA + FIFO LOTE ANTIGO")
        st.info("Ex: SAÍDA do GALPÃO -> Já registra ENTRADA na OFICINA com mesmo LOTE (PEPS)")
        with st.container(border=True):
            c1,c2,c3 = st.columns(3)
            with c1:
                id_t = st.selectbox("ID Produto", sorted(cat["ID_RASTREADOR"].unique()), key="id_t")
                origem = st.selectbox("📍 SAÍDA DE:", AREAS_REAIS, index=0, key="orig")
                destino = st.selectbox("➡️ ENTRADA EM:", AREAS_REAIS, index=2, key="dest")
            with c2:
                q_t = st.number_input("Qtd Transferir", 1, value=1, key="q_t")
                if not mov.empty:
                    saldo_lotes = mov[mov["ID_RASTREADOR"]==id_t].groupby(["LOTE","FABRICACAO","AREA_DESTINO","MARCA"]).agg(SALDO=("QTD_EMBALAGENS","sum")).reset_index()
                    saldo_lotes = saldo_lotes[(saldo_lotes["SALDO"]>0) & (saldo_lotes["AREA_DESTINO"]==origem)].sort_values("FABRICACAO")
                    if not saldo_lotes.empty:
                        st.write(f"**Estoque em {origem} (FIFO):**")
                        st.dataframe(saldo_lotes, use_container_width=True, height=200)
            with c3:
                p_t = get_lote_fifo(id_t, origem)
                if p_t is not None:
                    st.success(f"**LOTE FIFO QUE VAI SAIR:**\nLOTE: {p_t['LOTE']}\nFAB: {p_t['FABRICACAO']}\nMARCA: {p_t['MARCA']}\nVENC: {p_t['VENCIMENTO']}")
                else:
                    st.warning("Sem estoque nessa área ou sem cadastro")

            if st.button("🔄 TRANSFERIR AGORA - AUTO", type="primary", use_container_width=True, key="btn_transf"):
                if origem==destino: st.error("Origem e Destino iguais!")
                elif p_t is None: st.error("Sem lote para transferir")
                else:
                    total = float(p_t["QTD_POR_EMBALAGEM"])*q_t
                    saida = {"ID_RASTREADOR":id_t,"DESCRICAO":p_t["DESCRICAO"],"MARCA":p_t["MARCA"],"LOTE":p_t["LOTE"],"FABRICACAO":p_t["FABRICACAO"],"VENCIMENTO":p_t["VENCIMENTO"],"TIPO_EMBALAGEM":p_t["TIPO_EMBALAGEM"],"QTD_POR_EMBALAGEM":p_t["QTD_POR_EMBALAGEM"],"UN_MEDIDA":p_t["UN_MEDIDA"],"QTD_EMBALAGENS":-q_t,"TOTAL_KG_MEDIDA":-total,"AREA_ORIGEM":origem,"AREA_DESTINO":destino,"MOV_TIPO":f"SAÍDA {origem} -> {destino}","DATA_MOV":date.today(),"STATUS":f"Transferido LOTE {p_t['LOTE']}"}
                    entrada = {"ID_RASTREADOR":id_t,"DESCRICAO":p_t["DESCRICAO"],"MARCA":p_t["MARCA"],"LOTE":p_t["LOTE"],"FABRICACAO":p_t["FABRICACAO"],"VENCIMENTO":p_t["VENCIMENTO"],"TIPO_EMBALAGEM":p_t["TIPO_EMBALAGEM"],"QTD_POR_EMBALAGEM":p_t["QTD_POR_EMBALAGEM"],"UN_MEDIDA":p_t["UN_MEDIDA"],"QTD_EMBALAGENS":q_t,"TOTAL_KG_MEDIDA":total,"AREA_ORIGEM":origem,"AREA_DESTINO":destino,"MOV_TIPO":f"ENTRADA em {destino} vindo de {origem}","DATA_MOV":date.today(),"STATUS":f"Recebido de {origem} LOTE {p_t['LOTE']}"}
                    st.session_state.mov = pd.concat([st.session_state.mov, pd.DataFrame([saida, entrada])], ignore_index=True)
                    salvar()
                    st.success(f"✅ TRANSFERIDO! {q_t} LOTE {p_t['LOTE']} {origem} -> {destino}"); st.rerun()

        st.divider()
        # --- SAÍDA FINAL / DEVOLUÇÃO ---
        c1,c2 = st.columns(2)
        with c1:
            st.subheader("⬆️ SAÍDA FINAL (Uso/Consumo)")
            id_s = st.selectbox("ID", sorted(cat["ID_RASTREADOR"].unique()), key="id_s")
            area_s = st.selectbox("Área Saída", AREAS_REAIS, key="area_s")
            q_s = st.number_input("Qtd", 1, value=1, key="q_s")
            if st.button("💾 SAÍDA FINAL", key="btn_s"):
                p_s = get_lote_fifo(id_s, area_s)
                if p_s is not None:
                    total = float(p_s["QTD_POR_EMBALAGEM"])*q_s
                    nova = {"ID_RASTREADOR":id_s,"DESCRICAO":p_s["DESCRICAO"],"MARCA":p_s["MARCA"],"LOTE":p_s["LOTE"],"FABRICACAO":p_s["FABRICACAO"],"VENCIMENTO":p_s["VENCIMENTO"],"TIPO_EMBALAGEM":p_s["TIPO_EMBALAGEM"],"QTD_POR_EMBALAGEM":p_s["QTD_POR_EMBALAGEM"],"UN_MEDIDA":p_s["UN_MEDIDA"],"QTD_EMBALAGENS":-q_s,"TOTAL_KG_MEDIDA":-total,"AREA_ORIGEM":area_s,"AREA_DESTINO":"CONSUMO","MOV_TIPO":f"SAÍDA FINAL {area_s}","DATA_MOV":date.today(),"STATUS":f"Consumido LOTE {p_s['LOTE']}"}
                    st.session_state.mov = pd.concat([mov, pd.DataFrame([nova])], ignore_index=True)
                    salvar()
                    st.success("Saída final OK"); st.rerun()
        with c2:
            st.subheader("↩️ DEVOLUÇÃO")
            id_d = st.selectbox("ID Dev", sorted(cat["ID_RASTREADOR"].unique()), key="id_d")
            area_d = st.selectbox("Área Dev", AREAS_REAIS, key="area_d")
            q_d = st.number_input("Qtd Dev", 1, value=1, key="q_d")
            if st.button("💾 DEVOLUÇÃO", key="btn_d"):
                p_d = get_p(id_d)
                if p_d is not None:
                    total = float(p_d["QTD_POR_EMBALAGEM"])*q_d
                    nova = {"ID_RASTREADOR":id_d,"DESCRICAO":p_d["DESCRICAO"],"MARCA":p_d["MARCA"],"LOTE":p_d["LOTE"],"FABRICACAO":p_d["FABRICACAO"],"VENCIMENTO":p_d["VENCIMENTO"],"TIPO_EMBALAGEM":p_d["TIPO_EMBALAGEM"],"QTD_POR_EMBALAGEM":p_d["QTD_POR_EMBALAGEM"],"UN_MEDIDA":p_d["UN_MEDIDA"],"QTD_EMBALAGENS":q_d,"TOTAL_KG_MEDIDA":total,"AREA_ORIGEM":"DEVOLUÇÃO","AREA_DESTINO":area_d,"MOV_TIPO":f"DEVOLUÇÃO para {area_d}","DATA_MOV":date.today(),"STATUS":"Devolvido"}
                    st.session_state.mov = pd.concat([mov, pd.DataFrame([nova])], ignore_index=True)
                    salvar()
                    st.success("Devolução OK"); st.rerun()

with tab_est:
    if mov.empty:
        st.info("Sem movimentações ainda")
    else:
        saldo = mov.groupby(["ID_RASTREADOR","DESCRICAO","MARCA","LOTE","FABRICACAO","AREA_DESTINO"]).agg(QTD_PALETES=("QTD_EMBALAGENS","sum"), SOMA_KG=("TOTAL_KG_MEDIDA","sum")).reset_index()
        saldo = saldo[saldo["QTD_PALETES"]>0].sort_values(["AREA_DESTINO","FABRICACAO"])
        st.subheader("📋 ESTOQUE ATUAL POR ÁREA + LOTE (FIFO - Mais antigo primeiro)")
        st.dataframe(saldo, use_container_width=True)
        c1,c2,c3 = st.columns(3)
        c1.metric("PALETES", f"{saldo['QTD_PALETES'].sum():.0f}")
        c2.metric("KG TOTAL", f"{saldo['SOMA_KG'].sum():.2f}")
        c3.metric("LOTES", f"{saldo['LOTE'].nunique()}")
        st.divider()
        st.subheader("Histórico Completo (Persistente)")
        st.dataframe(mov.sort_values("DATA_MOV", ascending=False), use_container_width=True, height=400)

with tab_graf:
    if mov.empty:
        st.info("Sem dados para gráfico")
    else:
        saldo_lote = mov.groupby(["ID_RASTREADOR","LOTE","MARCA","FABRICACAO","AREA_DESTINO"]).agg(QTD_PALETES=("QTD_EMBALAGENS","sum"), SOMA_KG=("TOTAL_KG_MEDIDA","sum")).reset_index()
        saldo_lote = saldo_lote[saldo_lote["QTD_PALETES"]>0].sort_values("FABRICACAO")
        saldo_lote["LABEL"] = saldo_lote["ID_RASTREADOR"] + " | LOTE: " + saldo_lote["LOTE"] + " | FAB: " + saldo_lote["FABRICACAO"].astype(str) + " | " + saldo_lote["AREA_DESTINO"]

        fig1 = px.bar(saldo_lote, x="QTD_PALETES", y="LABEL", orientation='h', color="LOTE", text="QTD_PALETES", title="📦 QTD ATUAL POR ID + LOTE (Cada LOTE uma cor) - FIFO", color_discrete_sequence=px.colors.qualitative.Bold, hover_data=["MARCA","FABRICACAO","SOMA_KG","AREA_DESTINO"])
        fig1.update_layout(height=900)
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)

        st.divider()
        ultimas_saidas = mov[mov["QTD_EMBALAGENS"]<0].copy()
        if not ultimas_saidas.empty:
            ultimas_saidas["QTD_ABS"] = ultimas_saidas["QTD_EMBALAGENS"].abs()
            ultimas_saidas["LABEL_SAIDA"] = ultimas_saidas["ID_RASTREADOR"] + " | LOTE: " + ultimas_saidas["LOTE"] + " | FAB: " + ultimas_saidas["FABRICACAO"].astype(str) + " | " + ultimas_saidas["AREA_ORIGEM"] + " -> " + ultimas_saidas["AREA_DESTINO"]
            fig2 = px.bar(ultimas_saidas.sort_values("DATA_MOV", ascending=False).head(25), x="QTD_ABS", y="LABEL_SAIDA", orientation='h', color="ID_RASTREADOR", text="QTD_ABS", title="🔴 O QUE ESTÁ SAINDO AGORA - Últimas 25 Saídas/Transferências por LOTE", color_discrete_sequence=px.colors.qualitative.Vivid, hover_data=["MARCA","LOTE","FABRICACAO","DATA_MOV","MOV_TIPO"])
            fig2.update_layout(height=800, showlegend=False)
            fig2.update_traces(textposition='outside')
            st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.bar(saldo_lote, x="SOMA_KG", y="LABEL", orientation='h', color="MARCA", text="SOMA_KG", title="⚖️ SOMA KG POR LOTE E MARCA", color_discrete_sequence=px.colors.qualitative.Pastel)
        fig3.update_layout(height=900)
        st.plotly_chart(fig3, use_container_width=True)

with tab_edit:
    st.subheader("💾 BACKUP E RESTAURAÇÃO - Nunca perde")
    c1,c2 = st.columns(2)
    with c1:
        if not cat.empty:
            st.download_button("⬇️ BAIXAR CATALOGO CSV", cat.to_csv(index=False), "catalogo_backup.csv", "text/csv", use_container_width=True)
        if not mov.empty:
            st.download_button("⬇️ BAIXAR MOVIMENTAÇÕES CSV", mov.to_csv(index=False), "mov_backup.csv", "text/csv", use_container_width=True)
    with c2:
        up_cat = st.file_uploader("⬆️ RESTAURAR CATALOGO", type="csv", key="up_cat")
        if up_cat and st.button("RESTAURAR CATALOGO"):
            st.session_state.catalogo = pd.read_csv(up_cat)
            salvar()
            st.success("Catalogo restaurado!"); st.rerun()
        up_mov = st.file_uploader("⬆️ RESTAURAR MOVIMENTAÇÕES", type="csv", key="up_mov")
        if up_mov and st.button("RESTAURAR MOV"):
            st.session_state.mov = pd.read_csv(up_mov)
            salvar()
            st.success("Mov restaurado!"); st.rerun()

    st.divider()
    if not cat.empty:
        st.write("Editar Cadastro")
        ce = st.data_editor(cat, num_rows="dynamic", use_container_width=True, key="ce")
        if st.button("💾 SALVAR EDIÇÃO CADASTRO"):
            st.session_state.catalogo=ce
            salvar()
            st.success("Salvo!"); st.rerun()
    if st.button("🔥 LIMPAR TUDO (CUIDADO)"):
        if os.path.exists(CAT_FILE): os.remove(CAT_FILE)
        if os.path.exists(MOV_FILE): os.remove(MOV_FILE)
        st.session_state.catalogo=pd.DataFrame(columns=cat.columns if not cat.empty else ["ID_RASTREADOR"])
        st.session_state.mov=pd.DataFrame(columns=mov.columns if not mov.empty else ["ID_RASTREADOR"])
        st.rerun()
