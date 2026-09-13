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
