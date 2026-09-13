import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="BUILD STOCK BR",
    page_icon="📦",
    layout="wide",
)

st.title("📦 BUILD STOCK - BRASÍLIA")

# Menu lateral ou navegação simulada para o exemplo
menu = ["🆕 CADASTRO", "🔄 MOVIMENTAÇÕES", "📋 ESTOQUE", "📊 GRÁFICOS"]
escolha = st.sidebar.selectbox("Navegação", menu)

if escolha == "🆕 CADASTRO":
  st.subheader("Cadastro de Novo Lote")

  # Formulário de Cadastro
  with st.form(key="cadastro_form"):
    col1, col2 = st.columns(2)

    with col1:
      id_prod = st.text_input("🔖 ID *")
      descricao = st.text_input("DESCRIÇÃO *")
      marca = st.text_input("MARCA *")
      lote = st.text_input("LOTE *")

    with col2:
      fab_data = st.date_input("FABRICAÇÃO")
      validade_dias = st.number_input("VALIDADE DIAS", value=90)
      emb_externa = st.text_input("EMB EXTERNA", value="Palete")
      emb_interna = st.text_input("EMB INTERNA", value="Saco")

    col3, col4 = st.columns(2)
    with col3:
      # Chave corrigida/padronizada para evitar o KeyError
      qtd_int_por_ext = st.number_input(
          "QTD Saco POR Palete", value=40.0, format="%.2f"
      )
    with col4:
      medida_por_int = st.number_input(
          "MEDIDA POR Saco", value=25.0, format="%.2f"
      )

    un_final = st.selectbox("UN FINAL", ["KG", "UN", "L"])

    # Cálculo dinâmico para exibição prévia
    total_por_palete = qtd_int_por_ext * medida_por_int
    st.info(f"**TOTAL POR Palete: {total_por_palete:.2f} {un_final}**")

    submit_button = st.form_submit_button(label="💾 CADASTRAR")

    if submit_button:
      # Simulando o objeto p_e com chaves padronizadas em maiúsculas e snake_case
      p_e = {
          "ID": id_prod,
          "DESCRICAO": descricao,
          "MARCA": marca,
          "LOTE": lote,
          "FABRICACAO": str(fab_data),
          "VALIDADE_DIAS": validade_dias,
          "EMB_EXTERNA": emb_externa,
          "EMB_INTERNA": emb_interna,
          "QTD_INTERNA_POR_EXTERNA": qtd_int_por_ext,  # <- Chave unificada aqui!
          "MEDIDA_POR_INTERNA": medida_por_int,
          "UN_FINAL": un_final,
          "TOTAL_POR_EXTERNA": total_por_palete,
      }

      # Exemplo seguro onde a linha 106 original causava o erro:
      try:
        q_ext = 1.0  # Exemplo de quantidade externa padrão ou recebida
        # Linha ajustada que espelha a lógica original com segurança de chave
        q_int_tot = q_ext * float(p_e["QTD_INTERNA_POR_EXTERNA"])
        st.success(
            f"Cadastro realizado com sucesso! Total interno calculado: "
            f"{q_int_tot}"
        )
      except KeyError as e:
        st.error(
            f"Erro de chave encontrada: {e}. Verifique o dicionário de"
            " dados!"
        )

elif escolha == "📋 ESTOQUE":
  st.subheader("📋 Visualização de Estoque Atual")
  st.write("Aqui você poderá listar os itens cadastrados no seu banco de dados.")

elif escolha == "🔄 MOVIMENTAÇÕES":
  st.subheader("🔄 Controle de Entradas e Saídas")
  st.write("Registre as movimentações dos materiais do estoque.")

elif escolha == "📊 GRÁFICOS":
  st.subheader("📊 Gráficos ID x Data/Hora BR")
  st.write("Análise visual do fluxo de estoque.")
