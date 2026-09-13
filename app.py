import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="BUILD STOCK BR", page_icon="📦", layout="wide")

# ==========================================
# CADASTRO BASE (COM STATUS ATIVO/INATIVO)
# ==========================================
if "cat" not in st.session_state:
    st.session_state.cat = pd.DataFrame([
        # 1
        {"ID": 1, "Material": "CIMENTO LAFARGE FONDU", "Lote": "09/07/25_1400kg", "Fabricacao": "2025-07-09", "Validade": "12 Meses", "Unidade": "KG", "Status": "Ativo"},
        
        # 2
        {"ID": 2, "Material": "CARBETO DE SILICIO", "Lote": "LOTE-CS-1000", "Fabricacao": "2025-01-10", "Validade": "Indeterminada", "Unidade": "KG", "Status": "Ativo"},
        
        # 3
        {"ID": 3, "Material": "ARGAMASSA REFRATÁRIA TECNOFIRE 50S (1200kg)", "Lote": "TEC-50S-1200", "Fabricacao": "2025-02-01", "Validade": "6 Meses", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 3, "Material": "ARGAMASSA REFRATÁRIA TECNOFIRE 50S (400kg)", "Lote": "TEC-50S-400", "Fabricacao": "2025-02-02", "Validade": "6 Meses", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 3, "Material": "ARGAMASSA REFRATÁRIA PLACIBAR SG (1250kg)", "Lote": "PLAC-SG-1250", "Fabricacao": "2025-02-05", "Validade": "6 Meses", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 3, "Material": "ARGAMASSA REFRATÁRIA PLACIBAR SG (1000kg)", "Lote": "PLAC-SG-1000", "Fabricacao": "2025-02-06", "Validade": "6 Meses", "Unidade": "KG", "Status": "Ativo"},
        
        # 4
        {"ID": 4, "Material": "CASTIBAR PSI UG (1250kg)", "Lote": "CAST-UG-1250", "Fabricacao": "2025-03-01", "Validade": "12 Meses", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 4, "Material": "CASTIBAR PSI UG (1000kg)", "Lote": "CAST-UG-1000", "Fabricacao": "2025-03-02", "Validade": "12 Meses", "Unidade": "KG", "Status": "Ativo"},
        
        # 5
        {"ID": 5, "Material": "LÃ DE ROCHA IBAR SEM CORTE", "Lote": "LA-ROCHA-SC", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 5, "Material": "LÃ DE ROCHA IBAR CORTADO", "Lote": "LA-ROCHA-C", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        
        # 6
        {"ID": 6, "Material": "TIJOLO SEMI ISOLANTE SUPRA SKAMOL ALUPOROS-910", "Lote": "SKAMOL-910", "Fabricacao": "2025-01-15", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 6, "Material": "TIJOLO SEMI ISOLANTE SUPRA MOSCONI AB70-1020", "Lote": "MOSCONI-1020", "Fabricacao": "2025-01-15", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        
        # 7
        {"ID": 7, "Material": "TIJOLO ISOLANTE SKAMOL ALUPOROS 912", "Lote": "SKAMOL-912", "Fabricacao": "2025-02-01", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 7, "Material": "TIJOLO ISOLANTE MOSCONI AB 55-680", "Lote": "MOSCONI-680", "Fabricacao": "2025-02-01", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        
        # 8
        {"ID": 8, "Material": "TIJOLO REFRATÁRIO SA ALUM 512", "Lote": "SA-ALUM-512", "Fabricacao": "2025-02-10", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 8, "Material": "TIJOLO REFRATÁRIO VESUVIUS 336", "Lote": "VESUVIUS-336", "Fabricacao": "2025-02-10", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 8, "Material": "TIJOLO REFRATÁRIO VESUVIUS 416 [CHINA]", "Lote": "VESUVIUS-416", "Fabricacao": "2025-02-10", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 8, "Material": "TIJOLO REFRATÁRIO VESUVIUS 296 [CHINA]", "Lote": "VESUVIUS-296", "Fabricacao": "2025-02-10", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        
        # 11
        {"ID": 11, "Material": "CHAMOTE IBAR", "Lote": "CHAMOTE-IBAR", "Fabricacao": "2025-03-01", "Validade": "Indeterminada", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 11, "Material": "CHAMOTE TecFire", "Lote": "CHAMOTE-TEC", "Fabricacao": "2025-03-01", "Validade": "Indeterminada", "Unidade": "KG", "Status": "Ativo"},
        
        # 12
        {"ID": 12, "Material": "PASTA FRIA ELKEN T30 - REMENDO 74630_74631", "Lote": "74630_74631", "Fabricacao": "2025-03-10", "Validade": "3 Meses", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 12, "Material": "PASTA FRIA REMENDO 75074_75075 A 75085_75087", "Lote": "75074-87", "Fabricacao": "2025-03-11", "Validade": "3 Meses", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 12, "Material": "PASTA FRIA 75949_75952", "Lote": "75949_75952", "Fabricacao": "2025-03-12", "Validade": "3 Meses", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 12, "Material": "PASTA FRIA 76007_76010", "Lote": "76007_76010", "Fabricacao": "2025-03-13", "Validade": "3 Meses", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 12, "Material": "PASTA FRIA ELKEN 76323_76328", "Lote": "76323_76328", "Fabricacao": "2025-03-14", "Validade": "3 Meses", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 12, "Material": "PASTA FRIA ELKEN 76069_76086", "Lote": "76069_76086", "Fabricacao": "2025-03-15", "Validade": "3 Meses", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 12, "Material": "PASTA FRIA LOTES 76030_76037 e 76062_76067", "Lote": "76030-67", "Fabricacao": "2025-03-16", "Validade": "3 Meses", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 12, "Material": "PASTA FRIA CARBON LOTE 759", "Lote": "LOTE-759", "Fabricacao": "2025-03-17", "Validade": "3 Meses", "Unidade": "KG", "Status": "Ativo"},
        {"ID": 12, "Material": "PASTA FRIA CARBON LOTE 763", "Lote": "LOTE-763", "Fabricacao": "2025-03-18", "Validade": "3 Meses", "Unidade": "KG", "Status": "Ativo"},
        
        # 13
        {"ID": 13, "Material": "ITEM AUXILIAR ID-13", "Lote": "PADRÃO", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        
        # 14
        {"ID": 14, "Material": "BLOCOS LATERAL CARBON", "Lote": "BL-CARBON", "Fabricacao": "2025-01-05", "Validade": "Indeterminada", "Unidade": "CX", "Status": "Ativo"},
        
        # 15
        {"ID": 15, "Material": "BLOCOS ENGUSADOS/FUNDO ANEXA SEC", "Lote": "ANEXA-SEC", "Fabricacao": "2025-01-10", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 15, "Material": "BLOCOS ENGUSADOS/FUNDO BARRACAO SEC", "Lote": "BAR-SEC", "Fabricacao": "2025-01-10", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 15, "Material": "BLOCOS ENGUSADOS/FUNDO BARRACAO BLOCO DE FUNDO ENERGOPRON", "Lote": "ENEROPRON", "Fabricacao": "2025-01-10", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 15, "Material": "BLOCOS ENGUSADOS/FUNDO BARRACAO BLOCOS DE FUNDO TOKAYCOBEX", "Lote": "TOKAYCOBEX", "Fabricacao": "2025-01-10", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        
        # 16
        {"ID": 16, "Material": "BARRAS CATÓDICAS ANEXA", "Lote": "BC-ANEXA", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 16, "Material": "BARRAS CATÓDICAS BARRACAO", "Lote": "BC-BARRACAO", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 16, "Material": "BARRAS CATÓDICAS BARRACAO TESTE", "Lote": "BC-TESTE-1", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 16, "Material": "BARRAS CATÓDICAS BARRACAO TESTE 2", "Lote": "BC-TESTE-2", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        
        # 17
        {"ID": 17, "Material": "BLOCOS DE FUNDO SEC BARRACÃO", "Lote": "BF-BAR", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 17, "Material": "BLOCOS DE FUNDO SEC BARRACAO TOKAYCOBEX", "Lote": "BF-BAR-TOKA", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"},
        {"ID": 17, "Material": "BLOCOS DE FUNDO SEC ANEXA", "Lote": "BF-ANEXA", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN", "Status": "Ativo"}
    ])

cat = st.session_state.cat

if "movimentacoes" not in st.session_state:
    st.session_state.movimentacoes = pd.DataFrame(columns=[
        "Data/Hora", "ID", "Material", "Tipo", "Quantidade", "Fabricação", "Lote", "Validade", "Área", "Responsável"
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
    st.header("📊 Consulta Dinâmica: Saldo Consolidado, Lista Completa & Histórico")
    
    # Exibe a lista completa de itens ativos e inativos nesta tela também
    with st.expander("📌 Visualizar Lista Completa de Itens Cadastrados no Sistema"):
        st.dataframe(cat, use_container_width=True)
    
    cat["Label"] = "ID " + cat["ID"].astype(str) + " — " + cat["Material"].str.upper() + " (" + cat["Status"] + ")"
    
    ids_selecionados = st.multiselect(
        "Selecione as IDs para Exibir no Relatório",
        options=cat["Label"].tolist(),
        default=cat["Label"].tolist()
    )
    
    ids_filtrados = [int(item.split(" — ")[0].replace("ID ", "")) for item in ids_selecionados]
    
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
                    label=f"ID {row['ID']} ({row['Unidade']})", 
                    value=f"{saldo:.2f}", 
                    delta=f"{row['Material']} [{row['Status']}]"
                )
    else:
        st.info("Selecione ao menos uma ID acima para visualizar os dados.")

    st.subheader("🕒 Histórico de Movimentações das IDs Selecionadas")
    if not st.session_state.movimentacoes.empty and ids_filtrados:
        df_mov_filt = st.session_state.movimentacoes[st.session_state.movimentacoes["ID"].isin(ids_filtrados)]
        st.dataframe(df_mov_filt, use_container_width=True)
    else:
        st.info("Nenhuma movimentação registrada no sistema para os itens selecionados.")

# 2. MOVIMENTAÇÕES (COM EDIÇÃO DE LOTE E FABRICAÇÃO)
elif menu == "Movimentações (Entrada/Saída)":
    st.header("🔄 Registrar Entrada ou Saída de Materiais por ID Numérica")
    
    # Exibe a lista completa de referência nesta tela também
    with st.expander("📌 Consultar Lista de Itens Disponíveis para Movimentação"):
        st.dataframe(cat, use_container_width=True)
    
    # Filtra apenas itens com Status "Ativo" para a movimentação
    cat_ativos = cat[cat["Status"] == "Ativo"]
    
    id_num = st.number_input("DIGITE O NÚMERO DA ID (1 a 17):", min_value=1, max_value=100, value=1, step=1)
    
    itens_encontrados = cat_ativos[cat_ativos["ID"] == id_num]
    
    if not itens_encontrados.empty:
        st.success(f"ID {id_num} encontrada! Existem {len(itens_encontrados)} registro(s) ativo(s) vinculado(s) a ela.")
        
        if len(itens_encontrados) > 1:
            opcoes_mat = itens_encontrados["Material"].tolist()
            material_escolhido = st.selectbox("Selecione a especificação exata deste item:", options=opcoes_mat)
            item_selecionado = itens_encontrados[itens_encontrados["Material"] == material_escolhido].iloc[0]
        else:
            item_selecionado = itens_encontrados.iloc[0]
        
        limpo_id = item_selecionado["ID"]
        nome_mat = item_selecionado["Material"]
        lote_padrao = item_selecionado["Lote"]
        fab_padrao = item_selecionado["Fabricacao"]
        val_auto = item_selecionado["Validade"]
        unidade_auto = item_selecionado["Unidade"]
        
        st.info(f"✨ **Preenchimento Automático (ID {limpo_id}):**\n\n"
                f"- **Material:** {nome_mat}\n"
                f"- **Validade Padrão:** {val_auto}\n"
                f"- **Unidade:** {unidade_auto}")
        
        with st.form("form_mov_editavel"):
            tipo = st.selectbox("Tipo de Movimentação", ["Entrada", "Saída"])
            
            # Campos de Lote e Fabricação agora editáveis para ajuste pontual
            lote_editado = st.text_input("Lote (Você pode alterar se necessário)", value=lote_padrao)
            
            # Tenta converter a data padrão para objeto date do python
            try:
                data_fab_obj = datetime.datetime.strptime(str(fab_padrao), "%Y-%m-%d").date()
            except:
                data_fab_obj = datetime.date.today()
                
            fab_editada = st.date_input("Data de Fabricação (Você pode alterar se necessário)", value=data_fab_obj)
            
            qtd = st.number_input(f"Quantidade ({unidade_auto})", min_value=0.0, step=0.1)
            area = st.text_input("Área / Local")
            resp = st.text_input("Responsável")
            
            submitted = st.form_submit_button("Salvar Movimentação")
            if submitted:
                data_hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                nova_linha = {
                    "Data/Hora": data_hora_atual,
                    "ID": limpo_id,
                    "Material": nome_mat,
                    "Tipo": tipo,
                    "Quantidade": qtd,
                    "Fabricação": str(fab_editada),
                    "Lote": lote_editado,
                    "Validade": val_auto,
                    "Área": area,
                    "Responsável": resp
                }
                st.session_state.movimentacoes = pd.concat(
                    [st.session_state.movimentacoes, pd.DataFrame([nova_linha])], 
                    ignore_index=True
                )
                st.success(f"Movimentação registrada com sucesso em {data_hora_atual}!")
    else:
        st.warning("Nenhum item ATIVO cadastrado para este número de ID (ou ID inativada).")

    st.subheader("📋 Histórico Geral de Lançamentos")
    if not st.session_state.movimentacoes.empty:
        st.dataframe(st.session_state.movimentacoes, use_container_width=True)
    else:
        st.info("Nenhum lançamento efetuado ainda.")

# 3. CADASTRO BASE (COM OPÇÃO DE ATIVAR / DESATIVAR ITEM A ITEM)
elif menu == "Cadastro Base de Itens":
    st.header("📋 Cadastro Base de Materiais — Ativar / Desativar Itens")
    
    st.info("💡 Abaixo você pode conferir a lista completa e gerenciar o status (Ativo ou Inativo) de cada item individualmente.")
    
    # Exibe a tabela completa com a lista em evidência
    st.dataframe(cat, use_container_width=True)
    
    st.divider()
    st.subheader("⚙️ Ativar ou Desativar Item Existente")
    
    # Cria uma lista descritiva para selecionar o item que deseja alterar o status
    cat["Desc_Alt"] = "ID " + cat["ID"].astype(str) + " — " + cat["Material"] + " (Lote: " + cat["Lote"] + ")"
    item_para_mudar = st.selectbox("Selecione o item para alterar o status:", options=cat["Desc_Alt"].tolist())
    
    indice_encontrado = cat[cat["Desc_Alt"] == item_para_mudar].index[0]
    status_atual = cat.loc[indice_encontrado, "Status"]
    
    novo_status = st.radio("Alterar Status para:", ["Ativo", "Inativo"], index=0 if status_atual == "Ativo" else 1)
    
    if st.button("Atualizar Status do Item"):
        st.session_state.cat.loc[indice_encontrado, "Status"] = novo_status
        st.success(f"Status atualizado com sucesso para **{novo_status}**!")
        st.rerun()

    st.divider()
    with st.form("novo_item"):
        st.subheader("➕ Adicionar Novo Item na Base")
        novo_id = st.number_input("Número da ID", min_value=1, max_value=100, value=18, step=1)
        novo_mat = st.text_input("Nome / Especificação do Material")
        novo_lote = st.text_input("Lote")
        nova_fab = st.date_input("Data de Fabricação", value=datetime.date.today())
        nova_val = st.text_input("Tempo de Validade (Ex: 12 Meses, Indeterminada)")
        nova_un = st.text_input("Unidade (Ex: KG, UN, M2, CX)")
        
        add_submitted = st.form_submit_button("Cadastrar Item")
        if add_submitted and novo_mat:
            novo_registro = pd.DataFrame([{
                "ID": int(novo_id), 
                "Material": novo_mat, 
                "Lote": novo_lote, 
                "Fabricacao": str(nova_fab), 
                "Validade": nova_val, 
                "Unidade": nova_un,
                "Status": "Ativo"
            }])
            st.session_state.cat = pd.concat([st.session_state.cat, novo_registro], ignore_index=True)
            st.success(f"Item com ID {novo_id} adicionado com sucesso ao cadastro base!")
            st.rerun()
