
import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="BUILD STOCK BR", page_icon="📦", layout="wide")

LOCAIS = ["Galpão de Materiais", "Sala Anexa", "Oficina de Revestimento"]

# ==========================================
# 1. CADASTRO BASE DE ITENS (LISTA COMPLETA COM 17 ITENS)
# ==========================================
if "cat" not in st.session_state:
    st.session_state.cat = pd.DataFrame([
        {"ID": 1, "Material": "CIMENTO LAFARGE FONDU", "Lote": "09/07/25_1400kg", "Fabricacao": "2025-07-09", "Validade": "12 Meses", "Unidade": "KG", "QtdPorPalete": 1400.0, "Status": "Ativo"},
        {"ID": 2, "Material": "CARBETO DE SILICIO", "Lote": "LOTE-CS-1000", "Fabricacao": "2025-01-10", "Validade": "Indeterminada", "Unidade": "KG", "QtdPorPalete": 1000.0, "Status": "Ativo"},
        {"ID": 3, "Material": "ARGAMASSA REFRATÁRIA TECNOFIRE 50S (1200kg)", "Lote": "TEC-50S-1200", "Fabricacao": "2025-02-01", "Validade": "6 Meses", "Unidade": "KG", "QtdPorPalete": 1200.0, "Status": "Ativo"},
        {"ID": 4, "Material": "ARGAMASSA REFRATÁRIA PLACIBAR SG (1000kg)", "Lote": "PLAC-SG-1000", "Fabricacao": "2025-02-06", "Validade": "6 Meses", "Unidade": "KG", "QtdPorPalete": 1000.0, "Status": "Ativo"},
        {"ID": 5, "Material": "CASTIBAR PSI UG (1250kg)", "Lote": "CAST-UG-1250", "Fabricacao": "2025-03-01", "Validade": "12 Meses", "Unidade": "KG", "QtdPorPalete": 1250.0, "Status": "Ativo"},
        {"ID": 6, "Material": "LÃ DE ROCHA IBAR SEM CORTE", "Lote": "LA-ROCHA-SC", "Fabricacao": "2025-01-01", "Validade": "Indeterminada", "Unidade": "UN", "QtdPorPalete": 1.0, "Status": "Ativo"},
        {"ID": 7, "Material": "TIJOLO SEMI ISOLANTE SUPRA SKAMOL ALUPOROS-910", "Lote": "SKAMOL-910", "Fabricacao": "2025-01-15", "Validade": "Indeterminada", "Unidade": "UN", "QtdPorPalete": 1.0, "Status": "Ativo"},
        {"ID": 8, "Material": "TIJOLO REFRATÁRIO ALUMINA AL-70", "Lote": "AL-70-LOTE", "Fabricacao": "2025-01-20", "Validade": "Indeterminada", "Unidade": "UN", "QtdPorPalete": 1.0, "Status": "Ativo"},
        {"ID": 9, "Material": "CONCRETO REFRATÁRIO ISOLANTE", "Lote": "CONC-ISOL", "Fabricacao": "2025-01-25", "Validade": "6 Meses", "Unidade": "KG", "QtdPorPalete": 1000.0, "Status": "Ativo"},
        {"ID": 10, "Material": "FIBRA CERÂMICA MANTA 128kg/m³", "Lote": "FIBRA-128", "Fabricacao": "2025-02-10", "Validade": "Indeterminada", "Unidade": "RL", "QtdPorPalete": 1.0, "Status": "Ativo"},
        {"ID": 11, "Material": "CHAMOTE IBAR", "Lote": "CHAMOTE-IBAR", "Fabricacao": "2025-03-01", "Validade": "Indeterminada", "Unidade": "KG", "QtdPorPalete": 1000.0, "Status": "Ativo"},
        {"ID": 12, "Material": "PASTA FRIA ELKEN T30", "Lote": "74630_74631", "Fabricacao": "2025-03-10", "Validade": "3 Meses", "Unidade": "KG", "QtdPorPalete": 1000.0, "Status": "Ativo"},
        {"ID": 13, "Material": "PÓ DE GRAFITE INDUSTRIAL", "Lote": "GRAFITE-IND", "Fabricacao": "2025-03-15", "Validade": "Indeterminada", "Unidade": "KG", "QtdPorPalete": 500.0, "Status": "Ativo"},
        {"ID": 14, "Material": "BLOCOS LATERAL CARBON", "Lote": "BL-CARBON", "Fabricacao": "2025-01-05", "Validade": "Indeterminada", "Unidade": "CX", "QtdPorPalete": 1.0, "Status": "Ativo"},
        {"ID": 15, "Material": "ARGAMASSA DURAFIRE C", "Lote": "DURA-C", "Fabricacao": "2025-04-01", "Validade": "6 Meses", "Unidade": "KG", "QtdPorPalete": 1000.0, "Status": "Ativo"},
        {"ID": 16, "Material": "ANCORAGEM METÁLICA REFRATÁRIA", "Lote": "ANCOR-MET", "Fabricacao": "2025-04-05", "Validade": "Indeterminada", "Unidade": "PC", "QtdPorPalete": 1.0, "Status": "Ativo"},
        {"ID": 17, "Material": "PREMIX REFRATÁRIO ESPECIAL", "Lote": "PREMIX-ESP", "Fabricacao": "2025-04-10", "Validade": "6 Meses", "Unidade": "KG", "QtdPorPalete": 1000.0, "Status": "Ativo"}
    ])

