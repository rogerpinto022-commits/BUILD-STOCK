import pandas as pd
import streamlit as st
import json
import os

st.set_page_config(page_title="BUILD STOCK", page_icon="📦", layout="centered")

ARQUIVO_DADOS = "estoque_id.json"

@st.cache_data(ttl=1)
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {"GAV-001": {"nome": "Gaveta Principal", "movimentacoes": []}}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    st.cache_data.clear()

if "estoque" not in st.session_state:
    st.session_state.estoque = carregar_dados()

st.title("📦 BUILD STOCK")

# GERENCIAMENTO DE GAVETAS
st.subheader("⚙️ Gerenciar Gavetas")
tab_criar, tab_excluir = st.tabs(["➕ Criar", "❌ Excluir"])

with tab_criar:
    col1, col2 = st.columns(2)
    with col1:
        novo_id = st.text_input("ID da Gaveta:", placeholder="Ex: GAV-001")
    with col2:
        nome_item = st.text_input("Descrição:", placeholder="Ex: Elétrica")
    
    if st.button("➕ Criar Gaveta", use_container_width=True):
        if novo_id and nome_item:
            id_limpo = novo_id.strip().upper()
            if id_limpo not in st.session_state.estoque:
                st.session_state.estoque[id_limpo] = {
                    "nome": nome_item.strip(),
                    "movimentacoes": []
                }
                salvar_dados(st.session_state.estoque)
                st.success(f"Gaveta {id_limpo} criada!")
                st.rerun()
            else:
                st.warning("Este ID já existe!")
        else:
            st.error("Preencha o ID e a Descrição!")

with tab_excluir:
    if st.session_state.estoque:
        id_para_excluir = st.selectbox("Escolha a Gaveta:", options=list(st.session_state.estoque.keys()))
        if st.button("🗑️ Confirmar Exclusão", type="primary", use_container_width=True):
            del st.session_state.estoque[id_para_excluir]
            salvar_dados(st.session_state.estoque)
            st.success("Gaveta removida!")
            st.rerun()
    else:
        st.info("Nenhuma gaveta cadastrada.")

st.divider()

# ACESSO E SOMA AUTOMÁTICA DA GAVETA
st.subheader("🔍 Acessar Gaveta")
id_buscado = st.text_input("Digite o ID da Gaveta:", placeholder="Ex: GAV-001").strip().upper()

if id_buscado:
    if id_buscado in st.session_state.estoque:
        gaveta = st.session_state.estoque[id_buscado]
        historico = gaveta["movimentacoes"]

        st.markdown(f"### 🗄️ ID: `{id_buscado}` | **{gaveta['nome']}**")

        # FORMULÁRIO DE ENTRADA E SAÍDA
        with st.form(key=f"form_{id_buscado}"):
            st.write("**Entrada / Saída de Material**")
            c_mat, c_marca = st.columns(2)
            with c_mat:
                material = st.text_input("Material:", placeholder="Ex: Parafuso")
            with c_marca:
                marca = st.text_input("Marca:", placeholder="Ex: Bosch")

            c_qtd, c_tipo = st.columns(2)
            with c_qtd:
                qtd = st.number_input("Quantidade:", min_value=1, value=1)
            with c_tipo:
                tipo = st.radio("Ação:", ["Entrada (+)", "Saída (-)"], horizontal=True)

            if st.form_submit_button("💾 Salvar Movimentação", use_container_width=True):
                if material and marca:
                    valor_final = int(qtd) if tipo == "Entrada (+)" else -int(qtd)
                    st.session_state.estoque[id_buscado]["movimentacoes"].append({
                        "material": material.strip().title(),
                        "marca": marca.strip().title(),
                        "operacao": tipo,
                        "quantidade": valor_final
                    })
                    salvar_dados(st.session_state.estoque)
                    st.success("Registrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Informe o Material e a Marca!")

        # SOMATÓRIO AUTOMÁTICO POR MATERIAL E MARCA
        if historico:
            df = pd.DataFrame(historico)
            
            df_resumo = (
                df.groupby(["material", "marca"], as_index=False)["quantidade"]
                .sum()
                .rename(columns={"material": "Material", "marca": "Marca", "quantidade": "Saldo Atual (UN)"})
            )

            st.write("---")
            st.write("📊 **Resumo do Estoque na Gaveta:**")
            st.dataframe(df_resumo, use_container_width=True, hide_index=True)

            with st.expander("📜 Ver Histórico Detalhado"):
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Gaveta vazia no momento.")

    else:
        st.error("Gaveta não encontrada! Verifique o ID.")