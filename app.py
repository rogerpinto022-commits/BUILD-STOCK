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
st.title(f"📦 BUILD STOCK - GESTÃO INTEGRADA | {agora_br().strftime('%d/%m/%Y %H:%M:%S')}")

AREAS_REAIS = ["GALPÃO DE MATERIAIS REFRATÁRIOS", "SALA ANEXA", "OFICINA DE REVESTIMENTO"]
CAT_FILE = "catalogo_padrao.csv"
MOV_FILE = "movimentacoes.csv"

# BASE PADRÃO COM CONTROLE DE HABILITAÇÃO POR ÁREA
def criar_catalogo_padrao():
    dados_padrao = [
        {"ID": "ID-1", "Material": "CIMENTO LAFARGE FONDU", "Marca": "LAFARGE", "Unidade": "KG", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-2", "Material": "CARBETO DE SILICIO", "Marca": "PADRÃO", "Unidade": "KG", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-3", "Material": "ARGAMASSA REFRATÁRIA TECNOFIRE 50S", "Marca": "TECNOFIRE", "Unidade": "KG", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-4", "Material": "CASTIBAR PSI UG", "Marca": "CASTIBAR", "Unidade": "KG", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-5", "Material": "LÃ DE ROCHA IBAR", "Marca": "IBAR", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-6", "Material": "TIJOLO SEMI ISOLANTE SUPRA", "Marca": "SKAMOL", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-7", "Material": "TIJOLO ISOLANTE SKAMOL", "Marca": "SKAMOL", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-8", "Material": "TIJOLOS REFRATÁRIOS VESUVIUS", "Marca": "VESUVIUS", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-11", "Material": "CHAMOTE IBAR / TECFIRE", "Marca": "IBAR", "Unidade": "KG", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-12", "Material": "PASTA FRIA / CARBON", "Marca": "ELKEN", "Unidade": "KG", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-14", "Material": "BLOCOS LATERAL CARBON", "Marca": "CARBON", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-15", "Material": "BLOCOS ENGUSADOS / FUNDO", "Marca": "PADRÃO", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-16", "Material": "BARRAS CATÓDICAS", "Marca": "PADRÃO", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
        {"ID": "ID-17", "Material": "BLOCOS DE FUNDO SEC", "Marca": "PADRÃO", "Unidade": "UN", "HAB_GALPAO": True, "HAB_SALA_ANEXA": True, "HAB_OFICINA": True},
    ]
    return pd.DataFrame(dados_padrao)

def carregar():
    cat = pd.read_csv(CAT_FILE) if os.path.exists(CAT_FILE) else criar_catalogo_padrao()
    for col in ["HAB_GALPAO", "HAB_SALA_ANEXA", "HAB_OFICINA"]:
        if col not in cat.columns:
            cat[col] = True
    mov = pd.read_csv(MOV_FILE) if os.path.exists(MOV_FILE) else pd.DataFrame(columns=[
        "ID","Material","Marca","Lote","Fabricacao","Vencimento",
        "Unidade","Qtd","Area_Origem","Area_Destino","Mov_Tipo","Data_Hora_BR","Status"
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

tab_cad, tab_mov, tab_est, tab_geral, tab_graf = st.tabs([
    "⚙️ CATÁLOGO & HABILITAÇÃO", 
    "🔄 MOVIMENTAÇÕES (ENTRADA/SAÍDA/DEVOLUÇÃO)", 
    "📋 ESTOQUE POR ÁREA", 
    "📊 SOMA GERAL DO ESTOQUE", 
    "📈 GRÁFICOS"
])

with tab_cad:
    st.subheader("⚙️ Painel de Cadastro e Habilitação de Materiais por Área")
    st.write("Marque ou desmarque para habilitar/desabilitar a visualização e movimentação dos materiais em cada área.")
    
    edited_cat = st.data_editor(cat, num_rows="dynamic", use_container_width=True, key="editor_habilita")
    if st.button("💾 SALVAR ALTERAÇÕES DE HABILITAÇÃO", type="primary"):
        st.session_state.catalogo = edited_cat
        salvar()
        st.success("Habilitações atualizadas com sucesso!")
        st.rerun()

with tab_mov:
    if cat.empty:
        st.warning("Cadastre itens no catálogo primeiro.")
    else:
        st.subheader("🔄 Central de Movimentações (Entrada, Saída e Devolução)")
        
        tipo_op = st.selectbox("SELECIONE O TIPO DE OPERAÇÃO", ["ENTRADA (Geral / Galpão ou Áreas)", "SAÍDA / TRANSFERÊNCIA", "DEVOLUÇÃO"])
        
        if tipo_op == "ENTRADA (Geral / Galpão ou Áreas)":
            st.info("💡 A entrada principal ocorre no Galpão. Caso necessário, você também pode registrar diretamente em outras áreas.")
            area_entrada = st.selectbox("LOCAL DE ENTRADA", AREAS_REAIS, key="ent_area")
            id_e = st.selectbox("ID DO MATERIAL", sorted(cat["ID"].unique()), key="ent_id")
            p_e = get_p(id_e)
            
            with st.form("form_ent_geral", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write(f"**Material:** {p_e['Material']}")
                    st.write(f"**Marca:** {p_e['Marca']}")
                    lote = st.text_input("LOTE", value="LOTE-01")
                with c2:
                    fab = st.date_input("FABRICAÇÃO", value=date.today())
                    val_d = st.number_input("VALIDADE (DIAS)", 1, value=365)
                with c3:
                    qtd = st.number_input("QUANTIDADE", 0.01, value=1.0, key="qtd_ent")
                    st.write(f"Unidade: **{p_e['Unidade']}**")
                
                if st.form_submit_button("💾 REGISTRAR ENTRADA", type="primary", use_container_width=True):
                    dt = agora_br()
                    venc = fab + timedelta(days=int(val_d))
                    novo_reg = {
                        "ID": id_e, "Material": p_e["Material"], "Marca": p_e["Marca"],
                        "Lote": lote, "Fabricacao": str(fab), "Vencimento": str(venc),
                        "Unidade": p_e["Unidade"], "Qtd": qtd,
                        "Area_Origem": "FORNECEDOR", "Area_Destino": area_entrada,
                        "Mov_Tipo": "ENTRADA", "Data_Hora_BR": dt.strftime("%d/%m/%Y %H:%M:%S"),
                        "Status": f"Entrada em {area_entrada}"
                    }
                    st.session_state.mov = pd.concat([mov, pd.DataFrame([novo_reg])], ignore_index=True)
                    salvar()
                    st.success(f"Entrada de {qtd} {p_e['Unidade']} registrada com sucesso em {area_entrada}!")
                    st.rerun()

        elif tipo_op == "SAÍDA / TRANSFERÊNCIA":
            origem = st.selectbox("ÁREA DE ORIGEM", AREAS_REAIS, key="sai_origem")
            id_s = st.selectbox("ID DO MATERIAL", sorted(cat["ID"].unique()), key="sai_id")
            p_s = get_p(id_s)
            
            destino = st.selectbox("ÁREA DE DESTINO", [a for a in AREAS_REAIS if a != origem], key="sai_dest")
            
            with st.form("form_sai", clear_on_submit=True):
                qtd_s = st.number_input("QUANTIDADE A SAIR / TRANSFERIR", 0.01, value=1.0, key="qtd_sai")
                lote_s = st.text_input("LOTE", value="LOTE-01")
                
                if st.form_submit_button("🚀 CONFIRMAR SAÍDA / TRANSFERÊNCIA", type="primary", use_container_width=True):
                    dt = agora_br()
                    # Registro de Saída na Origem (negativo)
                    reg_saida = {
                        "ID": id_s, "Material": p_s["Material"], "Marca": p_s["Marca"],
                        "Lote": lote_s, "Fabricacao": str(date.today()), "Vencimento": str(date.today() + timedelta(days=365)),
                        "Unidade": p_s["Unidade"], "Qtd": -qtd_s,
                        "Area_Origem": origem, "Area_Destino": origem,
                        "Mov_Tipo": f"SAÍDA PARA {destino}", "Data_Hora_BR": dt.strftime("%d/%m/%Y %H:%M:%S"),
                        "Status": "OK"
                    }
                    # Registro de Entrada Automática no Destino (positivo)
                    reg_entrada = {
                        "ID": id_s, "Material": p_s["Material"], "Marca": p_s["Marca"],
                        "Lote": lote_s, "Fabricacao": str(date.today()), "Vencimento": str(date.today() + timedelta(days=365)),
                        "Unidade": p_s["Unidade"], "Qtd": qtd_s,
                        "Area_Origem": origem, "Area_Destino": destino,
                        "Mov_Tipo": f"ENTRADA VIA {origem}", "Data_Hora_BR": dt.strftime("%d/%m/%Y %H:%M:%S"),
                        "Status": "OK"
                    }
                    st.session_state.mov = pd.concat([mov, pd.DataFrame([reg_saida, reg_entrada])], ignore_index=True)
                    salvar()
                    st.success(f"Transferência de {origem} para {destino} realizada com sucesso!")
                    st.rerun()

        elif tipo_op == "DEVOLUÇÃO":
            st.info("💡 Use esta opção para devolver materiais de uma área de volta ao Galpão ou entre setores.")
            origem_dev = st.selectbox("ÁREA DE ORIGEM DA DEVOLUÇÃO", AREAS_REAIS, key="dev_origem")
            id_d = st.selectbox("ID DO MATERIAL", sorted(cat["ID"].unique()), key="dev_id")
            p_d = get_p(id_d)
            destino_dev = st.selectbox("DESTINO DA DEVOLUÇÃO", AREAS_REAIS, key="dev_dest")
            
            with st.form("form_dev", clear_on_submit=True):
                qtd_d = st.number_input("QUANTIDADE A DEVOLVER", 0.01, value=1.0, key="qtd_dev")
                lote_d = st.text_input("LOTE", value="LOTE-01")
                
                if st.form_submit_button("🔄 CONFIRMAR DEVOLUÇÃO", type="primary", use_container_width=True):
                    dt = agora_br()
                    reg_sai_dev = {
                        "ID": id_d, "Material": p_d["Material"], "Marca": p_d["Marca"],
                        "Lote": lote_d, "Fabricacao": str(date.today()), "Vencimento": str(date.today() + timedelta(days=365)),
                        "Unidade": p_d["Unidade"], "Qtd": -qtd_d,
                        "Area_Origem": origem_dev, "Area_Destino": origem_dev,
                        "Mov_Tipo": f"SAÍDA DEVOLUÇÃO PARA {destino_dev}", "Data_Hora_BR": dt.strftime("%d/%m/%Y %H:%M:%S"),
                        "Status": "OK"
                    }
                    reg_ent_dev = {
                        "ID": id_d, "Material": p_d["Material"], "Marca": p_d["Marca"],
                        "Lote": lote_d, "Fabricacao": str(date.today()), "Vencimento": str(date.today() + timedelta(days=365)),
                        "Unidade": p_d["Unidade"], "Qtd": qtd_d,
                        "Area_Origem": origem_dev, "Area_Destino": destino_dev,
                        "Mov_Tipo": f"DEVOLUÇÃO RECEBIDA DE {origem_dev}", "Data_Hora_BR": dt.strftime("%d/%m/%Y %H:%M:%S"),
                        "Status": "OK"
                    }
                    st.session_state.mov = pd.concat([mov, pd.DataFrame([reg_sai_dev, reg_ent_dev])], ignore_index=True)
                    salvar()
                    st.success(f"Devolução processada com sucesso de {origem_dev} para {destino_dev}!")
                    st.rerun()

with tab_est:
    st.subheader("📋 Estoque Separado por Área (Respeitando Habilitações)")
    if mov.empty:
        st.info("Nenhuma movimentação registrada.")
    else:
        # Calcular saldo por ID e Área de Destino
        saldo_geral = mov.groupby(["ID", "Material", "Marca", "Unidade", "Area_Destino"])["Qtd"].sum().reset_index()
        saldo_geral = saldo_geral[saldo_geral["Qtd"] != 0]
        
        col_filtro = st.selectbox("FILTRAR POR ÁREA", AREAS_REAIS)
        
        # Filtrar com base na habilitação da área escolhida no catálogo
        if col_filtro == "GALPÃO DE MATERIAIS REFRATÁRIOS":
            ids_hab = cat[cat["HAB_GALPAO"] == True]["ID"].tolist()
        elif col_filtro == "SALA ANEXA":
            ids_hab = cat[cat["HAB_SALA_ANEXA"] == True]["ID"].tolist()
        else:
            ids_hab = cat[cat["HAB_OFICINA"] == True]["ID"].tolist()
            
        df_filtrado = saldo_geral[(saldo_geral["Area_Destino"] == col_filtro) & (saldo_geral["ID"].isin(ids_hab))]
        
        st.write(f"Exibindo estoque para: **{col_filtro}** (Itens habilitados)")
        st.dataframe(df_filtrado, use_container_width=True)

with tab_geral:
    st.subheader("📊 Soma Geral do Estoque (Somando as 3 Áreas)")
    if mov.empty:
        st.info("Nenhuma movimentação registrada.")
    else:
        # Soma total consolidada por ID considerando todas as áreas
        soma_total = mov.groupby(["ID", "Material", "Marca", "Unidade"])["Qtd"].sum().reset_index()
        soma_total = soma_total[soma_total["Qtd"] != 0]
        
        # Detalhar por área em formato tabela cruzada (Pivot)
        pivot_area = mov.pivot_table(index=["ID", "Material", "Marca", "Unidade"], columns="Area_Destino", values="Qtd", aggfunc="sum").fillna(0).reset_index()
        
        st.write("### Visão Consolidada Global")
        st.dataframe(pivot_area, use_container_width=True)

with tab_graf:
    if mov.empty:
        st.info("Sem dados para gerar gráficos.")
    else:
        st.subheader("📈 Análise Gráfica de Estoque")
        df_graf = mov.groupby(["ID", "Area_Destino"])["Qtd"].sum().reset_index()
        df_graf = df_graf[df_graf["Qtd"] > 0]
        
        fig = px.bar(df_graf, x="ID", y="Qtd", color="Area_Destino", barmode="group", title="Estoque Atual por ID e por Área")
        st.plotly_chart(fig, use_container_width=True)