# ==========================================
# 2. CONTROLE DE HABILITAÇÃO POR LOCAL (MATRIZ)
# ==========================================
if "permissoes_locais" not in st.session_state:
    perm_dict = []
    for _, row in st.session_state.cat.iterrows():
        for loc in LOCAIS:
            perm_dict.append({
                "ID": row["ID"],
                "Material": row["Material"],
                "Local": loc,
                "Habilitado": True
            })
    st.session_state.permissoes_locais = pd.DataFrame(perm_dict)

if "movimentacoes" not in st.session_state:
    st.session_state.movimentacoes = pd.DataFrame(columns=[
        "Data/Hora", "ID", "Material", "Tipo", "Local", "Destino_Transferencia", "Quantidade", "Fabricação", "Lote", "Validade", "Responsável", "Obs"
    ])

st.title("📦 BUILD STOCK BR — Gestão Industrial Integrada por Locais")

menu = st.sidebar.selectbox("Navegação", [
    "Consulta Dinâmica & Estoque", 
    "Habilitação de Materiais por Local",
    "Movimentações & Transferências", 
    "Saída de Produto Acabado (Oficina)",
    "Cadastro Base de Itens"
])

cat = st.session_state.cat
df_perm = st.session_state.permissoes_locais
df_mov = st.session_state.movimentacoes

# ==========================================
# 1. CONSULTA DINÂMICA
# ==========================================
if menu == "Consulta Dinâmica & Estoque":
    st.header("📊 Saldo Consolidado por Local e Status de Habilitação")
    
    with st.expander("📌 Visualizar Cadastro Base (17 Itens)"):
        st.dataframe(cat, use_container_width=True)
        
    if not df_mov.empty:
        st.subheader("🌟 Saldo Atual de Cada ID em Cada Local")
        saldos_lista = []
        for id_item in cat["ID"].unique():
            info_item = cat[cat["ID"] == id_item].iloc[0]
            for local in LOCAIS:
                entradas = df_mov[(df_mov["ID"] == id_item) & (df_mov["Local"] == local) & (df_mov["Tipo"].isin(["Entrada", "Transferência Entrada"]))]["Quantidade"].sum()
                saidas = df_mov[(df_mov["ID"] == id_item) & (df_mov["Local"] == local) & (df_mov["Tipo"].isin(["Saída", "Transferência Saída", "Produção Acabada (Baixa Insumos)"]))]["Quantidade"].sum()
                
                saldo_local = entradas - saidas
                
                status_hab = df_perm[(df_perm["ID"] == id_item) & (df_perm["Local"] == local)]
                hab_str = "Habilitado ✅" if (not status_hab.empty and status_hab.iloc[0]["Habilitado"]) else "Desabilitado ❌"
                
                if saldo_local != 0 or hab_str == "Habilitado ✅":
                    saldos_lista.append({
                        "ID": id_item,
                        "Material": info_item["Material"],
                        "Unidade": info_item["Unidade"],
                        "Local": local,
                        "Status no Local": hab_str,
                        "Saldo": saldo_local
                    })
        if saldos_lista:
            st.dataframe(pd.DataFrame(saldos_lista), use_container_width=True)
        else:
            st.info("Nenhum dado para exibir.")
            
        st.subheader("🕒 Histórico Geral de Movimentações")
        st.dataframe(df_mov, use_container_width=True)
    else:
        st.info("Nenhuma movimentação registrada no sistema.")

