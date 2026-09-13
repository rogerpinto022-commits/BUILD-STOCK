import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="BUILD STOCK BR", page_icon="📦", layout="wide")

# ==========================================
# CATÁLOGO BASE COMPLETO (17 ITENS)
# ==========================================
if "cat" not in st.session_state:
    st.session_state.cat = pd.DataFrame([
        {"ID": "ID-1", "Material": "Cimento Lafarge Fondu", "Unidade": "KG"},
        {"ID": "ID-2", "Material": "Carbeto de Silicio", "Unidade": "KG"},
        {"ID": "ID-3", "Material": "Argamassa Refratária Tecnofire 50S", "Unidade": "KG"},
        {"ID": "ID-4", "Material": "Castibar Psi UG", "Unidade": "KG"},
        {"ID": "ID-5", "Material": "Lã de Rocha Ibar Sem Corte", "Unidade": "UN"},
        {"ID": "ID-6", "Material": "Tijolo Refratário Isolante", "Unidade": "UN"},
        {"ID": "ID-7", "Material": "Concreto Refratário Denso", "Unidade": "KG"},
        {"ID": "ID-8", "Material": "Manta de Fibra Cerâmica", "Unidade": "M2"},
        {"ID": "ID-9", "Material": "Cola para Fibra Cerâmica", "Unidade": "KG"},
        {"ID": "ID-10", "Material": "Aditivo Líquido", "Unidade": "L"},
        {"ID": "ID-11", "Material": "Chapa de Aço Inox 310", "Unidade": "KG"},
        {"ID": "ID-12", "Material": "Prisioneiro Cerâmico", "Unidade": "UN"},
        {"ID": "ID-13", "Material": "Papel Cerâmico Isolante", "Unidade": "M2"},
        {"ID": "ID-14", "Material": "Tubo de Alumina", "Unidade": "UN"},
        {"ID": "ID-15", "Material": "Massa Calafetar Alta Temperatura", "Unidade": "KG"},
        {"ID": "ID-16", "Material": "Pó de Grafite Industrial", "Unidade": "KG"},
        {"ID": "ID-17", "Material": "Tela Metálica Galvanizada", "Unidade": "M2"}
    ])

cat = st.session_state.cat

if "movimentacoes" not in st.session_state:
    st.session_state.movimentacoes = pd.DataFrame(columns=[
        "Data", "ID", "Material", "Tipo", "Quantidade", "Marca", "Lote", "Área", "Responsável"
    ])

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
st.title("📦 BUILD STOCK BR — Gestão Industrial Avançada por ID e Local")

menu = st.sidebar.selectbox("Navegação", [
    "Consulta Dinâmica e Gráficos", 
    "Movimentações (Entrada/Saída)", 
    "Cadastro Base de Itens"
])

# 1. CONSULTA DINÂMICA
if menu == "Consulta Dinâmica e Gráficos":
    st.header("📊 Consulta Dinâmica: Seleção Múltipla de IDs, Gráficos & Histórico")
    
    cat["Label"] = cat["ID"] + " — " + cat["Material"].str.upper()
    
    ids_selecionados = st.multiselect(
        "Selecione as IDs para Exibir no Gráfico e Relatório",
        options=cat["Label"].tolist(),
        default=cat["Label"].tolist()
    )
    
    ids_filtrados = [item.split(" — ")[0] for item in ids_selecionados]
    
    st.subheader("🌟 Saldo Geral Consolidado por ID")
    if ids_filtrados:
        cols = st.columns(min(len(ids_filtrados), 4) if len(ids_filtrados) > 0 else 1)
        for idx, item_id in enumerate(ids_filtrados):
            row = cat[cat["ID"] == item_id].iloc[0]
            
            df_mov = st.session_state.movimentacoes
            saldo = 0.0
            if not df_mov.empty and item_id in df_mov["ID"].values:
                df_item = df_mov[df_mov["ID"] == item_id]
                entradas = df_item[df_item["Tipo"] == "Entrada"]["Quantidade"].sum()
                saidas = df_item[df_item["Tipo"] == "Saída"]["Quantidade"].sum()
                saldo = entradas - saidas

            with cols[idx % len(cols)]:
                st.metric(
                    label=f"{row['ID']} ({row['Unidade']})", 
                    value=f"{saldo:.2f}", 
                    delta=row['Material']
                )
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
    
    cat["Label"] = cat["ID"] + " — " + cat["Material"]
    
    with st.form("form_mov"):
        # Linha corrigida com a variável 'cat' devidamente carregada
        id_e = st.selectbox("SELECIONE O ID DO MATERIAL", sorted(cat["ID"].unique()), key="id_e")
        
        # Filtra o nome correspondente ao ID selecionado
        mat_correspondente = cat[cat["ID"] == id_e]["Material"].values[0]
        st.write(f"**Material Selecionado:** {mat_correspondente}")
        
        tipo = st.selectbox("Tipo de Movimentação", ["Entrada", "Saída"])
        qtd = st.number_input("Quantidade", min_value=0.0, step=0.1)
        marca = st.text_input("Marca")
        lote = st.text_input("Lote")
        area = st.text_input("Área / Local")
        resp = st.text_input("Responsável")
        
        submitted = st.form_submit_button("Salvar Movimentação")
        if submitted:
            nova_linha = {
                "Data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ID": id_e,
                "Material": mat_correspondente,
                "Tipo": tipo,
                "Quantidade": qtd,
                "Marca": marca,
                "Lote": lote,
                "Área": area,
                "Responsável": resp
            }
            st.session_state.movimentacoes = pd.concat(
                [st.session_state.movimentacoes, pd.DataFrame([nova_linha])], 
                ignore_index=True
            )
            st.success("Movimentação registrada com sucesso!")

    st.subheader("📋 Histórico Geral de Lançamentos")
    if not st.session_state.movimentacoes.empty:
        st.dataframe(st.session_state.movimentacoes, use_container_width=True)
    else:
        st.info("Nenhum lançamento efetuado ainda.")

# 3. CADASTRO BASE
elif menu == "Cadastro Base de Itens":
    st.header("📋 Cadastro Base de Materiais (17 Itens)")
    st.dataframe(cat[["ID", "Material", "Unidade"]], use_container_width=True)
    
    with st.form("novo_item"):
        st.subheader("Adicionar Novo Item na Base")
        novo_id = st.text_input("ID (Ex: ID-18)")
        novo_mat = st.text_input("Nome do Material")
        nova_un = st.text_input("Unidade (Ex: KG, UN, M2)")
        add_submitted = st.form_submit_button("Cadastrar Item")
        if add_submitted and novo_id and novo_mat:
            novo_registro = pd.DataFrame([{"ID": novo_id, "Material": novo_mat, "Unidade": nova_un}])
            st.session_state.cat = pd.concat([st.session_state.cat, novo_registro], ignore_index=True)
            st.success(f"Item {novo_id} adicionado com sucesso! Atualize a página se necessário.")
