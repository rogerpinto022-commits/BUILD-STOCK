import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="BUILD STOCK BR", page_icon="📦", layout="wide")

# ==========================================
# BASE DE DADOS COMPLETA (17 ITENS)
# ==========================================
if "base_cadastros" not in st.session_state:
    st.session_state.base_cadastros = pd.DataFrame([
        {"ID": "ID-1", "Material": "Cimento Lafarge Fondu", "Unidade": "KG"},
        {"ID": "ID-2", "Material": "Carbeto de Silicio", "Unidade": "KG"},
        {"ID": "ID-3", "Material": "Argamassa Refratária Tecnofire 50S", "Unidade": "KG"},
        {"ID": "ID-4", "Material": "Castibar Psi UG", "Unidade": "KG"},
        {"ID": "ID-5", "Material": "Lã de Rocha Ibar Sem Corte", "Unidade": "UN"},
        {"ID": "ID-6", "Material": "Tijolo Refratário Isolante", "Unidade": "UN"},
        {"ID": "ID-7", "Material": "Concreto Refratário Densos", "Unidade": "KG"},
        {"ID": "ID-8", "Material": "Fibra Cerâmica Mantas", "Unidade": "M2"},
        {"ID": "ID-9", "Material": "Cola para Fibra Cerâmica", "Unidade": "KG"},
        {"ID": "ID-10", "Material": "Aditivo Líquido ускоритель", "Unidade": "L"},
        {"ID": "ID-11", "Material": "Chapa de Aço Inox 310", "Unidade": "KG"},
        {"ID": "ID-12", "Material": "Prisioneiro Cerâmico", "Unidade": "UN"},
        {"ID": "ID-13", "Material": "Papel Cerâmico Isolante", "Unidade": "M2"},
        {"ID": "ID-14", "Material": "Tubo de Alumina", "Unidade": "UN"},
        {"ID": "ID-15", "Material": "Massa Calafetar Alta Temperatura", "Unidade": "KG"},
        {"ID": "ID-16", "Material": "Pó de Grafite Industrial", "Unidade": "KG"},
        {"ID": "ID-17", "Material": "Tela Metálica Galvanizada", "Unidade": "M2"}
    ])

if "movimentacoes" not in st.session_state:
    st.session_state.movimentacoes = pd.DataFrame(columns=[
        "Data", "ID", "Material", "Tipo", "Quantidade", "Marca", "Lote", "Área", "Responsável"
    ])

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
st.title("📦 BUILD STOCK BR — Gestão Industrial Avançada por ID e Local")

menu = st.sidebar.selectbox("Navegação", ["Consulta Dinâmica e Gráficos", "Movimentações (Entrada/Saída)", "Cadastro Base de Itens"])

# 1. CONSULTA DINÂMICA
if menu == "Consulta Dinâmica e Gráficos":
    st.header("📊 Consulta Dinâmica: Seleção Múltipla de IDs, Gráficos & Histórico")
    
    df_cad = st.session_state.base_cadastros
    df_cad["Label"] = df_cad["ID"] + " — " + df_cad["Material"].str.upper()
    
    ids_selecionados = st.multiselect(
        "Selecione as IDs para Exibir no Gráfico e Relatório",
        options=df_cad["Label"].tolist(),
        default=df_cad["Label"].tolist()[:5] # Deixa alguns selecionados por padrão
    )
    
    ids_filtrados = [item.split(" — ")[0] for item in ids_selecionados]
    
    st.subheader("🌟 Saldo Geral Consolidado por ID")
    if ids_filtrados:
        cols = st.columns(min(len(ids_filtrados), 4))
        for idx, item_id in enumerate(ids_filtrados):
            row = df_cad[df_cad["ID"] == item_id].iloc[0]
            with cols[idx % len(cols)]:
                st.metric(label=f"ID: {row['ID']} ({row['Unidade']})", value="0.00", delta=row['Material'])
    else:
        st.info("Selecione ao menos uma ID acima para visualizar os dados.")

    st.subheader("🕒 Histórico de Movimentações das IDs Selecionadas")
    if not st.session_state.movimentacoes.empty and ids_filtrados:
        df_mov_filt = st.session_state.movimentacoes[st.session_state.movimentacoes["ID"].isin(ids_filtrados)]
        st.dataframe(df_mov_filt, use_container_width=True)
    else:
        st.info("Nenhuma movimentação registrada no sistema para os itens selecionados.")

# 2. MOVIMENTAÇÕES
elif menu == "Movimentações (Entrada/Saída)":
    st.header("🔄 Registrar Entrada ou Saída de Materiais")
    
    df_cad = st.session_state.base_cadastros
    with st.form("form_mov"):
        id_escolhida = st.selectbox("Selecione o Material por ID", options=df_cad["ID"] + " — " + df_cad["Material"])
        tipo = st.selectbox("Tipo de Movimentação", ["Entrada", "Saída"])
        qtd = st.number_input("Quantidade", min_value=0.0, step=0.1)
        marca = st.text_input("Marca")
        lote = st.text_input("Lote")
        area = st.text_input("Área / Local")
        resp = st.text_input("Responsável")
        
        submitted = st.form_submit_button("Salvar Movimentação")
        if submitted:
            limpo_id = id_escolhida.split(" — ")[0]
            nome_mat = id_escolhida.split(" — ")[1]
            nova_linha = {
                "Data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ID": limpo_id,
                "Material": nome_mat,
                "Tipo": tipo,
                "Quantidade": qtd,
                "Marca": marca,
                "Lote": lote,
                "Área": area,
                "Responsável": resp
            }
            st.session_state.movimentacoes = pd.concat([st.session_state.movimentacoes, pd.DataFrame([nova_linha])], ignore_index=True)
            st.success("Movimentação registrada com sucesso!")

# 3. CADASTRO BASE
elif menu == "Cadastro Base de Itens":
    st.header("📋 Cadastro Base de Materiais (17 Itens)")
    st.dataframe(st.session_state.base_cadastros, use_container_width=True)
    
    with st.form("novo_item"):
        st.subheader("Adicionar Novo Item na Base")
        novo_id = st.text_input("ID (Ex: ID-18)")
        novo_mat = st.text_input("Nome do Material")
        nova_un = st.text_input("Unidade (Ex: KG, UN, M2)")
        add_submitted = st.form_submit_button("Cadastrar Item")
        if add_submitted and novo_id and novo_mat:
            novo_registro = pd.DataFrame([{"ID": novo_id, "Material": novo_mat, "Unidade": nova_un}])
            st.session_state.base_cadastros = pd.concat([st.session_state.base_cadastros, novo_registro], ignore_index=True)
            st.success(f"Item {novo_id} adicionado com sucesso! Atualize a página se necessário.")
