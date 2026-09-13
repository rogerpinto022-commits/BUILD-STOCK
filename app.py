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
CAT_FILE = "catalogo_padrao.csv"
MOV_FILE = "movimentacoes_estoque.csv"

# CATÁLOGO PADRÃO (APENAS PARA AUTO-PREENCHIMENTO DOS DADOS FIXOS)
def criar_catalogo_padrao():
    dados_padrao = [
        {"ID_RASTREADOR": "ID-1", "DESCRICAO": "CIMENTO LAFARGE FONDU", "MARCA": "LAFARGE", "EMB_EXTERNA": "Palete", "EMB_INTERNA": "Saco", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 1400.0, "UN_MEDIDA": "KG"},
        {"ID_RASTREADOR": "ID-2", "DESCRICAO": "CARBETO DE SILICIO", "MARCA": "PADRÃO", "EMB_EXTERNA": "Palete", "EMB_INTERNA": "Saco", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 1000.0, "UN_MEDIDA": "KG"},
        {"ID_RASTREADOR": "ID-3", "DESCRICAO": "ARGAMASSA REFRATÁRIA TECNOFIRE 50S", "MARCA": "TECNOFIRE", "EMB_EXTERNA": "Palete", "EMB_INTERNA": "Saco", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 1200.0, "UN_MEDIDA": "KG"},
        {"ID_RASTREADOR": "ID-4", "DESCRICAO": "CASTIBAR PSI UG", "MARCA": "CASTIBAR", "EMB_EXTERNA": "Palete", "EMB_INTERNA": "Saco", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 1250.0, "UN_MEDIDA": "KG"},
        {"ID_RASTREADOR": "ID-5", "DESCRICAO": "LÃ DE ROCHA IBAR", "MARCA": "IBAR", "EMB_EXTERNA": "Caixa", "EMB_INTERNA": "PACOTE", "QTD_INTERNA_POR_EXTERNA": 6.0, "MEDIDA_POR_INTERNA": 1.0, "UN_MEDIDA": "UN"},
        {"ID_RASTREADOR": "ID-6", "DESCRICAO": "TIJOLO SEMI ISOLANTE SUPRA", "MARCA": "SKAMOL", "EMB_EXTERNA": "Palete", "EMB_INTERNA": "UN", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 1020.0, "UN_MEDIDA": "UN"},
        {"ID_RASTREADOR": "ID-7", "DESCRICAO": "TIJOLO ISOLANTE SKAMOL", "MARCA": "SKAMOL", "EMB_EXTERNA": "Palete", "EMB_INTERNA": "UN", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 680.0, "UN_MEDIDA": "UN"},
        {"ID_RASTREADOR": "ID-8", "DESCRICAO": "TIJOLOS REFRATÁRIOS VESUVIUS", "MARCA": "VESUVIUS", "EMB_EXTERNA": "Palete", "EMB_INTERNA": "UN", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 336.0, "UN_MEDIDA": "UN"},
        {"ID_RASTREADOR": "ID-11", "DESCRICAO": "CHAMOTE IBAR / TECFIRE", "MARCA": "IBAR", "EMB_EXTERNA": "Granel", "EMB_INTERNA": "KG", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 18000.0, "UN_MEDIDA": "KG"},
        {"ID_RASTREADOR": "ID-12", "DESCRICAO": "PASTA FRIA / CARBON", "MARCA": "ELKEN", "EMB_EXTERNA": "Tambor", "EMB_INTERNA": "KG", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 1000.0, "UN_MEDIDA": "KG"},
        {"ID_RASTREADOR": "ID-14", "DESCRICAO": "BLOCOS LATERAL CARBON", "MARCA": "CARBON", "EMB_EXTERNA": "CX", "EMB_INTERNA": "CX", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 1.0, "UN_MEDIDA": "UN"},
        {"ID_RASTREADOR": "ID-15", "DESCRICAO": "BLOCOS ENGUSADOS / FUNDO", "MARCA": "PADRÃO", "EMB_EXTERNA": "UN", "EMB_INTERNA": "UN", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 1.0, "UN_MEDIDA": "UN"},
        {"ID_RASTREADOR": "ID-16", "DESCRICAO": "BARRAS CATÓDICAS", "MARCA": "PADRÃO", "EMB_EXTERNA": "UN", "EMB_INTERNA": "UN", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 1.0, "UN_MEDIDA": "UN"},
        {"ID_RASTREADOR": "ID-17", "DESCRICAO": "BLOCOS DE FUNDO SEC", "MARCA": "PADRÃO", "EMB_EXTERNA": "UN", "EMB_INTERNA": "UN", "QTD_INTERNA_POR_EXTERNA": 1.0, "MEDIDA_POR_INTERNA": 1.0, "UN_MEDIDA": "UN"},
    ]
    return pd.DataFrame(dados_padrao)