# ==========================================
# 2. HABILITAÇÃO DE MATERIAIS POR LOCAL
# ==========================================
elif menu == "Habilitação de Materiais por Local":
    st.header("⚙️ Gerenciar Habilitação de Uso por Local")
    st.info("Aqui o operador define quais materiais podem ser movimentados ou utilizados em cada um dos 3 locais.")
    
    local_escolhido = st.selectbox("Selecione o Local para configurar:", LOCAIS)
    
    st.subheader(f"Lista de Materiais para: {local_escolhido}")
    
    idx_local = df_perm[df_perm["Local"] == local_escolhido].index
    
    with st.form("form_habilitacao"):
        novos_estados = []
        for i in idx_local:
            row_p = df_perm.loc[i]
            val_atual = row_p["Habilitado"]
            novo_val = st.checkbox(f"ID {row_p['ID']} — {row_p['Material']}", value=val_atual, key=f"hab_{i}")
            novos_estados.append((i, novo_val))
            
        if st.form_submit_button("Salvar Alterações de Habilitação"):
            for i, val in novos_estados:
                st.session_state.permissoes_locais.loc[i, "Habilitado"] = val
            st.success(f"Permissões atualizadas com sucesso para o **{local_escolhido}**!")
            st.rerun()

# ==========================================
# 3. MOVIMENTAÇÕES & TRANSFERÊNCIAS
# ==========================================
elif menu == "Movimentações & Transferências":
    st.header("🔄 Registrar Entrada, Saída ou Transferência entre Locais")
    
    col1, col2 = st.columns(2)
    with col1:
        local_origem = st.selectbox("Local de Operação / Origem:", LOCAIS)
    with col2:
        tipo_mov = st.selectbox("Tipo de Operação:", ["Entrada (Recebimento)", "Transferência para Outro Local", "Saída Simples (Baixa)"])
        
    ids_habilitados_neste_local = df_perm[(df_perm["Local"] == local_origem) & (df_perm["Habilitado"] == True)]["ID"].tolist()
    cat_filtrado = cat[cat["ID"].isin(ids_habilitados_neste_local)]
    
    if not cat_filtrado.empty:
        id_num = st.selectbox("Selecione o Material por ID e Nome:", options=cat_filtrado["ID"].tolist(), format_func=lambda x: f"ID {x} — {cat_filtrado[cat_filtrado['ID']==x]['Material'].values[0]}")
        
        item_sel = cat_filtrado[cat_filtrado["ID"] == id_num].iloc[0]
        limpo_id = item_sel["ID"]
        nome_mat = item_sel["Material"]
        lote_padrao = item_sel["Lote"]
        fab_padrao = item_sel["Fabricacao"]
        val_auto = item_sel["Validade"]
        unidade_auto = item_sel["Unidade"]
        fator_padrao = float(item_sel["QtdPorPalete"])
        
        st.info(f"✨ **Dados Automáticos:** Padrão por Palete/Volume: **{fator_padrao} {unidade_auto}** | Validade: {val_auto}")
        
        destino_transf = None
        if tipo_mov == "Transferência para Outro Local":
            locais_possiveis = [l for l in LOCAIS if l != local_origem]
            destino_transf = st.selectbox("Local de Destino da Transferência:", locais_possiveis)
            
            dest_hab = df_perm[(df_perm["ID"] == limpo_id) & (df_perm["Local"] == destino_transf) & (df_perm["Habilitado"] == True)]
            if dest_hab.empty:
                st.warning(f"⚠️ **Atenção:** Este item está desabilitado no destino ({destino_transf}). Habilite-o na aba de Habilitação se desejar.")
                
        with st.form("form_mov"):
            lote_edit = st.text_input("Lote", value=lote_padrao)
            try:
                fab_obj = datetime.datetime.strptime(str(fab_padrao), "%Y-%m-%d").date()
            except:
                fab_obj = datetime.date.today()
            fab_edit = st.date_input("Data de Fabricação", value=fab_obj)
            
            qtd_paletes = st.number_input("Quantidade de Paletes / Volumes:", min_value=0.1, value=1.0, step=0.5)
            qtd_calculada = qtd_paletes * fator_padrao
            
            st.success(f"🧮 Cálculo Automático: {qtd_paletes} palete(s) × {fator_padrao} = **{qtd_calculada:.2f} {unidade_auto}**")
            
            resp = st.text_input("Responsável")
            obs = st.text_input("Observações")
            
            if st.form_submit_button("Confirmar Movimentação"):
                hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tipo_final = "Entrada" if "Entrada" in tipo_mov else ("Transferência Saída" if destino_transf else "Saída")
                
                nova_mov = {
                    "Data/Hora": hora_atual, "ID": limpo_id, "Material": nome_mat, "Tipo": tipo_final,
                    "Local": local_origem, "Destino_Transferencia": destino_transf if destino_transf else "-",
                    "Quantidade": qtd_calculada, "Fabricação": str(fab_edit), "Lote": lote_edit,
                    "Validade": val_auto, "Responsável": resp, "Obs": obs
                }
                df_aux = pd.DataFrame([nova_mov])
                
                if destino_transf:
                    mov_dest = {
                        "Data/Hora": hora_atual, "ID": limpo_id, "Material": nome_mat, "Tipo": "Transferência Entrada",
                        "Local": destino_transf, "Destino_Transferencia": local_origem,
                        "Quantidade": qtd_calculada, "Fabricação": str(fab_edit), "Lote": lote_edit,
                        "Validade": val_auto, "Responsável": resp, "Obs": f"Transferência automática de {local_origem}"
                    }
                    df_aux = pd.concat([df_aux, pd.DataFrame([mov_dest])], ignore_index=True)
                    
                st.session_state.movimentacoes = pd.concat([st.session_state.movimentacoes, df_aux], ignore_index=True)
                st.success("Movimentação e transferência executadas com sucesso!")
    else:
        st.warning(f"Nenhum material habilitado para uso no **{local_origem}**. Verifique a aba de Habilitação.")

