import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="BUILD STOCK BR", page_icon="📦", layout="wide")

# ==========================================
# CADASTRO BASE (FIXO, SEM DADOS DINÂMICOS)
# ==========================================
if "cat" not in st.session_state:
    st.session_state.cat = pd.DataFrame([
        # ID-1
        {"ID": "ID-1", "Material": "CIMENTO LAFARGE FONDU", "Lote": "09/07/25_1400kg", "Fabricacao": "2025-07-09", "Validade": "12 Meses", "Unidade": "KG"},
        
        # ID-2
        {"ID": "ID-2", "Material": "CARBETO DE SILICIO", "Lote": "LOTE-CS-1000", "Fabricacao": "2025-01-10", "Validade": "Indeterminada", "Unidade": "KG"},
        
        # ID-3
        {"ID": "ID-3", "Material": "ARGAMASSA REFRATÁRIA TECNOFIRE 50S (1200kg)", "Lote": "TEC-50S-1200", "Fabricacao": "2025-02-01", "Validade": "6 Meses", "Unidade": "KG"},
        {"ID": "ID-3", "Material": "ARGAMASSA REFRATÁRIA TECNOFIRE 50S (400kg)", "Lote": "TEC-50S-400", "Fabricacao": "2025-02-02", "Validade": "6 Meses", "Unidade": "KG"},
        {"ID": "ID-3", "Material": "ARGAMASSA REFRATÁRIA PLACIBAR SG (1250kg)", "Lote": "PLAC-SG-1250", "Fabricacao": "2025-02-05", "Validade": "6 Meses", "Unidade": "KG"},
        {"ID": "ID-3", "Material": "ARGAMASSA REFRATÁRIA PLACIBAR SG (1000kg)", "Lote": "PLAC-SG-1000", "Fabricacao": "2025-02-06", "Validade": "6 Meses", "Unidade": "KG"},
        
        # ID-4
        {"ID": "ID-4", "Material": "CASTIBAR PSI UG (1250kg)", "Lote": "CAST-UG-1250", "Fabricacao": "2025-03-01", "Validade": "12 Meses", "Unidade": "KG"},
        {"ID": "ID-4", "Material": "CASTIBAR PSI UG (1000kg)", "Lote": "CAST-UG-1000", "Fabricacao": "2025-03-02", "Validade": "12 Meses", "Unidade": "KG"},
        
        # ID-5
        {"ID": "ID-5", "Material": "LÃ DE ROCHA IBAR SEM CORTE", "Lote": "LA-ROCHA-SC", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-5", "Material": "LÃ DE ROCHA IBAR CORTADO", "Lote": "LA-ROCHA-C", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN"},
        
        # ID-6
        {"ID": "ID-6", "Material": "TIJOLO SEMI ISOLANTE SUPRA SKAMOL ALUPOROS-910", "Lote": "SKAMOL-910", "Fabricacao": "2025-01-15", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-6", "Material": "TIJOLO SEMI ISOLANTE SUPRA MOSCONI AB70-1020", "Lote": "MOSCONI-1020", "Fabricacao": "2025-01-15", "Validade": "Indeterminada", "Unidade": "UN"},
        
        # ID-7
        {"ID": "ID-7", "Material": "TIJOLO ISOLANTE SKAMOL ALUPOROS 912", "Lote": "SKAMOL-912", "Fabricacao": "2025-02-01", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-7", "Material": "TIJOLO ISOLANTE MOSCONI AB 55-680", "Lote": "MOSCONI-680", "Fabricacao": "2025-02-01", "Validade": "Indeterminada", "Unidade": "UN"},
        
        # ID-8
        {"ID": "ID-8", "Material": "TIJOLO REFRATÁRIO SA ALUM 512", "Lote": "SA-ALUM-512", "Fabricacao": "2025-02-10", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-8", "Material": "TIJOLO REFRATÁRIO VESUVIUS 336", "Lote": "VESUVIUS-336", "Fabricacao": "2025-02-10", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-8", "Material": "TIJOLO REFRATÁRIO VESUVIUS 416 [CHINA]", "Lote": "VESUVIUS-416", "Fabricacao": "2025-02-10", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-8", "Material": "TIJOLO REFRATÁRIO VESUVIUS 296 [CHINA]", "Lote": "VESUVIUS-296", "Fabricacao": "2025-02-10", "Validade": "Indeterminada", "Unidade": "UN"},
        
        # ID-11
        {"ID": "ID-11", "Material": "CHAMOTE IBAR", "Lote": "CHAMOTE-IBAR", "Fabricacao": "2025-03-01", "Validade": "Indeterminada", "Unidade": "KG"},
        {"ID": "ID-11", "Material": "CHAMOTE TecFire", "Lote": "CHAMOTE-TEC", "Fabricacao": "2025-03-01", "Validade": "Indeterminada", "Unidade": "KG"},
        
        # ID-12
        {"ID": "ID-12", "Material": "PASTA FRIA ELKEN T30 - REMENDO 74630_74631", "Lote": "74630_74631", "Fabricacao": "2025-03-10", "Validade": "3 Meses", "Unidade": "KG"},
        {"ID": "ID-12", "Material": "PASTA FRIA REMENDO 75074_75075 A 75085_75087", "Lote": "75074-87", "Fabricacao": "2025-03-11", "Validade": "3 Meses", "Unidade": "KG"},
        {"ID": "ID-12", "Material": "PASTA FRIA 75949_75952", "Lote": "75949_75952", "Fabricacao": "2025-03-12", "Validade": "3 Meses", "Unidade": "KG"},
        {"ID": "ID-12", "Material": "PASTA FRIA 76007_76010", "Lote": "76007_76010", "Fabricacao": "2025-03-13", "Validade": "3 Meses", "Unidade": "KG"},
        {"ID": "ID-12", "Material": "PASTA FRIA ELKEN 76323_76328", "Lote": "76323_76328", "Fabricacao": "2025-03-14", "Validade": "3 Meses", "Unidade": "KG"},
        {"ID": "ID-12", "Material": "PASTA FRIA ELKEN 76069_76086", "Lote": "76069_76086", "Fabricacao": "2025-03-15", "Validade": "3 Meses", "Unidade": "KG"},
        {"ID": "ID-12", "Material": "PASTA FRIA LOTES 76030_76037 e 76062_76067", "Lote": "76030-67", "Fabricacao": "2025-03-16", "Validade": "3 Meses", "Unidade": "KG"},
        {"ID": "ID-12", "Material": "PASTA FRIA CARBON LOTE 759", "Lote": "LOTE-759", "Fabricacao": "2025-03-17", "Validade": "3 Meses", "Unidade": "KG"},
        {"ID": "ID-12", "Material": "PASTA FRIA CARBON LOTE 763", "Lote": "LOTE-763", "Fabricacao": "2025-03-18", "Validade": "3 Meses", "Unidade": "KG"},
        
        # ID-13
        {"ID": "ID-13", "Material": "ITEM AUXILIAR ID-13", "Lote": "PADRÃO", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN"},
        
        # ID-14
        {"ID": "ID-14", "Material": "BLOCOS LATERAL CARBON", "Lote": "BL-CARBON", "Fabricacao": "2025-01-05", "Validade": "Indeterminada", "Unidade": "CX"},
        
        # ID-15
        {"ID": "ID-15", "Material": "BLOCOS ENGUSADOS/FUNDO ANEXA SEC", "Lote": "ANEXA-SEC", "Fabricacao": "2025-01-10", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-15", "Material": "BLOCOS ENGUSADOS/FUNDO BARRACAO SEC", "Lote": "BAR-SEC", "Fabricacao": "2025-01-10", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-15", "Material": "BLOCOS ENGUSADOS/FUNDO BARRACAO BLOCO DE FUNDO ENERGOPRON", "Lote": "ENEROPRON", "Fabricacao": "2025-01-10", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-15", "Material": "BLOCOS ENGUSADOS/FUNDO BARRACAO BLOCOS DE FUNDO TOKAYCOBEX", "Lote": "TOKAYCOBEX", "Fabricacao": "2025-01-10", "Validade": "Indeterminada", "Unidade": "UN"},
        
        # ID-16
        {"ID": "ID-16", "Material": "BARRAS CATÓDICAS ANEXA", "Lote": "BC-ANEXA", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-16", "Material": "BARRAS CATÓDICAS BARRACAO", "Lote": "BC-BARRACAO", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-16", "Material": "BARRAS CATÓDICAS BARRACAO TESTE", "Lote": "BC-TESTE-1", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-16", "Material": "BARRAS CATÓDICAS BARRACAO TESTE 2", "Lote": "BC-TESTE-2", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN"},
        
        # ID-17
        {"ID": "ID-17", "Material": "BLOCOS DE FUNDO SEC BARRACÃO", "Lote": "BF-BAR", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-17", "Material": "BLOCOS DE FUNDO SEC BARRACAO TOKAYCOBEX", "Lote": "BF-BAR-TOKA", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN"},
        {"ID": "ID-17", "Material": "BLOCOS DE FUNDO SEC ANEXA", "Lote": "BF-ANEXA", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN"}
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

# 2. MOVIMENTAÇÕES (DIGITAÇÃO DA ID COM AUTO-PREENCHIMENTO)
elif menu == "Movimentações (Entrada/Saída)":
    st.header("🔄 Registrar Entrada ou Saída de Materiais por ID")
    
    # Campo para digitar a ID (ex: ID-1, ID-3, ID-12)
    id_digitada = st.text_input("DIGITE A ID (Ex: ID-1, ID-3, ID-12):", "").strip().upper()
    
    if id_digitada:
        itens_encontrados = cat[cat["ID"] == id_digitada]
        
        if not itens_encontrados.empty:
            st.success(f"ID Encontrada! Existem {len(itens_encontrados)} registro(s) vinculado(s) a ela.")
            
            # Se houver mais de um item cadastrado para a mesma ID, seleciona qual variação é
            if len(itens_encontrados) > 1:
                opcoes_mat = itens_encontrados["Material"].tolist()
                material_escolhido = st.selectbox("Selecione a especificação exata deste ID:", options=opcoes_mat)
                item_selecionado = itens_encontrados[itens_encontrados["Material"] == material_escolhido].iloc[0]
            else:
                item_selecionado = itens_encontrados.iloc[0]
            
            limpo_id = item_selecionado["ID"]
            nome_mat = item_selecionado["Material"]
            lote_auto = item_selecionado["Lote"]
            fab_auto = item_selecionado["Fabricacao"]
            val_auto = item_selecionado["Validade"]
            unidade_auto = item_selecionado["Unidade"]
            
            # Exibe o que foi preenchido automaticamente pelo sistema
            st.info(f"✨ **Dados Preenchidos Automaticamente pela ID:**\n\n"
                    f"- **Material:** {nome_mat}\n"
                    f"- **Lote:** {lote_auto}\n"
                    f"- **Data de Fabricação:** {fab_auto}\n"
                    f"- **Validade:** {val_auto}\n"
                    f"- **Unidade:** {unidade_auto}")
            
            with st.form("form_mov_digitado"):
                tipo = st.selectbox("Tipo de Movimentação", ["Entrada", "Saída"])
                qtd = st.number_input(f"Quantidade Recebida / Movimentada ({unidade_auto})", min_value=0.0, step=0.1)
                area = st.text_input("Área / Local")
                resp = st.text_input("Responsável")
                
                submitted = st.form_submit_button("Salvar Movimentação")
                if submitted:
                    # Data e Hora geradas de forma 100% automática no momento do clique
                    data_hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    nova_linha = {
                        "Data/Hora": data_hora_atual,
                        "ID": limpo_id,
                        "Material": nome_mat,
                        "Tipo": tipo,
                        "Quantidade": qtd,
                        "Fabricação": fab_auto,
                        "Lote": lote_auto,
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
            st.error(f"Nenhum material encontrado com a ID '{id_digitada}'. Verifique se digitou corretamente (Ex: ID-1, ID-12).")
    else:
        st.info("👆 Digite a ID acima (ex: **ID-1** ou **ID-3**) para o sistema preencher os dados automaticamente.")

    st.subheader("📋 Histórico Geral de Lançamentos")
    if not st.session_state.movimentacoes.empty:
        st.dataframe(st.session_state.movimentacoes, use_container_width=True)
    else:
        st.info("Nenhum lançamento efetuado ainda.")

# 3. CADASTRO BASE
elif menu == "Cadastro Base de Itens":
    st.header("📋 Cadastro Base de Materiais e Validades")
    st.dataframe(cat[["ID", "Material", "Lote", "Fabricacao", "Validade", "Unidade"]], use_container_width=True)
    
    with st.form("novo_item"):
        st.subheader("Adicionar Novo Item na Base")
        novo_id = st.text_input("ID (Ex: ID-18)")
        novo_mat = st.text_input("Nome / Especificação do Material")
        novo_lote = st.text_input("Lote")
        nova_fab = st.date_input("Data de Fabricação", value=datetime.date.today())
        nova_val = st.text_input("Tempo de Validade (Ex: 12 Meses, Indeterminada)")
        nova_un = st.text_input("Unidade (Ex: KG, UN, M2, CX)")
        
        add_submitted = st.form_submit_button("Cadastrar Item")
        if add_submitted and novo_id and novo_mat:
            novo_registro = pd.DataFrame([{
                "ID": novo_id, 
                "Material": novo_mat, 
                "Lote": novo_lote, 
                "Fabricacao": str(nova_fab), 
                "Validade": nova_val, 
                "Unidade": nova_un
            }])
            st.session_state.cat = pd.concat([st.session_state.cat, novo_registro], ignore_index=True)
            st.success(f"Item {novo_id} adicionado com sucesso ao cadastro base!")