def carregar():
    cat = pd.read_csv(CAT_FILE) if os.path.exists(CAT_FILE) else criar_catalogo_padrao()
    mov = pd.read_csv(MOV_FILE) if os.path.exists(MOV_FILE) else pd.DataFrame(columns=[
        "ID_RASTREADOR","DESCRICAO","MARCA","LOTE","FABRICACAO","VENCIMENTO",
        "EMB_EXTERNA","EMB_INTERNA","QTD_INTERNA_POR_EXTERNA","MEDIDA_POR_INTERNA","UN_MEDIDA",
        "QTD_EXTERNA","QTD_INTERNA_TOTAL","MEDIDA_TOTAL","AREA_ORIGEM","AREA_DESTINO","MOV_TIPO",
        "DATA_MOV","HORA_MOV","DATA_HORA_BR","STATUS"
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

tab_cad, tab_mov, tab_est, tab_graf = st.tabs(["🆕 NOVO MATERIAL", "🔄 ENTRADAS E MOVIMENTAÇÕES", "📋 SALDO DE ESTOQUE", "📊 GRÁFICOS"])

with tab_cad:
    st.subheader("Cadastrar / Editar Base Padrão de Materiais")
    with st.form("cad_padrao", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            id_r = st.text_input("🔖 ID * (Ex: ID-18)").upper()
            desc = st.text_input("DESCRIÇÃO *")
            marca = st.text_input("MARCA *")
        with c2:
            emb_ext = st.selectbox("EMB EXTERNA", ["Palete","Caixa","Fardo","Container","Tambor","UN","CX","Granel"])
            emb_int = st.selectbox("EMB INTERNA", ["Saco","Rolo","M²","M","UND","PÇ","PACOTE","KG","UN"])
            un = st.selectbox("UN FINAL", ["KG","M","M²","M³","LITROS","UND","TON","UN"])
        with c3:
            qtd_int = st.number_input(f"QTD {emb_int} POR {emb_ext}", 1.0, value=1.0)
            med_int = st.number_input(f"MEDIDA POR {emb_int}", 0.01, value=1.0)
            
        if st.form_submit_button("💾 ADICIONAR À BASE", type="primary", use_container_width=True):
            if id_r and desc and marca:
                novo = {
                    "ID_RASTREADOR": id_r, "DESCRICAO": desc, "MARCA": marca,
                    "EMB_EXTERNA": emb_ext, "EMB_INTERNA": emb_int,
                    "QTD_INTERNA_POR_EXTERNA": qtd_int, "MEDIDA_POR_INTERNA": med_int, "UN_MEDIDA": un
                }
                st.session_state.catalogo = pd.concat([cat, pd.DataFrame([novo])], ignore_index=True)
                salvar(); st.success("Adicionado com sucesso!"); st.rerun()
    
    st.divider()
    st.write("### Base de Materiais (Auto-Preenchimento)")
    st.dataframe(cat, use_container_width=True)

with tab_mov:
    if cat.empty: 
        st.warning("Cadastre ou carregue a base de materiais primeiro.")
    else:
        st.subheader("📥 Registrar Entrada de Lotes (Com personalização completa de Lote, Data e Qtd)")
        
        # Seleção do ID (Puxa os dados base automaticamente para agilizar)
        id_e = st.selectbox("ID DO MATERIAL (Auto-preenchimento de Descrição/Marca)", sorted(cat["ID_RASTREADOR"].unique()))
        dados_mat = cat[cat["ID_RASTREADOR"] == id_e].iloc[0]

        with st.form("form_entrada", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.info(f"**Descrição:** {dados_mat['DESCRICAO']}\n\n**Marca:** {dados_mat['MARCA']}")
                # Campos totalmente editáveis pelo usuário
                lote_digitado = st.text_input("📦 NÚMERO DO LOTE *", value="LOTE-01")
            with c2:
                fab_digitada = st.date_input("📅 DATA DE FABRICAÇÃO", value=date.today())
                val_d = st.number_input("VALIDADE (DIAS)", 1, value=365)
                area_e = st.selectbox("ÁREA DE DESTINO", AREAS_REAIS)
            with c3:
                q_ext_digitada = st.number_input("QTD EXTERNA (ALTERÁVEL)", 0.01, value=1.0)
                q_int_tot = q_ext_digitada * float(dados_mat["QTD_INTERNA_POR_EXTERNA"])
                med_tot = q_int_tot * float(dados_mat["MEDIDA_POR_INTERNA"])
                st.success((
                    f"**Cálculo Automático:**\n"
                    f"{q_ext_digitada} {dados_mat['EMB_EXTERNA']} = "
                    f"{med_tot:,.2f} {dados_mat['UN_MEDIDA']}"
                ))

            if st.form_submit_button("💾 REGISTRAR ENTRADA COM ESTES DADOS", type="primary", use_container_width=True):
                if lote_digitado:
                    dt = agora_br()
                    venc = fab_digitada + timedelta(days=int(val_d))
                    entrada = {
                        "ID_RASTREADOR": id_e, "DESCRICAO": dados_mat["DESCRICAO"], "MARCA": dados_mat["MARCA"],
                        "LOTE": lote_digitado, "FABRICACAO": fab_digitada, "VENCIMENTO": venc,
                        "EMB_EXTERNA": dados_mat["EMB_EXTERNA"], "EMB_INTERNA": dados_mat["EMB_INTERNA"],
                        "QTD_INTERNA_POR_EXTERNA": dados_mat["QTD_INTERNA_POR_EXTERNA"], 
                        "MEDIDA_POR_INTERNA": dados_mat["MEDIDA_POR_INTERNA"], "UN_MEDIDA": dados_mat["UN_MEDIDA"],
                        "QTD_EXTERNA": q_ext_digitada, "QTD_INTERNA_TOTAL": q_int_tot, "MEDIDA_TOTAL": med_tot,
                        "AREA_ORIGEM": "FORNECEDOR", "AREA_DESTINO": area_e, "MOV_TIPO": "ENTRADA",
                        "DATA_MOV": dt.date(), "HORA_MOV": dt.strftime("%H:%M:%S"),
                        "DATA_HORA_BR": dt.strftime("%d/%m/%Y %H:%M:%S"), "STATUS": "OK"
                    }
                    st.session_state.mov = pd.concat([mov, pd.DataFrame([entrada])], ignore_index=True)
                    salvar(); st.success("Entrada registrada com sucesso!"); st.rerun()

        st.divider()
        st.subheader("🔄 Saída / Transferência de Estoque")
        c1, c2 = st.columns(2)
        with c1:
            id_t = st.selectbox("ID para Movimentação", sorted(cat["ID_RASTREADOR"].unique()), key="id_t")
            origem = st.selectbox("SAÍDA DE:", AREAS_REAIS, index=0, key="orig")
            destino = st.selectbox("ENTRADA EM:", AREAS_REAIS, index=2, key="dest")
            lote_transf = st.text_input("LOTE REFERÊNCIA DA SAÍDA", value="LOTE-01", key="l_t")
            q_t = st.number_input("QTD EXTERNA A MOVIMENTAR", 0.01, value=1.0, key="q_t")
            
            if st.button("🔄 EXECUTAR MOVIMENTAÇÃO", type="primary", use_container_width=True):
                dados_t = cat[cat["ID_RASTREADOR"] == id_t].iloc[0]
                dt = agora_br()
                q_int = q_t * float(dados_t["QTD_INTERNA_POR_EXTERNA"])
                m_tot = q_int * float(dados_t["MEDIDA_POR_INTERNA"])
                
                saida = {
                    "ID_RASTREADOR": id_t, "DESCRICAO": dados_t["DESCRICAO"], "MARCA": dados_t["MARCA"], "LOTE": lote_transf,
                    "FABRICACAO": date.today(), "VENCIMENTO": date.today(), "EMB_EXTERNA": dados_t["EMB_EXTERNA"], "EMB_INTERNA": dados_t["EMB_INTERNA"],
                    "QTD_INTERNA_POR_EXTERNA": dados_t["QTD_INTERNA_POR_EXTERNA"], "MEDIDA_POR_INTERNA": dados_t["MEDIDA_POR_INTERNA"], "UN_MEDIDA": dados_t["UN_MEDIDA"],
                    "QTD_EXTERNA": -q_t, "QTD_INTERNA_TOTAL": -q_int, "MEDIDA_TOTAL": -m_tot,
                    "AREA_ORIGEM": origem, "AREA_DESTINO": destino, "MOV_TIPO": f"SAÍDA {origem}->{destino}",
                    "DATA_MOV": dt.date(), "HORA_MOV": dt.strftime("%H:%M:%S"), "DATA_HORA_BR": dt.strftime("%d/%m/%Y %H:%M:%S"), "STATUS": "OK"
                }
                entrada = saida.copy()
                entrada["QTD_EXTERNA"] = q_t
                entrada["QTD_INTERNA_TOTAL"] = q_int
                entrada["MEDIDA_TOTAL"] = m_tot
                entrada["MOV_TIPO"] = f"ENTRADA em {destino}"
                
                st.session_state.mov = pd.concat([st.session_state.mov, pd.DataFrame([saida, entrada])], ignore_index=True)
                salvar(); st.success("Movimentação realizada!"); st.rerun()

with tab_est:
    st.subheader("📋 Saldo Atual Consolidado por Área e Lote")
    if not mov.empty:
        saldo = mov.groupby(["ID_RASTREADOR", "DESCRICAO", "LOTE", "AREA_DESTINO", "UN_MEDIDA"]).agg(
            QTD_EXTERNA=("QTD_EXTERNA", "sum"),
            MEDIDA_TOTAL=("MEDIDA_TOTAL", "sum")
        ).reset_index()
        saldo = saldo[saldo["QTD_EXTER_NA"] > 0] if "QTD_EXTER_NA" in saldo.columns else saldo[saldo["QTD_EXTERNA"] > 0]
        st.dataframe(saldo, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📜 Histórico Completo de Movimentações")
        st.dataframe(mov.sort_values("DATA_HORA_BR", ascending=False), use_container_width=True)
    else:
        st.info("Nenhuma movimentação ou entrada registrada. O estoque está zerado.")

with tab_graf:
    if mov.empty:
        st.info("Nenhum dado de movimentação para gerar gráficos.")
    else:
        mov["TIPO_ENT_SAI"] = mov["QTD_EXTERNA"].apply(lambda x: "ENTRADA" if x>0 else "SAÍDA")
        mov["QTD_ABS"] = mov["QTD_EXTERNA"].abs()

        fig1 = px.bar(
            mov.groupby(["ID_RASTREADOR","TIPO_ENT_SAI"]).agg(QTD=("QTD_ABS","sum")).reset_index(), 
            x="ID_RASTREADOR", y="QTD", color="TIPO_ENT_SAI", barmode="group", 
            title="📊 ENTRADAS x SAÍDAS POR ID", color_discrete_map={"ENTRADA":"green","SAÍDA":"red"}
        )
        st.plotly_chart(fig1, use_container_width=True)