# ==========================================
# 4. SAÍDA DE PRODUTO ACABADO (OFICINA)
# ==========================================
elif menu == "Saída de Produto Acabado (Oficina)":
    st.header("🏭 Produto Acabado na Oficina & Baixa de Insumos")
    
    with st.form("form_prod_acabado"):
        codigo_7_char = st.text_input("Código do Produto Acabado (EXATAMENTE 7 CARACTERES):", max_chars=7)
        resp_prod = st.text_input("Responsável")
        
        st.divider()
        st.subheader("🛒 Combo de Insumos Utilizados na Oficina")
        
        ids_hab_oficina = df_perm[(df_perm["Local"] == "Oficina de Revestimento") & (df_perm["Habilitado"] == True)]["ID"].tolist()
        cat_oficina = cat[cat["ID"].isin(ids_hab_oficina)]
        
        materiais_disponiveis = cat_oficina["Material"].tolist()
        insumos_escolhidos = st.multiselect("Selecione os Insumos Consumidos:", options=materiais_disponiveis)
        
        quantidades_consumidas = {}
        if insumos_escolhidos:
            for mat in insumos_escolhidos:
                item_info = cat_oficina[cat_oficina["Material"] == mat].iloc[0]
                quantidades_consumidas[mat] = {
                    "ID": item_info["ID"],
                    "Qtd": st.number_input(f"Qtd consumida de {mat} ({item_info['Unidade']}):", min_value=0.01, value=1.0, step=1.0, key=f"cons_{mat}")
                }
                
        if st.form_submit_button("Registrar Produção & Descontar Estoque"):
            if len(codigo_7_char.strip()) != 7:
                st.error("❌ O código do produto acabado precisa ter EXATAMENTE 7 caracteres!")
            elif not insumos_escolhidos:
                st.error("❌ Selecione ao menos um insumo consumido.")
            else:
                hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                registros_baixa = []
                for mat, dados in quantidades_consumidas.items():
                    item_base = cat_oficina[cat_oficina["Material"] == mat].iloc[0]
                    registros_baixa.append({
                        "Data/Hora": hora_atual, "ID": dados["ID"], "Material": mat,
                        "Tipo": "Produção Acabada (Baixa Insumos)", "Local": "Oficina de Revestimento",
                        "Destino_Transferencia": "-", "Quantidade": dados["Qtd"],
                        "Fabricação": item_base["Fabricacao"], "Lote": item_base["Lote"],
                        "Validade": item_base["Validade"], "Responsável": resp_prod,
                        "Obs": f"Consumido para Produto Acabado [Cod: {codigo_7_char}]"
                    })
                st.session_state.movimentacoes = pd.concat([st.session_state.movimentacoes, pd.DataFrame(registros_baixa)], ignore_index=True)
                st.success(f"✅ Produto Acabado [Cod: {codigo_7_char}] registrado e insumos descontados da Oficina com sucesso!")

