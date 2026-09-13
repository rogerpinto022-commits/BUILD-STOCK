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
MOV_FILE = "movimentacoes.csv"

# BASE PADRÃO COM CONTROLE INDIVIDUAL DE HABILITAÇÃO POR ÁREA
def criar_catalogo_padrao():
    dados_padrao = [
        {"ID": "ID-1", "Material": "CIMENTO LAFARGE FONDU", "Marca": "LAFARGE", "Unidade": "KG", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-2", "Material": "CARBETO DE SILICIO", "Marca": "PADRÃO", "Unidade": "KG", "HAB_GALPAO": True, "HAB_SALA_ANEXA": False, "HAB_OFICINA": True},
        {"ID": "ID-3", "Material": "ARGAMASSA REFRATÁRIA TECNOFIRE 50S", "Marca": "TECNOFIRE", "Unidade": "KG", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-4", "Material": "CASTIBAR PSI UG", "Marca": "CASTIBAR", "Unidade": "KG", "HAB_GALPAO": True, "HAB_SALA_ANEXA": False, "HAB_OFICINA": True},
        {"ID": "ID-5", "Material": "LÃ DE ROCHA IBAR", "Marca": "IBAR", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": False},
        {"ID": "ID-6", "Material": "TIJOLO SEMI ISOLANTE SUPRA", "Marca": "SKAMOL", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-7", "Material": "TIJOLO ISOLANTE SKAMOL", "Marca": "SKAMOL", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": False},
        {"ID": "ID-8", "Material": "TIJOLOS REFRATÁRIOS VESUVIUS", "Marca": "VESUVIUS", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": False, "HAB_OFICINA": True},
        {"ID": "ID-11", "Material": "CHAMOTE IBAR / TECFIRE", "Marca": "IBAR", "Unidade": "KG", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-12", "Material": "PASTA FRIA / CARBON", "Marca": "ELKEN", "Unidade": "KG", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": False},
        {"ID": "ID-14", "Material": "BLOCOS LATERAL CARBON", "Marca": "CARBON", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": False, "HAB_OFICINA": True},
        {"ID": "ID-15", "Material": "BLOCOS ENGUSADOS / FUNDO", "Marca": "PADRÃO", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-16", "Material": "BARRAS CATÓDICAS", "Marca": "PADRÃO", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": False},
        {"ID": "ID-17", "Material": "BLOCOS DE FUNDO SEC", "Marca": "PADRÃO", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": False, "HAB_OFICINA": True},
    ]
    return pd.DataFrame(dados_padrao)

def carregar():
    cat = pd.read_csv(CAT_FILE) if os.path.exists(CAT_FILE) else criar_catalogo_padrao()
    for col in ["HAB_GALPAO", "HAB_SALA_ANEXA", "HAB_OFICINA"]:
        if col not in cat.columns:
            cat[col] = True
    mov = pd.read_csv(MOV_FILE) if os.path.exists(MOV_FILE) else pd.DataFrame(columns=[
        "ID","Material","Marca","Lote","Fabricacao","Vencimento",
        "Unidade","Qtd_Externa","Qtd_Interna_Total","Medida_Total",
        "Area_Origem","Area_Destino","Mov_Tipo","Data_Hora_BR","Status"
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

def get_p(id_b):
    if cat.empty: return None
    r = cat[cat["ID"]==id_b]
    return r.iloc[0] if not r.empty else None

def get_fifo(id_r, area):
    if cat.empty: return None
    if mov.empty: return get_p(id_r)
    est = mov.groupby(["ID","Lote","Fabricacao","Area_Destino"]).agg(Saldo=("Qtd_Externa","sum")).reset_index()
    est = est[(est["ID"]==id_r) & (est["Area_Destino"]==area) & (est["Saldo"]>0)].sort_values("Fabricacao")
    if not est.empty:
        lote = est.iloc[0]["Lote"]
        fab_lote = est.iloc[0]["Fabricacao"]
        return {"Lote": lote, "Fabricacao": fab_lote, **get_p(id_r).to_dict()}
    return get_p(id_r)

tab_cad, tab_mov, tab_est, tab_graf = st.tabs(["🆕 BASE / CATÁLOGO & HABILITAÇÃO", "🔄 MOVIMENTAÇÕES & ENTRADAS", "📋 ESTOQUE", "📊 GRÁFICOS"])

with tab_cad:
    st.subheader("📋 Catálogo Geral e Painel de Habilitação por Local")
    st.write("Marque ou desmarque nas colunas abaixo para **habilitar ou desabilitar** cada material para o respectivo local. O catálogo aparece integralmente para consulta.")
    
    # Tabela interativa para marcar/desmarcar
    edited_cat = st.data_editor(cat, num_rows="dynamic", use_container_width=True, key="editor_habilita")
    if st.button("💾 SALVAR CONFIGURAÇÃO DE HABILITAÇÃO", type="primary"):
        st.session_state.catalogo = edited_cat
        salvar()
        st.success("Configurações de habilitação salvas com sucesso!")
        st.rerun()

with tab_mov:
    if cat.empty: st.warning("Cadastre a base de materiais.")
    else:
        st.subheader("📥 1. Registro de Entrada (Galpão de Materiais Refratários - Estoque Geral)")
        id_e = st.selectbox("SELECIONE O ID DO MATERIAL", sorted(cat["ID"].unique()), key="id_e")
        p_e = get_p(id_e)
        
        with st.form("form_entrada", clear_on_submit=True):
            c1,c2,c3 = st.columns(3)
            with c1:
                st.info(f"**Material:** {p_e['Material']}\n\n**Marca:** {p_e['Marca']}")
                lote_sel = st.text_input("📦 LOTE *", value="LOTE-01")
            with c2:
                fab = st.date_input("📅 FABRICAÇÃO", value=date.today())
                val_d = st.number_input("VALIDADE (DIAS)", 1, value=365)
            with c3:
                q_ext = st.number_input("QUANTIDADE", 0.01, value=1.0, key="q_e")
                st.write(f"Unidade: **{p_e['Unidade']}**")
                st.write(Destino := "Destino fixo: **GALPÃO DE MATERIAIS REFRATÁRIOS**")

            if st.form_submit_button("💾 SALVAR ENTRADA NO GALPÃO", type="primary", use_container_width=True):
                if lote_sel:
                    dt = agora_br()
                    venc = fab + timedelta(days=int(val_d))
                    nova = {
                        "ID":id_e, "Material":p_e["Material"], "Marca":p_e["Marca"], "Lote":lote_sel,
                        "Fabricacao":fab, "Vencimento":venc, "Unidade":p_e["Unidade"], "Qtd_Externa":q_ext,
                        "Qtd_Interna_Total":q_ext, "Medida_Total":q_ext, "Area_Origem":"FORNECEDOR",
                        "Area_Destino":"GALPÃO DE MATERIAIS REFRATÁRIOS", "Mov_Tipo":"ENTRADA", 
                        "Data_Hora_BR":dt.strftime("%d/%m/%Y %H:%M:%S"), "Status":"OK"
                    }
                    st.session_state.mov = pd.concat([mov, pd.DataFrame([nova])], ignore_index=True)
                    salvar(); st.success("Entrada registrada no Galpão com sucesso!"); st.rerun()

        st.divider()
        st.subheader("🔄 2. Transferência do Galpão para Outras Áreas (Verifica Habilitação + FIFO)")
        c1,c2 = st.columns(2)
        with c1:
            id_t = st.selectbox("ID para Movimentar", sorted(cat["ID"].unique()), key="id_t")
            p_t_info = get_p(id_t)
            
            # Verificar quais áreas estão habilitadas (True) para este ID específico
            destinos_permitidos = []
            if p_t_info.get("HAB_SALA_ANEXA", False): destinos_permitidos.append("SALA ANEXA")
            if p_t_info.get("HAB_OFICINA", False): destinos_permitidos.append("OFICINA DE REVESTIMENTO")
            
            st.write(f"**Áreas habilitadas para este ID:** {', '.join(destinos_permitidos) if destinos_permitidos else 'Nenhuma (Apenas Galpão)'}")
            
            destino = st.selectbox("TRANSFERIR PARA:", destinos_permitidos if destinos_permitidos else ["Nenhuma área habilitada"])
            q_t = st.number_input("QUANTIDADE A TRANSFERIR", 0.01, value=1.0, key="q_t")
            
            if st.button("🚀 DAR SAÍDA NO GALPÃO E ENTRAR NO DESTINO", type="primary", use_container_width=True):
                if destinos_permitidos and destino != "Nenhuma área habilitada":
                    p_t = get_fifo(id_t, "GALPÃO DE MATERIAIS REFRATÁRIOS")
                    if p_t is not None:
                        dt = agora_br()
                        lote_usado = p_t.get("Lote", "LOTE-01")
                        fab_usada = p_t.get("Fabricacao", date.today())
                        venc_usado = p_t.get("Vencimento", date.today())
                        
                        saida = {
                            "ID":id_t, "Material":p_t["Material"], "Marca":p_t["Marca"], "Lote":lote_usado,
                            "Fabricacao":fab_usada, "Vencimento":venc_usado, "Unidade":p_t["Unidade"], "Qtd_Externa":-q_t,
                            "Qtd_Interna_Total":-q_t, "Medida_Total":-q_t, "Area_Origem":"GALPÃO DE MATERIAIS REFRATÁRIOS", 
                            "Area_Destino":"GALPÃO DE MATERIAIS REFRATÁRIOS",
                            "Mov_Tipo":f"SAÍDA GALPÃO -> {destino}", "Data_Hora_BR":dt.strftime("%d/%m/%Y %H:%M:%S"), "Status":f"LOTE {lote_usado}"
                        }
                        entrada = saida.copy()
                        entrada["Qtd_Externa"] = q_t
                        entrada["Qtd_Interna_Total"] = q_t
                        entrada["Medida_Total"] = q_t
                        entrada["Area_Origem"] = "GALPÃO DE MATERIAIS REFRATÁRIOS"
                        entrada["Area_Destino"] = destino
                        entrada["Mov_Tipo"] = f"ENTRADA em {destino}"
                        entrada["Status"] = f"Recebido LOTE {lote_usado}"
                        
                        st.session_state.mov = pd.concat([st.session_state.mov, pd.DataFrame([saida, entrada])], ignore_index=True)
                        salvar(); st.success(f"Transferência realizada para {destino}!"); st.rerun()
                else:
                    st.error("Este material não está habilitado para esta área. Vá na aba de Catálogo para habilitar.")
        with c2:
            if not mov.empty:
                st.write("Estoque Consolidado por Área (FIFO)")
                saldo = mov.groupby(["ID","Lote","Area_Destino"]).agg(Saldo=("Qtd_Externa","sum")).reset_index()
                saldo = saldo[saldo["Saldo"]>0].sort_values(["ID","Lote"])
                st.dataframe(saldo, use_container_width=True, height=300)

with tab_est:
    if not mov.empty:
        st.dataframe(mov.sort_values("Data_Hora_BR", ascending=False), use_container_width=True, height=500)
    else:
        st.info("Nenhuma movimentação registrada.")

with tab_graf:
    if mov.empty:
        st.info("Sem dados para gerar gráficos.")
    else:
        mov["Data_Hora_BR_DT"] = pd.to_datetime(mov["Data_Hora_BR"], format="%d/%m/%Y %H:%M:%S", errors='coerce')
        mov["Tipo_Ent_Sai"] = mov["Qtd_Externa"].apply(lambda x: "ENTRADA" if x>0 else "SAÍDA")
        mov["Qtd_Abs"] = mov["Qtd_Externa"].abs()

        fig1 = px.bar(
            mov.groupby(["ID","Tipo_Ent_Sai"]).agg(Qtd=("Qtd_Abs","sum")).reset_index(), 
            x="ID", y="Qtd", color="Tipo_Ent_Sai", barmode="group", text="Qtd", 
            title="📊 ENTRADA X SAÍDA POR ID", color_discrete_map={"ENTRADA":"green","SAÍDA":"red"}
        )
        st.plotly_chart(fig1, use_container_width=True)

        sl = mov.groupby(["ID","Lote","Fabricacao","Area_Destino"]).agg(Externa=("Qtd_Externa","sum")).reset_index()
        sl = sl[sl["Externa"]>0].sort_values("Fabricacao")
        if not sl.empty:
            sl["Label"] = sl["ID"] + " | LOTE: " + sl["Lote"] + " | " + sl["Area_Destino"]
            fig2 = px.bar(sl, x="Externa", y="Label", orientation='h', color="Area_Destino", text="Externa", title="📦 ESTOQUE ATUAL POR ÁREA (FIFO)")
            st.plotly_chart(fig2, use_container_width=True)