# ==========================================
# 5. CADASTRO BASE DE ITENS
# ==========================================
elif menu == "Cadastro Base de Itens":
    st.header("📋 Cadastro Base de Materiais (Galpão / Origem)")
    st.dataframe(cat, use_container_width=True)
    
    st.divider()
    with st.form("novo_item_base"):
        st.subheader("➕ Adicionar Novo Item")
        novo_id = st.number_input("Número da ID", min_value=1, max_value=100, value=18, step=1)
        novo_mat = st.text_input("Nome do Material")
        novo_lote = st.text_input("Lote Padrão")
        nova_fab = st.date_input("Data de Fabricação", value=datetime.date.today())
        nova_val = st.text_input("Validade")
        nova_un = st.text_input("Unidade (Ex: KG, UN)")
        novo_fator = st.number_input("Quantidade Padrão por Palete/Volume", min_value=0.1, value=1.0, step=0.1)
        
        if st.form_submit_button("Cadastrar Novo Item") and novo_mat:
            novo_df = pd.DataFrame([{
                "ID": int(novo_id), "Material": novo_mat, "Lote": novo_lote, 
                "Fabricacao": str(nova_fab), "Validade": nova_val, "Unidade": novo_un,
                "QtdPorPalete": float(novo_fator), "Status": "Ativo"
            }])
            st.session_state.cat = pd.concat([st.session_state.cat, novo_df], ignore_index=True)
            
            novas_perms = []
            for loc in LOCAIS:
                novas_perms.append({"ID": int(novo_id), "Material": novo_mat, "Local": loc, "Habilitado": True})
            st.session_state.permissoes_locais = pd.concat([st.session_state.permissoes_locais, pd.DataFrame(novas_perms)], ignore_index=True)
            
            st.success("Item cadastrado e disponibilizado para habilitação em todos os locais!")
            st.rerun()
